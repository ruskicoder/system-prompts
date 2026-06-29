---
inclusion: always
---

# Kiro Orchestrator Integration

This steering file loads the Central AI Agent Orchestrator for Kiro environments.

## Loading the Orchestrator

The orchestrator is loaded from the repo root:

#[[file:../../AGENT.md]]

## Auto-Loaded Skills

When AGENT.md selects a workflow, its required skills are loaded from:

- `skills/[name].md` (local repo)
- Fallback: OpenCode installed skills at `~/.config/opencode/skills/`

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
