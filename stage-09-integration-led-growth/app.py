import os
import sqlite3
import time

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store.sqlite3 import SQLite3InstallationStore
from slack_sdk.oauth.state_store.sqlite3 import SQLite3OAuthStateStore

DB = os.environ.get("SIGNALPING_DB", "signalping.db")
CLIENT_ID = os.environ.get("SLACK_CLIENT_ID", "mock-client-id")

installation_store = SQLite3InstallationStore(database=DB, client_id=CLIENT_ID)
state_store = SQLite3OAuthStateStore(database=DB, expiration_seconds=600)
installation_store.init()
state_store.init()

with sqlite3.connect(DB) as db:
    db.execute("CREATE TABLE IF NOT EXISTS events "
               "(team_id TEXT NOT NULL, name TEXT NOT NULL, ts INTEGER NOT NULL)")

app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET", "mock-signing-secret"),
    oauth_settings=OAuthSettings(
        client_id=CLIENT_ID,
        client_secret=os.environ.get("SLACK_CLIENT_SECRET", "mock-client-secret"),
        scopes=["commands"],
        installation_store=installation_store,
        state_store=state_store,
    ),
)

SIGNALS = {
    "acme.com": {"score": 82, "reason": "Visited pricing 3 times this week"},
    "globex.io": {"score": 41, "reason": "New hire: VP Sales"},
}

def lookup(domain):
    return SIGNALS.get(domain.strip().lower())

@app.command("/signal")
def signal_command(ack, command, respond):
    ack()
    domain = command.get("text", "").strip()
    with sqlite3.connect(DB) as db:
        db.execute("INSERT INTO events VALUES (?, 'command_used', ?)",
                   (command["team_id"], int(time.time())))
    hit = lookup(domain)
    if not hit:
        respond(f"No signal found for {domain}. Try /signal acme.com.")
        return
    respond(f"*{domain}* score *{hit['score']}*\n{hit['reason']}")

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
@flask_app.route("/slack/install", methods=["GET"])
@flask_app.route("/slack/oauth_redirect", methods=["GET"])
def slack_routes():
    return handler.handle(request)

if __name__ == "__main__":
    print("SignalPing Slack service running on port 3000...")
    flask_app.run(port=3000)
