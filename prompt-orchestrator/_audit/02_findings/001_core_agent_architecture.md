# Finding 001 — Core Agent Architecture & Persona Specs (`AGENT.md` vs `AGENTS.md`, `SOUL.md`, `IDENTITY.md`)

## Status
matched

## Folder1 Content Summary
[AGENT.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/AGENT.md) is a single, authoritative 328-line master AI agent orchestrator system prompt. It specifies:
- Perception -> Resource -> Routing -> Execution architecture
- Cascade File Loading (6 fallback steps)
- Discovery Protocol & Tool Catalog (C)
- Universal Pre-Action Protocol (Stage 1 Research, Stage 1.5 Risky Commands, Stage 2 Sanity Check)
- Power Modes (Eco, Balanced, Deep, Critical)
- Token Budget & Saving Rules
- Hallucination Detection Engine (Loop, Oscillation, Premature Action, Scope Creep)
- Intention Classifier, Complexity Assessor, Workflow Router
- Skill Composer, Subagent Dispatch Template, Dynamic Safety Engine, Session Continuation Manager

## Folder2 Content Summary
`openclaw-operator` splits core agent instructions across `AGENTS.md` (workspace entry, memory files, group chat rules, heartbeat vs cron), `SOUL.md` (mission control mindset, decision hierarchy, risk posture), `IDENTITY.md` (persona), and `RUNTIME_ENGAGEMENT_OS.md` (runtime engagement lifecycle).

## Comparison
- **Pros of folder1**: Unified single-file architecture (`AGENT.md`), highly structured, deterministic routing matrix, precise power modes, token budget management, formal pre-action protocol.
- **Cons of folder1**: Lacks explicit decision hierarchy, lacks crash-safe memory guard instructions, missing multi-platform chat surface formatting rules (Discord/WhatsApp), missing heartbeat vs cron operational guidance.
- **Pros of folder2**: Strong mission control mindset, explicit decision priority ranking (Safety > Integrity > Evidence > Correctness > Efficiency), practical memory guard protocols (`memory_guard.sh`), clear heartbeat vs cron distinction, platform-specific response constraints.
- **Cons of folder2**: Fragmented across multiple files, lacks power mode matrix, token budget rules, or intention classifier found in folder1.

## Web Verification
- **Question checked**: Best practices for LLM agent orchestrator system prompts (single-file vs multi-file prompt specs, crash-safe memory persistence).
- **Result**: Comprehensive master system prompts with modular skill/workflow includes (folder1 pattern) perform best for tool-calling agents, while incorporating explicit decision hierarchies and crash-safe state checkpoints reduces execution drift.
- **Source**: Modern AI Agent Architecture Patterns (2025/2026 guidelines).

## Verdict
**Action**: compile new from both.
**Rationale**: Keep `AGENT.md` as the unified master prompt in folder1. Synthesize and incorporate folder2's top enhancements:
1. Incorporate OpenClaw's **Decision Hierarchy** into `AGENT.md` Section A (Safety & Policy > System Integrity > Evidence Completeness > Task Correctness > Efficiency).
2. Enhance Section D (Universal Pre-Action Protocol) with **Crash-Safe Memory Checkpoints** (session start, milestone, risky op, closeout).
3. Enhance Section C/E with **Heartbeat vs. Cron Dispatch Guidelines** for background task orchestration.
4. Add **Multi-Platform Output Constraints** (Discord/WhatsApp formatting, embed suppression).

**Confidence**: high
**Status of implementation**: applied
