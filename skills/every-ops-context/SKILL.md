---
name: every-ops-context
description: Use when work depends on Every's operating context, internal tools, teams, approvals, onboarding, vendor management, finance operations, brand/product launch coordination, or cross-functional handoffs. Applies to Slack, Notion, Google Workspace, Ramp, GitHub, Proof, and related internal systems.
---

# Every Ops Context

Use this skill to reason with Every-specific operating context.

## Known Tool Surfaces

- Slack: fast-moving requests, access questions, launches, handoffs, quick approvals.
- Notion: meeting notes, systems docs, policies, onboarding, project context.
- Google Workspace: contracts, briefs, spreadsheets, slides, docs, inbox.
- Ramp: cards, spend, reimbursements, vendors, bills, procurement, approvals. For card issuance workflows, use `references/ramp-card-issuance-sop.md`.
- GitHub: PRs, site/product changes, engineering handoffs when available.
- Proof: product/content signals when available through connected surfaces.

## Operating Principles

- Identify the canonical source before making changes.
- Preserve approval gates around money, legal, access, people, and public-facing changes.
- For Ramp, do not perform write actions without explicit human instruction for the specific action. This is especially strict for issuing funds, creating cards, patching spend controls, changing owners or amounts, locking/unlocking cards, terminating cards, or any production mutation.
- Prefer creating one clear artifact over spreading updates across several tools.
- When a request crosses tools, name the handoff path and owner.
- When a workflow repeats, suggest turning it into a skill or automation.

## Common Work Patterns

Watch for:

- access requests and account setup
- vendor/card/payment questions
- contract and signature follow-through
- onboarding/offboarding
- launch/design review action items
- website or product copy changes moving between docs, Slack, and GitHub
- finance exceptions from email or Ramp

## Default Artifacts

Choose the lightest artifact that creates durable clarity:

- Slack draft for immediate coordination
- Notion page for recurring process or decision trail
- Google Doc for external-facing or polished prose
- Sheet for reconciliation, trackers, or finance review
- GitHub issue/PR comment for engineering follow-through

## Audience and Notion Policy QA

- Before drafting, identify the primary audience and how the artifact will be used or shared. Let the audience determine the tone, level of detail, framing, and calls to action. If the audience is not obvious from the request or available context, ask Arielle before drafting.
- Link every named policy, process, tracker, or related page to its canonical Notion source. Do not leave an existing internal resource as unlinked text.
- When separate versions serve restricted and workspace-wide audiences, add an explicit handoff from the restricted page to the shareable version and label which version should be shared.
- Verify the complete navigation path: hub to page, page to canonical supporting policies, and restricted page to the audience-appropriate version.
- Check links and permissions together. Confirm that each linked destination is accessible to the audience expected to use it.

## Open Context To Add

When available, incorporate:

- owner map for teams and systems
- canonical Notion pages
- recurring Slack channels
- approval thresholds
- vendor/payment policies
- launch process
- onboarding/offboarding checklist
