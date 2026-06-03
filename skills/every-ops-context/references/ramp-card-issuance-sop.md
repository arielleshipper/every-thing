# Ramp Card Issuance SOP

Use this SOP when converting approved recurring spend into Ramp virtual cards, especially when using agents or scripts to create cards through the Ramp API.

## Core Principle

This is finance work. Optimize for traceability, least privilege, explicit approval gates, and evidence-backed verification. Do not guess merchant restrictions, and do not replace durable cards when a later patch can update the same card.

Hard safety rule: do not act in Ramp without explicit human instruction for the specific write action. This is especially strict for issuing funds, creating cards, patching card controls, changing owners or amounts, locking/unlocking cards, terminating cards, or any other production Ramp mutation. Read-only planning and verification are allowed; write scopes alone are never approval.

## Source Of Truth

- The source sheet should contain a final `Ramp Cards to Issue` tab.
- Use the tab's visible rows as the source of truth for card creation.
- Standard columns:
  - Column A: inclusion note, approval flag, or cancel-by note.
  - Column B: card/vendor display name.
  - Column C: source monthly amount.
  - Column D: monthly card amount with slush.
- Use column D as the Ramp monthly card amount unless Arielle explicitly says otherwise.

## Sheet Conversion Rules

- Include only rows whose source inclusion value clearly means yes.
- Include examples: `Yes`, `Y`, `yes`, `YES`, `Yes cancel 6/30`, `yes - cancel after June`.
- Exclude examples: blank, `No`, `Cancelled`, `Cancel by 6/30`, `Maybe`, or any non-affirmative note.
- A cancellation note alone is not enough. Include it only if the cell also clearly contains an affirmative marker.
- Convert source amounts to positive values using absolute value.
- Dedupe by exact source vendor/description.
- Sum duplicate positive amounts into one output row.
- Add slush as `CEILING(amount * 1.30, 5)`.

## Cancel-By And Lock Date Handling

- If column A contains a cancel-by date, extract and normalize it to `MM/DD/YY`.
- If a row already appears in a final `Ramp Cards to Issue` tab, preserve the row and use the cancel-by date as the lock-date input.
- Ramp's API requires `lock_date` as a datetime, not a plain date.
- Timezone matters. For example, `2026-06-30T00:00:00Z` displays in Ramp as `Jun 29, 2026, 8:00 PM` for Eastern time.
- Before future runs, decide whether `Cancel by 6/30` means lock at the start of 6/30 local time or after the end of 6/30 local time, then convert that local intent to UTC.

## Permission Preflight

Before opening Ramp or calling the API:

- Map the intended actions to required scopes.
- Check the current token or app credentials for those scopes.
- If scopes are missing, authenticate or update app permissions first.
- Use the smallest practical scope set.
- Never commit API credentials, secrets, tokens, `.env` files, or local CLI config.
- Permission availability is not approval to act. Having `cards:write`, `funds:write`, or similar write scopes only means the action is technically possible; still wait for human instruction before using them.

Common scopes:

- Create cards: `cards:write`, `cards:read`, `users:read`, `merchants:read`.
- Verify cards: `cards:read`, `users:read`, `merchants:read`.
- Find post-charge merchant evidence: `transactions:read`, `merchants:read`, `cards:read`.
- Patch existing cards: `cards:write`, plus read scopes for verification.

## Card Creation Rules

- Create durable virtual cards for every approved row.
- Do not create throwaway or temporary cards unless Arielle explicitly asks.
- Use column B as the card display name.
- Use the requested owner from the run brief.
- Use column D as the monthly cap.
- Set `interval` to `MONTHLY`.
- Set `is_temporary` to `false`.
- Add a lock date only when the sheet includes a valid cancel-by date.
- Preserve an explicit approval checkpoint before production writes.

## Merchant Restriction Rules

- Add `spending_restrictions.vendor_whitelist` only when the Ramp merchant UUID safely matches the intended vendor.
- Merchant names alone are not enough. Prefer evidence from:
  - Ramp `/merchants` results when the merchant name is unambiguous.
  - Prior Ramp transactions with matching `merchant_descriptor`, `merchant_name`, `merchant_id`, and amount pattern.
  - Arielle-confirmed matches when Ramp's merchant name is imperfect but plausible.
- Do not use an unrelated or merely similar merchant. For example, a merchant like `TwitterShots` should not be used for X/Twitter developer-platform spend.
- If no safe merchant UUID exists, still create the durable card with the correct vendor name and monthly cap, but omit `vendor_whitelist`.
- The lack of a merchant UUID is a pending control, not a blocker for creating the card when Arielle has approved the durable-card approach.

## Updating Cards Later

When a missing merchant is discovered after first charge:

- Update the same existing card.
- Do not replace, terminate, or rename into a new card unless Arielle explicitly asks.
- Use `PATCH /developer/v1/cards/{card_id}` with `cards:write`.
- Patch `spending_restrictions.vendor_whitelist` with the verified merchant UUID.
- If needed, also patch `display_name` to normalize the card name.

Ramp's card update schema supports partial `spending_restrictions`, including:

- `vendor_whitelist`
- `vendor_blacklist`
- `amount`
- `interval`
- `transaction_amount_limit`
- `lock_date`

## Monthly Merchant-Lock Review

Run a monthly review for durable vendor-named cards that were created without `vendor_whitelist`.

For each pending card:

- Inspect transactions since the last review.
- Compare the transaction descriptor, Ramp merchant name, merchant UUID, amount, and timing to the intended vendor.
- If the match is safe, prepare a proposed PATCH to add `spending_restrictions.vendor_whitelist`.
- Report proposed changes to Arielle before applying any PATCH.
- Apply the patch only after Arielle approves.

The monthly report should include:

- Card name
- Card ID
- Intended vendor
- Transaction descriptor
- Ramp merchant name
- Merchant UUID
- Transaction date
- Transaction amount
- Why the match is believed safe
- Exact proposed patch

Edge cases:

- If there is no transaction yet, report the card as still pending and make no change.
- If multiple transactions all resolve to the same safe merchant UUID, propose one update and include the transaction count plus representative examples.
- If transactions resolve to multiple plausible merchant UUIDs, do not patch automatically. Report the candidates and ask which merchant or merchants should be allowed.
- If the descriptor looks like a payment processor, marketplace, generic billing platform, or unrelated vendor, do not patch automatically.
- If the transaction amount materially exceeds the card's expected monthly cap, or if the card has unexpected spend before merchant locking, flag it for review instead of treating it as routine evidence.

## Verification Rules

After creation or patching, run a read-back verification.

Verify:

- Expected number of cards exists.
- Card names match the source sheet.
- Owner/cardholder matches the run brief.
- Card type is virtual.
- Card state is active.
- Monthly amount matches column D.
- Interval is monthly.
- Lock date matches the normalized cancel-by date when present.
- Merchant restriction status is recorded as one of:
  - vendor whitelist requested with merchant UUID evidence;
  - intentionally unrestricted pending first charge;
  - patch proposed and awaiting Arielle approval;
  - patched after approval.

Important Ramp API limitation:

- Ramp card read/detail responses may not expose allowed merchant fields.
- When the API does not expose merchant restrictions, keep evidence from the create or patch payload plus Ramp task success.
- Use UI spot checks when the API does not show the restriction and the risk warrants extra confirmation.

## Agent Coordination

Use a hub-and-spoke workflow for high-stakes batches:

- Coordinator owns the source of truth, approvals, final writes, and final synthesis.
- Sheet agent verifies row inclusion, dedupe, amounts, and slush.
- Merchant agent resolves Ramp merchant UUIDs and flags ambiguous matches.
- Builder agent prepares the card creation or patch plan.
- Verifier agent independently checks plan, create results, and API read-back.
- Coordinator applies only approved writes and reports the evidence.

Do not port whole transcripts between agents. Port a short context packet with the source sheet, decisions, constraints, expected output, and verification checklist.

## Approval Gates

Ask Arielle before:

- Any Ramp write action unless Arielle has already given explicit instruction for that exact action in the current run.
- Any issuing of funds, including new funds, fund increases, fund owner changes, or fund restrictions.
- Any production card creation.
- Any card patch that changes merchant restrictions, card owner, card amount, or lock date.
- Any action that requires new Ramp scopes or app permissions.
- Any destructive or replacement action.

No approval needed for:

- Read-only planning.
- Read-only merchant lookup.
- Read-only verification.
- Local artifact generation that does not expose secrets.

## Evidence Artifacts

For each run, save:

- Source sheet URL and tab name.
- Card creation manifest.
- Merchant matching evidence.
- Creation result with deferred task IDs and card IDs.
- Verification result.
- Pending merchant-lock list.
- Monthly review decisions and approvals.

Do not save secrets in these artifacts.
