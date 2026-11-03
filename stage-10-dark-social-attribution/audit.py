import csv
import random
import sqlite3
import sys
from analyze import cohen_kappa
from code_answers import CHANNELS

db = sqlite3.connect("dark_social.db")
if sys.argv[1:] == ["export"]:
    rows = db.execute("SELECT signup_id, hdyhau_text FROM signups").fetchall()
    with open("audit_sample.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["signup_id", "answer", "my_channel"])
        w.writerows([i, text, ""] for i, text in random.Random(1).sample(rows, 50))
    print("Exported 50 sample answers to audit_sample.csv")
    print("Allowed channels:", ", ".join(CHANNELS))
elif sys.argv[1:] == ["score"]:
    with open("audit_sample.csv", newline="", encoding="utf-8") as f:
        mine = list(csv.DictReader(f))
    if any(r["my_channel"].strip() not in CHANNELS for r in mine):
        sys.exit("Error: every my_channel cell must be a valid channel name")
    coder = dict(db.execute("SELECT signup_id, channel FROM coded_answers"))
    human = [r["my_channel"].strip() for r in mine]
    model = [coder[int(r["signup_id"])] for r in mine]
    for r, h, m in zip(mine, human, model):
        if h != m:
            print(f"DISAGREE {r['answer']!r}: you={h} model={m}")
    print(f"kappa = {cohen_kappa(human, model):.2f} on {len(human)} answers")
else:
    sys.exit(__doc__)
