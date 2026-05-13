---
name: procurement-pricing-modeler
description: Model vendor procurement decisions and SaaS/tool pricing scenarios. Use when Codex needs to help a user evaluate an incumbent tool, identify challenger vendors, compare incompatible billing models such as annual vs monthly or seats vs usage, build conservative/base/aggressive usage scenarios, quantify commitment and underutilization risk, understand implementation work, and produce negotiation-ready pricing tables, questions, talking points, or internal recommendations.
---

# Procurement Pricing Modeler

## Overview

Use this skill to turn messy procurement context into a clear pricing model and negotiation plan. The core move is to gather the right source material, normalize proposals to a comparable unit, identify each vendor's billing primitive, and compare current usage, forecast scenarios, and realistic usage ramps.

## Workflow

1. Ask the user where to find the right context before modeling. Request pointers to relevant emails, Slack threads, Notion notes or transcripts, invoices, contracts, proposals, pricing pages, vendor decks, and internal usage dashboards. Do not assume all useful context is discoverable without user direction.
2. State the scenario in plain English before calculating. Include the business goal, incumbent vendor, challenger vendors, current usage, forecast range, and what decision needs to be made.
3. Understand incumbent terms first. Prefer invoices for actual spend and usage, then contracts, order forms, click-through terms, vendor emails, call transcripts, or self-serve pricing pages. Click-through terms often clarify legal mechanics but rarely replace invoice or order-form economics.
4. Identify challengers. Ask whether another vendor can do the same job similarly or better, then gather challenger pricing from quotes, pricing pages, procurement calls, or public docs.
5. Normalize pricing to a comparable unit. Use monthly cost, annual cost, per-seat cost, cost per unit of usage, or scenario-based total cost depending on the decision. Monthly/MRR is useful for annual-vs-monthly comparisons, but the real standard is apples-to-apples comparability.
6. Identify the billing primitive. Name whether each proposal is priced by seat, contact, send, API call, event, storage, feature tier, committed spend, or another driver. When vendors offer multiple primitives, model each separately against expected usage.
7. Model usage scenarios. Establish current usage, internal projections, vendor projections, and the gap between them. Build conservative, base/on-target, and aggressive cases whenever forecast uncertainty matters.
8. Separate steady-state from ramp. First calculate cost if the company is at the target usage immediately. Then calculate month-by-month cost under a realistic ramp from current usage to each forecast case.
9. Quantify optionality and commitment risk. Compare monthly usage billing against annual prepay, minimum commits, underutilization rules, overage rules, rollover, true-up, refunds, cancellation rights, and expansion triggers.
10. Scope implementation work. Identify whether engineering, data migration, admin setup, security review, deliverability/reputation work, or user retraining is required. Keep this separate from pure pricing unless the user asks for all-in cost.
11. Convert ambiguity into vendor asks. If terms are missing, produce crisp questions about underutilization, overutilization, billing unit definitions, active vs stored units, blended usage, and migration requirements.
12. Return receipts. Present the numbers in concise tables, then give negotiation talking points tied to those numbers.

## Modeling Standards

- Choose one comparison basis and use it consistently. For annual-vs-monthly vendor comparisons, monthly cost is often clearest. For usage primitives that differ, compare total cost under the same usage scenarios.
- Keep annual totals available when annual commitment risk matters, but do not lead with annual numbers unless they are the clearest comparison unit.
- Show the exact usage assumption next to every cost.
- Treat switching costs separately from vendor price unless the user asks to fold them into the model.
- Do not assume a prepaid annual contract refunds unused capacity. If unknown, model no refund as the conservative case and list it as a vendor question.
- Do not assume overage rates. If missing, mark them unknown and ask for them before recommending a commitment.
- Prefer ranges over false precision when forecasts are uncertain.
- When comparing billing primitives, model the unit that best matches actual product behavior, not just the vendor's default category.
- Treat vendor forecasts as evidence, not truth. Compare them against internal usage data and explicitly name the delta.
- Ask for call transcripts or meeting notes when vendor conversations contain pricing nuance that did not make it into an email or quote.

## Useful References

- For procurement intake questions, read `references/intake-checklist.md`.
- For output structures and negotiation language, read `references/output-templates.md`.
- For common billing primitives and modeling traps, read `references/billing-primitives.md`.

## Calculator Script

Use `scripts/pricing_model.mjs` when the model has enough structured numbers to compute repeatable scenarios. Create a small JSON input file with vendors and usage scenarios, then run:

```bash
node scripts/pricing_model.mjs path/to/input.json
```

Use the script for arithmetic and tables, then add judgment in the final answer: vendor fit, missing terms, commitment risk, and the strongest negotiation ask.

## Deliverables

Choose the smallest useful deliverable:

- Understanding summary: what is happening, what is known, what is unknown.
- Pricing table: normalized cost by vendor and usage scenario, using the comparison unit that makes the vendors comparable.
- Ramp model: month-by-month cost from current usage to target usage.
- Negotiation memo: receipts-backed talk track for the vendor.
- Vendor questions: missing terms, pricing clarifications, or a target ask to bring into the next call.
- Internal recommendation: preferred option, conditions, implementation scope, and decision risks.
