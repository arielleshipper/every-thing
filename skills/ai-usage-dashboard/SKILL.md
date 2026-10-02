---
name: ai-usage-dashboard
description: Set up, open, inspect, diagnose, update, or uninstall the Every AI Usage Dashboard on macOS. Use when a Codex user asks about their local AI usage metrics, Chronicle context, Codex or Claude history collection, dashboard health, visible-thread pairing, model-name presentation, or dashboard lifecycle.
---

# AI Usage Dashboard

Operate the source-based local installation through its checked-in commands. Keep private state outside the checkout and preserve the dashboard's evidence semantics.

## Locate The App

Use the current workspace when its `package.json` name is `ai-usage-dashboard`. Otherwise check, in order:

1. `$AI_USAGE_DASHBOARD_REPO`
2. `~/CascadeProjects/ai-usage-dashboard`
3. `~/CascadeProjects/ai-usage-diary` for migrated developer installations

If none exists and the user asked to install it, run `gh repo clone EveryInc/ai-usage-dashboard ~/CascadeProjects/ai-usage-dashboard`. Stop with the GitHub CLI error if access fails.

Run all commands from the app repository.

## Choose The Workflow

- Set up or repair: run `bun run setup`, then `bun run doctor`, then open the owner-authorized URL in Codex's in-app browser.
- Open: prefer Codex's in-app browser. Read the local config and credentials without printing the owner key, navigate to the configured loopback URL with the key in the URL fragment, and verify the app strips the fragment after storing it. If in-app browser control is unavailable, run `bun run open`. If the service is unreachable, run `bun run doctor` and repair with `bun run setup`.
- Check status or diagnose: run `bun run doctor`. Explain failed checks first; Chronicle and Claude warnings are optional-source warnings.
- Refresh evidence: run `bun run sample`, then reopen or refresh the dashboard.
- Update: run `bun run update`, then `bun run doctor`.
- Uninstall: run `bun run uninstall`. Preserve private data.
- Purge: run `bun run purge` only when the user explicitly asks to delete private dashboard data.
- Hide internal model names for sharing: run `bun run models:safe`.
- Restore real model names: run `bun run models:real`.

## Preserve The Boundaries

- Treat supported local Codex and Claude history events as activity evidence.
- Treat Chronicle as optional foreground and use-case context, not authoritative usage telemetry.
- Report missing Chronicle context as unknown, never as zero AI use.
- Never modify Chronicle files or source histories.
- Keep remote publishing disabled unless the user explicitly asks to work on the future team projection.
- Never print owner capability keys, credentials, prompt text, or private evidence.
- Pair semantic work to one exact visible `AI Usage Dashboard` Codex thread. Do not claim hidden work ran in that thread.

## Close The Loop

After lifecycle changes, report the dashboard URL, whether the service is running, whether a visible thread is paired, and any partial-source caveat. Open the local dashboard in Codex's in-app browser when that capability is available.
