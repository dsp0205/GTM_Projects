import random
import sqlite3
from collections import Counter

SQL = """
WITH f AS (
  SELECT s.account_id, MIN(s.created_at) AS first_day,
         MAX(c.channel IN ('peer_word_of_mouth', 'community')) AS wom
  FROM signups s JOIN coded_answers c USING (signup_id) GROUP BY s.account_id)
SELECT a.employees, f.wom,
       EXISTS (SELECT 1 FROM opportunities o WHERE o.account_id = a.account_id
               AND o.created_at <= date(f.first_day, '+90 days'))
FROM accounts a JOIN f USING (account_id)"""

def band(n):
    return "small" if n < 200 else "mid" if n < 2000 else "large"

def cohen_kappa(a, b):
    po = sum(x == y for x, y in zip(a, b)) / len(a)
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in ca) / len(a) ** 2
    if pe == 1:
        return 1.0 if po == 1 else 0.0
    return (po - pe) / (1 - pe)

def lift(rows):
    yes = [r["opp"] for r in rows if r["wom"]]
    no = [r["opp"] for r in rows if not r["wom"]]
    return sum(yes) / len(yes) - sum(no) / len(no) if yes and no else None

def adjusted_lift(rows):
    parts = [[r for r in rows if r["band"] == b] for b in ("small", "mid", "large")]
    pairs = [(lift(p), len(p)) for p in parts if lift(p) is not None]
    return sum(d * n for d, n in pairs) / sum(n for _, n in pairs)

if __name__ == "__main__":
    rows = [{"band": band(e), "wom": w, "opp": o}
            for e, w, o in sqlite3.connect("dark_social.db").execute(SQL)]
    print(f"accounts {len(rows)}")
    print(f"raw WOM lift in P(opp)      = {lift(rows):+.3f}")
    print(f"size-adjusted WOM lift      = {adjusted_lift(rows):+.3f}")
    rng = random.Random(7)
    boots = sorted(adjusted_lift(rng.choices(rows, k=len(rows))) for _ in range(2000))
    print(f"95% bootstrap CI (adjusted) = [{boots[50]:+.3f}, {boots[1949]:+.3f}]")
