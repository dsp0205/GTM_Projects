# Reverse ETL & Billing Data Architecture

A billing-to-CRM data pipeline built around a simple idea: **only sync records when their underlying data has changed**.

The project models Stripe customer, subscription and product-usage data in DuckDB, creates one account-level billing record, and syncs changed records to a HubSpot custom object.

## What it does

1. **Generate source data** – create sample Stripe customers, subscriptions and usage events in DuckDB.
2. **Model account data** – use SQL to produce one record per Stripe customer, including normalized MRR, subscription status, active users and latest usage activity.
3. **Detect changes** – calculate a SHA-256 hash for each account record and compare it with the last successful sync state.
4. **Sync to HubSpot** – send changed records through batched CRM upserts, with handling for API rate limits and failed batches.
5. **Receive Stripe events** – expose a webhook endpoint that verifies Stripe signatures and stores each event once using its event ID.

## Architecture

```text
Stripe customer + subscription data     Product usage events
                  \                       /
                   v                     v
                         DuckDB
                            |
                    account_billing.sql
                            |
                  Account-level billing row
                            |
                  SHA-256 change detection
                            |
                  HubSpot batch upsert
                            |
                     sync_state table

Stripe webhook --> Signature verification --> SQLite event inbox
```

## Key implementation details

- **Data modelling:** SQL CTEs join customer, subscription and usage data at the account level.
- **MRR logic:** active and past-due subscriptions contribute to MRR; trialing and canceled subscriptions do not.
- **Change detection:** stable JSON serialization and SHA-256 hashing identify changed rows.
- **Sync state:** hashes are persisted only after a successful HubSpot batch response.
- **API resilience:** batched requests include retry handling for HTTP 429 responses.
- **Webhook safety:** Stripe signature verification and a primary-key event ID prevent duplicate event records.

## Run locally

The mock data generator does not require Stripe or HubSpot credentials.

From this directory:

```bash
python seed_mock.py
```

Then create the account-level model in DuckDB:

```bash
python -c "import duckdb; c=duckdb.connect('gtm.duckdb'); c.execute(open('models/account_billing.sql').read()); print(c.execute('select * from account_billing').df()); c.close()"
```

For a safe preview of the CRM payloads, configure `DRY_RUN=1` and run:

```bash
python reverse_etl.py
```

For a live HubSpot sync, configure `HUBSPOT_TOKEN` and `HUBSPOT_OBJECT_TYPE_ID` in your environment. The target HubSpot custom object must have the expected properties, including `stripe_customer_id`.

The webhook receiver uses `STRIPE_WEBHOOK_SECRET` and can be started with:

```bash
python webhook_app.py
```

The webhook endpoint is `POST /stripe/webhook`. The included `test_webhook.py` exercises valid, duplicate and invalid webhook requests.

## Tech stack

Python · SQL · DuckDB · SQLite · Flask · Stripe API · HubSpot CRM API

## Design focus

This project demonstrates how billing and product activity can be turned into a clean CRM-facing account model, while keeping data movement controlled, repeatable and resilient to common API failures.
