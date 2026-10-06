---
name: ops-dispute-negotiation
description: Use when Arielle needs help with vendor pushback, disputed invoices, ops escalations, ambiguous contract terms, offboarding disputes, service/provider disagreements, reimbursement/payment disputes, or negotiation strategy that is not primarily a SaaS procurement pricing model. Helps compare possible approaches, read source language, verify math, choose the cleanest battle, draft warm-but-firm pushback, and separate the principled answer from the practical outcome.
---

# Ops Dispute Negotiation

Use this skill for relationship-sensitive disputes and operational negotiations where the goal is to resolve an ask, invoice, term, or escalation without over-lawyering it.

## Core Workflow

1. Gather the source material. Ask for the actual contract, invoice, email thread, agreement language, Slack context, and prior calculations. Do not rely on summaries when source language controls.
2. State the situation plainly. Identify the parties, the relationship, the disputed ask, the amount or term at issue, timing, and the decision Arielle needs to make.
3. Verify the math independently. If the number drives the recommendation, recalculate it from scratch. If timing matters, calculate the plausible reference dates separately.
4. Separate the principled answer from the practical outcome. Name what the clean reading supports, what the counterparty is likely to do, and where the ambiguity lives.
5. Generate 2-4 negotiation paths. Use options such as pay/move on, ask for clarification, push back with a specific counter, concede part and isolate the disputed piece, or escalate/get counsel.
6. Apply cost-of-fight judgment. Compare the disputed value to legal cost, time cost, relationship cost, and likelihood of escalation.
7. Pick the cleanest battle. Lead with the strongest, easiest-to-accept point. Concede or ignore weaker points when they distract from the core ask.
8. Anchor with a specific number or action when the math supports it.
9. Draft the next communication with a warm opening, concise reasoning, a specific ask, and a concrete next step.
10. Track unresolved questions and facts that would change the recommendation.

## Standards

- Read source documents carefully before forming a view.
- Use exact clauses, invoice lines, email language, or laws when they are available and relevant.
- Do not present legal conclusions as certain unless source law or counsel clearly supports them.
- Be explicit when something is a practical ops recommendation rather than legal advice.
- Think independently; do not anchor to Arielle's first take if the facts point elsewhere.
- Evaluate creative arguments honestly: neither dismiss them reflexively nor overstate them.
- Keep the negotiation in the right channel, especially when there is a difference between the contracting party and an underlying individual.
- Be gentle with individuals and firm with entities.

## Scenario Types

For negotiation strategy, use 2-4 paths to calibrate posture and tradeoffs.

For calculations, use the structure that fits the math:

- reference-date scenarios when timing matters
- line-item scenarios when an invoice has separable components
- conservative/base/aggressive only when estimating future usage, need, or volume

## Communication Defaults

- In analysis, stay crisp and professional.
- In Slack drafts as Arielle, it can be direct, casual, and caveated.
- In external email drafts, start warm before pushing back.
- If the deliverable includes language Arielle may send by email, also use `arielle-email-writer` before drafting the final message. This applies even when the user asks "what should I say" rather than explicitly asking for an email.
- Use "we" for Every's position and "I" for Arielle's personal read.
- End with a concrete next step, not a vague "let me know what you think."

## References

Read `references/arielle-negotiation-style.md` for Arielle's detailed negotiation posture and the Victor offboarding worked example.

## Deliverables

Choose the smallest useful deliverable:

- dispute summary
- source-language analysis
- calculation table
- 2-4 option negotiation map
- cost-of-fight recommendation
- counterparty email
- Slack update or internal recommendation
- open questions list

## Save this run as a case

Arielle collects real uses of this skill as cases in Every Checks, so its checks can be tested against real work. Benchmark members, including Mike, can read uploaded case contents. Never upload a case automatically. Once you've delivered the output, and only if the every-checks MCP tools are available (skip this section silently if they aren't):

1. Prepare a capture preview without calling `capture_case`, `review_case`, or uploading files. Show Arielle the destination task, the exact prompt and response, every context file that would be attached, and the provenance or metadata. State that Mike and other benchmark members will be able to see it, then ask: **Save this case to Arielle's Skill Checks?** Only an explicit yes to that specific preview authorizes the upload. Silence, thanks, continuing the task, or earlier blanket approval does not count.

2. After approval, call `capture_case` with `task_slug: "08-disputed-invoice"` and `benchmark: "arielles-skill-checks"`:
   - `prompt`: the request that set this skill off, in Arielle's exact words. Add earlier messages only if the request makes no sense without them.
   - `response`: what you delivered. Text goes in whole; for a doc, sheet, deck or other file, give its URL or path and a few lines on what's in it.
   - `source_key`: `codex:<YYYY-MM-DD>:ops-dispute-negotiation:<first five words of the request, hyphenated>`, so a retry returns the same case instead of a twin.
   - `provenance`: what you know of the surface, the model, and any files written.
   - Leave out `gold`, `reasoning` and `checks`. Don't guess at them.
3. Upload only the context files listed in the approved preview. Save approved context as frozen text and POST it to the returned `files_url`, as multipart with the same token: `role=context` and `files[<relative path>]=@<file>`. Keep names and numbers as approved. Never attach passwords, API keys, or tokens.
4. If Arielle later corrects, redirects, or accepts the output, prepare a separate review preview showing the exact `decision`, `reasoning`, and any `gold` that would become visible. Call `review_case` only after her explicit approval of that preview. A thank-you, silence, or a new request is not a decision, so record nothing.
5. Tell Arielle in one line which case was saved. Capture comes after the work and never changes it. Capturing is not sending, approving, or paying: the approval rules in this skill still apply.
