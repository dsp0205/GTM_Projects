# Dark Social & Community Attribution

An attribution analysis focused on channels that are often missed by conventional web analytics, especially peer recommendations and private communities.

The project uses self-reported “How did you hear about us?” responses, classifies them into acquisition channels, and compares opportunity outcomes across account segments.

## Workflow

1. Generate and store signup, account and opportunity data.
2. Code free-text acquisition answers into a defined channel taxonomy.
3. Support both LLM-assisted structured coding and a lightweight offline rules-based mode.
4. Audit coded answers and compare agreement between coding passes.
5. Calculate raw and company-size-adjusted word-of-mouth lift.
6. Use bootstrap resampling to estimate uncertainty around adjusted lift.

## Architecture

```text
Signup survey responses
          |
          v
  Channel classification
  LLM schema / offline rules
          |
          v
     Coded answers
          |
          v
  Coding agreement audit
          |
          v
  Account-size segmentation
          |
          v
  Opportunity conversion analysis
          |
          v
  Adjusted lift + bootstrap interval
```

## Files

- `code_answers.py` – classifies free-text answers using an LLM or offline rules.
- `audit.py` – supports coding quality checks.
- `analyze.py` – calculates raw and adjusted lift with bootstrap intervals.
- `gen_data.py` and `schema.sql` – data generation and database structure.

## Tech stack

Python · SQLite · SQL · Anthropic API · Statistical analysis · Bootstrap resampling

## Design focus

The project explores how self-reported attribution can reveal acquisition sources that are invisible to last-click tracking, while accounting for differences in company size across the customer base.
