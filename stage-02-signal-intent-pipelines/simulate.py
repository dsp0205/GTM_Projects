import hashlib, hmac, json, os, sys
import httpx

URL = os.environ.get("ROUTER_URL", "http://127.0.0.1:8000/events")
SECRET = os.environ.get("SEGMENT_SHARED_SECRET", "")
domain = sys.argv[1] if len(sys.argv) > 1 else "acme.com"

for visitor in ("v1", "v2", "v3", "v4"):
    evt = {"type": "page", "messageId": f"sim-{domain}-{visitor}", "anonymousId": visitor,
           "properties": {"path": "/pricing", "company_domain": domain}}
    body = json.dumps(evt, separators=(",", ":")).encode()
    headers = {"content-type": "application/json"}
    if SECRET:
        headers["x-signature"] = hmac.new(SECRET.encode(), body, hashlib.sha1).hexdigest()
    r = httpx.post(URL, content=body, headers=headers, timeout=5)
    print(domain, visitor, "->", r.status_code, r.json())
