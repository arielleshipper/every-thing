---
name: presentation-comms
description: Use when creating, revising, or critiquing presentations, readouts, exec updates, all-hands narratives, strategy docs, or internal comms that need to be clear, persuasive, easy to present live, and useful across teams. Applies to slide decks, scrollable presentations, speaking outlines, roadmap readouts, change-management narratives, and feedback-driven comms.
---

# Presentation Comms

Use this skill to turn messy context into communication that works in a live room: clear enough to skim, warm enough to earn trust, and structured enough to drive action.

## Core Principles

- Match the format to the moment. A screenshare, async memo, exec update, and working session need different density, pacing, and visual structure.
- Lead with the human context. Explain why the audience is hearing this now, what input shaped it, and what it means for their work.
- Separate diagnosis from action. First name what was heard or observed, then show what will happen because of it.
- Use structure to lower anxiety. Clear buckets, simple labels, and visible sequencing make change feel navigable.
- Make the work skimmable before it is complete. Headlines should carry the argument; supporting copy should add specificity, not rescue the slide.
- Preserve warmth while adding rigor. Operational clarity should feel supportive, not bureaucratic.
- Design for voiceover. Put the core idea on screen and leave room for the presenter to add nuance, examples, and judgment live.
- Prefer hierarchy over density. Use large type, generous spacing, and distinct sections so the audience can follow while listening.
- Keep the aesthetic emotionally consistent with the message. The design should reinforce the tone: calm, credible, intentional, and alive.
- End with participation when the work is evolving. Invite feedback explicitly when the goal is alignment, iteration, or shared ownership.

## Working Pattern

1. Identify the audience and room: live vs async, decision vs alignment, executive vs team-wide, polished vs working draft.
2. Define the message arc: context, what we learned, what it means, what we will do, how the audience can participate.
3. Group detail into memorable buckets. Three to five sections usually lands better than a long inventory.
4. Write headlines as claims, not labels, when persuasion matters. Use labels when scanability matters more than narrative.
5. Convert dense lists into visual structure: grids for parallel ideas, roadmap buckets for action, and section dividers for pacing.
6. Remove anything the presenter can say better out loud unless the audience needs it for recall.
7. Check the artifact at presentation size. If it cannot be read while someone is also listening, it is too dense.

## Useful Defaults

- For all-hands or team readouts, use a warm opening that acknowledges input before moving into recommendations.
- For roadmap communication, bucket by purpose or business outcome before listing initiatives.
- For change-management comms, show the "why this matters to you" layer, not just the operational benefit.
- For feedback-driven work, make the audience feel their input changed the plan.
- For high-context internal audiences, avoid over-explaining the company. Spend the space on judgment, tradeoffs, and next steps.

## Quality Bar

A strong presentation artifact should answer:

- What is the point?
- Why am I hearing this now?
- What changed or what did we learn?
- What are we doing next?
- What do you need from me?

If those answers are not visible in the structure, revise before polishing the design.

## Editorial Review Standard

Before building or polishing an audience-facing presentation artifact, run a "Kate Lee pass":

- Would a precise editor understand why each section, label, bucket, and visual exists?
- Does the audience know what this means without Arielle explaining the taxonomy live?
- Are roadmap/status labels accurate from the recipient's point of view, not just internally convenient?
- Is the on-page copy brief enough for live presentation while leaving speaker nuance off-page?
- Does every visual choice earn its place? If a generated graphic is weak, remove it or propose options before shipping it.

For feedback-heavy site or deck revisions, batch annotations before deploying. Apply all known copy/design edits together, verify the full artifact, then push once unless Arielle explicitly asks for incremental live updates.

## Save this run as a case

Arielle collects real uses of this skill as cases in Every Checks, so its checks can be tested against real work. Benchmark members, including Mike, can read uploaded case contents. Never upload a case automatically. Once you've delivered the output, and only if the every-checks MCP tools are available (skip this section silently if they aren't):

1. Prepare a capture preview without calling `capture_case`, `review_case`, or uploading files. Show Arielle the destination task, the exact prompt and response, every context file that would be attached, and the provenance or metadata. State that Mike and other benchmark members will be able to see it, then ask: **Save this case to Arielle's Skill Checks?** Only an explicit yes to that specific preview authorizes the upload. Silence, thanks, continuing the task, or earlier blanket approval does not count.

2. After approval, call `capture_case` with `task_slug: "06-live-readout-outline"` and `benchmark: "arielles-skill-checks"`:
   - `prompt`: the request that set this skill off, in Arielle's exact words. Add earlier messages only if the request makes no sense without them.
   - `response`: what you delivered. Text goes in whole; for a doc, sheet, deck or other file, give its URL or path and a few lines on what's in it.
   - `source_key`: `codex:<YYYY-MM-DD>:presentation-comms:<first five words of the request, hyphenated>`, so a retry returns the same case instead of a twin.
   - `provenance`: what you know of the surface, the model, and any files written.
   - Leave out `gold`, `reasoning` and `checks`. Don't guess at them.
3. Upload only the context files listed in the approved preview. Save approved context as frozen text and POST it to the returned `files_url`, as multipart with the same token: `role=context` and `files[<relative path>]=@<file>`. Keep names and numbers as approved. Never attach passwords, API keys, or tokens.
4. If Arielle later corrects, redirects, or accepts the output, prepare a separate review preview showing the exact `decision`, `reasoning`, and any `gold` that would become visible. Call `review_case` only after her explicit approval of that preview. A thank-you, silence, or a new request is not a decision, so record nothing.
5. Tell Arielle in one line which case was saved. Capture comes after the work and never changes it. Capturing is not sending, approving, or paying: the approval rules in this skill still apply.
