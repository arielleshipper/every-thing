# Operations

Requires Python 3.9+ and an installed Codex desktop adapter exposing `get_usage_limits`. No Python dependencies or API key. Other harnesses may install the folder, but live checks require an equivalent adapter; they are not claimed as tested.

The live response must contain `accountId`, `rateLimitsByLimitId` or legacy `rateLimits`, and `rateLimitResetCredits`. The script captures observed-at time immediately when invoked after the fresh tool call. Invoke without a fresh tool response only for `status`, which explicitly reports cached facts and never issues spending advice.

State is outside the package. Directory mode 0700 and files mode 0600 protect metadata from other local users. `--state-dir PATH` and `--sessions-dir PATH` support isolated testing. Do not share these directories. A profile is partitioned by account and reset when cleared; local histories are never modified. Current general Codex reset effect is recognized only for the returned `codexRateLimits` full resets; renewal/cycle changes are excluded from pace.

Scheduled prompt contract: invoke this skill by its installed path; obtain live limits; run `check --scheduled --timezone USER_ZONE`; keep commentary/output quiet for unchanged, non-actionable results. Notify for `notify=true`, newly failed observation, or recovery from a failed observation. Missing live-tool data is a health failure, not "zero use." Do not retry in a loop or send quiet daily summaries. The model-run guard in the script limits successful scheduled checks, not scheduler invocation costs: the schedule itself must run daily. Model selection belongs to the schedule; never claim a skill instruction forces Luna.

Commands: `check` accepts live JSON on stdin; `status` displays cached last result; `snooze --hours N` suppresses recommendations; `clear-profile` removes this skill's learned history. A user requested on-demand check bypasses the scheduled-run guard, but still respects snooze for push notifications.

Limitations: only sessions with matching `creator_account_id` are imported. User-message timestamps approximate initiation times, not all time spent thinking or reading. Pace comes from observed shared-account allowance changes and is affected by activity on other devices; local active hours are partial coverage. Cold-start thresholds and range estimates need pilot calibration. The script does not promise task-value judgments or predict unseen usage bursts.
