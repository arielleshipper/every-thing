---
name: personal-usage-resets
description: Check your own Codex usage, learn your pace and active hours, and recommend when to use or save expiring limit resets. Use for personal usage checks, reset advice, or a daily usage monitor.
---

# Personal Usage Resets

Check only the signed-in user's account. Use the bundled Python script for collection, learning, forecasts, and notification eligibility. Never read prompts into model context or redeem resets. The package contains no personal state; the script stores private state outside it.

## Check or setup

1. Call the Codex desktop `get_usage_limits` tool fresh. Preserve the entire returned JSON, including `accountId` and `rateLimitResetCredits`. Purchased `credits` are not resets. If the tool is unavailable, say this installation lacks the live Codex adapter; don't invent an endpoint.
2. Pipe that JSON into `python3 <this-skill>/scripts/monitor.py check --timezone <user-IANA-timezone>`. Resolve the script relative to this SKILL.md. Use the user's known timezone; ask if it isn't known. Use a safely quoted heredoc or stdin, never shell interpolation of arbitrary tool text. Do not print the raw response or account IDs. State defaults to `${CODEX_HOME:-~/.codex}/usage-reset-state`; source history is `${CODEX_HOME:-~/.codex}/sessions`. Read `references/operations.md` when changing these locations or scheduling.
3. Report the compact result: remaining allowance, natural renewal, reset count/expiry, learned usual active periods, forecast confidence, and use/save/wait/learning/needs-information reason. A quiet outcome is useful in an explicitly requested check; scheduled checks stay quiet unless `notify` is true or `health_change` identifies a new/recovered failure.

The first check imports up to 28 days of matching-account and matching-user metadata. It binds the local thread's creator identity because an account ID can represent a shared workspace. If creator identity cannot be established, it suppresses history-based personalization. Later checks read appended records only. Each line is inspected locally; only aggregate metadata is retained. No model calls occur in the script. Timestamped user-message events define observed active hours; allowance snapshots define percentage-point pace. Unknown-account sessions and missing periods cannot supply personalization.

Cold start is a working mode, not a fabricated forecast. Seven active days and three valid same-cycle intervals are needed for learned advice. A user's explicit "I'm working now" can be passed with `--working-now` to evaluate measured proximity while learning, but must be labeled as user intent rather than learned demand.

## Controls

- Explain: run another fresh check; show facts versus prediction and the partial-local-history caveat.
- Snooze: `monitor.py snooze --hours N` with the same state directory; user-requested only.
- Clear learned data: `monitor.py clear-profile`; deletes this skill's profile/cursors and preserves source histories and current snapshot.
- Correct timezone: supply the corrected IANA zone at check time; learned local-hour bins are rebuilt from retained timestamps.
- Manual redemption: open the provider UI if requested, then refresh. Do not decrement counts based on "I used a reset" alone.

## Daily schedule

Use the Codex automation tool only when the user asks for daily monitoring or authorizes setup of the monitor. Run once per day near their learned first usual active hour; if history is insufficient, ask for a daily check time. Prefer Luna when the scheduler supports model selection. Don't claim the serving model was changed unless the saved schedule confirms it. Do not change the user's global model.

The prompt must call the live tool, run this script with `--scheduled`, and notify only when its result requests it. The script enforces one scheduled check per local calendar day, deduplication, and snooze; calendar days avoid skipping a check when the scheduler starts a few seconds early or daylight saving changes. No separate polling loops, cron jobs, API-key models, or session watchers are needed. A local schedule needs the app and computer available; daily checks may miss sudden intraday spikes. See `references/operations.md` for the exact schedule contract and tests.

## Boundaries

The initial live adapter supports Codex `codexRateLimits` full-reset credits and general Codex windows. Unsupported reset types cannot justify advice. Account identity and reset metadata must be present. Store only metadata under the current account's hashed namespace. Never publish state, send it to another user, use workspace usage as a team leaderboard, or include it in the shareable skill folder. The compact check summary goes only to the user's current harness/model provider.
