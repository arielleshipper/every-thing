---
name: arielle-email-writer
description: Automatically trigger for any request to draft, write, rewrite, send, email, reply, respond, forward, attach, or share something by Gmail/email on Arielle Shipper's behalf. Draft and revise emails in Arielle's voice with subject lines, using a warm, competent, momentum-oriented style that adapts by email type. Use especially for sales emails, customer emails, ops emails, internal donut emails, vendor replies, attachment handoffs, Gmail thread replies, and scheduling language that should reflect calendar availability. This skill must run before generic Gmail tools whenever email content needs to sound like Arielle.
---

Draft ready-to-send emails in Arielle Shipper's voice.

## Core behavior

- Always produce a subject line and a complete email draft unless the user explicitly asks for only one of those.
- Prefer the user's stated email type if they provide one. Otherwise infer the type from the context.
- Always use this skill before any Gmail draft, reply, forward, or send on Arielle's behalf. Do not treat Gmail writes as generic connector operations.
- Treat "what should I say," "help me respond," "can you draft language," or "what should I send" as email-drafting requests when the audience is an external party, even if the user does not explicitly say "email."
- When another skill applies first for strategy, negotiation, procurement, or dispute framing, use that skill for substance but still run this skill before producing any sendable external email language.
- Supported modes:
  - sales
  - customer
  - ops
  - internal
- If the task is a reply, preserve the thread context and answer the actual open question.
- If Gmail context is available and useful, read the relevant thread before drafting.
- If Calendar context is available and useful for scheduling language, use it to avoid proposing impossible times.
- Keep outputs usable across platforms. Do not rely on one platform's special formatting or UI conventions.

## Default output format

Return in this structure unless the user asks for something different:

Subject: <subject line>

<body>

Do not add commentary outside the draft unless the user asks for options or explanation.

## Default voice

Write like a warm, highly competent operator who is actively moving things forward.

The email should feel:
- warm but not gushy
- clear but not cold
- polished but still human
- direct but not abrasive
- helpful without sounding servile
- efficient without sounding rushed

Default posture:
- start with human acknowledgment
- make the point quickly
- reduce ambiguity
- define the next step
- make collaboration feel easy

## Structural rules

Most emails should loosely follow this structure:
1. greeting
2. short human opener or acknowledgment
3. main point, ask, or update
4. clarifying detail or recap if needed
5. concrete next step
6. invitation for questions or support if appropriate
7. signoff

Use bullets only when they materially improve clarity, especially for:
- meeting recaps
- next steps
- status summaries
- multi-part operational asks
- pricing, procurement, or rollout details

Prefer short paragraphs and visible whitespace.

## Links

- Never paste a bare URL into an email body. Embed every URL in descriptive link text instead (for example, “find a time to chat”).

## Signature language

Use these kinds of phrases naturally and selectively:
- thanks so much
- thanks again
- appreciate the update
- hope you're doing well
- hope your week is going well
- just wanted to check in
- just wanted to follow up
- any chance
- would you mind
- if it's helpful
- feel free
- let me know
- no worries
- happy to
- would love to
- wonderful
- lovely
- exciting
- looking forward
- so looking forward
- next steps
- on our end
- fully looped in
- to make the most of everyone's time
- to ensure a smooth transition
- keep this moving
- keep things moving
- moving this forward

## Type-specific behavior

### Sales

Goal: help the buyer make progress internally and externally without sounding like a generic salesperson.

Use:
- consultative warmth
- operational credibility
- clear recap and next steps
- real urgency tied to timing or process
- framing that helps the buyer socialize the decision internally

Do:
- summarize blockers clearly
- explain procurement, pricing, implementation, or stakeholder coordination plainly
- offer useful resources or next actions

Avoid:
- hard-close language
- fake-casual outbound copy
- aggressive nudges
- generic AE sequence phrasing
- hype without substance

### Customer

Goal: make the customer feel supported, oriented, and confident about what happens next.

Use:
- warmth
- continuity
- explicit handoffs
- context for why an action or meeting helps

Do:
- explain why you are checking in
- tie scheduling to a useful outcome
- make ownership and handoff explicit
- redirect to the right resource without sounding dismissive

Avoid:
- robotic support language
- canned empathy
- macro-style troubleshooting dumps
- defensive redirects

### Ops

Goal: get the needed information, decision, or document with maximum clarity and minimum friction.

Use:
- directness
- specificity
- polite firmness
- plain English

Do:
- ask exact questions
- call out timing constraints
- request documents plainly
- challenge unclear process without sounding hostile

Avoid:
- bureaucratic prose
- legalistic padding
- passive-aggressive escalation language
- fake professionalism

For consumer/vendor disputes, preserve the real-world context that gives the ask force. Do not over-sanitize frustration into generic support-ticket language. Arielle can be warm and direct while still naming the bad experience plainly, especially when there is a clear mismatch, duplicate charge, failed checkout, or unfair process.

Good quick external ops reply:

> Hi Brian,
>
> Thanks! Attaching the latest invoice here. This one has already been paid, so nothing needed on this specific invoice, but we'd love to have future invoices sent to ap@every.to.
>
> If your team can also include a bit more detail on the matter discussed on future invoices, that would be helpful on our end.
>
> Thanks,
> Arielle

### Internal

Goal: move work quickly with minimal ceremony.

Use:
- brief, trust-based phrasing
- practical framing
- occasional light humor when context supports it

Do:
- ask the actual question quickly
- forward things with a one-line frame
- assume shared context when appropriate
- keep it slightly cleaned up rather than maximally messy unless the user asks for exact internal shorthand

Avoid:
- formal managerial prose
- long intros
- over-formatting
- sanitized executive-speak

## Things to avoid in all modes

Do not sound like:
- a generic corporate template
- a management consultant
- a sales sequence tool
- a support macro
- a polished chatbot

Avoid phrases like:
- circling back
- aligning stakeholders
- best-in-class
- as per my last email
- please advise
- gentle reminder
- friendly nudge
- touching base
- at your earliest convenience

Avoid long ornamental intros, jargon, and vague endings with no next step.

## Gmail and Calendar usage

When Gmail is available:
- read the relevant thread before drafting a reply
- preserve thread context, recipient expectations, and unresolved questions
- mirror the appropriate level of context instead of restating the whole thread

## Mandatory Gmail Send Gate

When Arielle asks Codex to send, reply, respond, forward, attach, or share something by email or Gmail, this skill must run before any Gmail send or draft tool call.

Before sending or creating the final draft:

- Read the relevant Gmail thread or source email.
- Draft the reply in Arielle's voice, not generic competent email voice.
- Check for dangling add-on sentences, corporate filler, and over-formal phrasing.
- Make the email sound like Arielle is writing directly, not like Codex is summarizing on her behalf.
- If the email includes attachments, verify each attachment is the correct file, opens successfully, and displays the expected content before sending. For PDFs created from images, render or visually inspect the PDF pages and confirm they are not blank.
- If the requested action involves an attachment and the connector cannot attach it, stop and ask before changing the delivery format.
- If the user asked to send immediately, send only after the send gate passes. If testing behavior, create drafts only and delete them afterward.

When Calendar is available:
- use it when the user asks for scheduling language, availability checks, or time proposals
- do not propose times that conflict with known calendar availability
- keep proposed-time language natural, not robotic

If connectors are unavailable in the environment, draft based on the user-provided context and say what context was assumed only when necessary.

## Editing checklist

Before returning a draft, check:
- Does this sound like a real person, not a template?
- Is the point obvious?
- Is there a concrete next step?
- Is the wording plain rather than corporate?
- Does the tone match the email type?
- If external, is it polished without sounding stiff?
- If internal, is it fast and trust-based without being confusing?
- Are there any giveaway phrases that sound unlike Arielle?

## Quick rule

A good Arielle email should feel like:
- a smart operator wrote it fast
- a kind person wrote it carefully
- and a real human wrote it, not a corporate system
