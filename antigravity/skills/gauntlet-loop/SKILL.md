---
name: gauntlet-loop
description: Runs an adversarial multi-agent engineering Gauntlet Loop. Use when the user asks to run the gauntlet, gauntlet loop, adversarial multi-agent review, implementation with independent critic/red-team/verifier, or high-confidence iterative verification. Supports native Antigravity subagents and optional OpenAI, Anthropic, Gemini, or Ollama reviewers.
---

# Multi-Provider Gauntlet Loop

Become the **Gauntlet Orchestrator**. Produce a solution that survives independent criticism, adversarial testing, deterministic verification, revision, and judging instead of relying on self-review.

## Defaults

Unless overridden: `max_iterations=4`, `minimum_judge_score=0.90`, `providers=auto`, and require tests for code changes.

Provider modes:
- `native`: Antigravity/Gemini subagents only.
- `auto`: use configured external providers when useful and permitted; otherwise native.
- `multi`: require at least one non-native provider for an independent review or judge; if unavailable, continue native work but report that cross-provider verification was unavailable.

Use MCP tools `provider_status` and `ask_provider` from `gauntlet-router`.

## Evidence precedence

For mechanically testable claims:

`execution/reproduction > tests > build/compiler/type-check/static analysis > schema/protocol validation > authoritative docs > recomputation > model judgment`

Model agreement is not proof.

## Phase 0 — Contract

Invoke `gauntlet-analyst` with the task and repository scope. Require objective, deliverables, constraints, assumptions, risks, and measurable acceptance criteria with verification methods.

Then invoke `gauntlet-planner` with task + acceptance criteria. Require approach, steps, dependencies, alternatives, expected failure modes, and deterministic verification plan. No edits in this phase.

## Phase 1 — Candidate

Invoke `gauntlet-builder` serially with task, acceptance criteria, plan, and repository context. Builder may edit. Require changed files, implementation summary, actual check results, and known weaknesses. Builder cannot declare PASS.

## Phase 2 — Independent parallel fan-out

After the candidate exists, invoke these concurrently with clean contexts:
1. `gauntlet-critic`
2. `gauntlet-red-team`
3. `gauntlet-verifier`

They receive task, acceptance criteria, and candidate/workspace but **not one another's initial reports**.

Critic issues contain: ID, severity (`critical|high|medium|low`), location, description, evidence, proposed fix.

Red-team attacks contain: ID, scenario, expected/observed failure, severity, reproducible boolean, evidence, mitigation.

Verifier checks contain: ID, claim, status (`VERIFIED|FAILED|UNCERTAIN`), method, evidence. It should run non-destructive tests/build/type checks when permitted.

## Optional external-provider fan-out

For `auto` or `multi`, call `provider_status`, then use `ask_provider` for independent `critic`, `red-team`, `judge`, `tie-breaker`, or `reviewer` roles.

A good heterogeneous routing when available is:
- Native Antigravity/Gemini: Builder + Verifier
- OpenAI: Critic
- Anthropic: Red Team
- OpenAI or Anthropic: Judge, preferably different from the critic provider
- Ollama: local/private extra reviewer or tie-breaker

This is a preference, not a fixed vendor hierarchy.

Send external providers only the minimum task/acceptance criteria/diff excerpts needed. Never send credentials, `.env`, secrets, unrelated proprietary files, or private scratch work. If repository policy prohibits source sharing, use native mode.

## Phase 3 — Reconcile

Wait for all initial reports. Create an issue ledger with consensus issues, disputed issues, false positives, and blockers. Do not decide by majority vote. Resolve material disputes by deterministic reproduction first; otherwise use a fresh focused tie-breaker; if unresolved, mark `UNCERTAIN`.

## Phase 4 — Revise

If warranted, invoke `gauntlet-reviser` serially with task, acceptance criteria, implementation, issue ledger, verification evidence, and previous judge feedback. Require a change manifest mapping every issue ID to `fixed|mitigated|rejected|deferred` with explanation. Blocking issues cannot be silently deferred; rejected findings require evidence.

## Phase 5 — Re-verify

After every revision invoke `gauntlet-verifier` again. Re-check prior failures, changed areas, regressions, and mandatory acceptance criteria. Never infer a fix worked merely because code changed.

## Phase 6 — Judge

Invoke `gauntlet-judge`. In multi-provider mode, also use an external judge when configured. Judge must not edit.

Weights: correctness .25, completeness .15, robustness .15, security .10, maintainability .10, clarity .10, requirement satisfaction .15.

Verdict exactly `PASS`, `REVISE`, or `FAIL`.

PASS requires score >= threshold, no unresolved critical issue, no unresolved high correctness/safety issue, mandatory criteria satisfied, and required deterministic verification succeeding.

If judges disagree, deterministic evidence wins; otherwise run a focused tie-breaker.

## Phase 7 — Loop

On PASS stop. On REVISE increment iteration, revise, re-verify, re-judge. On FAIL stop only for an immutable impossible/unsafe constraint; otherwise escalate architecture. At iteration limit return `BEST_EFFORT` with remaining blockers and best verified state.

## Stagnation

Invoke `gauntlet-architect` if the same blocker survives two rounds, score improves <0.02 across two rounds, or revisions are cosmetic. Architect returns exactly one: `KEEP_ARCHITECTURE`, `MODIFY_ARCHITECTURE`, or `REPLACE_ARCHITECTURE`.

## Parallelism

Parallelize read-heavy Critic, Red Team, Verifier, and external reviews. Never run Builder and Reviser concurrently. If adversarial testing needs experimental edits, use an isolated branch worktree and do not merge it automatically.

## Final response

Report:

`GAUNTLET: PASS | BEST_EFFORT | FAIL`
`Iterations: N`
`Judge score: X.XX`

Then concise Changed, Verified, Issues found/fixed, and Remaining non-blocking risks. Do not dump raw subagent transcripts unless asked.
