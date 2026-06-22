---
name: weekly-ops-update
description: Run Arielle's recurring weekly ops update workflow for the Monday sync site. Use when scouting Slack, Notion, Gmail, or ops context for weekly sync candidates; preparing approval packets; updating the weekly ops site; coordinating Jalaiyah feedback in #biz-ops; posting weekly previews; or running the post-update self-improvement loop for this workflow.
---

# Weekly Ops Update

Use this skill to turn the prior week's ops activity into Arielle's Monday weekly sync update: first a private approval packet, then a Jalaiyah feedback pass, then a site update, preview post, and weekly self-improvement.

Do not start by editing the site. Start by deciding what belongs on the page.

## Source Scan

Scan the prior work week, usually Friday-to-Friday or the week since the last sync. Prioritize:

- Slack: `#biz-ops`, `#account-requests`, `#contract-requests`, Arielle's posts and threads, ops-heavy conversations, and any threads Arielle explicitly references.
- Notion: roadmap pages, policy drafts, OKR/process docs, operating docs, and pages updated during the source window.
- Gmail: vendors, contracts, account/access, billing, onboarding, tooling, internal requests, legal/finance ops, and cross-functional support.

Keep source facts separate from interpretation. If a connector or source is unavailable, say what could not be verified instead of filling gaps with plausible copy.

## Candidate Buckets

Always surface candidates by destination section. Do not give Arielle one undifferentiated list.

### Roadmap / What We Said We'd Do

Use for actual progress against existing roadmap items or stated priorities. Candidate updates may include:

- progress bar changes;
- status changes: `Backlog`, `Up next`, `In progress`, `Blocked`, `Complete`;
- items that should be marked as started;
- items that are further along than the current site shows;
- items that should move out of the roadmap because they are no longer active or no longer belong there.

Only propose roadmap updates when there is evidence of real movement. Do not turn random tactical activity into roadmap progress unless it advances a stated roadmap item.

### New Signals

Use for things that happened last week that may become process, roadmap, or systems work. Good signals include repeated requests, new operational patterns, tool/account friction, policy gaps, workflow failures, and evidence that an existing process needs to change.

Frame these as potentials, not commitments. The question is: "Should the team know this surfaced?"

### Help, Please

Use only for team asks. A Help item must tell the audience what action to take, watch for, respond to, or prepare. If there is no team action, it belongs somewhere else.

Prefer short copy in this shape:

- Hed: noun phrase naming the ask.
- Dek: one concrete action or expectation.

### Bring Us The Messy Stuff

Use for examples of how ops can help the team: contracts, onboarding, access/ownership cleanup, recurring workflows, reporting, procurement, policy/process ambiguity, and other messy cross-functional requests.

This section should make ops feel useful and approachable, not bureaucratic. Keep examples concrete and team-relevant.

## Approval Packet

Produce a private approval packet before editing files, deploying, drafting Slack, or posting. Include:

- Recommended for the site, grouped under the four candidate buckets above.
- Maybe include / needs Arielle judgment.
- Do not include but useful context.
- Suggested on-page copy.
- Suggested speaker notes.
- Source links/evidence.
- Confidence and risks.
- Suggested `#biz-ops` preview post shape.

On-page copy should be brief enough for live presentation. Speaker nuance, caveats, source detail, and internal reasoning stay off-page.

## Editorial Gate

Run a Kate Lee pass before proposing page copy or site structure:

- Would the label make sense to the audience without Arielle explaining it live?
- Is the item grouped by recipient meaning, not internal convenience?
- Is the visible page showing only what the team needs to see?
- Is any nuance better handled in speaker notes?
- Does each visual or section earn its place?
- Would an editor object to fuzzy labels, weak buckets, or copy that sounds important but says little?

If the answer is weak, revise before showing Arielle.

## Jalaiyah Feedback Gate

After Arielle responds to the approval packet with what should belong on the site, post in `#biz-ops` tagging Jalaiyah and asking what she thinks of the list and whether anything is missing.

Before tagging, check whether Jalaiyah appears out of office. If she is visibly OOO, tell Arielle and ask whether to skip, delay, or tag someone else. If there is no OOO signal, proceed with the tag.

Use a concise Slack message in Arielle's voice. Include the candidate list by section, not as a long narrative. Do not update the site until Jalaiyah responds or Arielle explicitly says to proceed without waiting.

After Jalaiyah responds:

- If she agrees or adds straightforward items, incorporate the feedback and proceed to site updates.
- If there is discussion, disagreement, ambiguity, or a sensitive issue, pause and bring the thread back to Arielle.

## Site Update Workflow

After the approval and Jalaiyah gates:

1. Batch all approved edits before changing the site.
2. Update on-page copy separately from speaker notes or private notes.
3. Verify the exact changed sections locally.
4. Run the available site validation/build checks.
5. Deploy once, unless Arielle explicitly asks for incremental deploys.
6. Confirm the live URL and the specific sections changed.

For Sites deployments, read `.openai/hosting.json`, reuse the existing `project_id`, push the exact source state, save a version from that commit, and deploy the saved version.

## Preview Post

After the site is approved and deployed, prepare or post the `#biz-ops` Monday preview according to Arielle's instruction for that week. The preview should say what the team will see and what kind of input or action Arielle wants. Do not over-summarize the whole site in Slack.

## Weekly Self-Improve Loop

After Monday morning site updates and preview coordination, run `self-improve` on this workflow.

Review:

- Arielle's packet feedback;
- Jalaiyah's feedback;
- copy edits and annotations;
- deploy or tooling friction;
- what made the site clearer or more confusing;
- anything that caused rework.

Update this `weekly-ops-update` skill narrowly when the lesson would change next week's workflow. Do not update broader skills unless Arielle explicitly asks or the lesson is clearly cross-cutting.

Good updates add sharper section criteria, better approval gates, stronger source checks, or clearer deploy steps. Avoid adding one-off facts from a specific week.
