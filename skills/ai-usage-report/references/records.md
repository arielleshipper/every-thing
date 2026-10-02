# Normalized records for any AI tool

Supply a JSONL file, JSON array, or JSON object with a `records` array. Each record is metadata only. Source evidence should remain private. Use a stable event ID so repeated exports deduplicate.

```json
{"id":"request-123","timestamp":"2026-09-15T12:00:00Z","app":"Gemini API","model":"recorded-model-id","requests":1,"input_tokens":1500,"cached_input_tokens":1000,"output_tokens":100,"total_tokens":1600,"source":"personal-api-export"}
```

Fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable event/bucket ID. Required. IDs are private and omitted from report outputs. |
| `app` | Actual app or workload label. Required. |
| `timestamp` | ISO timestamp with offset, or epoch seconds/milliseconds. Required for an event. |
| `period_start`, `period_end` | Alternative for aggregate buckets; exclusive end. Both must fall wholly within the window. |
| `model` | Recorded model ID, otherwise omit. |
| `session` | Private conversation/session ID for distinct counts, otherwise omit. |
| `category`, `surface` | Optional short classifications; no titles, paths or prompt text. |
| `requests` | Observed model requests; omitted means unknown, not one request. |
| `user_messages`, `assistant_messages` | Message counts, separate from model requests. |
| `input_tokens` | Total input, including cache reads and cache writes. |
| `cached_input_tokens`, `cache_write_input_tokens` | Input subsets; do not add again. |
| `output_tokens`, `reasoning_output_tokens` | Total output and its reasoning subset. |
| `total_tokens` | Input + output, if known. Can be supplied alone when components are unavailable. |
| `cost_usd` | Numeric USD amount. Requires a cost basis; not a subscription price. |
| `cost_basis` | `billed`, `dashboard_usage`, or `estimate`. Different bases remain separate in reports. |
| `source` | Short provenance label without personal paths or secrets. |
| `requests_lower_bound` | `true` if request identities/counts are incomplete. |

Omit unavailable fields or use `null`. Do not fill missing cache fields with zero. If a provider reports uncached input separately, add reads/writes once when normalizing `input_tokens`. Reject negative or contradictory token vectors. Reasoning must not exceed output. Explicit zero cost is valid only when the source states a numeric zero with a known basis.

Import:

```bash
python3 /path/to/ai-usage-report/scripts/usage_report.py --days 7 --output /path/to/report --import generic=/path/to/normalized.jsonl
```

The importer validates a whitelist of these fields and discards everything else. It does not copy prompts, titles, emails, attachments or raw source records into reports. Do not include those fields in normalized files anyway.

Deduplication uses app + record ID. Two providers using different IDs for the same request cannot be reconciled automatically. Prefer one authoritative source for that workload, or normalize both to the same canonical app/ID. Use `--skip-local` when provider exports fully replace local histories, or `--skip-app 'Claude Code'` / `--skip-app Codex` for targeted replacement. Account-level API spend often overlaps app histories; leave it as a separate cost-only record if tokens cannot be scoped without duplication.
