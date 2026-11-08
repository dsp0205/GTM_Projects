# Product-Led Growth Telemetry & PQL Scoring

A product-usage scoring workflow that identifies free accounts showing meaningful activation and potential to convert.

The project combines firmographic fit with product usage to distinguish accounts that are simply active from accounts that may be commercially qualified.

## Scoring approach

- Evaluates account size and business email signals as indicators of fit.
- Tracks successful product events over a defined activation window.
- Measures API usage and the number of active users.
- Applies a configurable product-qualified lead score.
- Uses a persistent alert record to avoid repeatedly notifying sales about the same account and rule.
- Sends qualifying account alerts to Slack.

## Architecture

```text
Product events
      |
      v
Signed event ingestion
      |
Identity + account association
      |
Deduplicated event storage
      |
Activation window + usage metrics
      |
Firmographic fit + product usage
      |
PQL score + alert guard
      |
Slack notification
```

## Included components

- `aha_alert.py` – event receiver, account and user identity handling, scoring logic and Slack alert delivery.
- `fake_scan.py` – a separate synthetic analysis of usage thresholds and retention outcomes.

## Tech stack

Python · SQLite · HMAC · HTTP · Slack Webhooks · SQL

## Design focus

The scoring model combines product engagement with account fit. This makes the signal more useful to sales than a raw event count, while the alert guard keeps notifications focused.
