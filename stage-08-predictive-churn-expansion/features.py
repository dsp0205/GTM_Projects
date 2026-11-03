import numpy as np
import pandas as pd

FEATURES = ["ratio_7_28", "ratio_28_prev28", "slope_12w", "drawdown", "active_days_28",
            "days_since_call", "utilization", "log_arr", "plan_rank"]
PLAN_RANK = {"starter": 0, "team": 1, "scale": 2}

def one_account(calls, quota):
    c7, c28, p28 = calls[-7:].sum(), calls[-28:].sum(), calls[-56:-28].sum()
    weekly = calls[-84:].reshape(12, 7).sum(axis=1)
    slope = np.polyfit(np.arange(12), np.log1p(weekly), 1)[0]
    rolling28 = np.convolve(calls[-252:], np.ones(28), mode="valid")
    nonzero = np.flatnonzero(calls)
    return {
        "ratio_7_28": (c7 / 7 + 1) / (c28 / 28 + 1),
        "ratio_28_prev28": (c28 + 1) / (p28 + 1),
        "slope_12w": slope,
        "drawdown": c28 / max(rolling28.max(), 1),
        "active_days_28": int((calls[-28:] > 0).sum()),
        "days_since_call": len(calls) - 1 - nonzero[-1] if len(nonzero) else len(calls),
        "utilization": c28 / quota,
    }

def build(accounts, usage, snapshot):
    rows = []
    for acc in accounts.itertuples():
        if acc.account_id not in usage:
            continue
        u = usage[acc.account_id]
        last_day = snapshot[acc.account_id] - pd.Timedelta(1, "D")
        days = pd.date_range(u.index.min(), last_day)
        calls = u.reindex(days, fill_value=0).to_numpy(dtype=float)
        if len(calls) < 252:
            continue
        row = one_account(calls, acc.quota_30d)
        row.update(account_id=acc.account_id, log_arr=np.log(acc.arr),
                   plan_rank=PLAN_RANK[acc.plan])
        rows.append(row)
    if not rows:
        return pd.DataFrame(columns=FEATURES)
    return pd.DataFrame(rows).set_index("account_id")

def load(path_accounts="accounts.csv", path_usage="usage.csv"):
    accounts = pd.read_csv(path_accounts, parse_dates=["renewal_date"])
    usage = pd.read_csv(path_usage, parse_dates=["date"])
    series = {k: g.set_index("date")["api_calls"] for k, g in usage.groupby("account_id")}
    return accounts, series
