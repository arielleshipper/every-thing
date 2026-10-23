# Model routing

A skill does not add a provider, switch the current model, or grant execution permission. Revalidate these capabilities on every invocation; the observations below are not an availability guarantee.

## Codex as orchestrator

Use current model-capable task/agent tools with exact IDs. The Codex app's observed task controls enumerate OpenAI models; choosing two of them does not meet Loren's different-provider requirement. If the selected original model is the current model, it can perform the initial stages directly; otherwise use an explicitly selected supported task route. Resume that exact model/context for reconciliation. Never claim model switching just because a prompt names the model.

The CLI is bundled at `/Applications/Codex.app/Contents/Resources/codex-cli/bin/codex` on the inspected Mac, version `0.163.0-alpha.10.2`, although `codex` is not on the inspected shell PATH. Its `exec --help` verifies `--model`, `--sandbox read-only`, `--json`, `--output-last-message`, and `exec resume`. CLI help also exposes local-provider options for Ollama/LM Studio; no usable local runner was verified. Do not interpret those flags as authenticated support for Claude. Recheck paths and help rather than installing or modifying PATH automatically. App task tools are preferable when sufficient.

Local app-server discovery on the same date returned seven selectable IDs: `gpt-6.1-sol`, `gpt-6-astra`, `gpt-6-sol`, `gpt-6-luna`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`. These are observed catalog entries, not a fixed menu or proof of a successful future model call. `skills/list` with `forceReload: true` recognized `/Users/arielleshipper/.codex/skills/loren/SKILL.md` as enabled with user scope. This verifies local discovery without claiming a particular desktop selector was exercised.

## Claude Code bridge

Verified on Arielle’s Mac, 2026-10-21: `claude` version 2.1.299 is installed. The sandboxed `claude auth status` falsely appeared signed out (`loggedIn: false`, `authMethod: none`). A separately approved status check outside the Codex sandbox returned `loggedIn: true`, `authMethod: claude.ai`, organization Every, subscription type team. The existing login is available outside the sandbox; no new sign-in or credentials are needed. A subsequent synthetic tool-free model call succeeded through the approved route: requested alias `sonnet`, initialization and assistant response metadata both resolved to `claude-sonnet-5-5`, final result `LOREN_SMOKE_OK 4`, exit code 0, `is_error: false`. No project files were sent and no tools ran. This verifies cross-provider invocation, not the full Loren sequence or availability of every Claude model. If status differs across environments, check through an approved runner with normal login access before diagnosing a missing login. Do not read credential stores or bypass a denial. Claude Desktop login alone would not establish Claude Code access.

Once authenticated, verify current `claude --help` and exact requested model support before use. For a text-only independent critique, run in an isolated task directory with a minimal sanitized packet on stdin and disable tools, project customizations, and MCP. Installed CLI help supports these controls:

```text
claude --safe-mode --print --model EXACT_REQUESTED_MODEL \
  --tools "" --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --permission-mode dontAsk --no-session-persistence \
  --output-format stream-json --verbose
```

Use the host's safe subprocess API or properly quoted invocation. Save stdin packet, stdout events, stderr, exit status, and parsed final critique under the run workspace. This command shape was also exercised successfully in a synthetic call using the `sonnet` alias (resolved metadata: `claude-sonnet-5-5`) with an explicit synthetic system prompt. An actual requested model must still be checked; a test of one alias is not proof that another model is available. Check both process status and structured `result`/`is_error`; inspect returned initialization/model metadata against the selection before accepting the artifact. If identity, model availability, or successful result cannot be verified, block the stage. Never accept an auth error as critique. Tools are disabled, so include sufficient authorized source excerpts and provenance in the packet, and require the reviewer to acknowledge gaps. For repository-reading critique beyond a packet, use a separately verified read-only route within authorized boundaries; this example supplies no source-reading tools.

Avoid `--bare` as a casual replacement: current official Claude docs state it skips subscription OAuth and requires provider credentials. Do not add API keys to make this workflow work. Do not use bypass-permissions flags.

## Manual fallback

If an automatic route is unavailable, preserve the run and offer a handoff packet with original request, mode/scope, source revision, necessary source excerpts, audit, plan, and chunks. Wait for the selected provider's critique and record provenance limits. Manual handoff is not an automatic run. Same-provider adaptation is allowed only after explicit user agreement, labeled in the manifest and final result.

## Invocation references

- [Official skill discovery and invocation](https://learn.chatgpt.com/docs/build-skills): ChatGPT `@` selector; Codex CLI/IDE `$` or `/skills`. A literal `/loren` is unverified and not installed here.
- [Claude Code programmatic runs](https://code.claude.com/docs/en/headless): separate runner, model option, structured results, authentication and bare-mode differences.

Personal skill installation is local. No public repository, Claude Code skill, provider credentials, or persistent cross-provider integration is created by this package.
