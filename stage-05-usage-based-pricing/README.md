# Usage-Based Pricing & Credit Ledger

A usage metering and credit accounting system designed for products that charge customers based on consumption.

The project models how usage events become billable credits, how customer balances are consumed, and how a system can account for grants, expiry and spending limits.

## Core components

- **Usage metering:** maps event types and quantities to credit consumption through a configurable rate card.
- **Event integrity:** records usage transactions with unique transaction IDs to support deduplication.
- **Credit grants:** maintains customer credit grants, remaining balances, expiry and grant categories.
- **Ledger entries:** records balance movements against usage transactions.
- **Usage controls:** supports late-arriving event windows, timestamp-skew handling and customer-level monthly caps.
- **Simulation and tests:** includes a usage simulation and a dedicated meter test suite.

## Architecture

```text
Product usage event
        |
        v
Event validation + deduplication
        |
        v
Rate card / credit calculation
        |
        v
Customer credit grants
        |
        v
Credit consumption + ledger
        |
        v
Balance and usage limits
```

## Files

- `meter.py` – metering logic, customer records, credit grants and ledger operations.
- `simulate.py` – usage simulation.
- `test_meter.py` – test coverage for the metering system.

## Tech stack

Python · SQLite · Transactional data modelling

## Design focus

Usage-based pricing needs more than a counter. It needs a traceable record of what was consumed, how much it cost in credits, which balance funded it and whether the customer has reached a usage limit.
