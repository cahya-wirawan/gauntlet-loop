## Gauntlet Loop

When the user explicitly invokes `$gauntlet-loop`, asks to "run the gauntlet", or requests
adversarial multi-agent verification, follow the installed `gauntlet-loop` skill.

For Gauntlet runs:

- Treat acceptance criteria as the contract.
- Delegate independent review to subagents.
- Run Critic, Red Team, and Verifier independently and in parallel.
- Do not let these reviewers see one another's initial findings before they finish.
- Prefer deterministic evidence (tests, compilation, static analysis, official documentation)
  over model consensus.
- Only Builder/Reviser roles may edit files unless the user explicitly requests otherwise.
- Never allow a judge to repair the candidate it is judging.
- A PASS requires no unresolved blocking issue and successful required verification.
