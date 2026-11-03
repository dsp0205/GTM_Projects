import datetime as dt
import duckdb
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 4000
START = dt.datetime(2025, 1, 1)

CH = {
    "linkedin_ads": (1.15, 0.55, 0.0),
    "webinar":      (2.00, 0.08, 0.35),
    "cold_email":   (1.10, 0.20, 0.55),
    "organic":      (1.00, 0.10, 0.60),
}
sig = lambda x: 1 / (1 + np.exp(-x))
days = lambda lo, hi: dt.timedelta(days=float(rng.uniform(lo, hi)))
contacts, touches, opps, roles = [], [], [], []
truth = dict.fromkeys(CH, 0.0)
cid = oid = 0

for acct in range(N):
    intent = rng.beta(2, 5)
    members = []
    for _ in range(int(rng.integers(1, 7))):
        cid += 1
        members.append(cid)
        contacts.append((cid, acct, START + days(0, 330)))
    t_first = min(c[2] for c in contacts[-len(members):])
    logit = -4.0 + 4.0 * intent + 0.8
    last_touch = t_first
    hit = [k for k, (m, p0, s) in CH.items() if rng.random() < min(p0 + s * intent, 0.95)]
    logit += sum(np.log(CH[k][0]) for k in hit)
    p_opp = 0.35 + 0.4 * intent
    for k in hit:
        for _ in range(int(rng.integers(1, 5 if k == "linkedin_ads" else 3))):
            ts = t_first + days(0, 150)
            last_touch = max(last_touch, ts)
            touches.append((acct, int(rng.choice(members)), k, ts))
        truth[k] += p_opp * (sig(logit) - sig(logit - np.log(CH[k][0])))
    if rng.random() < p_opp:
        oid += 1
        created = last_touch + days(1, 30)
        opps.append((oid, acct, created, created + days(30, 120),
                     "won" if rng.random() < sig(logit) else "lost",
                     round(float(rng.lognormal(10.6, 0.5)), -2)))
        for c in rng.choice(members, size=max(1, len(members) // 2), replace=False):
            roles.append((oid, int(c), "champion" if c == members[0] else "influencer"))

con = duckdb.connect("revops.duckdb")
tables = {
    "contacts": (contacts, ["contact_id", "account_id", "created_at"]),
    "touches": ([(i + 1, *t) for i, t in enumerate(touches)],
                ["touch_id", "account_id", "contact_id", "channel", "touch_ts"]),
    "opportunities": (opps, ["opp_id", "account_id", "created_at", "closed_at", "stage", "amount"]),
    "opportunity_contact_roles": (roles, ["opp_id", "contact_id", "role"]),
}
for name, (rows, cols) in tables.items():
    df = pd.DataFrame(rows, columns=cols)
    con.execute(f"create or replace table {name} as select * from df")

print({k: round(float(v), 1) for k, v in truth.items()}, "true incremental wins")
print(len(contacts), "contacts,", len(touches), "touches,", len(opps), "opps,", sum(o[4] == "won" for o in opps), "won")
con.close()
