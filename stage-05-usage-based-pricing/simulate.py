import os
import random
import time

import meter

random.seed(7)
now = int(time.time())
if os.path.exists("ledger.db"):
    os.remove("ledger.db")
db = meter.connect("ledger.db")
meter.add_customer(db, "acme", cap=2_000)
meter.add_customer(db, "globex")
meter.grant_credits(db, "acme", 500, expires_at=now + 10 * 86400, category="promotional")
meter.grant_credits(db, "acme", 1_000)

results = {}
for i in range(300):
    e = {"transaction_id": f"evt-{i}", "customer_id": random.choice(["acme", "globex"]),
         "timestamp": now - random.choice([0, 0, 0, 60, 3600, 3 * 86400])}
    if random.random() < 0.8:
        e.update(event_type="agent_execution", quantity=1)
    else:
        e.update(event_type="tokens_processed", quantity=random.randint(500, 40_000))
    for _ in range(random.choice([1, 1, 1, 2, 3])):          # client retries
        r = meter.ingest(db, e, now)
        results[r] = results.get(r, 0) + 1

print("Ingest Results:", results)
d = time.gmtime(now)
lo, hi = meter.month_bounds(d.tm_year, d.tm_mon)
for cust in ("acme", "globex"):
    total = db.execute("SELECT COALESCE(SUM(credits), 0) FROM usage_events"
                       " WHERE customer_id=? AND ts >= ? AND ts < ?", (cust, lo, hi)).fetchone()[0]
    s = meter.statement(db, cust, d.tm_year, d.tm_mon)
    print(cust, "total usage credits:", round(total, 4), s)

print("acme, 10 credit run allowed?", meter.allowed(db, "acme", 10, now))
print("acme, 1,000,000 credit run allowed?", meter.allowed(db, "acme", 1_000_000, now))
