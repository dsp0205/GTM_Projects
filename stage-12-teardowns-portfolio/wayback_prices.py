import csv, gzip, json, re, sys, time, urllib.error, urllib.parse, urllib.request

UA = {"User-Agent": "gtm-teardown-research/1.0 (contact: gtm-engineer@example.com)"}
PRICE = re.compile(r"\$\s?(\d[\d,]*(?:\.\d\d)?)")

def get(url, tries=4):
    for n in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = r.read()
                if data[:2] == b"\x1f\x8b":
                    data = gzip.decompress(data)
                return data.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or n == tries - 1:
                raise
            time.sleep(10 * (n + 1))

def captures(page, year_from):
    q = urllib.parse.urlencode({"url": page, "output": "json", "from": year_from,
                                "fl": "timestamp", "filter": "statuscode:200",
                                "collapse": "timestamp:6"})
    body = get("https://web.archive.org/cdx/search/cdx?" + q)
    rows = json.loads(body) if body.strip() else []
    return [row[0] for row in rows[1:]]

def prices_in(html):
    body = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", html)
    return sorted({m.group(1).replace(",", "") for m in PRICE.finditer(body)}, key=float)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python wayback_prices.py <domain/path> <year_from> <out.csv>")
        sys.exit(1)
    page, year, out = sys.argv[1:4]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "prices_found"])
        for ts in captures(page, year):
            w.writerow([ts, " ".join(prices_in(get(f"https://web.archive.org/web/{ts}id_/https://{page}")))])
            time.sleep(2)
    print(f"Price history written to {out}")
