# Prompt Orchestrator

> A master AI agent orchestrator framework distilled from 73 leaked platform prompts. Extracts best practices from Anthropic, OpenAI, Gemini, Grok, Cursor, Windsurf, Cline, Kiro, Manus, and 65+ more platforms into reusable skills, workflows, and a central orchestrator system prompt — packaged so every major AI coding agent can discover and run them.

## Works everywhere, out of the box

This repo ships **49 skills/workflows** as a single canonical source (`skills/*.md`, `workflows/*.md`) plus **generated, ready-to-use integrations** for every major agent/IDE. Clone this repo as your project (or run one install command) and you get:

| Tool | Auto-discovery | Explicit `/name` invocation |
|---|---|---|
| **Claude / Claude Code** | `.claude/skills/<name>/SKILL.md` — Claude loads it when your request matches its description | Same file — in Claude Code, skills *are* slash commands. Type `/agent-loop`, `/security-audit-codebase`, etc. |
| **Codex** (CLI / IDE) | `.agents/skills/<name>/SKILL.md` — the open [Agent Skills standard](https://agentskills.io) | `.codex/prompts/<name>.md` → `/prompts:<name>` |
| **Cursor** | `.cursor/rules/orchestrator.mdc` — always-on project context | `.cursor/commands/<name>.md` → `/<name>` |
| **OpenCode** | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` — native `skill` tool discovers all three | `.opencode/commands/<name>.md` → `/<name>` |
| **Gemini CLI** | `.agents/skills/<name>/SKILL.md` — Skills framework | `.gemini/commands/<name>.toml` → `/<name>` |
| **Antigravity** | `.agents/skills/<name>/SKILL.md` — shares Gemini CLI's open-standard support | `.gemini/commands/<name>.toml` → `/<name>` |
| **Windsurf** | `.windsurf/rules/orchestrator.md` — always-on Cascade context | `.windsurf/workflows/<name>.md` → `/<name>` |
| **Any other Agent-Skills-compliant tool** | `.agents/skills/<name>/SKILL.md` | — |
| **Anything else** | `AGENTS.md` at the repo root — the plain-text fallback nearly every coding agent reads | — |

See [`INTEGRATIONS.md`](./INTEGRATIONS.md) for the full generated compatibility map (every one of the 49 skills/workflows, listed with its `/name`, argument hint, and description) — it's regenerated automatically, so it never drifts from the source.

## How it's built (single source of truth)

```
skills/*.md, workflows/*.md   (you edit these — 49 files, YAML frontmatter + instructions)
            │
            ▼   tools/generate_integrations.py
            │
   ┌────────┼─────────────────────────────────────────────────────────┐
   ▼        ▼             ▼            ▼           ▼          ▼       ▼
.agents/  .claude/     .opencode/   .cursor/    .codex/    .gemini/  .windsurf/
 skills/   skills/      skills/     commands/   prompts/   commands/  workflows/
           (+CLAUDE.md) commands/   rules/                           rules/
                                                                AGENTS.md, INTEGRATIONS.md
```

**Never hand-edit the generated directories** (`.agents/`, `.claude/`, `.opencode/`, `.cursor/`, `.codex/`, `.gemini/`, `.windsurf/`, `AGENTS.md`, `CLAUDE.md`, `INTEGRATIONS.md`, `.claude-plugin/`). Edit `skills/*.md` or `workflows/*.md`, then re-run:

```bash
python3 tools/generate_integrations.py
```

This keeps every tool-specific format (SKILL.md folders, slash-command wrappers, TOML commands, plugin manifests) perfectly in sync with the canonical content — there is exactly one place to update a skill's behavior.

Validate everything (canonical files + all generated output) with:

```bash
python3 skills/validate_skills.py
```

## Contents

| Path | Description |
|------|-------------|
| `AGENT.md` | Central orchestrator — core values, pre-action protocol, power modes, routing, safety engine, and more (canonical source) |
| `AGENTS.md` | Generated copy of `AGENT.md`, at the filename most agents (Codex, Gemini CLI, Cursor, Windsurf, OpenCode, Antigravity, Amp, Aider…) read natively |
| `CLAUDE.md` | Claude Code project memory — imports `AGENTS.md` and documents the installed skills |
| `skills/` | 39 specialized skill modules (canonical source, flat `.md` files with YAML frontmatter) |
| `workflows/` | 10 execution workflows (canonical source, same format as skills) |
| `.agents/skills/` | **Generated.** Every skill/workflow as an Agent-Skills-standard folder (`<name>/SKILL.md`) — the universal format |
| `.claude/skills/` | **Generated.** Same content, at Claude Code's discovery path |
| `.opencode/skills/`, `.opencode/commands/` | **Generated.** OpenCode native skills + explicit slash commands |
| `.cursor/commands/`, `.cursor/rules/` | **Generated.** Cursor slash commands + always-on rule |
| `.codex/prompts/` | **Generated.** Codex CLI legacy custom prompts (guaranteed `/prompts:<name>`) |
| `.gemini/commands/` | **Generated.** TOML slash commands for Gemini CLI and Antigravity |
| `.windsurf/workflows/`, `.windsurf/rules/` | **Generated.** Windsurf Cascade workflows + always-on rule |
| `.claude-plugin/` | **Generated.** Claude Code plugin marketplace manifest (`/plugin marketplace add .` then `/plugin install prompt-orchestrator@prompt-orchestrator`) |
| `tools/generate_integrations.py` | The generator — re-run after editing any skill/workflow |
| `tools/registry.json` | **Generated.** Machine-readable list of every skill/workflow |
| `INTEGRATIONS.md` | **Generated.** Full human-readable compatibility map |
| `.kiro/` | Steering configuration for Kiro |
| `install/` | Cross-platform installers (Bash + PowerShell) for every supported tool, plus universal project/global installers |

## Install

### Fastest path: make one project work with every tool

```bash
# Regenerate (optional — the repo already ships generated output)
python3 tools/generate_integrations.py

# Copy every integration into an existing project
bash install/install-project.sh /path/to/your/project
```

This drops `.agents/`, `.claude/`, `.cursor/`, `.codex/`, `.gemini/`, `.opencode/`, `.windsurf/`, `.claude-plugin/`, `AGENTS.md`, `AGENT.md`, `CLAUDE.md`, and the canonical `skills/`/`workflows/` sources straight into your project. Open that project in *any* of the supported tools and the skills/workflows are immediately discoverable and runnable via `/`.

On Windows:

```powershell
powershell install\install-project.ps1 -TargetDir C:\path\to\your\project
powershell install\install-windsurf.ps1 -TargetDir C:\path\to\your\project
```

### Global (per-user) installs

Installs into each tool's home-directory config so the orchestrator is available in *every* project, not just one.

```bash
# All tools that support a global/home-directory install
bash install/install-all.sh

# Or install to a specific tool
bash install/install-claude.sh        # ~/.claude — Claude Code Skills + CLAUDE.md
bash install/install-codex.sh         # ~/.agents/skills + ~/.codex/prompts + AGENTS.md
bash install/install-cursor.sh        # ~/.cursor/commands + ~/.cursor/rules
bash install/install-opencode.sh      # ~/.config/opencode/{skills,commands}
bash install/install-gemini.sh        # ~/.gemini/commands (TOML) + ~/.agents/skills + GEMINI.md
bash install/install-antigravity.sh   # ~/.gemini/antigravity{,-ide}/commands + ~/.agents/skills
bash install/install-openclaw.sh      # ~/.openclaw

# Windsurf and single-project setups are per-project, not global:
bash install/install-windsurf.sh /path/to/your/project
bash install/install-project.sh /path/to/your/project
```

### Windows (PowerShell / CMD)

```powershell
# All global-scope installers, run sequentially
powershell .\install\install-all.ps1

# Or from Command Prompt / double-click:
install\install-all.bat

# Or install to a specific tool
powershell .\install\install-claude.ps1
powershell .\install\install-codex.ps1
powershell .\install\install-cursor.ps1
powershell .\install\install-opencode.ps1
powershell .\install\install-gemini.ps1
powershell .\install\install-antigravity.ps1
powershell .\install\install-openclaw.ps1
```

### Claude Code plugin marketplace (alternative to install-claude.sh)

```
/plugin marketplace add /path/to/prompt-orchestrator
/plugin install prompt-orchestrator@prompt-orchestrator
```

## Using the skills once installed

Every skill/workflow is invocable two ways, in every supported tool:

1. **Automatically** — the agent reads each skill's `description` at session start and loads the full instructions when your request matches it. No action needed.
2. **Explicitly** — type `/` followed by the skill or workflow name (e.g. `/agent-loop`, `/plan-execute`, `/security-audit-codebase`, `/docx`). Arguments after the name are passed straight through (`argument-hint` in each skill's frontmatter shows the expected shape).

See [`INTEGRATIONS.md`](./INTEGRATIONS.md) for the full list of all 49 `/name` commands with descriptions, or inspect `tools/registry.json` for the machine-readable version.

## Architecture

```
AGENT.md (canonical) → AGENTS.md (generated copy, universal fallback)
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

skills/ (39, canonical)              workflows/ (10, canonical)
├── file-operations.md               ├── direct-implementation.md
├── codebase-understanding.md        ├── diagnostic-fix.md
├── code-execution.md                ├── plan-execute.md
├── web-search-research.md           ├── agent-loop.md
├── browser-automation.md            ├── spec-driven.md
├── communication-tone.md            ├── research-answer.md
├── code-quality-testing.md          ├── pair-programming.md
├── project-scaffolding.md           ├── summarization.md
├── memory-management.md             ├── turnaround-builder.md
├── safety-profiles.md               └── heartbeat-monitoring.md
├── api-integration.md
├── data-analysis.md
├── image-media.md
├── deployment.md
├── review-pull-request.md
├── review-software-architecture.md
├── security-audit-codebase.md
├── skill-creator.md
├── docx-skill.md
└── design-*/engineering-*/... (plugin-style skills, 20 more)
       │
       ▼  tools/generate_integrations.py
       ▼
.agents/skills/  .claude/skills/  .opencode/skills/  .opencode/commands/
.cursor/commands/  .cursor/rules/  .codex/prompts/  .gemini/commands/
.windsurf/workflows/  .windsurf/rules/  .claude-plugin/  AGENTS.md  CLAUDE.md
```

## Source Annotation

Every rule across all skills carries `_Source: [platform] (Category [letter])_` citations anchored to `platform-prompts/.cache/prompt-extractions.md`, which contains 1,938 exact verbatim sentences extracted from all 73 platform prompts across 19 categories (A–S).
