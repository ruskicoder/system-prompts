---
inclusion: always
---

# Kiro Orchestrator Integration

This steering file loads the Central AI Agent Orchestrator for Kiro environments.

## Loading the Orchestrator

The orchestrator is loaded from the repo root:

#[[file:../../AGENT.md]]

## Auto-Loaded Skills

When AGENT.md selects a workflow, its required skills are loaded from, in order:

- `skills/[name].md` / `workflows/[name].md` (local repo, canonical source)
- `.agents/skills/[name]/SKILL.md` (generated Agent Skills standard folder — same content, works with any tool that follows https://agentskills.io)
- Fallback: OpenCode installed skills at `~/.config/opencode/skills/`

These generated integration files (`.agents/`, `.claude/`, `.opencode/`, `.cursor/`, `.gemini/`, `.codex/`, `.windsurf/`) are produced by `tools/generate_integrations.py` from the canonical `skills/` and `workflows/` sources — see `INTEGRATIONS.md` for the full compatibility matrix.

## GitNexus Integration

GitNexus is available as pre-installed OpenCode skills. When the orchestrator selects `codebase-understanding` skill, these GitNexus skills are available:

- `gitnexus-exploring` — codebase exploration
- `gitnexus-debugging` — debugging with knowledge graph
- `gitnexus-impact-analysis` — blast radius analysis
- `gitnexus-refactoring` — safe refactoring
- `gitnexus-pr-review` — PR review with impact analysis
- `gitnexus-pdg-query` — control/data dependence queries
- `gitnexus-taint-analysis` — security vulnerability analysis
- `gitnexus-cli` — CLI commands reference
- `gitnexus-guide` — full tool/resource reference

## Notes for Kiro

- Kiro's `#[[file:path]]` syntax is the primary cascade method for loading skill/workflow files
- The orchestrator's cascade fallback handles non-Kiro environments
- Autonomy modes (Autopilot/Supervised) work alongside the orchestrator's power modes
- The orchestrator's subagent dispatch via `task` tool aligns with Kiro's execution model
