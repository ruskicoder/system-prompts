---
name: build-discipline
description: Build discipline for every code change. Understand first, prefer reuse over new code, fix root causes, avoid speculative structure, never simplify away safety, add one runnable check, mark deliberate shortcuts, and follow per-task-type rules for investigation, feature, migration, refactor, bug fix and verification. Use when writing, changing or reviewing code.
---

# Skill: Build Discipline

## Purpose
Keep changes small where small is right, coherent where coherence matters, and never
cheaper than the safety they must keep. Part 1 applies to every change. Part 2 adds rules
per task type.

## Part 1: General Rules

### Understand First
Read the request and every file the change touches. Trace the real flow end to end before
deciding how small the change can be.

### Choice Ladder
Stop at the first rung that holds without distorting the design:

1. The behaviour already exists: reuse it, or change nothing.
2. A helper, type or pattern in this codebase owns it: extend that.
3. The standard library does it.
4. The platform does it natively (HTML input types, CSS, database constraints).
5. An installed dependency does it. Do not add a dependency for a few lines.
6. Only then write the minimum new code, in the layer that owns the invariant.

### Root Cause Over Symptom
Find every caller of the function you will change. One guard in the shared function beats
one guard in each caller.

### No Speculative Structure
No interface with one implementation, no factory with one product, no configuration for a
value that never changes, no scaffolding for later.

### Clarity Over Smallest Diff
A coherent wider change beats a cramped patch in the wrong place. Total system clarity is
the goal, not the line count.

### Never Simplify Away
- Input validation at trust boundaries
- Authorization and other security checks
- Error handling that prevents data loss
- Accessibility
- Migration and rollback safety
- Concurrency protection
- Compatibility guarantees
- Required tests
- Behaviour the user explicitly requested

### One Runnable Check
Non-trivial logic (a branch, loop, parser, money path or security path) gets the smallest
test or assertion that fails if the logic breaks. Trivial one-liners need none.

### Deliberate Shortcut Marker
When a simplification has a known ceiling (global lock, quadratic scan, naive heuristic),
leave a comment that names the ceiling and the trigger to revisit it. Markers can be
collected into a debt list. Flag any marker without a trigger.

### Calibration Values Stay
Code that drives physical systems keeps its tuning values, even when a simpler model would
drop them. Hardware drifts.

### Over-Engineering Review
Run it separately from the correctness review. Write one line per finding with one tag:

| Tag | Meaning |
|-----|---------|
| `delete` | dead or speculative code |
| `stdlib` | hand-rolled version of a standard library function |
| `native` | dependency doing what the platform does |
| `yagni` | single-use abstraction or unused configuration |
| `shrink` | same logic in fewer lines |

End with the possible net reduction in lines and dependencies. Never flag the single
smoke test as excess.

## Part 2: Task-Type Rules
The user states the task type, or the agent reads it back for confirmation. Never assign
it silently.

### Investigate
- Separate the observed symptom from the inferred cause.
- Trace inputs, state changes, ownership boundaries and failure output.
- Rank hypotheses by evidence and by how cheaply each can be disproved.
- Do not edit until one mechanism explains all the evidence.
- Report the cause and the proof. Fix only if the task authorizes a fix.

### Feature
- Derive observable acceptance criteria and explicit non-goals.
- Trace the entry point through every layer that owns an invariant.
- Deliver one coherent end-to-end path.
- Omit modes, providers, configuration and polish that acceptance does not need.
- State the tradeoff of every new surface or dependency.

### Migration
- Map readers, writers, data shape, compatibility window and ownership.
- Define the forward path and the rollback path.
- Destructive steps are explicit and separately authorized.
- Sequence: expand, migrate, verify, contract. Retries are idempotent.
- Make partial failure observable. Verify old and new paths at each stage.
- Never run the destructive contraction implicitly.

### Refactor
- Define the behaviour-preservation boundary and how to verify it before editing.
- No feature changes inside a refactor.
- Move one ownership boundary at a time.
- Preserve public interfaces, failure behaviour and ordering.
- Every intermediate state builds and passes tests.

### Bug Fix
- Reproduce first when cheap. Otherwise capture the strongest evidence available.
- Change the narrowest layer that owns the wrong behaviour.
- No unrelated cleanup or renames.
- Add only the regression proof the fix needs.

### Verify
- Turn acceptance conditions into the smallest sufficient set of proofs.
- Reuse earlier results only if the repository state matches.
- Run focused checks before wide gates.
- Report pass, fail, unavailable and blocked as distinct outcomes.
