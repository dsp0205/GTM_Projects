# SignalPing: Marketplace Submission Packet

## 1. App Listing Copy
* **App Name:** SignalPing
* **Short Description (<= 10 words):** Account buying signals in Slack, one command.
* **Long Description:** 
  SignalPing delivers real-time buyer intent signals directly to your team's Slack channels. By typing /signal <domain>, sales reps and account executives instantly access buyer engagement scores and primary activity drivers without switching tabs.
* **Required Scopes:** 
  * commands (Add slash commands that users can trigger directly)

## 2. Eligibility & Review Criteria Checklist
* [x] **State Parameter on OAuth:** Cryptographically random state parameter used on /slack/install and validated at /slack/oauth_redirect to block CSRF.
* [x] **Request Signature Verification:** All incoming requests verified against X-Slack-Signature using the signing secret and timestamp window.
* [x] **Minimal Scopes Justification:** Restricts permissions to commands only; avoids broad or unsuitable scopes (dmin.*, search:read, identity.*).
* [x] **Token Storage & Rotation:** Bot tokens stored encrypted at rest with Fernet; refresh transactions locked via BEGIN IMMEDIATE to prevent duplicate refresh race conditions.
* [x] **Support SLA Commitment:** Dedicated support contact with a confirmed response time under 2 business days without requiring account creation.
* [x] **Marketplace Minimums Strategy:** Plans direct 'Add to Slack' onboarding for initial 10 customer workspaces prior to submitting for public listing.
