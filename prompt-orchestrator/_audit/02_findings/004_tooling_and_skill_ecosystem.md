# Finding 004 — Tooling & Skill Ecosystem (`skills/*` & `AGENT.md` Section C vs `TOOLS.md`, `openclaw-operator/skills/*`)

## Status
matched

## Folder1 Content Summary
[skills/](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/skills) contains 14 markdown skill files covering prompt-level skill guidance.
Section C of [AGENT.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/AGENT.md) details the tool catalog and discipline rules (list_dir, view_file, replace_file_content, etc.).

## Folder2 Content Summary
`openclaw-operator` defines `TOOLS.md` (local machine infrastructure cheat sheet separated from shared skill definitions) and TypeScript runtime skill registration with explicit audit checks (`auditSkill`) and permission boundaries (fileRead, fileWrite, network, exec, eval, spawn, secrets).

## Comparison
- **Pros of folder1**: 14 detailed, highly reusable markdown skill prompts designed for direct injection into any LLM agent context.
- **Cons of folder1**: Lacks explicit separation of local machine setup notes (`TOOLS.md`) from skill files, and does not formalize skill audit gates.
- **Pros of folder2**: Strong skill permission auditing and governed intake staging (`pending-review` -> `review-approved`). Clean separation of local infrastructure notes from core prompt files.
- **Cons of folder2**: Skills are coded as NestJS/TypeScript runtime modules, less portable across non-Node platforms.

## Web Verification
- **Question checked**: Best practice for managing local environment configurations vs. shared AI agent skills.
- **Result**: Local machine setup details (SSH hosts, API endpoints, local hardware aliases) should be stored in environment-specific uncommitted files (`TOOLS.md`), while skill specifications remain declarative and versioned.
- **Source**: AI Agent Development Standards (2025/2026).

## Verdict
**Action**: compile new from both.
**Rationale**:
1. Add `TOOLS.md` documentation guide into `AGENT.md` Section C.
2. Incorporate Governed Skill Intake & Security Audit rules (checking permissions: fileRead, fileWrite, network, exec, eval, secrets) into [skills/safety-profiles.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/skills/safety-profiles.md).

**Confidence**: high
**Status of implementation**: applied
