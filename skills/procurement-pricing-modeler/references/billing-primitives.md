# Billing Primitives

The most important procurement question is often not which vendor is cheaper, but which billing primitive best matches actual usage.

## Common Primitives

- Seats: best when value scales with users. Watch for inactive seats, contractors, admins, and minimum seat counts.
- Contacts or records: best when value scales with stored entities. Watch for active vs inactive contacts, duplicates, suppressed contacts, and opt-outs.
- Sends, events, or API calls: best when cost scales with throughput. Watch for burst pricing, retries, non-production usage, and blended use cases.
- Storage or data processed: best when infrastructure cost drives vendor cost. Watch for retention, logs, backups, and export costs.
- Revenue or GMV percentage: best when vendor value tracks monetization. Watch for margin compression as the business scales.
- Flat tier: simple, but often hides usage caps, support limits, or renewal cliffs.
- Annual committed spend: can be cheap at high utilization, but creates underutilization risk and reduces optionality.

## Modeling Traps

- Comparing annual prepaid cost to monthly usage cost without choosing a shared comparison period.
- Comparing vendors on their quoted unit prices instead of modeling the company's expected usage under each billing primitive.
- Modeling only the target run-rate instead of the ramp to that run-rate.
- Treating a vendor forecast as truth without checking historical growth.
- Ignoring active vs stored units.
- Ignoring whether each vendor counts units the same way.
- Treating overage rates as known when they are not in the quote.
- Forgetting that annual commitments can be rational only if the discount beats the value of monthly optionality.

## Heuristics

- If usage is growing but uncertain, monthly billing has option value.
- If a vendor wants annual prepay for a target volume the company will only reach late in the year, compare annual prepay against a ramp model.
- If two billing primitives are available, model both. A lower unit price can still lose if the wrong unit is being counted.
- If the incumbent's proposal has a cheaper high-volume tier than its mid-volume tier, challenge the quote structure directly.
- For self-serve vendors, start from the pricing page but confirm enterprise discounts, usage definitions, and overage mechanics before treating it as final.
- For incumbents, invoices usually beat contracts for economic reality because they reveal actual usage, discounts, overages, and fees.
