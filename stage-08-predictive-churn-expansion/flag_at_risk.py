import argparse
import os
import joblib
import pandas as pd
import requests

from features import FEATURES, build, load

ap = argparse.ArgumentParser()
ap.add_argument("--as-of", default=None, help="YYYY-MM-DD, default: the day after the newest usage row")
ap.add_argument("--within", type=int, default=1, help="days of catch-up for missed runs")
ap.add_argument("--top", type=int, default=25, help="how many accounts a CSM can review")
args = ap.parse_args()

accounts, usage = load()
newest = max(s.index.max() for s in usage.values())
today = pd.Timestamp(args.as_of) if args.as_of else newest + pd.Timedelta(1, "D")
accounts["days_left"] = (accounts["renewal_date"] - today).dt.days
due = accounts[(accounts["days_left"] <= 45) & (accounts["days_left"] > 45 - args.within)]
if due.empty:
    raise SystemExit("no accounts in the window")

X = build(due, usage, pd.Series(today, index=due["account_id"]))
if X.empty:
    raise SystemExit("no accounts with enough usage history")
model = joblib.load("churn_model.joblib")
out = due.set_index("account_id").loc[X.index, ["plan", "arr", "renewal_date"]].copy()
out["risk"] = model.predict_proba(X[FEATURES])[:, 1]
out["usage_vs_prev_28d"] = X["ratio_28_prev28"] - 1
out = out.sort_values("risk", ascending=False).head(args.top)
out.to_csv(f"at_risk_{today.date()}.csv")
print(out.head(10).to_string(float_format=lambda v: f"{v:.2f}"))

webhook = os.environ.get("SLACK_WEBHOOK_URL")
if webhook:
    lines = [f"Account {i} ({r.plan}, ) renews {r.renewal_date:%Y-%m-%d}: "
             f"risk {r.risk:.0%}, usage {r.usage_vs_prev_28d:+.0%} vs prior 28 days"
             for i, r in out.head(10).iterrows()]
    resp = requests.post(webhook, json={"text": "Churn risk, 45 days out:\n" + "\n".join(lines)},
                         timeout=10)
    resp.raise_for_status()
