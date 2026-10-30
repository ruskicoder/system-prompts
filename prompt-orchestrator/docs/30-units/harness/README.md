---
id: units.harness
type: section
status: draft
owner: Do Dang Khoa
summary: "Optional model-tier and plan-aware layer: tiered agents, plan profiles, power modes, frontier gate, verify gate."
kind: module
sources: [harness/**, install/install.py, install/install-tui.*, install/install-harness.*]
verified: {commit: eefac58, date: 2026-10-30}
---

# harness

## Purpose
Make the orchestrator model-aware and plan-aware without changing the core. The harness picks who
does a task (lead or a named agent), on which model (tier through the plan profile), how widely to
fan out (power mode from live plan usage), and when work is accepted (verify gate). It installs as
an optional layer; a core-only install behaves as before.

## Responsibilities
- `harness/HARNESS.md`: overlay loaded after `AGENTS.md`; supersedes core sections E, F and M (decision 0002).
- `harness/agents/*.md`: 16 canonical agents. Each declares a tier (`frontier`, `lead`, `worker`, `light`), an effort (`medium`, `high`, `xhigh`; never `low`) and read or write access.
- `harness/profiles/*.toml`: `claude-max`, `claude-pro`, `codex-plus`, `api`, `free` map tiers to models and hold mode thresholds and fan-out caps (decision 0003).
- `harness/scripts/`: standard-library Python 3.11+ runtime.
  - `statusline.py` caches Claude `rate_limits` and shows model, mode, 5-hour %, weekly % and context %.
  - `mode_hook.py` prints the mode tag at session start and when the mode changes, records a Fable command, and handles `harness profile: <name>`.
  - `fable_gate.py` denies frontier spawns without the user's command in the session, and Fable on profiles without included Fable unless the user said "Fable with credits".
  - `verify_gate.py` runs the repo's `verify` command on Stop and SubagentStop, blocks on failure, gives up after 3 blocks.
  - `codex_bridge.py` reads Codex plan usage and models from `codex app-server` (`account/rateLimits/read`, `model/list`).
  - `harnessctl.py` backs `/autosetup`: set the profile, cache usage-tool data, discover Codex models, re-render agents.
  - `render.py` renders agents per tool; `install_harness.py` installs, records a manifest and uninstalls.
- `harness/skills/autosetup.md`: the `/autosetup` skill. Plans change and no local file names the plan, so hooks never detect it.
- `harness/workflows/`: `pr-sweep` and `refactor-fanout`, started only when the user asks.
- `harness/dist/`: generated per tool and profile by `tools/generate_integrations.py`, used by the native installers.

## Modes

| Mode | Condition | Effect |
|---|---|---|
| Critical | 5-hour or weekly use at 90% or more | no new spawns unless the user asks |
| Conserve | weekly pace above +10 points, or 5-hour use at 75% or more | batch chores, fan-out cap 2 |
| Surplus | weekly pace at or below -15 points | fan-out up to the profile cap |
| Normal | otherwise, or quota data stale for 15 minutes | standard delegation |

Pace is percent used minus percent of the window elapsed. Mode never changes effort and never
triggers the frontier tier.

## Per-tool support

| Tool | Agents | Overlay | Mode tag | Frontier gate | Verify gate | Quota source |
|---|---|---|---|---|---|---|
| Claude Code | yes, per profile | `CLAUDE.md` import | hook | hook | hook | status line, desktop usage tool via `/autosetup` |
| Codex | yes, per profile | `AGENTS.md` block | hook | prompt only | hook | `codex app-server` |
| OpenCode | yes, Claude model ids | `AGENTS.md` block | none | prompt only | none | none |
| Cursor | yes, inherit; skipped when Claude agents exist (Cursor also loads `~/.claude/agents`) | rule file | none | prompt only | none | none |
| GitHub Copilot | yes, inherit; CLI loading of user agents has a reported bug (github/copilot-cli#452) | none documented | none | none | none | none |
| Gemini CLI | yes, inherit; needs `experimental.enableAgents` | `GEMINI.md` block | none | prompt only | none | none |
| Antigravity | yes, inherit | none | none | none | none | none |
| Kiro | yes, inherit | steering file | none | prompt only | none | none |
| OpenClaw | no subagent mechanism | none | none | none | none | none |
| Windsurf | held until its product status is confirmed | none | none | none | none | none |

## Code
`harness/`, `install/install.py`, `install/install-tui.sh`, `install/install-tui.ps1`, `install/install-harness.*`
