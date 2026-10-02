# Source acquisition

The report measures the person's own usage. Organization dashboards and APIs may contain other people's data: select the requested user, workspace, project or API key before importing. Never treat an organization total as one person's usage.

## Local sources

- **Codex:** `CODEX_HOME`, otherwise `~/.codex`; `state_*.sqlite` provides source metadata, and `sessions/` and `archived_sessions/` contain token records. Source schemas are discovered rather than pinned to a database version. No external `sqlite3` executable is required.
- **Claude Code:** `CLAUDE_CONFIG_DIR`, otherwise `~/.claude`; recursively scan `projects/**/*.jsonl`. Include sidechains and SDK/CLI sessions. Deduplicate streaming assistant copies by request/message identity. Do not use `stats-cache.json` for a current window.
- **ChatGPT local catalog:** when Codex Desktop has a readable `sqlite/codex-dev.db`, it may index a partial set of ChatGPT conversation timestamps. This supports new conversations and conversations whose last known update is in the window, not full message activity or tokens. Exports replace this fallback.
- **Cursor local tracking:** `~/.cursor/ai-tracking/ai-code-tracking.db` contains code activity, not a complete usage ledger. Timestamped code-tracking events are a separate metric. A usage export replaces this fallback.

Histories from another device can be collected by passing `--home`, tool-specific roots, or copying the relevant history directories into a read-only source directory. Do not copy credentials. Windows users can run `python` instead of `python3`; use UTC if the Python installation lacks IANA timezone data, or install `tzdata` when a named timezone is required.

## ChatGPT export

Use the official account export via **Settings → Data controls → Export data**, or the Privacy Portal. Some organization-managed workspaces require owner-managed data access rather than personal self-service export. Account ownership and any email download step remain with the user. Read the existing export directly; don't request a new one if one already covers the period.

Accept a ZIP, export directory, `conversations.json`, or split `conversations-*.json` files. The collector reads retained message nodes, including regenerated branches, deduplicates message IDs, and counts user/assistant messages, active retained conversations and message-level model IDs when present. It never outputs message content. Deleted or unexported conversations remain outside coverage. Missing message timestamps are not replaced by conversation update timestamps. Tokens and cost remain unknown unless supplied in a separate authoritative usage record.

Official source: [Exporting ChatGPT data](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data).

## Claude chat export

Use **Settings → Privacy → Export data** on Claude web or desktop. Team/Enterprise exports may require the organization's Primary Owner. The collector accepts a ZIP, directory or JSON containing conversations with `chat_messages`, and counts timestamped retained user/assistant messages. Do not equate this with Claude Code history or API organization usage.

Official source: [Export your Claude data](https://support.claude.com/en/articles/9450526-export-your-claude-data).

## Cursor usage CSV

Use the person's Cursor usage dashboard export. Team analytics charts also provide CSV downloads, but chart statistics such as lines accepted are not model-request or token records. The built-in importer supports timestamped per-event usage CSVs with recognized token or cost columns. It rejects an analytics-only or unknown schema with a coverage explanation instead of guessing.

Recognized columns include Date/Timestamp, Model, Input Tokens, Cache Read Tokens / Cached Input Tokens, Cache Write Tokens / Cache Creation Tokens, Output Tokens, Total Tokens, Request ID, and numeric Cost / Cost (USD). Explicit `Input Tokens (w/ Cache Write)` / `Input Tokens (w/o Cache Write)` columns describe uncached input and writes; cache reads are added separately. Generic `Input Tokens` can be ambiguous: specify `--cursor-input-mode inclusive` or `uncached` after checking the export's definitions. Omit token components when their meaning cannot be verified. “Included” and “free” cost labels are not numeric model usage cost and remain unknown.

A CSV Cost value is labeled **dashboard usage value**, not automatically an actual paid invoice amount. Invoice and subscription totals are separate. Never import all team members as the person's usage; filter the export first.

Official source: [Cursor usage analytics and CSV downloads](https://cursor.com/docs/account/teams/analytics). Export headers can change; inspect them before choosing a mapping.

## Provider APIs and other AI tools

This package does not obtain credentials or call provider APIs automatically. Use an already-authorized connector or documented API when it gives better coverage than exports, then normalize metadata using [records.md](records.md). Keep tokens in environment or connector credentials; never include secrets in logs, report data or command-line arguments.

- [OpenAI Usage API](https://platform.openai.com/docs/api-reference/usage): API workload usage is separate from ChatGPT subscription usage. Organization/project/key scope matters.
- [Claude Usage and Cost API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api): requires appropriate organization credentials; API, Claude Code analytics and Claude Enterprise analytics are distinct sources. Cost amounts may be expressed in cents: convert explicitly. Label estimated costs as estimates.
- Gemini, Copilot, Perplexity, Grok and other tools: look for official personal exports, dashboards or organization analytics. Use the authenticated browser only when available and appropriate; if sign-in or a user-controlled export is required, finish the available report and state precisely what is missing.

For aggregate API time buckets, use `period_start` and `period_end`. Buckets crossing the reporting boundary cannot be assigned precisely and are excluded with a coverage note; request smaller buckets or aligned bounds. Multi-day buckets appear as unallocated in the daily table. Never prorate tokens by elapsed time.
