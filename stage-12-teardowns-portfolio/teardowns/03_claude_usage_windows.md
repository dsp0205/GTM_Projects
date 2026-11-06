# Claude: Rolling 5-Hour Session Windows Replace Fixed Token Allowances
Checked on: 2026-10-07 | Subject: Anthropic (Claude.ai)

## 1. Claim and Why It Matters
Rather than selling fixed monthly token or message quotas, Anthropic structures consumer and pro usage around dynamic 5-hour rolling windows with weekly floors. This manages peak GPU cluster contention while limiting sustained scraping behavior.

## 2. Pricing Page
* **Free:**  base access to Claude 3.5 Sonnet with dynamic rate limiting.
* **Pro:** /month (/month billed annually at ).
* **Max:** 'From /month' providing 5x to 20x Pro capacity.

## 3. Metric
*Rolling 5-Hour Session Capacity:* No static message or token count is displayed to the user. Capacity fluctuates based on prompt length, model context size, and global platform load.

## 4. Credits and Limits
When a window limit is reached, users receive an explicit reset timestamp (e.g., 'Limits reset at 3:00 PM'). Alternatively, users can opt into overage credits billed at standard API rates.

## 5. Upgrade Path
Rate-limit banners present upgrade links to the Pro or Max tiers to extend window depth.

## 6. Benchmark
B2C and consumer-grade AI subscriptions exhibit lower retention (median 49% NRR per ChartMogul) than API-driven platform infrastructure (Snowflake 125% NRR).

## 7. What I Could Not Verify
The exact mathematical threshold that triggers rate limit throttling across model variants.
