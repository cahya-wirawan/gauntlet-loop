# Multi-Provider Gauntlet Loop for Google Antigravity

An installable Antigravity plugin implementing an evidence-driven engineering loop:

1. Analyst defines measurable acceptance criteria.
2. Planner designs the approach.
3. Builder implements the candidate.
4. Critic, Red Team, and Verifier run independently and in parallel.
5. Findings are reconciled by evidence, not majority voting.
6. Reviser fixes supported issues.
7. Verifier re-tests.
8. Judge returns PASS / REVISE / FAIL.
9. Repeat until PASS or the iteration limit.

Optional external reviewers: OpenAI, Anthropic, Gemini API, and Ollama/local models.

## Requirements

- Google Antigravity 2.0 / Antigravity CLI with plugin, skills, subagents, and MCP support.
- Python 3.10+ for the dependency-free provider router.
- External API keys only for providers you choose.

## Install globally

```bash
unzip antigravity-multi-provider-gauntlet.zip
cd antigravity-multi-provider-gauntlet
./install.sh
```

This installs into:

```text
~/.gemini/antigravity-cli/plugins/gauntlet-loop/
```

Restart Antigravity/`agy`, then inspect:

```text
/skills
/agents
/mcp
```

Antigravity CLI also supports `agy plugin install /path/to/plugin`. This package's installer additionally rewrites the local MCP script path to an absolute staged path for portability.

## Workspace-only install

```bash
./install.sh --workspace /path/to/project
```

Destination:

```text
/path/to/project/.agents/plugins/gauntlet-loop/
```

## Run

```text
/gauntlet-loop Implement JWT authentication for this FastAPI backend.
```

or:

```text
Run the gauntlet on the current authentication implementation.
```

Examples:

```text
/gauntlet-loop Refactor the RAG retrieval pipeline and verify error handling.
```

```text
/gauntlet-loop Review authentication using multi-provider mode. Max 5 rounds, minimum score 0.95.
```

Defaults are `max_iterations=4`, `minimum_judge_score=0.90`, `providers=auto`.

## External providers

Native Antigravity operation needs no additional keys. For cross-provider review, export any subset:

```bash
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
export GEMINI_API_KEY="..."
export OLLAMA_BASE_URL="http://localhost:11434"
```

Optional model overrides:

```bash
export GAUNTLET_OPENAI_MODEL="gpt-5.6"
export GAUNTLET_ANTHROPIC_MODEL="claude-opus-5"
export GAUNTLET_GEMINI_MODEL="gemini-3.6-flash"
export GAUNTLET_OLLAMA_MODEL="qwen3:32b"
```

Check status with `/gauntlet-providers`. The router never emits key values.

## Agents

- `gauntlet-analyst`
- `gauntlet-planner`
- `gauntlet-builder`
- `gauntlet-critic`
- `gauntlet-red-team`
- `gauntlet-verifier`
- `gauntlet-reviser`
- `gauntlet-judge`
- `gauntlet-architect`

Builder and Reviser are the intended write-capable roles. The independent reviewers are read-only except for sandboxed non-destructive command execution where verification requires it.

## Multi-provider routing

The bundled MCP server exposes:

```text
provider_status
ask_provider
```

`ask_provider` roles: `critic`, `red-team`, `judge`, `tie-breaker`, `reviewer`.

A typical heterogeneous run is:

```text
Antigravity/Gemini  -> Builder + deterministic Verifier
OpenAI              -> Critic
Anthropic           -> Red Team
OpenAI/Anthropic    -> independent Judge
Ollama              -> local tie-breaker
```

The routing is adaptive, not mandatory.

## Security

External calls are optional. The skill requires minimal excerpts/diffs and forbids transmitting credentials, `.env` contents, API keys, or unrelated proprietary files. For repositories that must never leave the machine, request native-only mode.

## Core principle

```text
execution / tests / compiler
            >
       model opinion
```

Multiple-model agreement is never enough for PASS when a claim can be checked mechanically.

## Uninstall

```bash
./uninstall.sh
```

or:

```bash
agy plugin uninstall gauntlet-loop
```
