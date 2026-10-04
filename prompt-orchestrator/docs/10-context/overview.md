---
id: context.overview
type: overview
status: draft
owner: unassigned
summary: "What prompt-orchestrator is and who uses it."
---

# Overview

## Vision
A master orchestrator prompt plus a catalog of skills and workflows, distilled from published platform prompts, packaged so every major AI coding agent can discover and run them from one canonical source.

## Stakeholders
- Maintainers editing `AGENT.md`, `skills/` and `workflows/`.
- Users installing the integrations into projects or per-user tool configuration.

## Boundaries
In scope: the orchestrator prompt, the catalog, the generator, the installers, and the docs-scaffold skill. The rest of this repository (`platform-prompts/`, `prompt-library/`) is outside these docs.

## Out of scope
Hosting, telemetry, and per-tool runtime behavior, which belongs to each agent.
