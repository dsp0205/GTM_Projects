import hashlib, hmac, json, os, time
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test123"
os.environ["INBOX_DB"] = ":memory:"
import webhook_app
c = webhook_app.app.test_client()
body = json.dumps({"id": "evt_1", "object": "event", "type": "invoice.paid", "created": 1, "data": {"object": {"id": "in_1"}}}).encode()

def sign(body, secret="whsec_test123", ts=None):
    ts = ts or int(time.time())
    sig = hmac.new(secret.encode(), f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"

print("good", c.post("/stripe/webhook", data=body, headers={"Stripe-Signature": sign(body)}).status_code)
print("dup", c.post("/stripe/webhook", data=body, headers={"Stripe-Signature": sign(body)}).status_code)
print("bad", c.post("/stripe/webhook", data=body, headers={"Stripe-Signature": sign(body, "whsec_wrong")}).status_code)
print("old", c.post("/stripe/webhook", data=body, headers={"Stripe-Signature": sign(body, ts=int(time.time()) - 3600)}).status_code)
print("nohd", c.post("/stripe/webhook", data=body).status_code)
print("stored rows:", webhook_app.db.execute("select count(*) from stripe_events").fetchone()[0])
