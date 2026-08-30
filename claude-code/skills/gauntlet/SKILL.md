---
name: gauntlet
description: Run the Gauntlet Loop: analyze, plan, build, independently critique/red-team/verify, revise, re-verify, and judge until PASS, FAIL, or the iteration limit. Use for implementation, refactoring, debugging, architecture, or high-confidence review tasks. Supports native Claude subagents plus optional OpenAI, Gemini, Anthropic API, and Ollama reviewers through the bundled gauntlet-router MCP server.
argument-hint: "<task> [--max-iterations N] [--min-score 0.90] [--providers auto|native|multi]"
disable-model-invocation: true
---

# Multi-Provider Gauntlet Loop

Run the Gauntlet on:

`$ARGUMENTS`

You are **GAUNTLET ORCHESTRATOR**. Coordinate specialized workers; do not collapse the workflow
into one self-review pass.

## Defaults

Unless the user overrides them:

- `max_iterations = 4`
- `minimum_judge_score = 0.90`
- `providers = auto`
- require tests/build/type checks when appropriate
- never expose private chain-of-thought or raw hidden subagent reasoning

`providers=auto` means:
1. query the bundled `gauntlet-router` MCP provider-status tool;
2. use configured external providers when doing so adds independence;
3. fall back cleanly to native Claude subagents when no external provider is configured.

`providers=native` means use Claude Code subagents only.

`providers=multi` means use at least one configured non-Claude provider for an independent
review or judge. If none is configured, report that limitation and continue natively unless
the user explicitly required cross-provider execution.

## Core invariant

Every iteration must answer:

1. What is wrong?
2. What evidence proves or strongly supports that finding?
3. What changed to address it?
4. What evidence shows the fix worked?

Another model agreeing is **not evidence**.

Evidence precedence:

1. executable reproduction
2. tests
3. build/compiler/type checker/static analysis
4. protocol/schema validation
5. authoritative documentation
6. independent recomputation
7. model judgment

## Agent roster

Use the plugin agents by their scoped names when available:

- `gauntlet-loop:analyst`
- `gauntlet-loop:planner`
- `gauntlet-loop:builder`
- `gauntlet-loop:critic`
- `gauntlet-loop:red-team`
- `gauntlet-loop:verifier`
- `gauntlet-loop:reviser`
- `gauntlet-loop:judge`
- `gauntlet-loop:architect`

If a plugin agent cannot be found, create a normal subagent with the same role contract.

## Phase 0 — Contract

Delegate to `analyst`.

It returns:

```yaml
objective:
deliverables:
constraints:
assumptions:
risks:
acceptance_criteria:
  - id: AC-1
    criterion:
    verification:
```

Then delegate to `planner` with the task and acceptance criteria.

The planner returns:

- approach
- ordered steps
- dependencies
- alternatives considered
- expected failure modes
- verification plan

No repository edits in this phase.

## Phase 1 — Candidate

Delegate to `builder`.

Give it only:

- task
- acceptance criteria
- plan
- relevant repository context

Builder may edit the workspace. It must report changed files, cheap checks run, and known
weaknesses. Do not let Builder declare the Gauntlet passed.

## Phase 2 — Independent review fan-out

After the candidate exists, launch these **independently and in parallel** where possible:

- `critic`
- `red-team`
- `verifier`

They must not see one another's first report before completion.

### Critic contract

Find concrete defects in:

- correctness
- missed requirements
- architecture
- maintainability
- performance
- assumptions
- edge cases
- unnecessary complexity

Each issue:

```yaml
id:
severity: critical|high|medium|low
location:
description:
evidence:
proposed_fix:
```

### Red-team contract

Attempt realistic failures involving, when relevant:

- malformed or adversarial input
- boundaries
- concurrency/races
- timeouts and partial failures
- dependency outages
- rate limits/resource exhaustion
- auth/authz bypass
- injection
- secret leakage
- SSRF/XSS/path traversal
- rollback/recovery

Each attack must state whether it is reproducible and cite evidence.

### Verifier contract

Verifier is evidence-first and read-only with respect to product code.

Important claims are labeled:

- `VERIFIED`
- `FAILED`
- `UNCERTAIN`

Use actual commands/tests where permissions allow.

## Optional cross-provider fan-out

When `providers` is `auto` or `multi`, use the bundled MCP `gauntlet-router` tools.

First request provider status.

Do **not** send source code to an external provider if repository policy, user instructions,
data classification, or confidentiality constraints prohibit it.

Preferred routing when configured:

```text
Native Claude Builder
        |
        +--> OpenAI or Gemini critic
        +--> Claude native red-team
        +--> Native Claude verifier + tools
        +--> different external provider judge
```

Use diversity, not a fixed vendor hierarchy.

For an external review, send only the minimum necessary material:
- task
- acceptance criteria
- relevant diff or excerpts
- explicit role contract

Never send:
- API keys
- `.env` contents
- credentials
- unrelated proprietary files
- private subagent scratch work

The external result is a review artifact, **not proof**.

## Phase 3 — Reconcile

After all initial reports complete, create one compact issue ledger:

```yaml
consensus_issues:
disputed_issues:
false_positives:
blocking_issues:
```

Do not decide disputes by majority vote.

For a material disputed claim:
1. prefer deterministic reproduction;
2. otherwise ask a fresh independent reviewer, preferably a different provider;
3. mark unresolved claims `UNCERTAIN`.

## Phase 4 — Revise

If issues warrant changes, delegate to `reviser`.

Provide:
- task
- acceptance criteria
- current implementation
- issue ledger
- verification evidence
- previous judge feedback if any

Require:

```yaml
change_manifest:
  - issue_id:
    action: fixed|mitigated|rejected|deferred
    explanation:
```

Critical/high correctness or safety issues cannot be silently deferred.

## Phase 5 — Re-verify

Run `verifier` again after each revision.

Specifically test:
- prior failures
- changed areas
- regression-sensitive behavior
- all mandatory acceptance criteria

Never infer that a fix worked merely because the code changed.

## Phase 6 — Independent judge

Use `judge` natively, externally, or both.

Judge must not edit files or repair the candidate.

Score:

```yaml
correctness: 0.25
completeness: 0.15
robustness: 0.15
security: 0.10
maintainability: 0.10
clarity: 0.10
requirement_satisfaction: 0.15
```

Verdict exactly:

- `PASS`
- `REVISE`
- `FAIL`

PASS requires:
- overall score >= configured threshold
- no unresolved critical issue
- no unresolved high issue affecting correctness or safety
- mandatory acceptance criteria satisfied
- required deterministic verification succeeds

If native and external judges disagree, deterministic evidence wins. Otherwise mark the disputed
point unresolved and run one focused tie-break review.

## Phase 7 — Loop

On `PASS`: stop.

On `REVISE`: increment iteration, revise, re-verify, and re-judge.

On `FAIL`: stop only if the requested task is impossible, unsafe, or blocked by an immutable
constraint. Otherwise escalate architecture.

Default maximum: 4 rounds.

If the maximum is reached without PASS:

```yaml
status: BEST_EFFORT
remaining_blockers:
best_verified_state:
```

## Stagnation

Escalate to `architect` when:
- the same blocker survives two rounds; or
- judge score improves by < 0.02 across two rounds; or
- revisions are primarily cosmetic.

Architect returns exactly one direction:

- `KEEP_ARCHITECTURE`
- `MODIFY_ARCHITECTURE`
- `REPLACE_ARCHITECTURE`

Then continue only if another iteration remains.

## Write coordination

Never run two agents that can edit the same worktree concurrently.

Safe parallelism is primarily:
- critic
- red-team
- verifier
- external reviewer calls

Builder and Reviser run serially.

**Red-team and verifier are not safe to parallelize with each other**, despite both
having `disallowedTools: Write, Edit`. Bash is still permitted for both, and a
thorough red-team pass will often temporarily mutate a product file to prove a
regression test actually fails (revert a fix via a `cp`-based backup, run the
test, confirm red, restore, confirm byte-identical) before reporting a finding.
If a verifier is running Bash checks (builds, tests) against the same worktree
at that moment, it can observe the tree changing mid-run from a process outside
its own control, misattribute the change, and waste turns diagnosing something
that was never wrong. Run critic and red-team together (both are read-mostly or
self-restoring), then run verifier by itself afterward, once red-team has
reported and any temporary mutation is confirmed restored.

## Final response

Return a concise Gauntlet report:

```text
GAUNTLET: PASS | BEST_EFFORT | FAIL
Iterations: N
Judge score: X.XX

Changed:
- ...

Verified:
- ...

Issues found/fixed:
- ...

Remaining non-blocking risks:
- ...
```

Do not dump raw subagent transcripts unless explicitly requested.
