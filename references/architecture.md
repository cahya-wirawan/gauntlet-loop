# Gauntlet architecture

```text
                         Claude Code
                    Gauntlet Orchestrator
                              |
             +----------------+----------------+
             |                                 |
      Native Claude agents            Multi-provider MCP
             |                                 |
   Analyst -> Planner -> Builder      OpenAI / Gemini / Anthropic API / Ollama
                    |
          +---------+----------+
          |         |          |
        Critic   Red Team   Verifier
          +---------+----------+
                    |
                 Reviser
                    |
                Re-verify
                    |
                  Judge
                    |
             PASS / REVISE / FAIL
```

## Why the split matters

Native subagents can inspect the working repository with isolated contexts. External models are
used only as independent reviewers/judges and receive a deliberately minimized prompt.

Deterministic tools remain the source of truth whenever the claim is mechanically testable.
