import datetime as dt, os
import requests

GH = "https://api.github.com"

def gh_headers():
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2026-03-10"}
    if os.environ.get("GITHUB_TOKEN"):
        h["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    return h

def recent_commits(login, days=30, max_repos=3):
    r = requests.get(f"{GH}/users/{login}/events/public", headers=gh_headers(),
                     params={"per_page": 100}, timeout=20)
    if r.status_code != 200:
        return []
    repos = []
    for ev in r.json():
        if ev.get("type") == "PushEvent" and ev.get("repo", {}).get("name") not in repos:
            repos.append(ev["repo"]["name"])
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    for repo in repos[:max_repos]:
        c = requests.get(f"{GH}/repos/{repo}/commits", headers=gh_headers(), timeout=20,
                         params={"author": login, "since": since, "per_page": 5})
        if c.status_code != 200:
            continue
        for item in c.json():
            out.append({"url": item.get("html_url", ""),
                        "text": f"{repo}: {item['commit']['message'].splitlines()[0]}"})
    return out

def podcast_evidence(feed_url):
    return []
