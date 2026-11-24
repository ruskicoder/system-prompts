# Prompt Orchestrator

> A master AI agent orchestrator framework distilled from 73 leaked platform prompts. Extracts best practices from Anthropic, OpenAI, Gemini, Grok, Cursor, Windsurf, Cline, Kiro, Manus, and 65+ more platforms into reusable skills, workflows, and a central orchestrator system prompt, packaged so every major AI coding agent can discover and run them.

## Works everywhere, out of the box

This repo ships **73 core skills/workflows** as a single canonical source (`skills/*.md`, `workflows/*.md`) plus **generated, ready-to-use integrations** for every major agent/IDE. Clone this repo as your project (or run one install command) and you get:

| Tool | Auto-discovery | Explicit `/name` invocation |
|---|---|---|
| **Claude / Claude Code** | `.claude/skills/<name>/SKILL.md`: Claude loads it when your request matches its description | Same file. In Claude Code, skills *are* slash commands. Type `/agent-loop`, `/security-audit-codebase`, etc. |
| **Codex** (CLI / IDE) | `.agents/skills/<name>/SKILL.md`: the open [Agent Skills standard](https://agentskills.io) | `.codex/prompts/<name>.md` → `/prompts:<name>` |
| **Cursor** | `.cursor/rules/orchestrator.mdc`: always-on project context | `.cursor/commands/<name>.md` → `/<name>` |
| **OpenCode** | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/`: native `skill` tool discovers all three | `.opencode/commands/<name>.md` → `/<name>` |
| **Gemini CLI** | `.agents/skills/<name>/SKILL.md`: Skills framework | `.gemini/commands/<name>.toml` → `/<name>` |
| **Antigravity** | Workspace: `.agents/skills/<name>/SKILL.md`; global: `~/.gemini/config/plugins/prompt-orchestrator/skills/<name>/SKILL.md` | Native skill invocation; browse `/` in a fresh session |
| **Windsurf** | `.windsurf/rules/orchestrator.md`: always-on Cascade context | `.windsurf/workflows/<name>.md` → `/<name>` |
| **Any other Agent-Skills-compliant tool** | `.agents/skills/<name>/SKILL.md` | — |
| **Anything else** | `AGENTS.md` at the repo root: the plain-text fallback nearly every coding agent reads | — |

See [`INTEGRATIONS.md`](./INTEGRATIONS.md) for the full generated compatibility map (every one of the 73 core skills/workflows, listed with its `/name`, argument hint, and description): it's regenerated automatically, so it never drifts from the source.

## How it's built (single source of truth)

```
skills/*.md, workflows/*.md   (you edit these — 71 files, YAML frontmatter + instructions)
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

**Never hand-edit the generated directories** (`.agents/`, `.claude/`, `.opencode/`, `.cursor/`, `.codex/`, `.gemini/`, `.windsurf/`, `integrations/antigravity/`, `AGENTS.md`, `CLAUDE.md`, `INTEGRATIONS.md`, `.claude-plugin/`). Edit `skills/*.md` or `workflows/*.md`, then re-run:

```bash
python3 tools/generate_integrations.py
```

This keeps every tool-specific format (SKILL.md folders, slash-command wrappers, TOML commands, plugin manifests) perfectly in sync with the canonical content: there is exactly one place to update a skill's behavior.

Validate everything (canonical files + all generated output) with:

```bash
python3 skills/validate_skills.py
```

## Contents

| Path | Description |
|------|-------------|
| `AGENT.md` | Central orchestrator: core values, pre-action protocol, power modes, routing, safety engine, and more (canonical source) |
| `AGENTS.md` | Generated copy of `AGENT.md`, at the filename most agents (Codex, Gemini CLI, Cursor, Windsurf, OpenCode, Antigravity, Amp, Aider…) read natively |
| `CLAUDE.md` | Claude Code project memory: imports `AGENTS.md` and documents the installed skills |
| `skills/` | 60 specialized skill modules (canonical source, flat `.md` files with YAML frontmatter). A sibling folder named after a skill (for example `skills/docs-scaffold/`) holds companion files that the generator copies next to every generated `SKILL.md` |
| `workflows/` | 13 execution workflows (canonical source, same format as skills) |
| `.agents/skills/` | **Generated.** Every skill/workflow as an Agent-Skills-standard folder (`<name>/SKILL.md`): the universal format |
| `.claude/skills/` | **Generated.** Same content, at Claude Code's discovery path |
| `.opencode/skills/`, `.opencode/commands/` | **Generated.** OpenCode native skills + explicit slash commands |
| `.cursor/commands/`, `.cursor/rules/` | **Generated.** Cursor slash commands + always-on rule |
| `.codex/prompts/` | **Generated.** Codex CLI legacy custom prompts (guaranteed `/prompts:<name>`) |
| `.gemini/commands/` | **Generated.** TOML slash commands for Gemini CLI |
| `integrations/antigravity/prompt-orchestrator/` | **Generated.** Antigravity plugin manifest and all skills/workflows as native skill folders |
| `.windsurf/workflows/`, `.windsurf/rules/` | **Generated.** Windsurf Cascade workflows + always-on rule |
| `.claude-plugin/` | **Generated.** Claude Code plugin marketplace manifest (`/plugin marketplace add .` then `/plugin install prompt-orchestrator@prompt-orchestrator`) |
| `tools/generate_integrations.py` | The generator: re-run after editing any skill/workflow |
| `tools/registry.json` | **Generated.** Machine-readable list of every skill/workflow |
| `INTEGRATIONS.md` | **Generated.** Full human-readable compatibility map |
| `.kiro/` | Steering configuration for Kiro, and change specs in `.kiro/specs/` |
| `docs/` | This repository's own documentation, maintained with the `docs-scaffold` skill (embedded layout). Start at `docs/README.md` |
| `ignore/` | Git-ignored, local only: session journals and health reports written by `docs-scaffold` |
| `install/` | `spec.json` (the installer spec) and the generated installers `install.sh`, `install.ps1` and `install.cmd`, with menu and command line, for global and project installs |
| `packs/` | Opt-in packs (pack format v1): `claude-red-offense`, `logo-design`, `procable`. The default install skips them |
| `tools/generate_installers.py`, `tools/installer/` | The installer generator and the bash and PowerShell runtime it embeds |
| `tools/validate_packs.py` | The pack format validator |
| `harness/` | Optional layer: tiered agents, plan profiles (Claude Max, Pro, Codex Plus, API, free), power modes driven by live plan usage, frontier (Fable) gate, verify gate, `/autosetup`. See `docs/30-units/harness/README.md` |

## Install

`tools/generate_installers.py` builds three native installers from one spec (`install/spec.json`) and
the pack descriptions (`packs/*/pack.json`). The generated files carry a "Generated by" header; edit
the spec or a `pack.json` and run the generator again.

| Installer | Platform | Runs on |
|---|---|---|
| `install/install.sh` | Linux, macOS | bash 3.2 or later and standard POSIX tools |
| `install/install.ps1` | Windows | Windows PowerShell 5.1 or PowerShell 7 |
| `install/install.cmd` | Windows | cmd or a double-click; starts `install.ps1` |

The core and the packs install without Python. The harness part calls
`harness/scripts/install_harness.py` and needs Python 3.11 or later. On a machine without Python 3.11,
the installers skip the harness and say so.

### Menu (TUI)

Run the installer without arguments in a terminal. The menu has five screens (tools, core, harness,
packs and review). Each screen names what the next step installs and where. A number toggles an item.
Enter moves to the next screen.

```bash
bash install/install.sh
```

```powershell
powershell -ExecutionPolicy Bypass -File install\install.ps1
```

The menu also reads scripted input:

```bash
printf 'n\n1\n\n\nh\n\n\n\n' | bash install/install.sh tui
```

### Command line (CLI)

Core for three tools, without the harness, without the menu:

```bash
bash install/install.sh --tools claude,codex,opencode --no-harness --yes
```

Core, harness with a plan profile, and two packs:

```bash
bash install/install.sh --tools claude,codex --profile-claude claude-max --packs claude-red-offense:web,recon,logo-design --yes
```

Packs and sets:

```bash
bash install/install.sh packs list
bash install/install.sh packs install logo-design
bash install/install.sh packs remove claude-red-offense:web
bash install/install.sh packs remove logo-design
```

Status, dry run and uninstall:

```bash
bash install/install.sh status
bash install/install.sh --tools claude --packs logo-design --dry-run
bash install/install.sh uninstall --tools cursor
bash install/install.sh uninstall
```

Project installs (every tool inside one project, or Windsurf only):

```bash
bash install/install.sh project /path/to/your/project
bash install/install.sh windsurf /path/to/your/project
bash install/install.sh uninstall --project /path/to/your/project
```

On Windows, `install\install.cmd` and `install\install.ps1` take the same commands and flags:

```powershell
install\install.cmd --tools claude,codex --no-harness --yes
powershell -ExecutionPolicy Bypass -File install\install.ps1 packs list
```

`bash install/install.sh --help` lists every flag. For the flags `--tools`, `--core`, `--no-core`,
`--harness`, `--no-harness`, `--harness-only`, `--profile`, `--packs`, `--sets`, `--dry-run` and `--yes`,
the PowerShell installer uses the same names.

### Manifest, re-runs and removal

The installers record each file they write in `<data_home>/install-manifest.tsv`. On Linux and macOS,
`<data_home>` is `$XDG_DATA_HOME/prompt-orchestrator` or `~/.local/share/prompt-orchestrator`. On
Windows, `<data_home>` is `%LOCALAPPDATA%\prompt-orchestrator`.

- A second run with the same choices changes nothing and reports `no change`.
- `packs remove` and `uninstall` delete only files from the manifest. A file changed after install
  stays in place with a warning.
- Before the installer replaces a file it did not write, the installer moves that file to
  `<data_home>/backups/`. Uninstall moves the file back.
- `uninstall` also removes the folders the installer created once they are empty.

### Targets

| Tool | Core | Pack skills |
|---|---|---|
| Claude Code | `~/.claude/skills`, `~/.claude/AGENTS.md`, import block in `~/.claude/CLAUDE.md`, AI attribution off | `~/.claude/skills` |
| Codex | `~/.agents/skills`, `$CODEX_HOME/prompts`, `$CODEX_HOME/AGENTS.md` | `~/.agents/skills` |
| OpenCode | `~/.config/opencode/skills`, `commands`, `AGENTS.md` | `~/.config/opencode/skills` |
| Cursor | `~/.cursor/commands`, `~/.cursor/rules/prompt-orchestrator.mdc`, `~/.cursor/AGENTS.md` | `~/.cursor/skills` |
| Gemini CLI | `~/.gemini/commands`, `~/.agents/skills`, `~/.gemini/GEMINI.md` | `~/.agents/skills` |
| Antigravity | `~/.gemini/config/plugins/prompt-orchestrator` | `~/.gemini/config/skills` |
| OpenClaw | `~/.openclaw` (`AGENT.md`, `AGENTS.md`, `skills`, `workflows`, `agents-skills`) | `~/.openclaw/agents-skills` |
| GitHub Copilot, Kiro | harness agents only | none |

On Windows, `~` is `%USERPROFILE%`. OpenCode uses `%APPDATA%\opencode` when `%USERPROFILE%\.config`
does not exist.

### Packs

A pack is an opt-in skill set under `packs/<pack-id>/`. The default install skips packs. The user picks
packs per set. `packs/README.md` describes pack format v1, including the optional kind `release`.
`python3 tools/validate_packs.py` checks the format.

| Pack | Kind | Sets | Content |
|---|---|---|---|
| `claude-red-offense` | skills | 23 | 79 offensive security checklists from SnailSploit claude-red (MIT), one set per upstream category |
| `logo-design` | skills | 1 | Logo and brand-mark design with references, SVG scripts and the logo library catalog (MIT) |
| `procable` | release | 1 | The offline design skill, installed from a release pinned by digest (Apache-2.0) |
| `rea` | skills | 2 | The rea reverse engineering MCP server and its skill (MIT), with Frida as the add-on set `rea-frida` |

`bash install/install.sh packs list` prints each set with its skill count and description.

### Antigravity plugin

The Antigravity step copies `integrations/antigravity/prompt-orchestrator/` to
`~/.gemini/config/plugins/prompt-orchestrator/`. Before the copy, the installer checks that the package
skills match `.agents/skills/` byte for byte. An existing plugin that the installer did not write moves to
`~/.gemini/config/plugin-backups/prompt-orchestrator-<timestamp>`. Uninstall moves the plugin back.
Sibling plugins stay untouched.

These paths follow Google's [plugin documentation](https://antigravity.google/docs/plugins)
and [installation codelab](https://codelabs.developers.google.com/cloud-dev-plugin-agy?hl=en).
The [CLI reference](https://antigravity.google/docs/cli/plugins/) lists a different
legacy-looking path; verify CLI discovery on the installed version rather than
assuming parity. Workspace installations continue using `.agents/skills`.

After installing, open a **fresh session outside this repository**. In Settings →
Customizations, confirm the plugin skills are listed. Browse `/` and load both a
regular skill and `plan-execute`, checking that their source is the installed plugin.
A successful file copy alone does not prove runtime discovery.

### Optional harness

The harness adds model tiers and plan awareness on top of the core: an Opus 5.5 lead with Sonnet 5.5
workers and Haiku 5.5 light agents on Claude, power modes paced against the 5-hour and weekly limits,
Fable 5.1 only on your explicit command, and a test gate on finished work. The installers run it by
default when Python 3.11 exists. Add it later to an existing core install:

```bash
bash install/install.sh --harness-only --tools claude,codex --yes
```

Then run `/autosetup` in a Claude Code or Codex session to set your plan. `uninstall` removes the
harness through `install_harness.py uninstall`. Details: `docs/30-units/harness/README.md`.

### procable: offline design skill (pack)

[procable](https://github.com/ruskicoder/procable) is a cleaned fork of Impeccable: one design skill
(`/procable polish`, `critique`, `audit`, `a11y` for WCAG 2.2 AA, and more) with its design detector
hooks. It runs fully offline once installed: no telemetry, no update checks, no downloads, and every
network client in its engine refuses non-loopback hosts. prompt-orchestrator's communication rules
take precedence over its directives.

procable is the opt-in pack `procable`. The installer downloads the release pinned in
`packs/procable/procable.lock.json` once, checks `SHA256SUMS` against the pinned digest and each file
against `SHA256SUMS`, runs procable's own installer at user scope, and places the engine next to each
installed skill. For a machine without network, pass a folder that already holds the release:

```bash
bash install/install.sh packs install procable
bash install/install.sh packs install procable --procable-bundle /path/to/procable-release
bash install/install.sh packs remove procable
```

### rea: reverse engineering MCP server (pack)

[rea](https://github.com/morluto/rea) is an MCP server and CLI for reverse engineering native,
managed, JavaScript, firmware and browser targets. The opt-in pack `rea` has two sets:

- `rea` installs `rea-agents@6.10.1` into `<data_home>/packages/rea/` with
  `npm install --omit=optional --ignore-scripts`, checks its integrity against the pin, registers the
  `rea` server for Claude Code, Codex, Cursor, Gemini CLI and OpenCode, and copies the skill
  `reverse-engineer-anything`.
- `rea-frida` adds `frida@17.23.2` and the Frida Node binding. The installer checks the binding archive
  against the sha256 pinned per platform. Pinned platforms: `linux-x64`, `darwin-arm64`, `win32-x64`.
  The installer refuses other platforms. It also refuses `rea-frida` without `rea`, and the menu checks
  both together.

The server runs `node <data_home>/packages/rea/node_modules/rea-agents/scripts/rea.mjs mcp` with
`NO_UPDATE_NOTIFIER=1`. The installer sets no auto-approval, so each client asks before each tool call
that its approval rules cover. The pack needs Node.js (`^22.23.4`, `^24.22.1` or `>=26.12.1`) and npm.

```bash
bash install/install.sh packs install rea --tools claude,codex,cursor,gemini,opencode
bash install/install.sh packs install rea:rea,rea-frida
bash install/install.sh packs remove rea:rea-frida
bash install/install.sh packs remove rea
```

Removal deletes only the `rea` entry from each client config and leaves the rest of the file
byte-identical. `packs/README.md` describes the `npm` and `mcp` objects.

### No AI attribution

For Claude Code, the installers run the `no-ai-trailer` skill's `scripts/ensure_attribution_off.py`. The script turns commit and PR attribution off in Claude Code, VS Code and Cursor CLI, sets a global git `core.hooksPath` whose `commit-msg` strips AI trailers before handing over to each repository's own hooks, and registers a Claude Code SessionStart hook and PreToolUse guard. It runs again at every Claude Code session start. Uninstall removes the hook entries and the `core.hooksPath` setting. See `skills/no-ai-trailer.md` for the gaps it does not close.

### Checks

Run regression checks from `prompt-orchestrator/`:

```bash
python3 -B skills/validate_skills.py
python3 -B tools/validate_packs.py
python3 -B tools/generate_installers.py --check
python3 -B -m unittest discover -s install -p 'test_*.py' -v
python3 -B -m unittest discover -s tests/installers -t tests/installers -v
```

### Claude Code plugin marketplace (alternative to the Claude Code install)

```
/plugin marketplace add /path/to/prompt-orchestrator
/plugin install prompt-orchestrator@prompt-orchestrator
```

## Using the skills once installed

Every skill/workflow is invocable two ways, in every supported tool:

1. **Automatically**: the agent reads each skill's `description` at session start and loads the full instructions when your request matches it. No action needed.
2. **Explicitly**: type `/` followed by the skill or workflow name (e.g. `/agent-loop`, `/plan-execute`, `/security-audit-codebase`, `/docx`). Arguments after the name are passed straight through (`argument-hint` in each skill's frontmatter shows the expected shape).

See [`INTEGRATIONS.md`](./INTEGRATIONS.md) for the full list of all 71 `/name` commands with descriptions, or inspect `tools/registry.json` for the machine-readable version.

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

skills/ (52, canonical)              workflows/ (12, canonical)
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
├── human.md
├── prose-and-wording.md
├── no-ai-trailer.md
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
