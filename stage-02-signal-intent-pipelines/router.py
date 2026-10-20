import csv, hashlib, hmac, json, os, sqlite3, time
from typing import Optional
from urllib.parse import quote

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Request

DB_PATH = os.environ.get("ROUTER_DB", "signals.db")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
SHARED_SECRET = os.environ.get("SEGMENT_SHARED_SECRET", "")
IPINFO_TOKEN = os.environ.get("IPINFO_TOKEN", "")
TARGETS_CSV = os.environ.get("TARGETS_CSV", "targets.csv")
WINDOW_DAYS = int(os.environ.get("WINDOW_DAYS", "7"))
THRESHOLD = int(os.environ.get("THRESHOLD", "3"))
ISP_DOMAINS = {"comcast.com", "att.com", "verizon.com", "spectrum.com", "cox.com"}
app = FastAPI()


def db():
    conn = sqlite3.connect(DB_PATH, isolation_level=None, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS views (message_id TEXT PRIMARY KEY,
        domain TEXT NOT NULL, visit_key TEXT NOT NULL, ts INTEGER NOT NULL)""")
    conn.execute("CREATE INDEX IF NOT EXISTS views_domain_ts ON views(domain, ts)")
    conn.execute("CREATE TABLE IF NOT EXISTS alerts (domain TEXT NOT NULL, ts INTEGER NOT NULL)")
    return conn


def load_targets():
    with open(TARGETS_CSV, newline="", encoding="utf-8-sig") as f:
        return {r["domain"].strip().lower(): r for r in csv.DictReader(f)}


def signature_ok(raw, header):
    if not SHARED_SECRET:
        return True
    if not header:
        return False
    candidates = [raw]
    try:
        candidates.append(json.dumps(json.loads(raw), separators=(",", ":"),
                                     ensure_ascii=False).encode())
    except ValueError:
        pass
    key = SHARED_SECRET.encode()
    given = header.strip().lower().encode()
    return any(hmac.compare_digest(hmac.new(key, c, hashlib.sha1).hexdigest().encode(), given)
               for c in candidates)


def resolve_domain(evt):
    dom = ((evt.get("properties") or {}).get("company_domain") or "").strip().lower()
    ip = (evt.get("context") or {}).get("ip")
    if dom or not (ip and IPINFO_TOKEN):
        return dom or None
    try:
        r = httpx.get(f"https://api.ipinfo.io/lite/{ip}", params={"token": IPINFO_TOKEN}, timeout=3)
        dom = (r.json().get("as_domain") or "").lower() if r.status_code == 200 else ""
    except (httpx.HTTPError, ValueError):
        return None
    return None if dom in ISP_DOMAINS else dom or None


def slack_blocks(target, count):
    name, domain = target["name"], target["domain"]
    return {
        "text": f"{name} viewed pricing {count} times in {WINDOW_DAYS} days",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": f"Hot account: {name}"[:150]}},
            {"type": "section", "fields": [
                {"type": "mrkdwn", "text": f"*Account*\n{domain}"},
                {"type": "mrkdwn", "text": f"*Pricing visits*\n{count} in {WINDOW_DAYS} days"},
                {"type": "mrkdwn", "text": f"*Segment*\n{target['segment']}"}],
             "accessory": {"type": "button", "text": {"type": "plain_text", "text": "Open account"},
                           "url": f"https://crm.example.com/search?q={quote(domain)}"}},
            {"type": "context", "elements": [
                {"type": "mrkdwn", "text": "First-party signal. Company-level match, not a person."}]},
        ],
    }


def post_to_slack(payload):
    if not SLACK_WEBHOOK_URL:
        print("DRY RUN:", json.dumps(payload)[:200])
        return
    try:
        r = httpx.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        if r.status_code == 429:
            time.sleep(int(r.headers.get("Retry-After", "1")))
            r = httpx.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        r.raise_for_status()
    except httpx.HTTPError as exc:
        print("SLACK FAILED:", exc)


async def raw_body(request: Request) -> bytes:
    return await request.body()


@app.post("/events")
def events(background: BackgroundTasks, raw: bytes = Depends(raw_body),
           x_signature: Optional[str] = Header(None)):
    if not signature_ok(raw, x_signature):
        raise HTTPException(401, "bad signature")
    try:
        evt = json.loads(raw)
    except ValueError:
        raise HTTPException(400, "body is not JSON")
    if not isinstance(evt, dict) or not evt.get("messageId"):
        raise HTTPException(400, "messageId is required")
    path = (evt.get("properties") or {}).get("path")
    if evt.get("type") not in ("page", "track") or path not in ("/pricing", "/pricing/"):
        return {"status": "ignored"}
    domain = resolve_domain(evt)
    target = load_targets().get(domain or "")
    if not target or target["segment"] != "enterprise":
        return {"status": "not a target"}

    now = int(time.time())
    visitor = evt.get("anonymousId") or evt.get("userId") or "unknown"
    visit_key = f"{visitor}:{time.strftime('%Y-%m-%d', time.gmtime(now))}"
    conn = db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        cur = conn.execute("INSERT OR IGNORE INTO views VALUES (?,?,?,?)",
                           (evt["messageId"], domain, visit_key, now))
        if cur.rowcount == 0:
            conn.execute("COMMIT")
            return {"status": "duplicate"}
        since = now - WINDOW_DAYS * 86400
        (count,) = conn.execute(
            "SELECT COUNT(DISTINCT visit_key) FROM views WHERE domain=? AND ts>=?",
            (domain, since)).fetchone()
        recent = conn.execute("SELECT 1 FROM alerts WHERE domain=? AND ts>=?",
                              (domain, since)).fetchone()
        fire = count >= THRESHOLD and not recent
        if fire:
            conn.execute("INSERT INTO alerts VALUES (?,?)", (domain, now))
        conn.execute("COMMIT")
    finally:
        conn.close()
    if fire:
        background.add_task(post_to_slack, slack_blocks(target, count))
    return {"status": "alerted" if fire else "counted", "count": count}
