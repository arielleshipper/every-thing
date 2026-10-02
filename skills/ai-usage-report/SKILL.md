---
name: ai-usage-report
description: Measure a person's AI usage across apps and providers. Use for weekly or custom-period usage reports, token/model/day breakdowns, spending audits, and reports combining Codex, Claude Code, ChatGPT, Claude, Cursor or other AI tools.
---

# AI Usage Report

Produce a source-grounded report for the current person, using local histories, account exports, usage dashboards or provider APIs. The bundled collector runs locally with Python 3.10+ and the standard library. It never sends data anywhere.

## Collect

Infer the reporting window and timezone from the request and session. Default to the last seven days, freeze an exclusive cutoff, and label the timezone. For “this week,” start on Monday. Resolve an ambiguous calendar-week boundary when it would materially change the answer.

Run the collector using absolute paths to this skill and the output directory:

```bash
python3 /path/to/ai-usage-report/scripts/usage_report.py --days 7 --timezone America/New_York --output /path/to/report
```

Use `--start` and `--end` for a frozen window; `--exclude-session` for the current reporting session when its ID is available. `--home` and `--codex-root` / `--claude-root` support moved histories and test environments. The person’s own home and tool-specific environment variables are the defaults. Do not substitute another user's account.

Automatic collection covers local Codex and Claude Code token histories. A partial ChatGPT conversation catalog and Cursor code-tracking history provide supplemental activity only. Check every coverage row before describing a tool as measured. An absent, stale, unreadable or unsupported source is unknown coverage, never proof of zero usage.

Ask which additional tools they use only when the request or discovered sources leave that unclear; continue collecting available data while waiting. For tools requiring an export or account connection, read [sources.md](references/sources.md). Import supplied exports directly:

```bash
python3 /path/to/ai-usage-report/scripts/usage_report.py --days 7 --output /path/to/report \
  --import chatgpt=/path/to/chatgpt-export.zip \
  --import claude=/path/to/claude-export.zip \
  --import cursor=/path/to/cursor-usage.csv
```

For another AI tool, use its official usage export, supported connector, authenticated dashboard or documented API. Inspect the actual schema and map it into [records.md](references/records.md), then add `--import generic=/path/to/normalized.jsonl`. The app label is arbitrary: Gemini, Copilot, Perplexity, Grok, API workloads and future tools can share this format. Do not claim a built-in collector exists for a tool that only has this import path.

## Interpret

- Distinguish processed tokens, model requests, user messages, assistant messages, conversations, code-tracking events and cost. Do not add different units together or convert conversation counts into token totals.
- Preserve missing fields as unknown. Show measured subtotals and their coverage. A chat export can establish retained messages and conversations without establishing tokens or spend.
- Prefer canonical per-response records; deduplicate repeated records and alternate copies. Never sum lifetime database counters or stale usage caches. The Codex collector handles counter resets and shortened approval histories; recovery without response identities makes request counts minimums.
- Treat cache reads and writes as input subsets, and reasoning as an output subset. Do not add them twice. Costs need an explicit currency and basis: billed, dashboard usage value, or estimate. Subscription price is separate from usage cost.
- Avoid overlapping sources for the same workload. The collector replaces its ChatGPT catalog or Cursor tracking fallback when the corresponding export is supplied. For generic imports overlapping local or account records, select one source using `--skip-local` or `--skip-app`. Resolve overlap before presenting a grand total.
- Model IDs come from usage records. Unknown attribution stays unknown; do not invent model aliases or infer preferences, quality, hours worked or time saved from token volume.

## Deliver

The collector writes `report.json`, `report.md`, `report.html` and `daily.csv`. Read its validation and coverage results, then summarize the period, measured totals, major breakdowns and material gaps. Link the full local report. Keep source paths, session IDs, prompts, conversation titles, attachments and credentials out of shared reports.

Publishing or external sharing is a separate requested action. A normal usage-report request stays local. When the user requests a site or Slack delivery, build the concrete report first, use the available hosting or messaging workflow, preserve the requested audience, and verify publication and delivery. This skill does not grant permission to share future reports.
