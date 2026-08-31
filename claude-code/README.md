# Multi-Provider Gauntlet Loop for Claude Code

A self-contained Claude Code plugin implementing an adversarial engineering loop with:

- native Claude Code subagents;
- independent Critic, Red Team, and Verifier roles;
- iterative Reviser + re-verification;
- explicit PASS / REVISE / FAIL judging;
- stagnation-driven architecture escalation;
- optional cross-provider reviews via OpenAI, Gemini, Anthropic API, and Ollama;
- no Python dependencies beyond the standard library for the provider router.

## Requirements

- Claude Code with plugin, Skills, and custom-subagent support.
- Python 3.10+ for the bundled multi-provider MCP router.
- External provider API keys only for providers you want to use.

## Quick test — no installation

From the directory containing this plugin:

```bash
claude --plugin-dir ./claude-code-multi-provider-gauntlet
```

Then invoke:

```text
/gauntlet-loop:gauntlet Implement JWT authentication for this FastAPI project.
```

Or inspect configured external providers:

```text
/gauntlet-loop:gauntlet-providers
```

## Install for repeated use

The most portable distribution path for Claude Code plugins is a marketplace. This ZIP also
includes a local installer that copies the plugin to a stable user directory so you can launch
it with a short wrapper command.

```bash
./install.sh
```

It installs to:

```text
~/.claude/plugins/local/gauntlet-loop
```

and creates:

```text
~/.local/bin/claude-gauntlet
```

Run:

```bash
claude-gauntlet
```

The wrapper launches:

```bash
claude --plugin-dir ~/.claude/plugins/local/gauntlet-loop
```

If `~/.local/bin` is not on PATH, add it or run the wrapper by full path.

## External providers

Native mode needs no extra keys.

For cross-provider execution, export any combination of:

```bash
export OPENAI_API_KEY="..."
export GEMINI_API_KEY="..."
export ANTHROPIC_API_KEY="..."

export OLLAMA_BASE_URL="http://localhost:11434"
export GAUNTLET_OLLAMA_MODEL="qwen3:32b"
```

Optional base-URL overrides for gateways/proxies:

```bash
export OPENAI_BASE_URL="https://api.openai.com/v1"
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

Optional model overrides:

```bash
export GAUNTLET_OPENAI_MODEL="gpt-5.6"
export GAUNTLET_GEMINI_MODEL="gemini-3.6-flash"
export GAUNTLET_ANTHROPIC_MODEL="claude-opus-5"
```

The provider status tool never returns key values.

## Usage

Full automatic provider selection:

```text
/gauntlet-loop:gauntlet Refactor the RAG retrieval pipeline and run the full gauntlet.
```

Native-only:

```text
/gauntlet-loop:gauntlet Fix the race condition in the queue worker --providers native
```

Require multi-provider review:

```text
/gauntlet-loop:gauntlet Review the authentication implementation --providers multi
```

Tighter loop:

```text
/gauntlet-loop:gauntlet Implement Redis Cluster support --max-iterations 3 --min-score 0.92
```

## Security model

The plugin does **not** automatically upload your repository to external providers.

The orchestration skill instructs Claude to:
- send only minimum necessary excerpts/diffs;
- never send credentials or `.env` data;
- respect project/user confidentiality rules;
- use external output as review evidence, not as proof.

If the repository must never leave the machine, invoke with `--providers native`.

## Plugin structure

```text
claude-code-multi-provider-gauntlet/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
├── agents/
│   ├── analyst.md
│   ├── planner.md
│   ├── builder.md
│   ├── critic.md
│   ├── red-team.md
│   ├── verifier.md
│   ├── reviser.md
│   ├── judge.md
│   └── architect.md
├── skills/
│   ├── gauntlet/
│   │   └── SKILL.md
│   └── gauntlet-providers/
│       └── SKILL.md
├── servers/
│   └── gauntlet_mcp.py
├── scripts/
│   └── gauntlet_state.py
├── config/
│   └── gauntlet.env.example
└── references/
    └── architecture.md
```

## Notes

Plugin skills are namespaced by Claude Code, so the command is:

```text
/gauntlet-loop:gauntlet
```

rather than plain `/gauntlet`.

For a team/public distribution, put this plugin in a Git repository and publish a Claude Code
plugin marketplace that references it.
