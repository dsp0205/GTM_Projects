# GTM Engineering & Revenue Architecture Portfolio
Production-grade Go-To-Market infrastructure, data pipelines, and reverse ETL architectures.

---

## 1. Executive Summary & Market Findings
Based on automated ATS audits across Tier-1 AI companies (OpenAI, Anthropic, Ramp, Clay, Cursor), modern revenue engineering roles prioritize:
* **Production Data Engineering:** Strict idempotency, atomic deduplication, and schema validation over ad-hoc scripting.
* **Commercial Systems Judgment:** Balancing customer UX against API inference costs (rate limiting, credit pools, realization haircuts).
* **Defensible Metrics:** Rejecting ungrounded AI summaries in favor of verifiable facts.

---

## 2. Technical Course Projects (Stages 1 - 11)

### [Stage 01: Reverse ETL & Data Architecture](../stage-01-gtm-data-architecture-reverse-etl)
* **Problem:** Direct database-to-CRM syncing creates API rate limit exhaustion and sync thrashing.
* **Metric:** 100% change-only synchronization via SHA-256 state hashing; zero redundant HubSpot API calls.
* **Tradeoff:** Used DuckDB persistent hashing instead of webhook listeners to guarantee deterministic replayability.

### [Stage 02: HMAC Intent Pipelines](../stage-02-signal-intent-pipelines)
* **Problem:** Inbound webhooks from intent providers are vulnerable to spoofing and noisy duplicate signals.
* **Metric:** 100% cryptographic HMAC-SHA256 signature verification with rolling 7-day alert debounce windows.
* **Tradeoff:** Discarded sub-threshold signals early in memory to protect database connection pools.

### [Stage 03: AI SDR Hyper-Personalization](../stage-03-ai-sdr-hyper-personalization)
* **Problem:** LLM-generated outbound emails hallucinate company claims and trigger deliverability penalties.
* **Metric:** Strict Pydantic JSON schema outputs with an automated quote-or-drop verification pass.
* **Tradeoff:** Dropped non-verifiable prospect claims instead of attempting automated prompt correction.

### [Stage 04: Product-Led Telemetry Scoring](../stage-04-plg-telemetry)
* **Problem:** Segment event volume overwhelms CRM record limits with irrelevant low-intent actions.
* **Metric:** Atomic SQLite event deduplication pairing Fit (firmographic) and Usage (consumption velocity) scoring.
* **Tradeoff:** Implemented sliding 14-day decay windows over all-time event counters to surface active PQLs.

### [Stage 05: Usage-Based Credit Architecture](../stage-05-usage-based-pricing)
* **Problem:** Overdrafts in usage-based SaaS lead to uncollectible bills and margin loss.
* **Metric:** ACID-compliant balance ledger spending expiring promotional grants before paid balances.
* **Tradeoff:** Enforced hard compute caps at balance depletion rather than allowing unmetered debt.

### [Stage 06: Multi-Touch RevOps Attribution](../stage-06-revops-attribution)
* **Problem:** First-touch and last-touch attribution models misallocate marketing budget.
* **Metric:** Built 5 rule-based models alongside Shapley Value and Markov Removal Effect algorithms.
* **Tradeoff:** Validated synthetic paths against randomized holdout baselines to prevent self-fulfilling model bias.

### [Stage 07: AI Sales Enablement & Objection Battle Cards](../stage-07-ai-sales-enablement)
* **Problem:** Sales reps fail objection handling due to generic marketing collateral.
* **Metric:** Parsed lost-call transcripts, clustered themes via ChromaDB, and generated RAG battle cards.
* **Tradeoff:** Grounded proof points in verified ground-truth fact IDs; rejected ungrounded rep assertions.

### [Stage 08: Predictive Churn & Expansion Flagger](../stage-08-predictive-churn-expansion)
* **Problem:** Churn notifications arrive after the contract cancellation notice window closes.
* **Metric:** HistGradientBoosting classifier achieving 0.88 precision@25 evaluated 45 days prior to renewal.
* **Tradeoff:** Implemented a strict 45-day temporal gap split between train and test sets to eliminate data leakage.

### [Stage 09: Integration-Led Growth Slack OAuth App](../stage-09-integration-led-growth)
* **Problem:** OAuth tokens stored in plaintext create security vulnerabilities and refresh collisions.
* **Metric:** Built an RFC 7636 PKCE OAuth client with Fernet encryption and SQLite BEGIN IMMEDIATE locks.
* **Tradeoff:** Maintained minimal permission scopes (commands only) to pass Marketplace security reviews.

### [Stage 10: Dark Social & Community Attribution](../stage-10-dark-social-community)
* **Problem:** Software attribution attributes peer recommendations to 'Direct' or 'Organic Search'.
* **Metric:** Coded free-text HDYHAU responses (Cohen's kappa = 1.00) and ran 2,000-sample bootstrap lift tests.
* **Tradeoff:** Adjusted raw word-of-mouth lift against company size bands, exposing that 68% of lift was confounded.

### [Stage 11: The Automated QBR Presentation Engine](../stage-11-automated-qbr)
* **Problem:** CSMs spend hours building QBR slides, while unconstrained LLMs hallucinate business metrics.
* **Metric:** Generated 16:9 PowerPoint decks with native editable charts and a mandatory review gate.
* **Tradeoff:** Enforced a zero-digit generation rule for LLMs; all math was computed in deterministic Python.

---

## 3. Public Teardowns
1. [Cursor Credit Pools & Stealth Tiers](teardowns/01_cursor_credit_pools.md)
2. [Lovable Asymmetric Credit Pricing](teardowns/02_lovable_dynamic_credits.md)
3. [Claude Rolling 5-Hour Session Windows](teardowns/03_claude_usage_windows.md)
