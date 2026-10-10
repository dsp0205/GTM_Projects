"""Receive Stripe webhooks: verify the signature, store the raw event once, answer 200 fast."""
import os
import sqlite3

import stripe
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_test123")
db = sqlite3.connect(os.environ.get("INBOX_DB", "inbox.sqlite"), check_same_thread=False)
db.execute("""create table if not exists stripe_events (
    id text primary key, type text, created integer, payload text, processed integer default 0)""")


@app.post("/stripe/webhook")
def stripe_webhook():
    payload = request.get_data()
    try:
        event = stripe.Webhook.construct_event(payload, request.headers.get("Stripe-Signature"), SECRET)
    except (ValueError, stripe.SignatureVerificationError):
        return "invalid", 400
    db.execute("insert or ignore into stripe_events (id, type, created, payload) values (?, ?, ?, ?)",
               (event.id, event.type, event.created, payload.decode()))
    db.commit()
    return "", 200
