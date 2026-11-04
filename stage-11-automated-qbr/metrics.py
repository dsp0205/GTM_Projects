from dataclasses import dataclass
import pandas as pd

LOAD_FACTOR = 46.89 / 32.82
REALIZATION = 0.80

@dataclass
class Fact:
    id: str
    label: str
    value: float
    fmt: str

    def show(self) -> str:
        v = self.value
        if v != v:
            return "not reached"
        return {"int": f"{v:,.0f}", "usd": f"", "pct": f"{v:.0%}",
                "hours": f"{v:,.0f} hours", "months": f"{v:.1f} months"}[self.fmt]

def in_quarter(usage: pd.DataFrame, q: pd.Period) -> pd.DataFrame:
    d = pd.to_datetime(usage["week_start"])
    return usage[(d >= q.start_time) & (d <= q.end_time)]

def compute(account: pd.Series, usage: pd.DataFrame, q: pd.Period) -> dict[str, Fact]:
    u = usage[usage.account_id == account.account_id]
    cur, prev = in_quarter(u, q), in_quarter(u, q - 1)
    tasks, tasks_prev = cur.tasks_completed.sum(), prev.tasks_completed.sum()
    wau = cur.weekly_active_users.mean()
    minutes_saved = account.baseline_min - account.tool_min
    hours = tasks * account.displaced_share * minutes_saved / 60 * REALIZATION
    loaded = account.wage_per_hour * LOAD_FACTOR
    value = hours * loaded
    cost = account.license_per_quarter
    net_monthly = (value - cost) / 3
    payback = account.onboarding_fee / net_monthly if net_monthly > 0 else float("nan")
    f = [
        Fact("tasks", "Tasks completed this quarter", tasks, "int"),
        Fact("tasks_change", "Change in tasks vs last quarter", tasks / tasks_prev - 1, "pct"),
        Fact("utilization", "Average weekly active users / licensed seats", wau / account.seats, "pct"),
        Fact("hours_saved", "Hours saved (after 80% realization haircut)", hours, "hours"),
        Fact("value", "Labor value of hours saved", value, "usd"),
        Fact("cost", "License cost this quarter", cost, "usd"),
        Fact("roi", "ROI: (value - cost) / cost", (value - cost) / cost, "pct"),
        Fact("payback", "Payback on onboarding fee", payback, "months"),
    ]
    return {x.id: x for x in f}
