# Intent Signal Pipelines

A real-time intent router that turns repeated pricing-page activity into actionable account signals for a sales team.

## How it works

- Accepts page and track events through a FastAPI endpoint.
- Verifies incoming event signatures using HMAC.
- Resolves the company domain from first-party event properties, with optional IP intelligence lookup.
- Filters events against a target-account list and enterprise segment.
- Deduplicates events and tracks distinct visitor activity in SQLite.
- Applies a configurable time window and threshold before triggering a Slack alert.
- Uses a background task for Slack delivery.

## Architecture

```text
Web / product event
        |
        v
FastAPI event endpoint
        |
 Signature verification
        |
 Event + target filtering
        |
 Domain resolution
        |
 SQLite deduplication + windowed count
        |
 Threshold + alert cooldown
        |
 Slack account alert
```

## Key design choices

**Signal quality:** only pricing-page activity from matching target accounts is considered.

**Noise control:** duplicate message IDs are ignored, distinct visits are counted, and an alert cooldown prevents repeated notifications.

**Operational controls:** the time window, threshold, target list, signing secret and Slack destination are configurable through environment variables.

## Files

- `router.py` – event ingestion, validation, account matching, persistence and alert routing.
- `simulate.py` – sends sample pricing-page events to a running router.
- `targets.csv` – target-account and segment configuration.
- `test_router.py` – router test coverage.

## Tech stack

Python · FastAPI · SQLite · HMAC-SHA1 · HTTPX · Slack Incoming Webhooks

## Outcome

A focused signal pipeline that connects product behaviour to account-level sales context, while filtering noise before it reaches the team.
