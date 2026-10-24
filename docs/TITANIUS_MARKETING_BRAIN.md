# TITANIUS: Permission-first digital marketing brain (2026-10-24)

**Source materials:** user-supplied YouTube descriptions/chapter timestamps and
community comments, not complete video transcripts. The assistant also
checked the independently available episode descriptions and Anthropic's
official announcement. We must not attribute unseen quotes to presenters.

- Seth Godin / Calum Johnson, 21 September 2026:
  https://www.youtube.com/watch?v=dNWkwrqAkcM
  Description covers specificity, trust, finding a meaningful offer,
  repeat customers and referrals, rather than requiring virality.
- Sabri Suby, 31 July 2026:
  https://www.youtube.com/watch?v=HsjuAvqs3zU
  Marketing education about turning attention into actual purchase intent.
  Do not copy anyone's paid marketing playbooks.
- "Elon Musk and Anthropic Are Giving Away $59 Billion" (21 Oct 2026):
  https://www.youtube.com/watch?v=iP8ctH6_nOw
  Headline requires fact-check, not a presumption of accessible grant money.
  Anthropic's *official* 18 Oct announcement is about a proposed allocation
  of equity to a public-benefit fund, subject to approval:
  https://www.anthropic.com/news/public-benefit-fund
- Windows "God Mode" is a Windows settings shortcut, **not** AI cognition
  or elevated powers for the TITANIUS system.

## Mission, not promises

TITANIUS → `growth_brain` → `marketing_brain.py` monitors one
**already available** digital product: MicroVault paid CSV-quality reports
(€5/€29, one-time, original data stays in the purchaser's own browser).
The aim is direct checkout with automatic report delivery. No unpaid
custom projects, outbound cold messaging, lead sales, ads, testimonial
fabrication, or speculative charity/grant applications.

The production website is independently fetched in the existing 6-hour
`titanius-control-center.yml` GitHub Action. Eight measurable on-page
signals are checked:

1. Specific CSV data-quality problem and intended use.
2. Both product prices visible plus one-time-payment disclosure.
3. Clear purchase call to action.
4. Report download / fulfillment expectations.
5. How CSV data is handled.
6. Legal/privacy links.
7. Simple questions/FAQ and offer scope.
8. Payment-merchant identity.

Signals describe **visible HTML disclosure only**, not actual quality,
user trust, real traffic, purchase conversion, customer satisfaction,
legal compliance, or successful digital file delivery.

When a check is missing, the growth brain records **one persistent review
task** with the missing signal names. This makes repeated checks
idempotent, identifies changes and preserves memory without paid model
credits. If all pass, it emits no unnecessary task.

## External truth boundaries

A paid order is true only after authenticated provider payment
reconciliation, refund and settlement readback; file delivery is true
only after confirmed entitlement and report-download receipt.

Without both independent feeds, `finance.verified_net_revenue_eur=null`,
`confirmed_paid_orders=null`, and `confirmed_deliveries=null`.
Do not turn those unknowns into reported sales, profit or customer success.

## Implementation evidence

- Public runner source: `workflows/marketing_brain.py`
- Enclosing loop: `workflows/titanius_control_center.py`
- Tests: `tests/test_marketing_brain.py`
- Read-only scheduled action: `.github/workflows/titanius-control-center.yml`
- Persistent real-world issue: https://github.com/charlysmoky2010-hub/ai-guardrails-protocol/issues/1
- Reference passing run (13 tests): https://github.com/charlysmoky2010-hub/ai-guardrails-protocol/actions/runs/40076259259

The result is a **deterministic marketing auditor**, not a self-directed,
self-rewriting large language model. The next unresolved technical jobs
are authoritative receipts and verifiable file fulfillment; new consumer
marketing messages are not needed to cover up these missing proofs.
