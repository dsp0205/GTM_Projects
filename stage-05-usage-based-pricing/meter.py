import math
import sqlite3
import time
from datetime import datetime, timezone

LATE_WINDOW_S = 35 * 86400
FUTURE_SKEW_S = 300
OVERAGE_CENTS_PER_CREDIT = 1.5
RATE_CARD = {
    "agent_execution": lambda qty: 10.0 * qty,
    "tokens_processed": lambda qty: qty / 1000.0,
}
SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
  id TEXT PRIMARY KEY, stripe_customer_id TEXT, monthly_cap_credits REAL);
CREATE TABLE IF NOT EXISTS usage_events (
  transaction_id TEXT PRIMARY KEY,
  customer_id TEXT NOT NULL REFERENCES customers(id),
  event_type TEXT NOT NULL, ts INTEGER NOT NULL, quantity REAL NOT NULL,
  credits REAL NOT NULL, received_at INTEGER NOT NULL,
  forwarded INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS credit_grants (
  id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id TEXT NOT NULL,
  credits REAL NOT NULL, remaining REAL NOT NULL,
  expires_at INTEGER, category TEXT NOT NULL DEFAULT 'paid');
CREATE TABLE IF NOT EXISTS credit_ledger (
  id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id TEXT NOT NULL,
  grant_id INTEGER, transaction_id TEXT NOT NULL,
  delta REAL NOT NULL, ts INTEGER NOT NULL);
"""


def connect(path=":memory:"):
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def add_customer(conn, cid, stripe_id=None, cap=None):
    conn.execute("INSERT OR REPLACE INTO customers VALUES (?, ?, ?)", (cid, stripe_id, cap))


def grant_credits(conn, cid, credits, expires_at=None, category="paid"):
    conn.execute("INSERT INTO credit_grants (customer_id, credits, remaining, expires_at,"
                 " category) VALUES (?, ?, ?, ?, ?)",
                 (cid, credits, credits, expires_at, category))


def ingest(conn, event, now=None):
    """Return 'accepted', 'duplicate' or 'rejected:<reason>'."""
    now = int(now if now is not None else time.time())
    try:
        txn, cust = str(event["transaction_id"]), str(event["customer_id"])
        etype, ts = event["event_type"], int(event["timestamp"])
        qty = float(event["quantity"])
    except (KeyError, TypeError, ValueError, OverflowError):
        return "rejected:malformed"
    if not txn or etype not in RATE_CARD or not math.isfinite(qty) or qty < 0:
        return "rejected:invalid"
    if ts < now - LATE_WINDOW_S:
        return "rejected:too_old"
    if ts > now + FUTURE_SKEW_S:
        return "rejected:future"
    credits = RATE_CARD[etype](qty)
    conn.execute("BEGIN IMMEDIATE")
    try:
        if not conn.execute("SELECT 1 FROM customers WHERE id=?", (cust,)).fetchone():
            conn.execute("ROLLBACK")
            return "rejected:unknown_customer"
        cur = conn.execute(
            "INSERT OR IGNORE INTO usage_events (transaction_id, customer_id, event_type,"
            " ts, quantity, credits, received_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (txn, cust, etype, ts, qty, credits, now))
        if cur.rowcount == 0:
            conn.execute("ROLLBACK")
            return "duplicate"
        _burn(conn, cust, txn, credits, ts)
        conn.execute("COMMIT")
        return "accepted"
    except Exception:
        conn.execute("ROLLBACK")
        raise


def _burn(conn, cust, txn, credits, ts):
    """Spend grants valid at usage time, soonest expiry first. The rest is overage."""
    left = credits
    grants = conn.execute(
        "SELECT id, remaining FROM credit_grants WHERE customer_id=? AND remaining > 0"
        " AND (expires_at IS NULL OR expires_at > ?)"
        " ORDER BY expires_at IS NULL, expires_at, id", (cust, ts)).fetchall()
    sql = "INSERT INTO credit_ledger (customer_id, grant_id, transaction_id, delta, ts) VALUES (?,?,?,?,?)"
    for g in grants:
        take = min(left, g["remaining"])
        if take <= 0:
            break
        conn.execute("UPDATE credit_grants SET remaining = remaining - ? WHERE id=?",
                     (take, g["id"]))
        conn.execute(sql, (cust, g["id"], txn, -take, ts))
        left -= take
    if left > 1e-9:
        conn.execute(sql, (cust, None, txn, -left, ts))


def month_bounds(year, month):
    lo = datetime(year, month, 1, tzinfo=timezone.utc)
    hi = datetime(year + (month == 12), month % 12 + 1, 1, tzinfo=timezone.utc)
    return int(lo.timestamp()), int(hi.timestamp())


def allowed(conn, cust, credits_needed, now=None):
    """Call before the agent runs. This is the hard spend cap."""
    d = datetime.fromtimestamp(now if now is not None else time.time(), timezone.utc)
    row = conn.execute("SELECT monthly_cap_credits FROM customers WHERE id=?", (cust,)).fetchone()
    if row is None:
        return False
    if row[0] is None:
        return True
    lo, hi = month_bounds(d.year, d.month)
    used = conn.execute("SELECT COALESCE(SUM(credits), 0) FROM usage_events"
                        " WHERE customer_id=? AND ts >= ? AND ts < ?", (cust, lo, hi)).fetchone()[0]
    return used + credits_needed <= row[0]


def statement(conn, cust, year, month):
    lo, hi = month_bounds(year, month)
    r = conn.execute(
        "SELECT COALESCE(-SUM(CASE WHEN grant_id IS NOT NULL THEN delta END), 0) AS grants,"
        " COALESCE(-SUM(CASE WHEN grant_id IS NULL THEN delta END), 0) AS overage"
        " FROM credit_ledger WHERE customer_id=? AND ts >= ? AND ts < ?", (cust, lo, hi)).fetchone()
    return {"credits_from_grants": round(r["grants"], 4),
            "overage_credits": round(r["overage"], 4),
            "overage_cents": round(r["overage"] * OVERAGE_CENTS_PER_CREDIT)}
