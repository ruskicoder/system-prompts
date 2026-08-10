# Finding 006 — Continuous Monitoring, Heartbeat & Environmental Scanning (`prompt-orchestrator` vs `HEARTBEAT.md`, `RADAR.md`)

## Status
folder2-only

## Folder1 Content Summary
`prompt-orchestrator` has no dedicated workflow file for continuous scheduled heartbeat execution or RADAR governance monitoring.

## Folder2 Content Summary
`openclaw-operator` defines:
- [HEARTBEAT.md](file:///mnt/DATA/DATA/Github/system-prompts/openclaw-operator/HEARTBEAT.md): Scheduled periodic background execution (health check -> task integrity check -> artifact review -> security scan -> digest generation).
- [RADAR.md](file:///mnt/DATA/DATA/Github/system-prompts/openclaw-operator/RADAR.md): Governance matrix tracking **R**isks, **A**ssumptions, **D**ecisions, **A**ctions, **R**esults, and Review Cadence.

## Comparison
- **Pros of folder1**: Clean Focus on active interactive coding and agent workflows without extra background polling overhead.
- **Cons of folder1**: Missing formal workflow instructions for background agent heartbeats, periodic health checks, and token-bounded digest generation.
- **Pros of folder2**: Excellent framework for autonomous background agent heartbeats and governance RADAR tracking.
- **Cons of folder2**: Hardcodes specific OpenClaw paths (`/artifacts/digests/`).

## Web Verification
- **Question checked**: Standards for autonomous LLM agent heartbeat routines and health monitoring.
- **Result**: Autonomous background agents require token-efficient heartbeat rules with explicit skip conditions ("no state change since last check = skip") to avoid unnecessary API cost.
- **Source**: Autonomous Agent Monitoring Standards (2025/2026).

## Verdict
**Action**: compile new from both.
**Rationale**: 
1. Create a new workflow in folder1: [workflows/heartbeat-monitoring.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/workflows/heartbeat-monitoring.md), codifying 5-step heartbeat runs (Health -> Task Integrity -> Artifact Review -> Risk Scan -> Digest Generation) with token efficiency rules.
2. Incorporate RADAR framework into folder1 governance & steering principles.

**Confidence**: high
**Status of implementation**: applied
