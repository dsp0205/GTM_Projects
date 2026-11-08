# GTM Engineering & Revenue Systems Portfolio

I build systems at the intersection of go-to-market strategy, data, automation and AI. This portfolio brings together hands-on projects across revenue data architecture, CRM integrations, sales automation, product-led growth, attribution and customer analytics.

My background spans strategy, operations and AI. I enjoy taking a business problem, understanding the systems behind it, and building a practical technical solution.

The repository contains 11 project stages and 3 product teardowns developed through hands-on implementation. The projects include working code and test coverage, with sample or synthetic data used where appropriate.

---

## Featured Projects

### 1. Reverse ETL & Data Architecture
[Explore the project](./stage-01-gtm-data-architecture-reverse-etl)

A data pipeline that transforms billing and product-usage data into CRM-ready records and syncs changes to HubSpot.

- Built data models using SQL and DuckDB to combine Stripe billing and product usage.
- Implemented SHA-256 row hashing to detect changes and avoid unnecessary CRM updates.
- Added batched HubSpot upserts with retry handling for API rate limits.
- Built a Stripe webhook receiver with signature verification and duplicate-event protection.

**Stack:** Python, SQL, DuckDB, Flask, Stripe API, HubSpot API.

### 2. AI SDR & Prospect Personalization
[Explore the project](./stage-03-ai-sdrs-hyper-personalization)

An AI-assisted outbound workflow that uses public prospect activity to identify relevant signals and generate personalized email drafts.

- Retrieves recent public GitHub activity as prospect context.
- Uses structured LLM outputs to extract specific, source-backed observations.
- Verifies generated claims against the original evidence and drops unsupported hooks.
- Produces personalized drafts for human review rather than sending outreach automatically.

**Stack:** Python, Anthropic API, GitHub API, structured JSON outputs.

### 3. Multi-Touch Revenue Attribution
[Explore the project](./stage-06-revops-attribution)

A revenue analytics project comparing different ways of assigning credit to marketing and sales touchpoints.

- Implemented first-touch, last-touch, linear, U-shaped and time-decay attribution in SQL.
- Built Markov removal-effect and Shapley-value models in Python.
- Generated account, contact, touchpoint and opportunity data to test attribution approaches.
- Added funnel and cohort analysis with a locally generated HTML dashboard.
- Compared attribution outputs against holdout experiments.

**Stack:** Python, SQL, DuckDB, Pandas, NumPy.

---

## Project Portfolio

### Revenue Data & Automation

| Project | What it covers |
|---|---|
| [Stage 01 · Reverse ETL & Data Architecture](./stage-01-gtm-data-architecture-reverse-etl) | Billing data models, change detection, HubSpot sync and Stripe webhooks |
| [Stage 02 · HMAC Intent Pipelines](./stage-02-signal-intent-pipelines) | Webhook signature verification, intent signals and deduplication |
| [Stage 04 · Product-Led Telemetry Scoring](./stage-04-plg-telemetry) | Product event processing, account fit and usage-based PQL scoring |
| [Stage 05 · Usage-Based Credit Architecture](./stage-05-usage-based-pricing) | Usage metering, credit ledgers, promotional balances and compute limits |
| [Stage 09 · Integration-Led Growth](./stage-09-integration-led-growth) | Slack OAuth, PKCE, encrypted token storage and activation tracking |

### AI, Sales & Customer Operations

| Project | What it covers |
|---|---|
| [Stage 03 · AI SDR Hyper-Personalization](./stage-03-ai-sdrs-hyper-personalization) | Prospect research, evidence validation and personalized outbound drafts |
| [Stage 07 · AI Sales Enablement](./stage-07-ai-sales-enablement) | Call transcript analysis, objection clustering and RAG-based battle cards |
| [Stage 08 · Predictive Churn & Expansion](./stage-08-predictive-churn-expansion) | Churn-risk modelling and renewal-focused account prioritization |
| [Stage 11 · Automated QBR Engine](./stage-11-automated-qbr) | Automated PowerPoint generation with deterministic metrics and review controls |

### Revenue Intelligence & Attribution

| Project | What it covers |
|---|---|
| [Stage 06 · Multi-Touch RevOps Attribution](./stage-06-revops-attribution) | Rule-based attribution, Markov models, Shapley values and funnel analysis |
| [Stage 10 · Dark Social & Community Attribution](./stage-10-dark-social-community) | Self-reported attribution, response coding and incremental lift analysis |

---

## Product & Pricing Teardowns

These teardowns look at how AI and SaaS products structure usage, pricing and monetization.

1. [Cursor · Credit Pools & Usage Tiers](./stage-12-teardowns-portfolio/teardowns/01_cursor_credit_pools.md)
2. [Lovable · Asymmetric Credit Pricing](./stage-12-teardowns-portfolio/teardowns/02_lovable_dynamic_credits.md)
3. [Claude · Rolling Usage Windows](./stage-12-teardowns-portfolio/teardowns/03_claude_usage_windows.md)

---

## Technical Toolkit

- **Languages:** Python, SQL
- **Data & storage:** DuckDB, SQLite, Pandas, NumPy
- **Integrations:** REST APIs, webhooks, OAuth, Stripe, HubSpot, Slack, GitHub
- **AI workflows:** LLM APIs, structured outputs, evidence validation, RAG and prompt design
- **GTM systems:** CRM data sync, lead signals, outbound personalization, product analytics, attribution and customer retention
- **Outputs:** HTML dashboards, automated PowerPoint reports and data pipelines

---

## How I Approach GTM Engineering

I look at GTM engineering as more than connecting tools. The work starts with understanding the business process and the data behind it, then designing systems that make the process more reliable and measurable.

Across these projects, I focus on:

- **Reliable data movement:** validation, deduplication, idempotency and API failure handling.
- **Useful automation:** workflows that reduce manual work without removing necessary human review.
- **Commercial context:** connecting product usage, customer signals and revenue outcomes.
- **Measurable decisions:** making assumptions visible and testing models against defined data.

Each project folder contains the implementation files and supporting material. The repository is intended to be explored project by project.
