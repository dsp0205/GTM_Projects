from datetime import datetime, timezone
import meter

NOW = int(datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc).timestamp())
DAY = 86400


def ev(txn, qty=1, etype="agent_execution", ts=NOW):
    return {"transaction_id": txn, "customer_id": "acme", "event_type": etype,
            "timestamp": ts, "quantity": qty}


def fresh():
    c = meter.connect()
    meter.add_customer(c, "acme", cap=500)
    return c


def test_duplicates_and_burn_order():
    c = fresh()
    meter.grant_credits(c, "acme", 15, expires_at=NOW + 5 * DAY, category="promotional")
    meter.grant_credits(c, "acme", 100)
    assert meter.ingest(c, ev("a"), NOW) == "accepted"
    assert meter.ingest(c, ev("a"), NOW) == "duplicate"
    meter.ingest(c, ev("b"), NOW)
    left = [r[0] for r in c.execute("SELECT remaining FROM credit_grants ORDER BY id")]
    assert left == [0, 95]                      # expiring promo grant burned first
    meter.ingest(c, ev("big", qty=12), NOW)     # 120 credits, 95 left
    s = meter.statement(c, "acme", 2026, 10)
    assert s["overage_credits"] == 25 and s["credits_from_grants"] == 115


def test_late_event_and_cap():
    c = fresh()
    meter.grant_credits(c, "acme", 50, expires_at=NOW - DAY)    # expired yesterday
    assert meter.ingest(c, ev("late", ts=NOW - 3 * DAY), NOW) == "accepted"
    assert c.execute("SELECT remaining FROM credit_grants").fetchone()[0] == 40
    assert meter.ingest(c, ev("old", ts=NOW - 36 * DAY), NOW) == "rejected:too_old"
    meter.ingest(c, ev("t", qty=480_000, etype="tokens_processed"), NOW)
    assert meter.allowed(c, "acme", 10, NOW) is True
    assert meter.allowed(c, "acme", 11, NOW) is False


if __name__ == "__main__":
    test_duplicates_and_burn_order()
    test_late_event_and_cap()
    print("ok")
