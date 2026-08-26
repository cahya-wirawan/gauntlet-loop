# Gauntlet Safety and Evidence Rules

When the `gauntlet-loop` skill is active:

1. Deterministic evidence outranks model consensus.
2. Never send API keys, credentials, `.env` contents, private tokens, or unrelated source files to an external provider.
3. External providers receive only the minimum task context/diff needed for their assigned role.
4. Analyst, Planner, Critic, Red Team, Verifier, Judge, and Architect must not modify product code.
5. Builder and Reviser are the only Gauntlet roles intended to edit the implementation.
6. Do not run two write-capable Gauntlet agents concurrently against the same workspace.
7. A PASS requires required tests/checks to succeed when mechanically testable.
8. Never expose private chain-of-thought as part of Gauntlet reports.
