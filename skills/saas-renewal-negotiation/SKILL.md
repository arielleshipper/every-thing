---
name: saas-renewal-negotiation
description: Run a SaaS or API vendor renewal negotiation with commercial leverage. Use when a vendor sends a renewal proposal, reshapes pricing, or pushes a renewal call. Surfaces stealth price hikes, builds counter-proposals grounded in usage data, sequences pricing-then-legal, and anticipates common vendor playbooks (CSM dodge to live call, cross-product bundling, "pricing expires" urgency). Does NOT review contract language — pair with vendor-agreement-review or saas-msa-review for the legal track.
---

# SaaS Renewal Negotiation

## Purpose

Renewal-specific commercial tactics. Most vendor playbooks bury the actual price change in discount mechanics, unit structure, or new clauses. This skill catches those moves and builds counters grounded in your own usage data.

Pricing is treated as **separate from contract-language review**. Close commercial terms first, then push on language. Don't let the vendor reopen pricing because you raised legal questions.

## Step 1: Establish the unit economics floor

Before any call or counter, compute three numbers:

1. **Current effective per-unit rate** = current net price ÷ current units. This is your floor. Anything above is a per-unit price hike, regardless of how the vendor frames it.
2. **Current discount %** = (list − net) ÷ list. Discount erosion is the most common stealth hike.
3. **Underutilization in absolute dollars** = (contracted units − average actual usage) × effective per-unit rate. Dollar framing lands harder than percentage framing in vendor conversations.

Pull usage from the vendor's own dashboard, not your internal estimates. They can't dispute their own numbers.

## Step 2: Anchor in writing before any call

Send the proposed terms by email before the first renewal call. Forces the vendor to respond to your number rather than anchor on theirs. The opening anchor should include:

- Requested unit count (grounded in actual usage projection, not aspiration)
- Requested net price (computed at current effective per-unit rate)
- Same platform fee and discount % structure
- Short justification quoting underutilization in dollars

If the vendor refuses to send pricing async ("we'd like to discuss it live"), that's the CSM dodge. Insist on a written proposal or open the call with: "What's the proposed pricing?" — get the number on the record before any framing.

## Step 3: Decode their counter

When the vendor sends a counter, run four checks in this order:

**Check 1 — Topline vs. effective per-unit.** Topline $ and unit count can both move in the buyer's direction while the per-unit rate goes up. Always divide: counter net ÷ counter units. Compare to your current effective rate.

**Check 2 — Discount % delta.** Compare the new discount % to the prior contract. Any drop > 2 percentage points is a stealth hike achieved by leaving list price flat and shrinking the discount. Vendors do this because the dollar topline looks better than the discount-point number.

**Check 3 — Overage and "at renewal" clauses.** Search for any language tying overage units to future-renewal pricing. Phrases like "at renewal, the price for [excess units] will be the same as the price set forth above" convert temporary overage into a permanent rate hike. Always reject — escalate to legal review.

**Check 4 — Prepay/bulk options.** If the vendor offers a "discounted" prepay rate for additional units, compute it against (a) current effective per-unit rate and (b) the next-tier upgrade rate. Prepay overage is almost always more expensive than negotiating the right tier upfront.

## Step 4: Counter — "same dollars, different units"

When the vendor's total $ has been blessed by their finance team, the highest-leverage counter is to accept the dollar amount and push for more units. Two reasons:

1. The vendor's finance already approved that $ — there's no procedural reason to re-route the deal
2. It moves the per-unit rate back toward your historical effective rate without re-litigating discounts

The counter email should:

- Lead with the ask sentence ("Please send over an agreement for [X units] for $[their total].")
- Note explicitly that you're not changing the topline — preempts the finance-review delay
- Quantify the concession in their favor ("you're asking us to absorb a [X]% increase")
- Quantify your prior overpayment ("we paid for ~$[Y] of unused capacity over the last year")
- Offer a quick close ("we can get this signed [day]")
- Add a single hedge for the legal track ("provided there is no material change in the contract language")

## Step 5: Sequence — close price, then push language

Once the counter is accepted on commercial terms, switch tracks. Treat language review as a separate workstream:

- Acknowledge agreement on the dollar amount
- Note that legal review is the next step ("we're checking with counsel on the [specific clause] provisions")
- Do not reopen pricing in the same email as language redlines — gives the vendor an opening to retrade
- Hold the close timeline visible while pausing on language

See `vendor-agreement-review` for clause-level review.

## Common vendor playbooks to recognize

**CSM dodge to live call.** Vendor refuses to share pricing in writing. Goal: anchor on their number live, prevent you from running the math before responding. Counter: send your number in writing first; get pricing in writing before any call.

**Cross-product bundling.** Vendor pitches a different product mid-renewal ("we have a new offering that might be a better fit"). Goal: muddy the renewal so the per-unit comparison gets harder. Counter: "Happy to evaluate that product separately on its own merits — out of scope for this renewal."

**Give the volume concession, take it back on rate.** Vendor accepts your unit-count ask while shrinking the discount. The topline savings collapse. Counter: compute effective per-unit rate; counter on units at the same total $.

**"Pricing expires [date]" tactic.** Expiration set close to renewal date to create urgency. Counter: ignore it, negotiate it out, or push it back. Your leverage increases as the renewal date approaches — they want to close the quarter.

**"This is a clarification, not a material change."** Used to defend introduced language without actually defending its meaning. Counter: this is a legal-track issue — escalate to `vendor-agreement-review`. The phrase is a hand-wave, not an answer.

**Reframing new clauses as customer benefits.** "We now extend every customer the option to prepay…" — sounds like a courtesy, often hides a worse rate. Counter: math it out before accepting.

## What to avoid

- Negotiating price on a live call without the offer in writing
- Reopening pricing alongside legal redlines
- Accepting "trust me, the per-LA price went up because the unit count went down" — discounts and unit count are independent levers
- Letting the vendor's framing ("savings of $X") replace your own math (effective per-unit rate)
- Signing before legal review of new clauses, even under "pricing expires" pressure

## Output format

When asked to evaluate a renewal proposal, return:

**Bottom line:** 1–2 sentences — accept / counter / reject, with target counter-position
**Effective per-unit rate:** current vs proposed, with % delta
**Discount %:** current vs proposed, with point delta
**Stealth flags:** any "at renewal" clauses, prepay traps, or quietly worsened terms
**Counter proposal:** specific units + $ + justification
**Legal items to escalate:** any clauses that need contract-language review (route to `vendor-agreement-review`)

## Related skills

- `vendor-agreement-review` — clause-level legal review of the agreement
- `saas-msa-review` — for the underlying master services agreement
- `renewal-tracker` — for tracking upcoming renewal deadlines across the portfolio
- `stakeholder-summary` — for translating renewal findings into a plain-English brief for non-procurement stakeholders
