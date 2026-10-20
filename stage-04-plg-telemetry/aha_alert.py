import hashlib
import hmac
import json
import os
import sqlite3
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

DB_PATH = os.environ.get("PQL_DB", "pql.db")
SECRET = os.environ.get("INGEST_SECRET", "dev-secret").encode()
SLACK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
AHA_EVENT = "API Request Completed"
AHA_CALLS = 100
AHA_DAYS = 7
PQL_MIN_SCORE = 70
RULE = "aha_api_100_in_7d"
FREE_MAIL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  message_id TEXT PRIMARY KEY, account_id TEXT, user_id TEXT,
  name TEXT, ts TEXT, status INTEGER);
CREATE INDEX IF NOT EXISTS ix_events ON events (account_id, name, ts);
CREATE TABLE IF NOT EXISTS accounts (
  account_id TEXT PRIMARY KEY, name TEXT, plan TEXT,
  employees INTEGER, created_at TEXT);
CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY, email TEXT, account_id TEXT);
CREATE TABLE IF NOT EXISTS alerts (
  account_id TEXT, rule TEXT, fired_at TEXT, score INTEGER,
  PRIMARY KEY (account_id, rule));
"""

def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db

def to_utc(s):
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)

def fmt(d):
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

def score_account(acct, calls, users, emails):
    n = acct["employees"] or 0
    fit = 40 if n >= 200 else 25 if n >= 20 else 10 if n >= 5 else 0
    if any(e.split("@")[-1].lower() not in FREE_MAIL for e in emails):
        fit += 10
    usage = 30 if calls >= AHA_CALLS else 0
    usage += 10 if users >= 2 else 0
    usage += 10 if calls >= 3 * AHA_CALLS else 0
    return fit + usage, {"fit": fit, "usage": usage}

def evaluate(db, account_id):
    acct = db.execute("SELECT * FROM accounts WHERE account_id = ?",
                      (account_id,)).fetchone()
    if not acct or acct["plan"] != "free" or not acct["created_at"]:
        return None
    start = to_utc(acct["created_at"])
    row = db.execute(
        "SELECT COUNT(*) AS calls, COUNT(DISTINCT user_id) AS users FROM events "
        "WHERE account_id = ? AND name = ? AND status BETWEEN 200 AND 299 "
        "AND ts >= ? AND ts < ?",
        (account_id, AHA_EVENT, fmt(start), fmt(start + timedelta(days=AHA_DAYS))),
    ).fetchone()
    if row["calls"] < AHA_CALLS:
        return None
    emails = [r["email"] for r in db.execute(
        "SELECT email FROM users WHERE account_id = ? AND email IS NOT NULL",
        (account_id,))]
    score, parts = score_account(acct, row["calls"], row["users"], emails)
    if score < PQL_MIN_SCORE:
        if row["calls"] == AHA_CALLS:
            print(f"usage-only, no alert: {account_id} score={score} {parts}")
        return None
    claim = db.execute(
        "INSERT OR IGNORE INTO alerts (account_id, rule, fired_at, score) "
        "VALUES (?, ?, ?, ?)",
        (account_id, RULE, fmt(datetime.now(timezone.utc)), score))
    db.commit()
    if claim.rowcount == 0:
        return None
    msg = (f":rotating_light: PQL: {acct['name']} ({account_id}) has {row['calls']} "
           f"successful API calls, {row['users']} user(s), "
           f"{acct['employees']} employees, score {score} {parts}.")
    try:
        send_slack(msg)
    except Exception as exc:
        db.execute("DELETE FROM alerts WHERE account_id = ? AND rule = ?",
                   (account_id, RULE))
        db.commit()
        print(f"slack failed, will retry: {exc}", file=sys.stderr)
        return None
    return score

def send_slack(text):
    if not SLACK_URL:
        print(f"[dry run] {text}")
        return
    req = urllib.request.Request(
        SLACK_URL, data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        resp.read()

def handle_event(db, ev):
    kind, uid = ev.get("type"), ev.get("userId")
    if kind == "identify":
        email = (ev.get("traits") or {}).get("email")
        db.execute("INSERT INTO users (user_id, email) VALUES (?, ?) "
                   "ON CONFLICT(user_id) DO UPDATE SET "
                   "email = COALESCE(excluded.email, users.email)",
                   (uid, email))
    elif kind == "group":
        t, gid = ev.get("traits") or {}, ev.get("groupId")
        db.execute(
            "INSERT INTO accounts (account_id, name, plan, employees, created_at) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT(account_id) DO UPDATE SET "
            "name = COALESCE(excluded.name, accounts.name), "
            "plan = COALESCE(excluded.plan, accounts.plan), "
            "employees = COALESCE(excluded.employees, accounts.employees), "
            "created_at = COALESCE(excluded.created_at, accounts.created_at)",
            (gid, t.get("name"), t.get("plan"), t.get("employees"), t.get("createdAt")))
        db.execute("INSERT INTO users (user_id, account_id) VALUES (?, ?) "
                   "ON CONFLICT(user_id) DO UPDATE SET account_id = excluded.account_id",
                   (uid, gid))
    elif kind == "track":
        gid = (ev.get("context") or {}).get("groupId")
        if not gid:
            r = db.execute("SELECT account_id FROM users WHERE user_id = ?",
                           (uid,)).fetchone()
            gid = r["account_id"] if r else None
        if not gid or not ev.get("messageId"):
            return
        status = (ev.get("properties") or {}).get("status_code")
        when = to_utc(ev["timestamp"]) if ev.get("timestamp") else datetime.now(timezone.utc)
        db.execute("INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?, ?, ?)",
                   (ev["messageId"], gid, uid, ev.get("event"), fmt(when), status))
        db.commit()
        if ev.get("event") == AHA_EVENT:
            evaluate(db, gid)
    db.commit()

class Receiver(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        want = hmac.new(SECRET, body, hashlib.sha1).hexdigest().encode()
        got = self.headers.get("X-Signature", "").encode()
        if not hmac.compare_digest(want, got):
            return self._reply(401, {"error": "bad signature"})
        try:
            data = json.loads(body)
        except ValueError:
            return self._reply(400, {"error": "bad json"})
        events = data if isinstance(data, list) else data.get("batch", [data])
        db = connect()
        for ev in events:
            handle_event(db, ev)
        db.close()
        self._reply(200, {"processed": len(events)})

    def _reply(self, code, obj):
        out = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

def post(events, url="http://127.0.0.1:8080/events"):
    body = json.dumps({"batch": events}).encode()
    sig = hmac.new(SECRET, body, hashlib.sha1).hexdigest()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json", "X-Signature": sig})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode()

def simulate():
    now = datetime.now(timezone.utc)
    signup = fmt(now - timedelta(days=2))
    plan = [("acct_acme", "Acme Logistics", 250,
             ["ana@acme.example", "raj@acme.example"], 130),
            ("acct_tiny", "Solo Dev", 1, ["solo@gmail.com"], 120),
            ("acct_slow", "Slow Corp", 120, ["sam@slow.example"], 40)]
    events = []
    for acct, name, staff, emails, calls in plan:
        for i, email in enumerate(emails):
            uid = f"{acct}_u{i}"
            events.append({"type": "identify", "userId": uid,
                           "traits": {"email": email}})
            events.append({"type": "group", "userId": uid, "groupId": acct,
                           "traits": {"name": name, "plan": "free",
                                      "employees": staff, "createdAt": signup}})
        for n in range(calls):
            when = now - timedelta(days=1, minutes=calls - n)
            events.append({
                "type": "track", "event": AHA_EVENT, "messageId": f"sim-{acct}-{n}",
                "userId": f"{acct}_u{n % len(emails)}", "timestamp": fmt(when) + "Z",
                "context": {"groupId": acct},
                "properties": {"endpoint": "/v1/transcribe", "status_code": 200}})
    print(post(events))
    print(post(events))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "serve":
        print("listening on http://127.0.0.1:8080/events")
        HTTPServer(("127.0.0.1", 8080), Receiver).serve_forever()
    elif cmd == "simulate":
        simulate()
    else:
        sys.exit(__doc__)
