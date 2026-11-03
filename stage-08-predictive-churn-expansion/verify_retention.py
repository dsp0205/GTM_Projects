import duckdb

con = duckdb.connect()
con.execute("""
CREATE TABLE arr_snapshots(account_id INT, month DATE, arr DOUBLE);
INSERT INTO arr_snapshots VALUES
  (1, DATE '2025-09-01', 300), (1, DATE '2026-09-01', 450),
  (2, DATE '2025-09-01', 200), (2, DATE '2026-09-01', 180),
  (3, DATE '2025-09-01', 100),
  (4, DATE '2025-09-01', 400), (4, DATE '2026-09-01', 400),
  (5, DATE '2025-09-01', 500), (5, DATE '2026-09-01', 600),
  (6, DATE '2026-09-01', 700);
""")

query = """
WITH cohort AS (
  SELECT account_id, arr AS arr_start
  FROM arr_snapshots
  WHERE month = DATE '2025-09-01' AND arr > 0
),
later AS (
  SELECT account_id, arr AS arr_end
  FROM arr_snapshots
  WHERE month = DATE '2026-09-01'
)
SELECT
  ROUND(SUM(COALESCE(l.arr_end, 0)) * 100.0 / SUM(c.arr_start), 1) AS nrr_pct,
  ROUND(SUM(LEAST(COALESCE(l.arr_end, 0), c.arr_start)) * 100.0 / SUM(c.arr_start), 1) AS grr_pct
FROM cohort c
LEFT JOIN later l USING (account_id);
"""

res = con.execute(query).fetchall()
print(f"NRR: {res[0][0]}% | GRR: {res[0][1]}%")
