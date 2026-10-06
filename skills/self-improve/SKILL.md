---
name: self-improve
description: Use when Arielle asks Codex to reflect on its work, critique an output, learn from corrections, improve a workflow, update a skill, or capture durable judgment for future sessions. Also use near the end of substantial tasks involving analysis, automation, code, comms, workflows, approvals, or cross-tool work when there was friction, correction, ambiguity, or a reusable lesson.
---

# Self Improve

Turn task-level feedback into durable improvement in Codex's future judgment, process, verification, and communication with Arielle.

## Goal

Help Codex learn how Arielle thinks, not just what Arielle says.

Use real artifacts, corrections, questions, failures, and workflow friction to identify reusable rules. Capture the smallest useful update in the right place: a domain skill, Arielle Operating System, an automation spec, a checklist, or no durable artifact if the lesson is too local.

## When To Run

Run when Arielle says `/self-improve` or asks:

- what went wrong?
- what should we add to a skill?
- what should you remember next time?
- why did this feel fake/generic/wrong?
- how can we make this process better?
- should this become a skill or automation?
- what did you learn from this?

At the end of substantial tasks, consider suggesting it when:

- Arielle corrected a claim, workflow, draft, artifact, or assumption.
- A data result did not pass Arielle's sniff test.
- A generated artifact needed multiple rounds because behavior did not match intent.
- A workflow involved recurring reports, automations, approvals, or cross-tool handoffs.
- The task revealed a reusable preference about source-of-truth, verification, scope, or communication.
- Codex had to be taught how to work better with Arielle.

Do not run for trivial one-off tasks unless Arielle invokes it.

## Core Workflow

1. Identify the actual artifact or behavior.
   - Use the real draft, file, output, automation, analysis, commit, or message.
   - Do not critique from memory if the artifact can be read.
   - Name the task context and what Arielle was trying to accomplish.

2. Capture Arielle's correction.
   - What did Arielle notice?
   - What question did she ask that exposed the issue?
   - Was the problem accuracy, judgment, scope, process, tone, UX, verification, or durability?
   - Did Arielle ask for options before changes, a readback, a source check, or a deeper explanation?

3. Diagnose the failure mode.
   - Did Codex rely on a weak source of truth?
   - Did Codex over-polish, over-generalize, or make a generic suggestion?
   - Did Codex skip a needed approval gate?
   - Did Codex verify technically but not in the way Arielle would inspect the result?
   - Did Codex use the wrong grain, date range, population, or definition?
   - Did Codex build the thing but fail to make it durable across sessions?
   - Did Codex answer the literal ask but miss the operational reason behind it?

4. Extract the durable lesson.
   - Separate one-off facts from reusable judgment.
   - Prefer rules that would change future behavior.
   - Capture negative examples when they are more diagnostic than positive examples.
   - Name the trigger: when should future Codex apply this lesson?

5. Choose the right destination.
   - Arielle Operating System: cross-cutting judgment, approvals, source-of-truth, verification, communication, or collaboration rules.
   - Domain skill: repeatable procedure in a specific area such as Slack, procurement, sales tax, Ramp, Gmail, docs, or analytics.
   - Automation spec: recurring monitoring, reporting, reminders, exception checks, or scheduled background work.
   - Checklist/test: artifact-specific verification that should happen before handoff.
   - No update: if the lesson is too local or already covered.

6. Propose before editing.
   - State the observed pattern.
   - State the durable lesson.
   - Name the proposed target skill/file.
   - Include the exact draft update.
   - Ask Arielle to confirm before making changes.

7. After confirmation, edit narrowly.
   - Read the target skill first.
   - Preserve unrelated changes.
   - Patch only the relevant section.
   - Show the diff or summary.
   - Commit/push only when Arielle asks.

## Arielle Judgment Patterns To Check

### Source Of Truth

Ask:

- Did we use the actual source material?
- Did we treat the right doc/system/export as canonical?
- Did we distinguish source facts from interpretation?
- If a connector/tool was unavailable, did we stop instead of inventing?

Arielle often prefers: "I can't verify this from the available source" over a plausible answer.

### Analysis Accuracy

Ask:

- Does the result pass a basic business sniff test?
- Are we using the right denominator, population, date range, and grain?
- Are we confusing a boolean/status field with the underlying data?
- Are active records being confused with all historical records?
- Can we sample rows or examples to prove the interpretation?
- If the result changed, did the actual exported artifact change too?

For high-stakes analysis, include a verification loop that Arielle could inspect.

### Automation Quality

Ask:

- What are the input sources?
- What is the output artifact?
- Who receives it?
- How often should it run?
- What approval is needed before sending or acting?
- What would make this worth keeping?
- What failure modes should be monitored?
- Is this an automation, a skill, a checklist, or just a one-off task?

Automations should reduce coordination load, not create mystery machinery.

### Artifact And UX Quality

Ask:

- Does the artifact behave the way Arielle would expect when she clicks it?
- Are controls wired uniformly?
- Does the visible state match the underlying state?
- Did we verify the exact workflow Arielle reported as broken?
- Does the structure preserve the source material where it matters?
- Did we run proposed structural changes by Arielle before changing them?

A technical pass is not enough if the artifact fails the user-facing inspection.

### Approval And Change Control

Ask:

- Is this reversible and low-risk?
- Does it affect money, access, legal, people, customer-facing work, or external commitments?
- Did Arielle ask for options before changes?
- Should Codex draft/recommend instead of acting?

When unsure, propose the next move and ask for approval.

### Durability

Ask:

- Is this likely to recur?
- Should the lesson become a skill update?
- Should the workflow become an automation?
- Should the repo/skill path/GitHub sync be updated so future sessions inherit it?
- Does the skill trigger description make clear when to use it?

Arielle values compounding infrastructure over one-off cleverness.

### Communication Fit

Ask:

- Does the response match the channel, relationship, and stakes?
- Did Codex make it too formal, too generic, too confident, or too assistant-like?
- Did Codex explain in Arielle's mental model before technical detail?
- Did the response end with a useful next step?

## Default Output

Use this shape:

**Observed Pattern**
What happened, grounded in the actual task/artifact.

**Arielle Correction**
What Arielle noticed, asked, rejected, or reframed.

**Failure Mode**
The reusable reason Codex missed.

**Durable Lesson**
The future rule.

**Proposed Update**
Target skill/file and exact Markdown to add.

**Confirm?**
Ask before editing.

## Save this run as a case

Arielle collects real uses of this skill as cases in Every Checks, so its checks can be tested against real work. Benchmark members, including Mike, can read uploaded case contents. Never upload a case automatically. Once you've delivered the output, and only if the every-checks MCP tools are available (skip this section silently if they aren't):

1. Prepare a capture preview without calling `capture_case`, `review_case`, or uploading files. Show Arielle the destination task, the exact prompt and response, every context file that would be attached, and the provenance or metadata. State that Mike and other benchmark members will be able to see it, then ask: **Save this case to Arielle's Skill Checks?** Only an explicit yes to that specific preview authorizes the upload. Silence, thanks, continuing the task, or earlier blanket approval does not count.

2. After approval, call `capture_case` with `task_slug: "17-self-improve-proposal"` and `benchmark: "arielles-skill-checks"`:
   - `prompt`: the request that set this skill off, in Arielle's exact words. Add earlier messages only if the request makes no sense without them.
   - `response`: what you delivered. Text goes in whole; for a doc, sheet, deck or other file, give its URL or path and a few lines on what's in it.
   - `source_key`: `codex:<YYYY-MM-DD>:self-improve:<first five words of the request, hyphenated>`, so a retry returns the same case instead of a twin.
   - `provenance`: what you know of the surface, the model, and any files written.
   - Leave out `gold`, `reasoning` and `checks`. Don't guess at them.
3. Upload only the context files listed in the approved preview. Save approved context as frozen text and POST it to the returned `files_url`, as multipart with the same token: `role=context` and `files[<relative path>]=@<file>`. Keep names and numbers as approved. Never attach passwords, API keys, or tokens.
4. If Arielle later corrects, redirects, or accepts the output, prepare a separate review preview showing the exact `decision`, `reasoning`, and any `gold` that would become visible. Call `review_case` only after her explicit approval of that preview. A thank-you, silence, or a new request is not a decision, so record nothing.
5. Tell Arielle in one line which case was saved. Capture comes after the work and never changes it. Capturing is not sending, approving, or paying: the approval rules in this skill still apply.
