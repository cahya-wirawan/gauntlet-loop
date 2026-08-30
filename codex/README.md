# Codex Gauntlet Loop

An installable Codex skill for iterative multi-agent implementation, adversarial review,
verification, revision, and judging.

## What it does

For a task such as:

```text
$gauntlet-loop Implement JWT authentication for this FastAPI project.
```

Codex will:

1. Analyze the task and define acceptance criteria.
2. Plan the implementation.
3. Build an initial candidate.
4. Spawn independent Critic, Red Team, and Verifier subagents in parallel.
5. Reconcile findings without treating model consensus as proof.
6. Revise the implementation.
7. Re-run deterministic verification.
8. Ask an independent Judge to PASS / REVISE / FAIL.
9. Repeat until PASS or the configured iteration limit is reached.

## Installation

### Repository-scoped installation

From your repository root:

```bash
unzip codex-gauntlet-skill.zip
cp -R codex-gauntlet-skill/.agents .
cp -R codex-gauntlet-skill/.codex .
```

Optionally merge the contents of:

```text
codex-gauntlet-skill/AGENTS.gauntlet-snippet.md
```

into your repository's existing `AGENTS.md`.

### User-scoped skill

For the skill itself, you can instead install it globally:

```bash
mkdir -p ~/.agents/skills
cp -R .agents/skills/gauntlet-loop ~/.agents/skills/
```

Custom agents are repository-scoped in `.codex/agents/` in this package. You can move them
to `~/.codex/agents/` if you want them available in every project.

## Invocation

In Codex CLI or IDE, explicitly mention the skill:

```text
$gauntlet-loop Implement JWT authentication for this FastAPI backend.
```

or select it from `/skills`.

You can also write:

```text
Use the gauntlet-loop skill. Refactor the cache layer to support Redis Cluster.
```

## Modes

### Native mode

Uses Codex custom subagents only. This requires no external API keys.

### Multi-provider mode

The optional `scripts/provider_router.py` can ask:

- OpenAI
- Anthropic
- Google Gemini
- Ollama / OpenAI-compatible local endpoints

Enable providers through environment variables described in `references/multi-provider.md`.

The skill treats provider diversity as an enhancement, not a requirement. Tool-based
verification always outranks model consensus.

## Recommended repository layout

```text
.
├── AGENTS.md
├── .agents/
│   └── skills/
│       └── gauntlet-loop/
│           ├── SKILL.md
│           ├── references/
│           │   ├── orchestration.md
│           │   ├── state-schema.json
│           │   └── multi-provider.md
│           └── scripts/
│               ├── gauntlet_state.py
│               └── provider_router.py
└── .codex/
    └── agents/
        ├── gauntlet-analyst.toml
        ├── gauntlet-planner.toml
        ├── gauntlet-builder.toml
        ├── gauntlet-critic.toml
        ├── gauntlet-red-team.toml
        ├── gauntlet-verifier.toml
        ├── gauntlet-reviser.toml
        ├── gauntlet-judge.toml
        └── gauntlet-architect.toml
```

## Safety / write coordination

Critic, Red Team, Verifier, Judge, Analyst, Planner, and Architect agents are configured
read-only. Builder and Reviser may modify the workspace. The skill never intentionally
runs multiple write-heavy agents against the same working tree in parallel.

## License

MIT

## OpenAI-compatible endpoints

The optional provider router supports both APIs:

```bash
# Official OpenAI Responses API
export OPENAI_API_KEY="..."
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_API_MODE="responses"
export GAUNTLET_OPENAI_MODEL="gpt-5.6"
```

```bash
# OpenAI-compatible gateway / local server
export OPENAI_API_KEY="..."
export OPENAI_BASE_URL="http://localhost:8000/v1"
export OPENAI_API_MODE="chat_completions"
export GAUNTLET_OPENAI_MODEL="my-model"
```

Check the resolved configuration with:

```bash
python .agents/skills/gauntlet-loop/scripts/provider_router.py status
```
