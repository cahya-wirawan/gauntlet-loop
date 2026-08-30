# Gauntlet Orchestration Reference

## Core invariant

Every loop must answer:

1. What is wrong?
2. What evidence shows it is wrong?
3. What changed?
4. What evidence shows the fix worked?

A new answer without new evidence is not progress.

## Role contracts

### Analyst

Read-only.

Output:

```yaml
objective: ""
deliverables: []
constraints: []
assumptions: []
risks: []
acceptance_criteria:
  - id: AC-1
    criterion: ""
    verification: ""
```

### Planner

Read-only.

Output:

```yaml
approach: ""
steps: []
alternatives_considered: []
rejected_alternatives: []
dependencies: []
expected_failure_modes: []
verification_plan: []
```

### Builder

May edit.

Output summary:

```yaml
changed_files: []
implementation_summary: ""
checks_run: []
known_weaknesses: []
```

### Critic

Read-only.

```yaml
issues:
  - id: C-001
    severity: high
    location: ""
    description: ""
    evidence: ""
    proposed_fix: ""
verdict: PASS|BLOCK
confidence: 0.0
```

### Red Team

Read-only.

```yaml
attacks:
  - id: R-001
    scenario: ""
    expected_failure: ""
    severity: high
    reproducible: true
    evidence: ""
    mitigation: ""
```

### Verifier

Read-only unless a test artifact explicitly needs temporary creation; avoid modifying product
code.

```yaml
checks:
  - id: V-001
    claim: ""
    status: VERIFIED|FAILED|UNCERTAIN
    method: ""
    evidence: ""
failures: []
confidence: 0.0
```

### Reviser

May edit.

```yaml
change_manifest:
  - issue_id: C-001
    action: fixed|mitigated|rejected|deferred
    explanation: ""
changed_files: []
remaining_risks: []
```

### Judge

Read-only.

```yaml
scores:
  correctness: 0.0
  completeness: 0.0
  robustness: 0.0
  security: 0.0
  maintainability: 0.0
  clarity: 0.0
  requirement_satisfaction: 0.0
overall_score: 0.0
blocking_issues: []
verdict: PASS|REVISE|FAIL
required_changes: []
confidence: 0.0
```

## Context isolation

Analyst gets:
- user task
- repository context

Planner gets:
- task
- acceptance criteria

Builder gets:
- task
- acceptance criteria
- plan

Critic gets:
- task
- acceptance criteria
- candidate

Red Team gets:
- task
- candidate

Verifier gets:
- task
- acceptance criteria
- candidate
- tools/repository

Reviser gets:
- task
- acceptance criteria
- current candidate
- issue ledger
- verification evidence
- judge feedback

Judge gets:
- task
- acceptance criteria
- current candidate
- issue ledger
- verification evidence
- change manifest

## Write coordination

Never run Builder and Reviser concurrently on the same worktree.

Critic, Red Team, Verifier, Analyst, Planner, Architect, and Judge should be read-only.

Parallelize primarily read-heavy work.

## Evidence rules

Strong evidence:
- failing/passing command with relevant output
- unit/integration/e2e test
- compiler/type checker
- static analyzer
- deterministic reproduction
- protocol/schema validation
- official specification/documentation

Weak evidence:
- "looks correct"
- model agreement
- builder confidence
- absence of an observed failure without targeted testing

## Severity

Critical:
- exploitable security issue
- data loss/corruption
- fundamental correctness failure
- unsafe operation
- task cannot fulfill its central purpose

High:
- major requirement broken
- likely production failure
- important unhandled edge case
- material security/reliability weakness

Medium:
- limited functional issue
- maintainability/performance concern
- non-critical gap

Low:
- polish
- minor clarity
- low-impact cleanup

## Stagnation

If architecture escalation triggers, the architect should first inspect the original acceptance
criteria and evidence, not merely the latest implementation. The goal is to identify a bad
assumption or solution family, not produce another cosmetic rewrite.
