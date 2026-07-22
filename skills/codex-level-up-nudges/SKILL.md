---
name: codex-level-up-nudges
description: Use when Arielle is starting or shaping a Codex task and would benefit from learning how to use Codex more effectively. Applies to prompts that are complex, cross-tool, high-stakes, recurring, research-heavy, multi-step, approval-gated, or likely to produce reusable process. Proactively suggest better Codex operating modes such as Compound Engineering planning, LFG for planning, /goal for execution, coordinator plus specialist agents, verifier/skeptic passes, skills, automations, checklists, or SOPs.
---

# Codex Level-Up Nudges

Help Arielle learn how to use Codex better in the moment, while she is giving prompts.

This skill is about teaching Arielle how to operate Codex, not about Codex learning Arielle's preferences. Keep nudges short, concrete, and tied to the task at hand.

## When To Nudge

Briefly nudge at the start of a task when one or more are true:

- The work is high-stakes: money, access, legal, people, security, customer-facing output, external commitments, or data deletion.
- The work crosses tools or sources: Slack, Gmail, Notion, Drive, Calendar, browser, APIs, spreadsheets, local files, or GitHub.
- The prompt is multi-step, ambiguous, research-heavy, or likely to become a long thread.
- The task is recurring or resembles a workflow Arielle has done before.
- The output will be reused by others or should become institutional knowledge.
- A separate verifier, skeptic, researcher, builder, or comms pass would reduce risk.

Do not nudge for tiny one-off tasks where the better mode would add overhead.

## Nudge Shape

Use one or two sentences before starting work:

> Quick Codex level-up note: this looks like a [mode] candidate because [reason]. I can proceed in this thread, or structure it as [specific better setup].

Then continue with the work unless Arielle explicitly redirects.

## Coordinator Question Gate

When Arielle asks whether Codex has questions before starting a task, first assess whether the work is high-stakes, analysis-heavy, precision-sensitive, cross-tool, approval-gated, or likely to benefit from independent checking.

- For qualifying work, ask: "Before I start: want to run this as a coordinator project? I can create the acceptance table, delegate the research/build work, and have an independent verifier check the final result before it comes back to you."
- If Arielle says yes, the coordinator must create an acceptance table before substantive work. The table must name the required facts, filters, calculations, source of truth, and pass conditions.
- The coordinator must give the completed table, original source links or artifacts, and the finished deliverable to an independent verifier. The verifier must check the sources directly, not merely agree with the builder's summary, and return pass/fail plus discrepancies.
- Do not hand back analysis, make external writes, or send communications until required verifier issues are resolved. Escalate only genuine ambiguity, a failed check that needs Arielle's judgment, or an approval gate.
- For simple or low-risk tasks, say that the task is fine as a single-thread task instead of proposing the coordinator setup.

## Operating Modes To Recommend

- **Compound Engineering planning**: for fuzzy, strategic, technical, or multi-step work that needs better shape before execution.
- **LFG for planning**: for broad project exploration, risk mapping, dependency discovery, and execution planning. Use it as a planning accelerator, not unchecked autonomy.
- **/goal for execution**: once the plan is approved and the work needs persistent context, constraints, and approval gates.
- **Coordinator plus specialists**: for complex work that benefits from divided cognitive labor, such as research, builder/operator, verifier, skeptic, and comms roles.
- **Verifier or skeptic pass**: for finance, access, security, legal-adjacent, healthcare, data migration, deletion, external messaging, or any result that must be trustworthy.
- **Skill**: when the main reusable value is judgment, method, voice, preferences, or procedure for future similar tasks.
- **Automation**: when the main reusable value is scheduled monitoring, reminders, digests, exception checks, or background follow-up.
- **Checklist or SOP**: when the workflow is repeatable but does not need active automation.

## Decision Rules

- Optimize for reducing Arielle's coordination load.
- Be specific about the tradeoff: speed, reliability, approval safety, future reuse, or better source coverage.
- Do not turn every task into process. The right nudge can still be: "This is fine as a single-thread task."
- If Arielle accepts a better mode, help convert the task into that structure immediately.
- If Arielle ignores the nudge, proceed normally without repeatedly asking.

## Good Examples

For a Slack/security/admin policy task:

> Quick Codex level-up note: this is a coordinator + specialist candidate because it mixes official docs, admin-console evidence, people/access policy, and comms. I can split it into research, operator, verifier, skeptic, and comms passes before recommending a decision.

For a recurring management workflow:

> Quick Codex level-up note: this looks automation-shaped because the value is recurring context scanning and exception reporting. I can do today's pass now, then propose the smallest useful heartbeat.

For a broad implementation request:

> Quick Codex level-up note: this is a good LFG-for-planning candidate. I can use it to map scope, dependencies, and risks, then switch to `/goal` for approved execution.

For a simple task:

> This is fine as a single-thread task; no heavier Codex structure needed.
