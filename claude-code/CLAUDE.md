# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A self-contained **Claude Code plugin** called `gauntlet-loop`. It is not an application with a
build/test pipeline — it is plugin config (agents as markdown, a skill-driven orchestration
prompt, and one dependency-free Python MCP server). There is no package manifest, no test suite,
and no linter configured in this repo.

## Running / testing the plugin locally

There is no automated test suite. "Testing" this repo means launching Claude Code with the plugin
loaded and exercising the `/gauntlet-loop:gauntlet` skill end-to-end.

```bash
# from the directory containing this plugin
claude --plugin-dir .

# then inside Claude Code
/gauntlet-loop:gauntlet <task description> [--max-iterations N] [--min-score 0.90] [--providers auto|native|multi]
/gauntlet-loop:gauntlet-providers   # show which external providers are configured
```

Install for repeated use (copies the plugin to `~/.claude/plugins/local/gauntlet-loop` and creates
a `claude-gauntlet` launcher on PATH):

```bash
./install.sh
./uninstall.sh
```

Sanity-check the MCP server directly (it speaks line-delimited JSON-RPC over stdio, e.g. via a
manual `tools/list` / `tools/call` request):

```bash
python3 servers/gauntlet_mcp.py
```

No build step, no lint config, no CI in this repo — the only "correctness" check is running the
gauntlet skill against a real task and confirming the phases execute as described below.

## Architecture

The plugin implements an **adversarial multi-agent review loop** ("the Gauntlet"), driven entirely
by a skill prompt (`skills/gauntlet/SKILL.md`) that acts as orchestrator, delegating to native
Claude Code subagents defined in `agents/*.md`, with optional fan-out to external LLM providers
through the bundled `gauntlet-router` MCP server.

### Orchestration flow (see `references/architecture.md` and `skills/gauntlet/SKILL.md`)

```
Analyst -> Planner -> Builder -> {Critic, Red Team, Verifier} (parallel, independent)
        -> Reconcile -> Reviser -> Re-verify -> Judge -> PASS | REVISE (loop) | FAIL
```

- **Analyst** and **Planner** are read-only; they must not edit the repo (Phase 0).
- **Builder** is the only agent that produces the initial candidate; it may edit the workspace
  (Phase 1). It must never declare the Gauntlet passed itself.
- **Critic**, **Red Team**, and **Verifier** run independently and in parallel (Phase 2) and must
  not see each other's first report before completing — this independence is the point of the
  design. Critic and Verifier are read-only (`Read, Grep, Glob` [+ `Bash` for Verifier]);
  Red Team gets `Bash` but `Write`/`Edit`/`NotebookEdit` are explicitly disallowed for both
  Red Team and Verifier (see their frontmatter `disallowedTools`).
- Findings are reconciled into a single issue ledger (consensus / disputed / false positives /
  blocking) — disputes are resolved by deterministic reproduction or a fresh independent reviewer,
  **never by majority vote** (Phase 3).
- **Reviser** (may edit) fixes evidenced issues; critical/high correctness or safety issues cannot
  be silently deferred (Phase 4).
- **Verifier** re-runs after every revision — a fix is never assumed to work just because code
  changed (Phase 5).
- **Judge** is independent, read-only, and scores against a fixed rubric
  (correctness 0.25, completeness 0.15, robustness 0.15, security 0.10, maintainability 0.10,
  clarity 0.10, requirement_satisfaction 0.15), returning exactly `PASS` / `REVISE` / `FAIL`
  (Phase 6). If native and external judges disagree, deterministic evidence wins.
- On `REVISE`, the loop repeats (default max 4 rounds); on stagnation (same blocker survives two
  rounds, judge score improves < 0.02 across two rounds, or revisions are cosmetic), escalate to
  **Architect**, which returns exactly one of `KEEP_ARCHITECTURE` / `MODIFY_ARCHITECTURE` /
  `REPLACE_ARCHITECTURE` (Phase 7 / Stagnation).
- **Evidence precedence** (used throughout, especially by Verifier/Judge): executable
  reproduction > tests > build/compiler/type-checker/static analysis > protocol/schema validation
  > authoritative documentation > independent recomputation > model judgment. Another model
  agreeing is explicitly *not* evidence.
- **Write coordination**: never run two agents that can edit the same worktree concurrently.
  Builder and Reviser run serially; Critic/Red Team/Verifier/external reviewer calls are the safe
  parallelism.

### Multi-provider fan-out (`servers/gauntlet_mcp.py`)

A dependency-free, stdlib-only MCP server (`gauntlet-router`, registered in `.mcp.json`) exposes
two tools over stdio JSON-RPC:

- `provider_status` — reports which of OpenAI / Gemini / Anthropic API / Ollama are configured
  (via env vars) and their default models, **never** returning key values.
- `ask_provider` — sends a role-scoped prompt (`critic` / `red-team` / `judge` / `tie-breaker` /
  `reviewer`, each with its own system prompt baked into `ROLE_SYSTEM`) to one external provider
  and returns only the output text.

`providers=auto` (the skill's default) queries `provider_status` first and only uses configured
external providers to add independence; it falls back cleanly to native-only when nothing is
configured. `providers=native` forces Claude-only; `providers=multi` requires at least one
external provider. External calls must receive only the minimum necessary context (task,
acceptance criteria, diff/excerpts, role contract) — never API keys, `.env` contents, credentials,
or unrelated proprietary files. External output is treated as review evidence, never as proof.

### Optional state ledger (`scripts/gauntlet_state.py`)

Standalone stdlib script for tracking long Gauntlet runs as `.gauntlet/state.json`
(`init` / `show` / `round` subcommands). Not wired into the skill automatically — it's an optional
aid for persisting iteration history/verdicts across a long-running loop.

### Plugin wiring

- `.claude-plugin/plugin.json` — plugin manifest (name, description, version).
- `.mcp.json` — registers the `gauntlet-router` server, launched as
  `python3 ${CLAUDE_PLUGIN_ROOT}/servers/gauntlet_mcp.py`.
- Skills are namespaced by Claude Code, so the commands are `/gauntlet-loop:gauntlet` and
  `/gauntlet-loop:gauntlet-providers`, not the bare names.
- Agents are referenced by scoped name (`gauntlet-loop:analyst`, etc.); if a scoped agent can't be
  found, the orchestrator creates an equivalent ad hoc subagent with the same role contract.
- `marketplace.example.json` is a template for publishing this plugin via a Claude Code plugin
  marketplace (replace `YOUR_ORG/YOUR_REPO`).

## Security model

The plugin never auto-uploads the repository to external providers. `--providers native` keeps
everything on-device. When external providers are used, only minimized excerpts/diffs are sent,
and secrets/`.env` content are explicitly excluded by the skill instructions.
