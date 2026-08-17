# Prompt Orchestrator

> A master AI agent orchestrator framework distilled from 73 leaked platform prompts. Extracts best practices from Anthropic, OpenAI, Gemini, Grok, Cursor, Windsurf, Cline, Kiro, Manus, and 65+ more platforms into reusable skills, workflows, and a central orchestrator system prompt.

## Contents

| File | Lines | Description |
|------|-------|-------------|
| `AGENT.md` | 556 | Central orchestrator — core values, pre-action protocol, power modes, routing, safety engine, and more |
| `skills/` | 17 files | Specialized skill modules (code operations, research, communication, safety, review, architecture, audit) — all source-annotated |
| `workflows/` | 10 files | Execution workflows (diagnostic-fix, agent-loop, spec-driven, research-answer, heartbeat-monitoring, etc.) |
| `.kiro/` | 1 file | Steering configuration for the orchestrator |
| `install/` | 15 scripts | Cross-platform installers for POSIX (Bash), Windows (PowerShell), and Windows (CMD) across 6 platforms |

## Install

### Linux / macOS (Bash)
```bash
# Install to all supported platforms
bash install/install-all.sh

# Or install to a specific platform
bash install/install-opencode.sh
bash install/install-gemini.sh
bash install/install-antigravity.sh
bash install/install-codex.sh
bash install/install-cursor.sh
bash install/install-openclaw.sh
```

### Windows (PowerShell / CMD)
```powershell
# Install to all supported platforms (PowerShell)
powershell .\install\install-all.ps1

# Or run from Command Prompt (CMD) or double-click:
install\install-all.bat

# Or install to a specific platform (PowerShell)
powershell .\install\install-opencode.ps1
powershell .\install\install-gemini.ps1
powershell .\install\install-antigravity.ps1
powershell .\install\install-codex.ps1
powershell .\install\install-cursor.ps1
powershell .\install\install-openclaw.ps1
```

## Architecture

```
AGENT.md
├── Identity & Operating Principles
├── Universal Pre-Action Protocol
├── Power Mode Engine (Eco/Balanced/Deep/Critical)
├── Token Budget & Resource Manager
├── Token Saving System
├── Hallucination Detection Engine
├── Intention Classifier
├── Complexity Assessor
├── Workflow Router
├── Skill Composer
├── Subagent Dispatch
├── Dynamic Safety Engine
└── Session Continuation Manager

skills/ (17)                     workflows/ (10)
├── file-operations.md           ├── direct-implementation.md
├── codebase-understanding.md    ├── diagnostic-fix.md
├── code-execution.md            ├── plan-execute.md
├── web-search-research.md       ├── agent-loop.md
├── browser-automation.md        ├── spec-driven.md
├── communication-tone.md        ├── research-answer.md
├── code-quality-testing.md      ├── pair-programming.md
├── project-scaffolding.md       ├── summarization.md
├── memory-management.md         ├── turnaround-builder.md
├── safety-profiles.md           └── heartbeat-monitoring.md
├── api-integration.md
├── data-analysis.md
├── image-media.md
├── deployment.md
├── review-pull-request.md
├── review-software-architecture.md
└── security-audit-codebase.md
```

## Source Annotation

Every rule across all skills carries `_Source: [platform] (Category [letter])_` citations anchored to `platform-prompts/.cache/prompt-extractions.md`, which contains 1,938 exact verbatim sentences extracted from all 73 platform prompts across 19 categories (A–S).
