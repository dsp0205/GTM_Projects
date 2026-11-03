import duckdb

con = duckdb.connect("revops.duckdb")

def run(path):
    stmts = [s for s in open(path).read().split(";") if s.strip()]
    for s in stmts[:-1]:
        con.execute(s)
    return con.execute(stmts[-1]).fetchdf()

models = run("models.sql").set_index("channel")
print("=== SOURCED REVENUE BY MODEL ===")
print(models.round().to_string())
print()

touched = models.drop("no_touch")
share = (touched / touched.sum() * 100).round(1)
funnel = run("funnel.sql")
cohort = run("cohort.sql").pivot(index="cohort", columns="months_since", values="pct_with_opp")

parts = [
    "<h2>Sourced won revenue by channel (USD)</h2>", models.to_html(float_format="{:,.0f}".format),
    "<h2>Share of sourced revenue by model (%)</h2>", share.to_html(),
    "<h2>Funnel leakage</h2>", funnel.to_html(index=False, na_rep=""),
    "<h2>Cohort: % of accounts with an opportunity, by months since first seen</h2>",
    cohort.to_html(na_rep=""),
]
html = ("<!doctype html><meta charset=utf-8><title>Revenue attribution</title>"
        "<style>body{font:15px system-ui;margin:2rem}table{border-collapse:collapse}"
        "td,th{border:1px solid #ccc;padding:4px 10px;text-align:right}</style>" + "".join(parts))
open("dashboard.html", "w", encoding="utf-8").write(html)
print("wrote dashboard.html")
con.close()
