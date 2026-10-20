import csv, json, os, sys
import signals
from writer import make_draft

SENDER = {"name": os.environ.get("SENDER_NAME", "Deep Pimpale"),
          "address": os.environ.get("SENDER_ADDRESS", "Mumbai, India")}
OFFER = "A free 20-minute audit of your revenue automation workflows."

def gather(row, mock):
    if mock:
        fixture_path = f"fixtures/{row['github_login']}.json"
        if os.path.exists(fixture_path):
            with open(fixture_path, encoding='utf-8-sig') as f:
                return json.load(f)
        return []
    ev = signals.recent_commits(row["github_login"]) if row.get("github_login") else []
    return ev

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py prospects.csv [--mock]")
        return
    csv_file = sys.argv[1]
    is_mock = "--mock" in sys.argv
    os.makedirs("drafts", exist_ok=True)
    with open(csv_file, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            evidence = gather(row, is_mock)
            d = make_draft(row, evidence, OFFER, SENDER)
            name = row["github_login"] or row["name"].replace(" ", "_")
            with open(f"drafts/{name}.json", "w", encoding='utf-8') as out:
                json.dump(d, out, indent=2)
            print(row["name"], "->", d["status"], d.get("problems", ""))

if __name__ == "__main__":
    main()
