# Finding 003 — Workflows & Operating Systems (`workflows/*` vs `ASSISTANT_WORKFLOW.md`, `ENGAGEMENT_OS.md`, `WORKBOARD.md`)

## Status
matched

## Folder1 Content Summary
[workflows/](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/workflows) contains 9 specialized agent workflows:
- `agent-loop.md`: Autonomous subagent loop with token budgets
- `diagnostic-fix.md`: Root-cause debugging without superficial symptom patching
- `direct-implementation.md`: Rapid single-task implementation
- `pair-programming.md`: Interactive developer pair programming
- `plan-execute.md`: Two-phase plan-then-execute lifecycle
- `research-answer.md`: Information query and research workflow
- `spec-driven.md`: Complete Kiro 3-phase spec-driven development (Requirements -> Design -> Tasks)
- `summarization.md`: Session state persistence and handoff prompt generator
- `turnaround-builder.md`: Fast app scaffolding and prototyping

## Folder2 Content Summary
`openclaw-operator` defines `ASSISTANT_WORKFLOW.md`, `ENGAGEMENT_OS.md`, `RUNTIME_ENGAGEMENT_OS.md`, and `WORKBOARD.md`. It emphasizes shipping verification contracts (`npm run verify:main`), real asynchronous test rules (wait on signals, no fixed sleeps, cache boundary isolation), and synchronized documentation updates.

## Comparison
- **Pros of folder1**: Clear, modular workflow files covering every core engineering task type with explicit token budgets and power modes.
- **Cons of folder1**: Does not explicitly codify real-test verification contracts (avoiding brittle sleep-based assertions) or documentation sync discipline during shipping.
- **Pros of folder2**: Excellent real-test discipline and shipping verification guidelines.
- **Cons of folder2**: Focuses heavily on OpenClaw internal workboard state rather than universal developer agent workflows.

## Web Verification
- **Question checked**: Best practice for AI agent testing and verification protocols.
- **Result**: Verification steps in AI workflows must explicitly mandate testing against real completion signals rather than fixed sleep durations and require doc-sync upon feature completion.
- **Source**: AI Engineering Practices & Verification Standards (2025/2026).

## Verdict
**Action**: compile new from both.
**Rationale**: Incorporate folder2's verification rules into folder1's existing workflows:
1. Enhance [plan-execute.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/workflows/plan-execute.md) and [direct-implementation.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/workflows/direct-implementation.md) with explicit **Real Test Verification Protocol** (real completion signals, cache invalidation testing, non-flaky assertions) and **Shipping Sync Rules**.

**Confidence**: high
**Status of implementation**: applied
