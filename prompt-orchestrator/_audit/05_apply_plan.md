# Apply Plan — Faithful Enhancement Protocol

**Folder1 Target**: `/mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator`  
**Folder2 Reference**: `/mnt/DATA/DATA/Github/system-prompts/openclaw-operator`  
**Audit Directory**: `/mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/_audit`

---

## Ordered List of Findings to Apply

### 1. Finding 001 — Core Agent Architecture & Persona Specs (`AGENT.md`)
- **Target File**: [AGENT.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/AGENT.md)
- **Target Sections**: Section A, Section D, Section E, Section G, Section M
- **Action Plan**:
  - Add Decision Hierarchy to Section A (Safety & Policy > System Integrity > Evidence Completeness > Task Correctness > Efficiency).
  - Add Crash-Safe Memory Checkpoint Protocol to Section D (Stage 2.5).
  - Add Heartbeat vs Cron Dispatch Rules to Section E.
  - Add Multi-Platform Output Rules (Discord/WhatsApp bullet conversions, link embed suppression `<url>`) to Section G.
- **Rule 3 Identity Preservation Check**:
  - *Does this change what folder1 does, how it's structured, or how it's invoked?*
  - **Answer**: No. `AGENT.md` remains the unified single master system prompt file. The structure, section lettering (A–O), and core power mode / intention classification workflows are 100% preserved. The additions are purely additive enhancements.
- **Rule 5 Neutralization Check**:
  - Strip all references to "OpenClaw", "Mission Control", "SOUL.md", or OpenClaw specific scripts (`scripts/memory_guard.sh`). Use generic prompt-orchestrator conventions (e.g. `.kiro/session-summary.md` and workspace memory files).

### 2. Finding 002 — Installation & Deployment Framework (`install/`)
- **Target Files**: 
  - [install/install-openclaw.sh](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/install/install-openclaw.sh) [NEW]
  - [install/systemd/prompt-orchestrator.service](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/install/systemd/prompt-orchestrator.service) [NEW]
  - [install/install-all.sh](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/install/install-all.sh) [MODIFY]
- **Action Plan**:
  - Create `install/install-openclaw.sh` to support deploying `prompt-orchestrator` to OpenClaw target workspaces (`~/.openclaw`).
  - Create `install/systemd/prompt-orchestrator.service` as a systemd user unit template for background daemon runs.
  - Update `install/install-all.sh` to include `install-openclaw.sh`.
- **Rule 3 Identity Preservation Check**:
  - *Does this change what folder1 does, how it's structured, or how it's invoked?*
  - **Answer**: No. `install/` already contains modular bash installation scripts (`install-cursor.sh`, `install-gemini.sh`, `install-antigravity.sh`, `install-opencode.sh`, `install-codex.sh`). Adding `install-openclaw.sh` follows the exact same pattern and naming convention.
- **Rule 5 Neutralization Check**:
  - Name service unit `prompt-orchestrator.service` (not `orchestrator.service`). Use neutral script paths.

### 3. Finding 003 — Workflows & Real Test Contracts (`workflows/plan-execute.md`)
- **Target File**: [workflows/plan-execute.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/workflows/plan-execute.md)
- **Action Plan**:
  - Update Phase 5 in `workflows/plan-execute.md` with **Real Test Verification Protocol** (real completion signals, cache key variations, state isolation) and **Shipping Sync Rules**.
- **Rule 3 Identity Preservation Check**:
  - *Does this change what folder1 does, how it's structured, or how it's invoked?*
  - **Answer**: No. `workflows/plan-execute.md` retains its exact 6-phase flow structure, GitNexus integration, token budget matrix, and hallucination watchpoints. Phase 5 is enhanced with rigorous real-test criteria.
- **Rule 5 Neutralization Check**:
  - Remove all openclaw-operator script references (`npm run verify:main`, `WORKBOARD.md`). Use standard test runners (`pnpm test` / `npm test`) and generic documentation sync guidance.

### 4. Finding 004 — Tooling & Skill Ecosystem (`AGENT.md` Section C)
- **Target File**: [AGENT.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/AGENT.md) Section C
- **Action Plan**:
  - Add Local Setup Cheat Sheet (`TOOLS.md`) note to Section C of `AGENT.md`.
- **Rule 3 Identity Preservation Check**:
  - *Does this change what folder1 does, how it's structured, or how it's invoked?*
  - **Answer**: No. Section C's 12 core tool catalog items remain unchanged. The `TOOLS.md` note clarifies how environment-specific notes should be separated from shared skill definitions.
- **Rule 5 Neutralization Check**:
  - Completely neutral, generic description of workspace cheat sheets.

### 5. Finding 005 — Specialized Subagent Catalog & Execution (`AGENT.md` Section M)
- **Target File**: [AGENT.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/AGENT.md) Section M
- **Action Plan**:
  - Add Specialized Subagent Catalog (Code Indexer, QA Verifier, Security Auditor, Compliance Reviewer, Deployment Ops, Test Intelligence, Operations Analyst) and Subagent Result Contract (`operatorSummary`, `recommendedNextActions`, `specialistContract` with status `completed` | `watching` | `blocked` | `escalate` | `refused`).
- **Rule 3 Identity Preservation Check**:
  - *Does this change what folder1 does, how it's structured, or how it's invoked?*
  - **Answer**: No. The `task()` invocation signature and subagent dispatch structure remain fully backward compatible while offering structured result fields.
- **Rule 5 Neutralization Check**:
  - Strip folder2 NestJS manifest keys. Present subagent roles as native prompt-orchestrator subagent task types.

### 6. Finding 006 — Continuous Monitoring, Heartbeat & RADAR (`workflows/heartbeat-monitoring.md`)
- **Target File**: [workflows/heartbeat-monitoring.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/workflows/heartbeat-monitoring.md) [NEW]
- **Action Plan**:
  - Create `workflows/heartbeat-monitoring.md` codifying a 5-step background monitoring flow (Health -> Task Integrity -> Artifact Review -> Risk Scan -> Digest Generation) with token efficiency rules.
- **Rule 3 Identity Preservation Check**:
  - *Does this change what folder1 does, how it's structured, or how it's invoked?*
  - **Answer**: No. `workflows/` is designed to hold individual workflow files. Adding `heartbeat-monitoring.md` follows the existing markdown structure of `agent-loop.md`, `plan-execute.md`, etc.
- **Rule 5 Neutralization Check**:
  - Neutral digest output path (`_audit/digests/YYYY-MM-DD_digest.md`). No openclaw-operator specific paths.

### 7. Finding 007 — Security, Safety & Governance Protocols (`skills/safety-profiles.md`)
- **Target File**: [skills/safety-profiles.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/skills/safety-profiles.md)
- **Action Plan**:
  - Add Runtime Security & Isolation Governance section (Child Agent Environment Isolation, Fail-Closed Secret Validation, Tool Permission Auditing) to `skills/safety-profiles.md`.
- **Rule 3 Identity Preservation Check**:
  - *Does this change what folder1 does, how it's structured, or how it's invoked?*
  - **Answer**: No. `skills/safety-profiles.md` retains its 3 safety levels (Default, Strict, Relaxed), safety selection logic, evenhandedness, and user wellbeing sections intact.
- **Rule 5 Neutralization Check**:
  - Generic LLM runtime security definitions without folder2 implementation references.
