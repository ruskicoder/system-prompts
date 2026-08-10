# Audit Inventory — prompt-orchestrator vs openclaw-operator
Generated: 2026-08-10

## Target Folders
- **Folder1 (Authoritative Target)**: `/mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator`
- **Folder2 (Candidate Source)**: `/mnt/DATA/DATA/Github/system-prompts/openclaw-operator`

---

## Folder1 Inventory (32 files)

### Root Files
- `AGENT.md` (15,668 bytes) - Central AI Agent Orchestrator prompt specification
- `README.md` (2,767 bytes) - Framework documentation and usage guide

### Installation Scripts (`install/`)
- `install/install-all.sh` (388 bytes) - Master installation runner
- `install/install-antigravity.sh` (584 bytes) - Antigravity platform target installer
- `install/install-codex.sh` (697 bytes) - OpenAI Codex platform target installer
- `install/install-cursor.sh` (451 bytes) - Cursor platform target installer
- `install/install-gemini.sh` (599 bytes) - Gemini platform target installer
- `install/install-opencode.sh` (710 bytes) - OpenCode platform target installer

### Skills (`skills/`)
- `skills/api-integration.md` (4,858 bytes) - API integration skill
- `skills/browser-automation.md` (4,205 bytes) - Browser automation skill
- `skills/code-execution.md` (4,549 bytes) - Terminal and code execution skill
- `skills/code-quality-testing.md` (4,339 bytes) - Code quality and testing skill
- `skills/codebase-understanding.md` (5,846 bytes) - Codebase search and indexing skill
- `skills/communication-tone.md` (5,250 bytes) - Communication and response tone skill
- `skills/data-analysis.md` (4,519 bytes) - Data analysis skill
- `skills/deployment.md` (3,519 bytes) - Deployment and CI/CD skill
- `skills/file-operations.md` (5,218 bytes) - File operation discipline skill
- `skills/image-media.md` (4,176 bytes) - Image and media processing skill
- `skills/memory-management.md` (4,563 bytes) - State and memory management skill
- `skills/project-scaffolding.md` (3,957 bytes) - Project initialization skill
- `skills/safety-profiles.md` (6,792 bytes) - Security and safety profile skill
- `skills/web-search-research.md` (5,052 bytes) - Web search and research skill

### Workflows (`workflows/`)
- `workflows/agent-loop.md` (4,542 bytes) - Multi-step agent execution loop
- `workflows/diagnostic-fix.md` (3,749 bytes) - Error diagnosis and bug fix workflow
- `workflows/direct-implementation.md` (2,871 bytes) - Quick direct implementation workflow
- `workflows/pair-programming.md` (2,910 bytes) - Interactive pair programming workflow
- `workflows/plan-execute.md` (4,238 bytes) - Plan-then-execute workflow
- `workflows/research-answer.md` (3,456 bytes) - Deep research and synthesis workflow
- `workflows/spec-driven.md` (48,363 bytes) - Kiro spec-driven development lifecycle
- `workflows/summarization.md` (3,776 bytes) - Session summarization workflow
- `workflows/turnaround-builder.md` (3,513 bytes) - Rapid app turnaround builder workflow

### Steering (`.kiro/steering/`)
- `.kiro/steering/orchestrator-steering.md` (1,471 bytes) - Persistent steering rule

---

## Folder2 Inventory Summary (`openclaw-operator`)

### Core Architecture & Prompt Files
- `AGENTS.md` (11,612 bytes) - Multi-agent hierarchy and agent interaction rules
- `ASSISTANT_WORKFLOW.md` (5,509 bytes) - Assistant workflow engine
- `CHANGELOG.md` (6,245 bytes) - Project version log
- `CONTRIBUTING.md` (2,903 bytes) - Contribution rules
- `DEPLOYMENT.md` (9,004 bytes) - Deployment guide and orchestration runbooks
- `Dockerfile` (1,458 bytes) - Container manifest
- `ENGAGEMENT_OS.md` (3,730 bytes) - Runtime operating system engagement model
- `HEARTBEAT.md` (3,899 bytes) - Periodic pulse and health check monitoring protocol
- `IDENTITY.md` (1,706 bytes) - Persona definition
- `OPENCLAW_CONTEXT_ANCHOR.md` (298 bytes) - Workspace context anchor
- `QUICKSTART.md` (7,791 bytes) - Quickstart manual
- `RADAR.md` (3,665 bytes) - Continuous environmental radar and external scan protocol
- `README.md` (15,972 bytes) - Main OpenClaw operator manual
- `RUNTIME_ENGAGEMENT_OS.md` (4,175 bytes) - Execution framework rules
- `SOUL.md` (5,230 bytes) - Deep core principles and tone
- `SPRINT_HARDENING_BASELINE.md` (1,530 bytes) - Sprint hardening baseline
- `TOOLS.md` (1,223 bytes) - Tool catalog and usage conventions
- `USER.md` (567 bytes) - User preference anchor
- `WORKBOARD.md` (27,618 bytes) - Autonomous task workboard specification

### Subdirectories
- `agents/` (21 specialized agent role definitions)
- `skills/` (11 TypeScript skill runtime definitions)
- `orchestrator/` (Full NestJS/Docker orchestration backend codebase)
- `config/`, `governance/`, `operations/`, `security/`, `docs/`, `scripts/`

---

## Comparison Units Mapping

- **Unit 001**: Core Agent Architecture & Persona Specs (`AGENT.md` vs `AGENTS.md`, `IDENTITY.md`, `SOUL.md`, `RUNTIME_ENGAGEMENT_OS.md`)
- **Unit 002**: Installation & Deployment Framework (`install/*` & `README.md` vs `DEPLOYMENT.md`, `QUICKSTART.md`, `orchestrator/build-docker.sh`)
- **Unit 003**: Workflows & Engagement OS (`workflows/*` vs `ASSISTANT_WORKFLOW.md`, `ENGAGEMENT_OS.md`, `WORKBOARD.md`)
- **Unit 004**: Tool Discipline & Skill Definitions (`skills/*` vs `TOOLS.md`, `openclaw-operator/skills/*`)
- **Unit 005**: Specialized Subagent Catalog & Execution (`AGENT.md` Section M vs `openclaw-operator/agents/*`)
- **Unit 006**: Continuous Monitoring, Heartbeat & Environmental Scanning (`prompt-orchestrator` vs `HEARTBEAT.md`, `RADAR.md`)
- **Unit 007**: Security, Safety & Governance Protocols (`skills/safety-profiles.md` vs `security/`, `governance/`)
