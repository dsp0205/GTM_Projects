"""Reverse ETL: send changed warehouse rows to a HubSpot custom object (sync mode: upsert)."""
import hashlib
import json
import os
import random
import time

import duckdb
import requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.environ.get("HUBSPOT_BASE_URL", "https://api.hubapi.com")
VERSION = "2026-09"
DRY_RUN = os.environ.get("DRY_RUN") == "1"
OBJECT = os.environ.get("HUBSPOT_OBJECT_TYPE_ID", "2-0")
HEADERS = {"Authorization": f"Bearer {os.environ.get('HUBSPOT_TOKEN', '')}"}
URL = f"{BASE}/crm/objects/{VERSION}/{OBJECT}/batch/upsert"
BATCH = 100
KEY = "stripe_customer_id"

con = duckdb.connect("gtm.duckdb")
con.execute("create table if not exists sync_state (id varchar primary key, row_hash varchar)")


def changed_rows():
    cur = con.execute("select * from account_billing")
    cols = [c[0] for c in cur.description]
    values_list = cur.fetchall()
    sent = dict(con.execute("select id, row_hash from sync_state").fetchall())
    for values in values_list:
        row = dict(zip(cols, values))
        digest = hashlib.sha256(json.dumps(row, sort_keys=True, default=str).encode()).hexdigest()
        if sent.get(row[KEY]) != digest:
            yield row, digest


def post(body):
    if DRY_RUN:
        print(json.dumps(body["inputs"][0]), "... and", len(body["inputs"]) - 1, "more")
        return {"numErrors": 0}
    for attempt in range(6):
        r = requests.post(URL, headers=HEADERS, json=body, timeout=30)
        if r.status_code == 429:
            wait = float(r.headers.get("Retry-After", 2 ** attempt)) + random.random()
            print(f"429, waiting {wait:.1f}s")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("still rate limited after 6 attempts")


def to_input(row):
    props = {k: str(v) for k, v in row.items() if v is not None}
    return {"idProperty": KEY, "id": row[KEY], "properties": props}


def main():
    pending = list(changed_rows())
    print(len(pending), "changed rows")
    for i in range(0, len(pending), BATCH):
        chunk = pending[i:i + BATCH]
        result = post({"inputs": [to_input(row) for row, _ in chunk]})
        if result.get("numErrors") or result.get("errors"):
            print("errors:", json.dumps(result.get("errors"))[:500])
            continue
        if DRY_RUN:
            continue
        con.executemany(
            "insert or replace into sync_state values (?, ?)",
            [[row[KEY], digest] for row, digest in chunk],
        )
        print("synced", len(chunk), "rows")


if __name__ == "__main__":
    main()
