# Finding 005 — Specialized Subagent Catalog & Execution (`AGENT.md` Section M vs `openclaw-operator/agents/*`)

## Status
matched

## Folder1 Content Summary
Section M of [AGENT.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/AGENT.md) contains a generic `task()` subagent dispatch template requiring subtask description, workflow name, power mode, active skills, and basic return fields (modified files, summary, verification).

## Folder2 Content Summary
`openclaw-operator/agents/` defines a catalog of 21 specialized subagent role surfaces:
- `build-refactor-agent`
- `code-index-agent`
- `compliance-agent`
- `deployment-ops-agent`
- `operations-analyst-agent`
- `qa-verification-agent`
- `release-manager-agent`
- `security-agent`
- `skill-audit-agent`
- `test-intelligence-agent`
- `summarization-agent`, etc.
It enforces a **Shared Specialist Result Contract**:
- `operatorSummary`: 1-line answer to "what happened here?"
- `recommendedNextActions`: bounded follow-up steps
- `specialistContract`: status (`completed` | `watching` | `blocked` | `escalate` | `refused`) and refusal/escalation reasons.

## Comparison
- **Pros of folder1**: Standardized single subagent dispatch format compatible with generic agent frameworks.
- **Cons of folder1**: Lacks explicit role catalog mapping and lacks standard refusal/escalation status vocabulary in subagent responses.
- **Pros of folder2**: Rich catalog of specialized role templates and deterministic response contracts (`completed`, `blocked`, `escalate`, `refused`).
- **Cons of folder2**: Overly complex file layout (21 separate agent folders with individual NestJS/JSON manifests).

## Web Verification
- **Question checked**: Standard pattern for subagent dispatch and response schema in multi-agent orchestrators.
- **Result**: Multi-agent systems should provide a clear role catalog for subagent selection and enforce typed return payloads with explicit status codes (`completed`, `blocked`, `escalate`, `refused`).
- **Source**: Multi-Agent Orchestration Design Patterns (2025/2026).

## Verdict
**Action**: compile new from both.
**Rationale**: 
1. Expand [AGENT.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/AGENT.md) Section M with a **Specialized Subagent Role Catalog** (Code Indexer, QA Verifier, Security Reviewer, Compliance Auditor, Deployment Ops, Test Intelligence, Operations Analyst).
2. Enhance the Subagent Dispatch template in Section M to mandate the **Specialist Result Contract** (`operatorSummary`, `recommendedNextActions`, `status`: `completed` | `watching` | `blocked` | `escalate` | `refused`).

**Confidence**: high
**Status of implementation**: applied
