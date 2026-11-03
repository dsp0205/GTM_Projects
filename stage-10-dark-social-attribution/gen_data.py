import math
import random
import sqlite3
from datetime import date, timedelta

random.seed(42)
db = sqlite3.connect("dark_social.db")
db.executescript(open("schema.sql").read())
for t in ("opportunities", "coded_answers", "signups", "accounts"):
    db.execute(f"DELETE FROM {t}")

DARK = ["a friend sent me the link", "my old coworker told me", "saw it in a slack group",
        "someone in the discord", "word of mouth"]
OTHER = ["google", "searched for dictation api", "a podcast, forgot which",
         "chatgpt suggested it", "G2 reviews", "not sure", "n/a"]

for acc in range(1, 1501):
    employees = max(5, int(math.exp(random.gauss(5.5, 1.4))))
    size = math.log(employees) - 3.5
    in_comm = random.random() < min(0.95, max(0.02, 0.12 * size))
    db.execute("INSERT INTO accounts VALUES (?,?,?)", (acc, f"co{acc}.example", employees))
    first = date(2026, 1, 1) + timedelta(days=random.randint(0, 120))
    answer = random.choice(DARK if random.random() < (0.55 if in_comm else 0.12) else OTHER)
    db.execute("INSERT INTO signups (account_id, created_at, hdyhau_text) VALUES (?,?,?)",
               (acc, first.isoformat(), answer))
    if random.random() < min(0.9, max(0.01, 0.10 * size + (0.06 if in_comm else 0))):
        db.execute("INSERT INTO opportunities (account_id, created_at, amount_usd) VALUES (?,?,?)",
                   (acc, (first + timedelta(days=random.randint(5, 80))).isoformat(),
                    round(employees * random.uniform(8, 20), 2)))
db.commit()
print("Generated 1500 accounts, signups, and opportunities in dark_social.db")
db.close()
