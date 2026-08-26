# Architecture

```text
                      Antigravity Orchestrator
                               |
             +-----------------+-----------------+
             |                                   |
      Native subagents                    gauntlet-router MCP
             |                                   |
 Analyst -> Planner -> Builder       OpenAI / Anthropic / Gemini / Ollama
                     |
             +-------+--------+
             |       |        |
          Critic  Red Team  Verifier
             +-------+--------+
                     |
                  Reviser
                     |
                 Re-verify
                     |
                   Judge
                     |
             PASS / REVISE / FAIL
```

Native reviewers use clean subagent contexts. External reviewers receive only minimal task/diff context. Deterministic verification outranks model opinions.
