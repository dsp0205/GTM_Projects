from datetime import timedelta
import numpy as np
import pandas as pd

AS_OF = pd.Timestamp("2026-10-07")
N = 1500
rng = np.random.default_rng(7)

PLANS = {"starter": (50_000, 6_000), "team": (500_000, 24_000), "scale": (5_000_000, 90_000)}
names = rng.choice(list(PLANS), size=N, p=[0.55, 0.35, 0.10])
renewal = [AS_OF + timedelta(days=int(d)) for d in rng.integers(-450, 90, size=N)]

accounts, usage = [], []
for i in range(N):
    quota, arr = PLANS[names[i]]
    arr = int(arr * rng.uniform(0.7, 1.4))
    end = renewal[i]
    days = pd.date_range(end - timedelta(days=364), end, freq="D")
    base = quota / 30 * rng.uniform(0.15, 0.9)
    t = np.arange(len(days))
    weekday = np.where(days.dayofweek < 5, 1.0, 0.3)
    level = np.ones(len(days)) * (1 + rng.uniform(-0.1, 0.5) * t / 365)
    churner = rng.random() < 0.20
    quiet = churner and rng.random() < 0.25
    if churner and not quiet:
        start = len(days) - rng.integers(35, 130)
        level[start:] *= np.exp(-rng.uniform(0.01, 0.04) * (t[start:] - start))
    if not churner and rng.random() < 0.12:
        s = len(days) - rng.integers(20, 80)
        level[s:s + 21] *= rng.uniform(0.2, 0.5)
    calls = rng.poisson(base * level * weekday * rng.lognormal(0, 0.25, len(days)))
    keep = days <= AS_OF
    usage.append(pd.DataFrame({"account_id": i, "date": days[keep], "api_calls": calls[keep]}))
    renewed = np.nan if end > AS_OF else float(not churner)
    accounts.append(dict(account_id=i, plan=names[i], quota_30d=quota, arr=arr,
                         renewal_date=end.date(), renewed=renewed))

pd.DataFrame(accounts).to_csv("accounts.csv", index=False)
pd.concat(usage).to_csv("usage.csv", index=False)
print(len(accounts), "accounts written")
