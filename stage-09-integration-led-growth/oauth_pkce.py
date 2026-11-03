import base64
import hashlib
import os
import secrets
import sqlite3
import time
import urllib.parse
import requests
from cryptography.fernet import Fernet

HUBSPOT = {
    "authorize_url": "https://app.hubspot.com/oauth/authorize",
    "token_url": "https://api.hubapi.com/oauth/v3/token",
    "scopes": ["oauth", "crm.objects.contacts.read"],
    "pkce": False,
}

def pkce_pair():
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge

def authorize_url(cfg, state, challenge=None):
    params = {
        "client_id": os.environ.get("HUBSPOT_CLIENT_ID", "mock_hubspot_id"),
        "redirect_uri": os.environ.get("HUBSPOT_REDIRECT_URI", "https://localhost:3000/oauth/callback"),
        "scope": " ".join(cfg["scopes"]),
        "state": state,
        "response_type": "code",
    }
    if cfg["pkce"] and challenge:
        params.update(code_challenge=challenge, code_challenge_method="S256")
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return cfg["authorize_url"] + "?" + query

def token_request(cfg, **fields):
    fields["client_id"] = os.environ.get("HUBSPOT_CLIENT_ID", "mock_hubspot_id")
    fields["client_secret"] = os.environ.get("HUBSPOT_CLIENT_SECRET", "mock_hubspot_secret")
    fields["redirect_uri"] = os.environ.get("HUBSPOT_REDIRECT_URI", "https://localhost:3000/oauth/callback")
    r = requests.post(cfg["token_url"], data=fields, timeout=15)
    r.raise_for_status()
    return r.json()

class TokenStore:
    def __init__(self, path, key):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=30)
        self.fernet = Fernet(key)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS tokens "
            "(tenant TEXT PRIMARY KEY, blob BLOB, expires_at REAL)"
        )

    def save(self, tenant, resp):
        pair = resp["access_token"] + "\n" + resp["refresh_token"]
        self.db.execute(
            "INSERT OR REPLACE INTO tokens VALUES (?, ?, ?)",
            (tenant, self.fernet.encrypt(pair.encode()),
             time.time() + int(resp["expires_in"])),
        )

    def load(self, tenant):
        row = self.db.execute(
            "SELECT blob, expires_at FROM tokens WHERE tenant=?", (tenant,)
        ).fetchone()
        if not row:
            return None
        access, refresh = self.fernet.decrypt(row[0]).decode().split("\n")
        return {"access": access, "refresh": refresh, "expires_at": row[1]}

def get_access_token(cfg, store, tenant, skew=60):
    store.db.execute("BEGIN IMMEDIATE")
    try:
        tok = store.load(tenant)
        if tok is None:
            raise LookupError("tenant has not connected")
        if tok["expires_at"] - skew > time.time():
            return tok["access"]
        body = token_request(cfg, grant_type="refresh_token", refresh_token=tok["refresh"])
        body.setdefault("refresh_token", tok["refresh"])
        store.save(tenant, body)
        return body["access_token"]
    finally:
        store.db.execute("COMMIT")
