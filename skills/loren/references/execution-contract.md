# Execution contract

## Run manifest

Keep a small Markdown or JSON manifest in the task workspace. Record project/environment, branch and source revision or snapshot, mode, authorized scope/publication limits, requested and actually accepted model IDs and providers, route/task/session IDs, and stage statuses (`pending`, `running`, `complete`, `blocked`, `skipped by explicit mode`). Include artifact paths, current chunk, tests, decisions, and next action. Record a running checkpoint before dispatch and inspect output before marking complete.

Model self-identification in generated prose is not proof. Use explicit route parameters, model catalog, and returned execution metadata. Resolve fallback or identity uncertainty before claiming cross-provider critique.

## Durable artifacts

Keep these logically separate, even if sections share one report:

1. Audit: architecture map, findings/evidence, impact/confidence, inspection gaps.
2. Initial plan: priorities, rationale, scope, acceptance criteria, risks, non-goals.
3. Initial chunks: stable IDs, dependencies, files/components, notes and checks.
4. Independent critique: verbatim second-provider result, model identity, receipt.
5. Reconciliation: disposition of each material criticism; revised plan/chunks.
6. Implementation log: chunk status, diff/commit references, commands and outcomes, checks not run, remaining work.

Preserve initial plan/chunks as well as revised versions. Do not overwrite critique to make it agree. Record meaningful decisions and milestones, not hidden reasoning or secrets. In review/planning modes keep reports outside the application repository unless requested.

Each chunk includes ID/title, goal, priority/source finding, dependency IDs or none, in/out scope, expected files, implementation approach, acceptance criteria, verification and observable result, compatibility/migration/rollback risk, status and completion evidence.

## Context and resumption

Discover routes afresh per host; availability in another task is not evidence of availability here. Keep critique independent. For cross-provider sharing, verify integration, authorized destination, and restrictions; use the necessary sanitized evidence only. Do not read credential stores or scrape logged-in browser sessions.

Resume from the latest verified stage and source snapshot. Recheck source changes before reusing findings. An interrupted running stage has an uncertain outcome: inspect artifacts and task/session state before repeating. Do not repeat possibly completed external actions. Invalidate dependent artifacts when source or plan changes materially; retain previous artifacts for traceability. A stage requires an inspected result, not just successful launch.
