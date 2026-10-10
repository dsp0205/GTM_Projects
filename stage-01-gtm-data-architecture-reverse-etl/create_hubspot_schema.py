"""Create the custom object 'billing_account' in HubSpot. Run once. Needs an Enterprise-trial test account."""
import os
import requests
from dotenv import load_dotenv, find_dotenv

# Search upwards from current directory to find .env in project root
load_dotenv(find_dotenv(usecwd=True))

BASE = os.environ.get("HUBSPOT_BASE_URL", "https://api.hubapi.com")
VERSION = "2026-09"
token = os.environ.get("HUBSPOT_TOKEN")

if not token:
    raise ValueError("HUBSPOT_TOKEN is missing or empty. Ensure HUBSPOT_TOKEN=pat-... is defined in your .env file.")

headers = {"Authorization": f"Bearer {token}"}

def text(name, label, **extra):
    return {"name": name, "label": label, "type": "string", "fieldType": "text", **extra}

def number(name, label):
    return {"name": name, "label": label, "type": "number", "fieldType": "number"}

schema = {
    "name": "billing_account",
    "labels": {"singular": "Billing account", "plural": "Billing accounts"},
    "primaryDisplayProperty": "customer_name",
    "requiredProperties": ["stripe_customer_id"],
    "searchableProperties": ["stripe_customer_id", "customer_name", "company_domain"],
    "associatedObjects": ["0-2"],
    "properties": [
        text("stripe_customer_id", "Stripe customer ID", hasUniqueValue=True),
        text("customer_name", "Customer name"),
        text("company_domain", "Company domain"),
        number("mrr_cents", "MRR (cents)"),
        text("subscription_status", "Subscription status"),
        number("active_users_30d", "Active users (30d)"),
        {"name": "last_event_at", "label": "Last product event", "type": "datetime", "fieldType": "date"},
    ],
}

r = requests.post(f"{BASE}/crm-object-schemas/{VERSION}/schemas", headers=headers, json=schema, timeout=30)
if r.status_code == 409:
    print("Schema 'billing_account' already exists in this portal.")
else:
    r.raise_for_status()
    print("Set HUBSPOT_OBJECT_TYPE_ID to", r.json()["objectTypeId"])
