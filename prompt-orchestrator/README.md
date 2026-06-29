# Prompt Orchestrator

> A master AI agent orchestrator framework distilled from 73 leaked platform prompts. Extracts best practices from Anthropic, OpenAI, Gemini, Grok, Cursor, Windsurf, Cline, Kiro, Manus, and 65+ more platforms into reusable skills, workflows, and a central orchestrator system prompt.

## Contents

| File | Lines | Description |
|------|-------|-------------|
| `AGENT.md` | 556 | Central orchestrator — core values, pre-action protocol, power modes, routing, safety engine, and more |
| `skills/` | 14 files (1,298 lines) | Specialized skill modules (code operations, research, communication, safety, etc.) — all source-annotated |
| `workflows/` | 9 files (946 lines) | Execution workflows (diagnostic-fix, agent-loop, spec-driven, research-answer, etc.) |
| `.kiro/` | 1 file | Steering configuration for the orchestrator |
| `install/` | 5+ scripts | Install to any platform (opencode, Gemini, antigravity, Codex, Cursor, etc.) |

## Install

```bash
# Install to all supported platforms
bash install/install-all.sh

# Or install to a specific platform
bash install/install-opencode.sh
bash install/install-gemini.sh
bash install/install-antigravity.sh
bash install/install-codex.sh
```

## Architecture

```
AGENT.md (556 lines)
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

skills/ (14)                 workflows/ (9)
├── file-operations.md       ├── direct-implementation.md
├── codebase-understanding   ├── diagnostic-fix.md
├── code-execution.md        ├── plan-execute.md
├── web-search-research.md   ├── agent-loop.md
├── browser-automation.md    ├── spec-driven.md
├── communication-tone.md    ├── research-answer.md
├── code-quality-testing.md  ├── pair-programming.md
├── project-scaffolding.md   ├── summarization.md
├── memory-management.md     └── turnaround-builder.md
├── safety-profiles.md
├── api-integration.md
├── data-analysis.md
├── image-media.md
└── deployment.md
```

## Source Annotation

Every rule across all skills carries `_Source: [platform] (Category [letter])_` citations anchored to `platform-prompts/.cache/prompt-extractions.md`, which contains 1,938 exact verbatim sentences extracted from all 73 platform prompts across 19 categories (A–S).
