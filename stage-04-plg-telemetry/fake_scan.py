import random
import sqlite3

random.seed(7)
db = sqlite3.connect("fake.db")
db.executescript("""
DROP TABLE IF EXISTS calls_7d;
DROP TABLE IF EXISTS accounts;
CREATE TABLE calls_7d (account_id INTEGER PRIMARY KEY, calls INTEGER);
CREATE TABLE accounts (account_id INTEGER PRIMARY KEY, retained_d60 INTEGER);
""")
for acct in range(2000):
    calls = int(random.expovariate(1 / 45))
    p_retain = min(0.10 + 0.007 * calls, 0.70)
    retained = 1 if random.random() < p_retain else 0
    db.execute("INSERT INTO calls_7d VALUES (?, ?)", (acct, calls))
    db.execute("INSERT INTO accounts VALUES (?, ?)", (acct, retained))
db.commit()

query = """
WITH t(threshold) AS (VALUES (10), (25), (50), (100), (150))
SELECT t.threshold,
       SUM(CASE WHEN c.calls >= t.threshold THEN 1 ELSE 0 END) AS reached,
       ROUND(100.0 * AVG(CASE WHEN c.calls >= t.threshold THEN a.retained_d60 END), 1) AS ret_reached,
       ROUND(100.0 * AVG(CASE WHEN c.calls <  t.threshold THEN a.retained_d60 END), 1) AS ret_missed
FROM t
CROSS JOIN calls_7d c
JOIN accounts a ON a.account_id = c.account_id
GROUP BY t.threshold
ORDER BY t.threshold;
"""

print(f"{'Threshold':>9} | {'Reached':>7} | {'Retained (Reached)':>18} | {'Retained (Missed)':>17}")
print("-" * 62)
for row in db.execute(query):
    print(f"{row[0]:>9} | {row[1]:>7} | {row[2]:>17}% | {row[3]:>16}%")
db.close()
