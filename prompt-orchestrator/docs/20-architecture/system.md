---
id: architecture.system
type: architecture
status: draft
owner: unassigned
summary: "Canonical sources, the generator, generated outputs, and installers."
---

# System

## Context
Maintainers edit canonical files; the generator derives every agent-specific format; installers copy the derived output to users.

## Components
- [orchestrator](../30-units/orchestrator/README.md)
- [catalog](../30-units/catalog/README.md)
- [generator](../30-units/generator/README.md)
- [installers](../30-units/installers/README.md)
- [docs-scaffold](../30-units/docs-scaffold/README.md)

## Flows
```mermaid
flowchart LR
    A[AGENT.md] --> G[tools/generate_integrations.py]
    S[skills/*.md + companion folders] --> G
    W[workflows/*.md] --> G
    G --> O[".agents/ .claude/ .opencode/ .cursor/ .codex/ .gemini/ .windsurf/"]
    G --> P[integrations/antigravity/]
    G --> M[AGENTS.md CLAUDE.md INTEGRATIONS.md registry.json .claude-plugin/]
    O --> I[install/*]
    P --> I
```
