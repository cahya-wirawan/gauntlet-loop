# Multi-Provider Gauntlet Loop

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An evidence-driven, multi-agent adversarial engineering framework for AI coding assistants. Available as an installable plugin for both **Google Antigravity** and **Claude Code**.

Instead of relying on single-pass generation or subjective self-review, Gauntlet Loop orchestrates specialized subagents through an adversarial cycle of implementation, multi-perspective criticism, security red-teaming, deterministic verification, iterative revision, and empirical judging.

---

## Core Principle: Evidence Precedence

The Gauntlet Loop operates on a strict evidence hierarchy:

$$\text{execution / reproduction} > \text{tests} > \text{build / compiler / types} > \text{docs} > \text{model opinion}$$

> [!IMPORTANT]
> Multiple AI models agreeing on an outcome is never treated as proof when a claim can be mechanically verified by code execution, test suites, or static type checking.

---

## Architecture & Lifecycle

```text
                        Orchestrator
                             │
               Analyst ──► Planner ──► Builder
                                          │
                     ┌────────────────────┼────────────────────┐
                     ▼                    ▼                    ▼
                   Critic              Red Team             Verifier
            (Quality/Edge Cases) (Security/Adversarial) (Tests/Compiler)
                     └────────────────────┬────────────────────┘
                                          ▼
                                       Reviser
                                          │
                                      Re-verify
                                          │
                                        Judge
                                          │
                                PASS / REVISE / FAIL
```

### Specialized Agents

| Agent | Responsibility | Primary Capability |
|---|---|---|
| **Analyst** | Defines measurable acceptance criteria, constraints, and verification methods. | Read-only |
| **Planner** | Designs architecture, implementation steps, and deterministic test plans. | Read-only |
| **Builder** | Implements the code changes and candidate solutions. | Write-capable |
| **Critic** | Inspects code quality, edge cases, maintainability, and regression risks. | Read-only |
| **Red Team** | Probes for security vulnerabilities, race conditions, and adversarial failure modes. | Read-only |
| **Verifier** | Executes tests, builds, linters, and runtime validation. | Execution / Non-destructive |
| **Reviser** | Implements fixes for verified issues mapped from the issue ledger. | Write-capable |
| **Judge** | Evaluates results against acceptance criteria and issues verdicts (`PASS`, `REVISE`, `FAIL`). | Read-only |
| **Architect** | Escalation role triggered upon stagnation to modify or replace structural approaches. | Read-only |

---

## Supported Platforms

The repository is structured into modular plugin distributions:

- [`antigravity/`](antigravity/) — Plugin for **Google Antigravity** and the **`agy` CLI**.
- [`claude-code/`](claude-code/) — Plugin for **Claude Code**.

---

## Multi-Provider Support

Gauntlet Loop includes a zero-dependency Python MCP router (`gauntlet_mcp.py`) that enables cross-provider evaluations across different AI models:

* **Google Gemini** (Gemini 3.7 / 3.6 Flash / Pro)
* **Anthropic** (Claude 3.7 / 3.5 Sonnet / Opus)
* **OpenAI** (GPT-4o, o3, GPT-5 series)
* **Ollama** (Local models such as Qwen 2.5/3, DeepSeek-R1, Llama 3)

### Heterogeneous Review Routing (Example)

```text
Builder & Deterministic Verifier  ──►  Native Antigravity (Gemini)
Independent Critic                ──►  OpenAI (GPT-4o / GPT-5)
Adversarial Red Team              ──►  Anthropic (Claude Sonnet / Opus)
Independent Judge                 ──►  OpenAI / Anthropic
Local Private Tie-Breaker         ──►  Ollama (Qwen / DeepSeek)
```

---

## Installation & Setup

### 1. Google Antigravity

#### Global Installation
```bash
cd antigravity
./install.sh
```
Installs to `~/.gemini/antigravity-cli/plugins/gauntlet-loop/`.

#### Workspace-Only Installation
```bash
cd antigravity
./install.sh --workspace /path/to/project
```
Installs to `/path/to/project/.agents/plugins/gauntlet-loop/`.

#### Invoking in Antigravity
```text
/gauntlet-loop Implement JWT authentication for this FastAPI backend.
```
```text
/gauntlet-loop Review authentication using multi-provider mode. Max 5 rounds, minimum score 0.95.
```

---

### 2. Claude Code

#### Global Installation
```bash
cd claude-code
./install.sh
```
Installs to `~/.claude/plugins/local/gauntlet-loop` and creates a `claude-gauntlet` wrapper in `~/.local/bin/`.

#### Quick Run (Without Installation)
```bash
claude --plugin-dir ./claude-code
```

#### Invoking in Claude Code
```text
/gauntlet-loop:gauntlet Implement JWT authentication for this FastAPI project.
```
```text
/gauntlet-loop:gauntlet Fix race condition in queue worker --providers native
```

---

## Configuration & Environment Variables

Native mode requires no external API keys. To enable cross-provider review, export the desired environment variables:

```bash
# Provider API Keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AIza..."

# Optional Base URL Overrides (gateways / proxies / local endpoints)
export OPENAI_BASE_URL="https://api.openai.com/v1"
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
export OLLAMA_BASE_URL="http://localhost:11434"
export GAUNTLET_OLLAMA_MODEL="qwen3:32b"

# Optional Model Overrides
export GAUNTLET_OPENAI_MODEL="gpt-5.6"
export GAUNTLET_ANTHROPIC_MODEL="claude-opus-5"
export GAUNTLET_GEMINI_MODEL="gemini-3.6-flash"
```

Check provider availability at any time:
- In Antigravity: `/gauntlet-providers`
- In Claude Code: `/gauntlet-loop:gauntlet-providers`

---

## Security & Privacy Model

* **Minimal Diffs**: When external providers are enabled, only minimal diffs and necessary task context are transmitted.
* **Redaction**: `.env` files, API keys, credentials, and unrelated proprietary files are strictly excluded from external prompts.
* **Air-Gapped / Native Mode**: For sensitive codebases that must not leave the local environment, set `--providers native` to run entirely within the native agent runtime.

---

## Repository Structure

```text
gauntlet-loop/
├── README.md                  # Root documentation
├── antigravity/               # Google Antigravity plugin
│   ├── plugin.json            # Antigravity plugin manifest
│   ├── mcp_config.json        # MCP server configuration
│   ├── agents/                # Native Antigravity subagent specifications
│   ├── skills/                # Gauntlet skills (orchestration & provider status)
│   ├── rules/                 # Safety & verification rules
│   ├── servers/               # Multi-provider MCP router (Python stdlib)
│   └── install.sh             # Antigravity plugin installer
└── claude-code/               # Claude Code plugin
    ├── .claude-plugin/        # Claude Code plugin metadata
    ├── .mcp.json              # Claude Code MCP configuration
    ├── agents/                # Claude Code custom subagents
    ├── skills/                # Claude Code skills
    ├── servers/               # Multi-provider MCP router (Python stdlib)
    └── install.sh             # Claude Code local installer
```

---

## License

This project is open-source under the [MIT License](LICENSE).
