import csv, json, re, sys, urllib.request

BOARDS = [
    ("Anthropic", "greenhouse", "anthropic"),
    ("OpenAI", "ashby", "openai"),
    ("Clay", "ashby", "claylabs"),
    ("Ramp", "ashby", "ramp"),
    ("Cursor", "ashby", "cursor")
]
TITLE = re.compile(r"\bgtm\b|go[- ]to[- ]market|gtme\b|revenue operations|revops", re.I)
BUILDER = re.compile(r"engineer|developer|analytics|data (scientist|analyst)|systems", re.I)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "gtm-portfolio-study/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)

def greenhouse(token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?pay_transparency=true"
    for j in fetch(url).get("jobs", []):
        pay = ""
        if j.get("pay_input_ranges"):
            p = j["pay_input_ranges"][0]
            pay = f" -"
        yield j["title"], j.get("first_published", ""), pay, j["absolute_url"]

def ashby(name):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{name}?includeCompensation=true"
    for j in fetch(url).get("jobs", []):
        pay = (j.get("compensation") or {}).get("scrapeableCompensationSalarySummary", "")
        yield j["title"], j.get("publishedAt", ""), pay, j["jobUrl"]

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "jobs.csv"
    rows = []
    for company, vendor, token in BOARDS:
        try:
            jobs = list(greenhouse(token) if vendor == "greenhouse" else ashby(token))
            hits = [(company, t, "builder" if BUILDER.search(t) else "other", d[:10], pay, url)
                    for t, d, pay, url in jobs if TITLE.search(t)]
            rows += hits
            print(f"{company}: {len(jobs)} open, {len(hits)} GTM-titled, "
                  f"{sum(h[2] == 'builder' for h in hits)} builder")
        except Exception as e:
            print(f"Error fetching {company}: {e}")
            
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([("company", "title", "kind", "posted", "pay", "url")] + rows)
    print(f"Saved {len(rows)} matching roles to {out_file}")
