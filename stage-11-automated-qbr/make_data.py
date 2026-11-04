import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
accounts = pd.DataFrame([
    ("acme", "Acme Logistics", 40, 6000, 4000, 18, 2, 0.30, 45.0),
    ("globex", "Globex Health", 25, 4500, 3000, 25, 3, 0.25, 52.0),
], columns=["account_id", "name", "seats", "license_per_quarter", "onboarding_fee",
            "baseline_min", "tool_min", "displaced_share", "wage_per_hour"])

weeks = pd.date_range("2026-04-06", "2026-09-28", freq="W-MON")
rows = []
for a in accounts.itertuples():
    ramp = np.linspace(0.45, 0.80, len(weeks))
    for w, r in zip(weeks, ramp):
        wau = int(a.seats * r + rng.integers(-2, 3))
        rows.append((a.account_id, w.date().isoformat(), wau,
                     int(wau * rng.integers(8, 14))))
usage = pd.DataFrame(rows, columns=["account_id", "week_start", "weekly_active_users", "tasks_completed"])
accounts.to_csv("accounts.csv", index=False)
usage.to_csv("usage.csv", index=False)
print(f"Generated {len(accounts)} accounts and {len(usage)} usage rows.")
