from collections import Counter
from itertools import combinations
from math import factorial

import duckdb
import numpy as np

con = duckdb.connect("revops.duckdb", read_only=True)
rows = con.execute("""
    select list(t.channel order by t.touch_ts, t.touch_id) as path,
           coalesce(bool_or(o.stage = 'won'), false) as converted
    from touches t
    left join opportunities o on o.account_id = t.account_id
    where o.created_at is null or t.touch_ts <= o.created_at
    group by t.account_id
""").fetchall()
journeys = [(list(p), bool(c)) for p, c in rows]

def p_conv(journeys, drop=None):
    n = Counter()
    for path, conv in journeys:
        seq = ["start", *path, "conv" if conv else "null"]
        for a, b in zip(seq, seq[1:]):
            if a != drop:
                n[(a, "null" if b == drop else b)] += 1
    out = Counter()
    for (a, _), c in n.items():
        out[a] += c
    ix = {s: i for i, s in enumerate(sorted(out))}
    Q, r = np.zeros((len(ix), len(ix))), np.zeros(len(ix))
    for (a, b), c in n.items():
        if b == "conv":
            r[ix[a]] += c / out[a]
        elif b in ix:
            Q[ix[a], ix[b]] += c / out[a]
    return np.linalg.solve(np.eye(len(ix)) - Q, r)[ix["start"]]

channels = sorted({c for p, _ in journeys for c in p})
base = p_conv(journeys)
removal = {c: 1 - p_conv(journeys, drop=c) / base for c in channels}
markov = {c: v / sum(removal.values()) for c, v in removal.items()}

def shapley(journeys, channels):
    sets = Counter(frozenset(p) for p, conv in journeys if conv)
    v = lambda S: sum(n for s, n in sets.items() if s <= S)
    k, out = len(channels), {}
    for c in channels:
        rest = [x for x in channels if x != c]
        out[c] = sum(
            factorial(len(S)) * factorial(k - len(S) - 1) / factorial(k)
            * (v(frozenset(S) | {c}) - v(frozenset(S)))
            for m in range(k) for S in combinations(rest, m))
    return {c: x / sum(out.values()) for c, x in out.items()}

shap = shapley(journeys, channels)
print(f"{'channel':14}{'markov':>8}{'shapley':>9}")
for c in channels:
    print(f"{c:14}{markov[c]:8.1%}{shap[c]:9.1%}")
con.close()
