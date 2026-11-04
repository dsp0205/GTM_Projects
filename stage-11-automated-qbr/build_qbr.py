import argparse
import os
from pathlib import Path
import pandas as pd
import deck
import metrics
import narrative

p = argparse.ArgumentParser()
p.add_argument("account_id")
p.add_argument("quarter")
p.add_argument("--llm", action="store_true")
a = p.parse_args()

accounts, usage = pd.read_csv("accounts.csv"), pd.read_csv("usage.csv")
acct = accounts[accounts.account_id == a.account_id].iloc[0]
q = pd.Period(a.quarter)
facts = metrics.compute(acct, usage, q)

client = None
if a.llm:
    from dotenv import load_dotenv, find_dotenv
    import anthropic
    load_dotenv(find_dotenv(usecwd=True))
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        client = anthropic.Anthropic(api_key=api_key)

summary = narrative.write_summary(facts, client)
weekly = metrics.in_quarter(usage[usage.account_id == a.account_id], q)
assumptions = [
    f"Minutes per task: {acct.baseline_min} before, {acct.tool_min} with the tool (measured at kickoff).",
    f"{acct.displaced_share:.0%} of tasks replace manual work (sampled with your team).",
    f"Hourly cost:  wage x {metrics.LOAD_FACTOR:.2f} load (BLS, June 2026).",
    f"We count {metrics.REALIZATION:.0%} of measured savings.",
    "Payback = onboarding fee / (monthly value - monthly license).",
]

Path("out").mkdir(exist_ok=True)
name = f"out/{a.account_id}-{a.quarter}-DRAFT.pptx"
deck.build(acct["name"], f"{q.year} Q{q.quarter}", weekly, facts, summary, assumptions, name)

review_checklist = ["# Review checklist"]
for f in facts.values():
    review_checklist.append(f"- [ ] {f.label}: {f.show()}")
review_checklist.append("- [ ] Next-quarter slide written\n")

Path("out/review.md").write_text("\n".join(review_checklist), encoding="utf-8")
print("wrote", name)
