---
name: gauntlet-loop
description: Run an adversarial multi-agent engineering Gauntlet Loop for implementation, refactoring, debugging, architecture, or review tasks that need independent critique, red-teaming, deterministic verification, iterative revision, and an explicit PASS/REVISE/FAIL judge. Use when the user says gauntlet, gauntlet loop, adversarial review, multi-agent verification, or explicitly invokes $gauntlet-loop. Do not use for trivial edits unless explicitly requested.
---

# Gauntlet Loop

You are the **Gauntlet Orchestrator**. Coordinate the work; do not collapse all roles into one
undifferentiated reasoning pass.

Read `references/orchestration.md` before starting a Gauntlet run.

Use custom Codex agents when available:

- `gauntlet-analyst`
- `gauntlet-planner`
- `gauntlet-builder`
- `gauntlet-critic`
- `gauntlet-red-team`
- `gauntlet-verifier`
- `gauntlet-reviser`
- `gauntlet-judge`
- `gauntlet-architect`

If a named custom agent is unavailable, spawn a normal subagent with the corresponding role
instructions from `references/orchestration.md`.

## Inputs

Derive these from the user request and repository:

- `task`
- `constraints`
- `acceptance_criteria`
- `max_iterations` (default 4)
- `minimum_judge_score` (default 0.90)
- `require_tests` (default true for code changes)
- `multi_provider` (default auto: use only if configured)

Do not ask for values that can be reasonably inferred.

## Phase 0 — Understand

Spawn `gauntlet-analyst`.

It must return concise structured output containing:

- objective
- deliverables
- constraints
- assumptions
- risks
- acceptance criteria

Then spawn `gauntlet-planner` with the task plus acceptance criteria.

The planner must identify:

- implementation approach
- dependencies
- alternatives considered
- expected failure modes
- verification plan

Do not edit the repository in this phase.

## Phase 1 — Build

Spawn `gauntlet-builder`.

Give it only:

- task
- acceptance criteria
- plan
- relevant repository context

The builder may inspect and edit the workspace.

Require it to:

1. implement the candidate,
2. run cheap local checks where practical,
3. report changed files,
4. report known weaknesses,
5. avoid claiming success without evidence.

## Phase 2 — Independent parallel gauntlet

After the candidate exists, spawn all three agents **in parallel**:

1. `gauntlet-critic`
2. `gauntlet-red-team`
3. `gauntlet-verifier`

Wait for all three before continuing.

Important isolation rule:

- Give each reviewer the task, acceptance criteria, and current candidate/worktree.
- Do **not** give any reviewer another reviewer's initial report.
- Reviewers must not edit the implementation.
- Prefer read-only agent configurations.

### Critic

Look for:

- correctness defects
- missed requirements
- poor architecture
- maintainability problems
- performance issues
- unsupported assumptions
- edge cases
- unnecessary complexity

Every issue must have:

- ID
- severity: critical/high/medium/low
- location
- evidence
- proposed fix

### Red Team

Try to make the candidate fail.

Consider when relevant:

- malformed input
- boundary cases
- concurrency
- partial failures
- timeouts
- rate limits
- dependency failure
- auth/authz bypass
- injection
- secret leakage
- SSRF/XSS/path traversal
- race conditions
- resource exhaustion
- operational rollback/recovery

Every attack must state whether it is reproducible and what evidence supports it.

### Verifier

Verification is evidence-first.

Use this precedence:

1. execution
2. tests
3. compilation/type checking/static analysis
4. schema/protocol validation
5. authoritative documentation
6. independent recomputation
7. model judgment

Label important claims:

- VERIFIED
- FAILED
- UNCERTAIN

Do not mark a claim verified merely because the builder says it is true.

## Phase 3 — Reconcile

The main orchestrator compares the three reports.

Produce a compact issue ledger:

- consensus issues
- disputed issues
- newly discovered issues
- false positives / rejected findings
- blocking issues

Do not use majority voting as proof.

When reviewers disagree on a material factual claim, prefer deterministic evidence. If evidence
is insufficient, spawn an additional read-only agent to evaluate only the disputed claim.

## Phase 4 — Revise

If blocking or worthwhile non-blocking issues exist, spawn `gauntlet-reviser`.

Give it:

- task
- acceptance criteria
- current candidate
- issue ledger
- verifier evidence
- previous judge feedback, if any

Require a change manifest:

- issue ID
- action: fixed / mitigated / rejected / deferred
- explanation

Rules:

- Critical/high issues may not be silently deferred.
- Rejected criticism must include evidence.
- Preserve working behavior.
- Avoid unrelated refactors.

## Phase 5 — Re-verify

After every revision, spawn `gauntlet-verifier` again.

Require regression checks for:

- previous failures
- modified areas
- acceptance criteria
- tests/build/type checks required by the repository

Never infer that a fix worked merely because code changed.

## Phase 6 — Judge

Spawn `gauntlet-judge`.

The judge receives:

- task
- acceptance criteria
- current candidate/diff
- issue ledger
- verification results
- change manifest

The judge must not edit files.

Score 0.0–1.0:

- correctness: 0.25
- completeness: 0.15
- robustness: 0.15
- security: 0.10
- maintainability: 0.10
- clarity: 0.10
- requirement satisfaction: 0.15

Verdict must be exactly one of:

- PASS
- REVISE
- FAIL

PASS requires:

- overall score >= configured threshold
- zero unresolved critical issues
- zero unresolved high issues that affect correctness or safety
- mandatory acceptance criteria satisfied
- required verification passes

## Phase 7 — Loop

On PASS:
- stop
- summarize the implementation and evidence
- report iterations and remaining non-blocking risks

On REVISE:
- increment iteration
- revise, re-verify, and judge again
- do not rebuild from scratch unless architecture is implicated

On FAIL:
- stop if the constraints make the task impossible or unsafe
- otherwise treat it as architecture escalation

Default maximum: 4 iterations.

## Stagnation detection

Escalate to `gauntlet-architect` if:

- the same blocking issue survives 2 rounds, or
- judge score improves by less than 0.02 across 2 rounds, or
- revisions are cosmetic rather than substantive.

The architecture agent must answer:

- KEEP_ARCHITECTURE
- MODIFY_ARCHITECTURE
- REPLACE_ARCHITECTURE

with evidence.

## Multi-provider enhancement

If `scripts/provider_router.py status` shows external providers available, you may use them for
independent critique/judging.

Read `references/multi-provider.md`.

Provider diversity is optional. It must never replace deterministic verification.

Do not expose API keys, hidden chain-of-thought, or private subagent scratch work.

## State

For long Gauntlet runs, maintain `.gauntlet/state.json`.

Use:

```bash
python .agents/skills/gauntlet-loop/scripts/gauntlet_state.py init \
  --task "<task>" --max-iterations 4 --min-score 0.90
```

Update only compact results, issue summaries, scores, and evidence references. Do not store
private chain-of-thought.

## Final response

Keep the user-facing response concise. Include:

- final verdict
- what changed
- tests / verification performed
- iterations
- judge score
- remaining non-blocking risks

Do not dump raw subagent transcripts unless the user asks.
