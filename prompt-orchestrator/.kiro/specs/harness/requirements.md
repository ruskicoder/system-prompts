# Requirements Document

## Introduction

The harness is an optional layer for prompt-orchestrator that makes the orchestrator model-aware and plan-aware. The core orchestrator (`AGENT.md`) routes a task to a workflow and a power mode but never chooses a model, never reads plan quota, and lists subagent roles that have no definitions. The harness adds tiered agent definitions, per-plan profiles that map tiers to real models, power modes driven by live plan usage, a gated path to the frontier tier, test-gated acceptance, and an installer that lets users choose core only or core plus harness.

Claude Code on the Claude Max plan is the primary target: an Opus 5.5 main session, Sonnet 5.5 workers, Haiku 5.5 for light work, and Fable 5.1 only on the user's explicit command. Codex on ChatGPT Plus is second. OpenCode, Cursor, GitHub Copilot, Gemini CLI, Antigravity and Kiro receive agent definitions and the overlay with prompt-level gates where they lack hooks. OpenClaw receives documentation only. Windsurf is held until its product status is confirmed.

The harness saves tokens moderately without starving work: it spends unused quota when the user is behind pace, cuts fan-out when ahead of pace, and never lowers reasoning effort below `medium`. Decisions behind this document are recorded in the grill of 2026-10-30 (Q1 to Q28) and in decision records added by this work.

### Glossary

- **Core**: the existing prompt-orchestrator (`AGENT.md`, `skills/`, `workflows/`, generator, installers).
- **Harness**: everything under `prompt-orchestrator/harness/` plus the installer and generator changes in this spec.
- **Overlay**: `harness/HARNESS.md`, loaded after the core; it supersedes `AGENT.md` sections E, F and M while installed.
- **Tier**: an abstract capability level an agent declares: `frontier`, `lead`, `worker`, `light`, or `inherit`.
- **Profile**: a file under `harness/profiles/` mapping tiers to models and holding mode thresholds for one plan.
- **Window**: a plan usage window with a percent used and a reset time (5-hour, weekly, weekly Fable).
- **Pace**: percent of a window used minus percent of that window elapsed, in points.
- **Mode**: one of `Surplus`, `Normal`, `Conserve`, `Critical`, computed from pace and usage.
- **Lead**: the main session agent.
- **Fable command**: a user message that explicitly asks for the frontier tier ("spin up Fable", "use Fable", "Fable with credits").
- **Quota cache**: a local file the status line script writes with the latest window data.

## Requirements

### Requirement 1: Optional packaging as an overlay

**User Story:** As a user of prompt-orchestrator, I want the harness to be a separate, optional layer, so that I can install the original skills and workflows without it.

#### Acceptance Criteria

1. The harness SHALL live under `prompt-orchestrator/harness/` and SHALL NOT change the text of `AGENT.md`.
2. The overlay SHALL state that it supersedes `AGENT.md` sections E, F and M while installed and SHALL be loaded after the core on every target that receives it.
3. WHEN the harness is uninstalled THEN the target SHALL behave as a core-only install, with every file and setting the harness added removed or restored from backup.
4. The overlay SHALL stay at or under 160 lines, because it loads into every session.
5. Every harness file that agents read SHALL follow the always-on conventions (prose-and-wording, no-ai-trailer).

### Requirement 2: Installer selection and cross-platform TUI

**User Story:** As a user on Windows, macOS or Linux, I want an interactive installer that lets me pick tools and components, so that "install all" installs everything and I can still choose core only.

#### Acceptance Criteria

1. WHEN `install-all` runs without flags in an interactive terminal THEN the system SHALL show a menu of tools and components, with core and harness both selected by default.
2. WHEN `install-all` runs without flags in a non-interactive context THEN the system SHALL install core and harness for every global tool.
3. The installers SHALL accept `--core` (core only), `--with-harness` (core and harness), `--yes` (no menu, defaults) and `--tools <list>`; per-tool scripts SHALL accept `--core` and `--with-harness`; `install-harness [tool...]` SHALL add the harness to an existing core install.
4. The primary TUI SHALL be `install/install.py`, using only the Python standard library.
5. IF Python 3 is not available THEN the launcher SHALL run a native TUI: bash for Linux and macOS, PowerShell for Windows, with `.bat` launching PowerShell.
6. WHEN the native TUI installs the harness THEN it SHALL install the pre-rendered agents and the overlay, and SHALL state that status line, mode, Fable gate and verify features need Python 3.11 or later.
7. The menu SHALL list each global machine change (subagent model variable, status line, hooks, legacy Kiro rules file) as a separate item, selected by default.
8. Before changing a global file the installer SHALL write a timestamped backup, and `--uninstall-harness` SHALL restore it.
9. The installer SHALL NOT overwrite an agent file at a target that lacks the harness marker; it SHALL report the conflict and skip that file.

### Requirement 3: Tiered agent roster

**User Story:** As the lead agent, I want named agents with fixed tiers, tools and effort, so that I can offload work to the cheapest agent that can do it well.

#### Acceptance Criteria

1. The harness SHALL ship one canonical file per agent in `harness/agents/`, declaring `name`, `description`, `tier`, `effort`, `access` (`read` or `write`) and an instruction body.
2. The roster SHALL contain: `ingest`, `researcher`, `chore`, `test-runner`, `reviewer`, `refactor`, `critical-architect`, `critical-reviewer`, `convention-auditor`, `claim-verifier`, `debugger`, `security-auditor`, `commit-pr-writer`, `handoff-writer`, `session-logger`, `session-syncer`.
3. Tiers SHALL be: `frontier` for `critical-architect` and `critical-reviewer`; `light` for `test-runner`, `commit-pr-writer`, `handoff-writer`, `session-logger`, `session-syncer`; `worker` for all others.
4. Effort SHALL be `xhigh` for the two critical agents; `high` for `researcher`, `refactor`, `reviewer`, `convention-auditor`, `claim-verifier`, `debugger`; `medium` for all others. No agent SHALL use `low`.
5. No two agent descriptions SHALL claim the same job; the validator SHALL flag description overlap above a set threshold.
6. Read-only agents SHALL NOT have write or edit tools.
7. `refactor` SHALL run in an isolated worktree, commit only on its own branch, and SHALL NOT merge.
8. `claim-verifier` SHALL re-run the commands another agent claims passed, including at least one negative check, and SHALL flag every claim without matching tool output.
9. Agents that produce prose for people SHALL carry the prose-and-wording rules; `commit-pr-writer` output SHALL pass the no-ai-trailer guard.
10. Mechanical convention checks SHALL stay in hooks and scripts, not in agents.

### Requirement 4: Plan profiles and detection

**User Story:** As a user with a given plan, I want the harness to map tiers to the right models for my plan, so that it uses what I pay for without guessing model names.

#### Acceptance Criteria

1. The harness SHALL ship profiles `claude-max`, `claude-pro`, `codex-plus`, `api` and `free`.
2. `claude-max` SHALL map `frontier`, `lead`, `worker`, `light` to Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5 and SHALL record the Fable share of the weekly limit as 50%, editable.
3. `claude-pro` SHALL map `frontier` to Opus 5.5 at `xhigh`, and SHALL use Fable only when the user's command includes "Fable with credits".
4. `codex-plus` SHALL be filled at install from the live Codex model list when discovery succeeds; IF discovery fails THEN every tier SHALL use the user's configured model (`gpt-5.6-sol` on this machine) with effort `xhigh`, `xhigh`, `high`, `medium` for frontier, lead, worker, light.
5. `api` and `free` SHALL be templates where the user sets each tier's model, with OpenRouter free and Ollama examples; where a tier is unset the agent SHALL inherit the session model.
6. WHEN a profile has no Fable THEN `frontier` SHALL resolve to the strongest model in that profile at `xhigh`, and the lead SHALL say Fable is not used.
7. The active profile SHALL be chosen in this order: a session override, per-repo `.harness.toml`, user `~/.config/prompt-orchestrator/harness.toml`, then the fallback `claude-pro` (or `codex-plus` on Codex) with a tag asking the user to run `/autosetup`. Hooks SHALL NOT detect the plan on their own, because plans change and no local file names the plan.
8. The harness SHALL ship an `/autosetup` skill. WHEN the user runs it THEN the agent SHALL read the plan from the desktop usage tool when available and Codex `planType` from the app-server; IF neither is available THEN it SHALL ask the user to choose a profile with options; THEN it SHALL write `profile`, `plan_source` and `plan_set_at` to the user config and report the tier mapping.
9. WHEN the user runs `/autosetup <profile>` THEN the agent SHALL write that profile without detection.
10. WHEN a user prompt contains `harness profile: <name>` THEN the mode hook SHALL use that profile for the rest of the session only and SHALL NOT write it to disk.
11. WHEN `/autosetup` later reads a plan that differs from the stored profile, or the stored profile is older than 30 days, THEN the mode tag SHALL add one line suggesting `/autosetup`.
12. The installer TUI MAY ask for the plan and write the same config; WHEN it is skipped THEN the fallback in 4.7 SHALL apply.

### Requirement 5: Quota reading and power modes

**User Story:** As a Max subscriber, I want the harness to pace usage against my 5-hour and weekly limits, so that it uses my plan fully without running out early.

#### Acceptance Criteria

1. The harness status line SHALL write `rate_limits` from its input to the quota cache with a timestamp and SHALL display model, mode, 5-hour %, weekly % and context %.
2. IF a status line command already exists THEN the harness SHALL wrap it, show its output, and add its own segment.
3. The mode SHALL be `Critical` WHEN 5-hour or weekly usage is at or above 90%; otherwise `Conserve` WHEN weekly pace is above +10 points or 5-hour usage is at or above 75%; otherwise `Surplus` WHEN weekly pace is at or below -15 points; otherwise `Normal`. Thresholds SHALL come from the profile.
4. WHILE the mode is `Surplus` THEN the lead MAY widen fan-out; `Surplus` SHALL NOT trigger or suggest the frontier tier.
5. WHILE the mode is `Conserve` THEN the lead SHALL batch chores into single spawns and cap parallel subagents at the profile's conserve limit.
6. WHILE the mode is `Critical` THEN the lead SHALL NOT spawn new subagents except on a user command, and SHALL checkpoint and finish the current task.
7. WHEN a session starts, and WHEN a user prompt arrives and the mode differs from the last mode injected in that session, THEN a hook SHALL inject one line with profile, mode, 5-hour %, weekly % and Fable status.
8. IF the quota cache is missing or older than 15 minutes THEN the mode SHALL be `Normal` and the tag SHALL say the data is stale.
9. Power mode SHALL change tier choice and fan-out only; it SHALL NOT lower any agent's effort.
10. On Codex, the harness SHALL read `account/rateLimits/read` from the app-server, cached for at least 5 minutes; on other tools the mode SHALL be set by the user in config.
11. The harness SHALL NOT call undocumented quota endpoints.

### Requirement 6: Frontier tier (Fable) gate

**User Story:** As a user, I want Fable to run only when I command it, at full strength until the task is done, so that its tokens are never wasted on unrequested or unfinished work.

#### Acceptance Criteria

1. The lead SHALL spawn a frontier-tier agent, or pass `model: fable` on any spawn, only after a Fable command in the current session.
2. A PreToolUse hook SHALL block any Agent call that selects a critical agent or the `fable` model WHEN no Fable command was recorded for the session, and SHALL tell the lead to ask the user.
3. WHEN a task touches a path or keyword in the critical list THEN the lead SHALL suggest the frontier tier to the user in one line and SHALL NOT spawn it.
4. The critical list SHALL combine the harness default (infrastructure as code, CI/CD, auth and secrets, database migrations, payments, security configuration, release scripts) with the repo's `[critical]` entries.
5. WHEN a Fable command arrives THEN the lead SHALL write acceptance criteria before spawning, and the hook SHALL inject one line with mode, weekly %, and the Fable window or its estimate.
6. WHEN the mode is `Conserve` or `Critical`, or the Fable window is at or above 80%, THEN the lead SHALL warn in that line and SHALL still spawn.
7. A frontier agent SHALL run at `xhigh` to completion; the harness SHALL NOT downgrade its tier or effort during the run.
8. A frontier agent SHALL receive the smallest context that meets the criteria (paths, criteria, constraints), SHALL do only the critical reasoning, and SHALL end with a result checked against each criterion.
9. The Fable window SHALL come from the desktop usage tool when available; otherwise the harness SHALL show weekly % and a local count of frontier runs this week.
10. IF a frontier spawn fails on a usage or credits limit THEN the lead SHALL report it and SHALL NOT retry silently.

### Requirement 7: Delegation policy and token diet

**User Story:** As a user who pays per plan window, I want the lead to delegate only when delegation saves tokens or improves quality, so that subagent overhead does not waste the plan.

#### Acceptance Criteria

1. The overlay SHALL direct delegation for high-output reads (ingest, search, logs), independent work (review, test triage, audits) and long isolated work (refactor), and SHALL keep short sequential edits in the lead.
2. The lead SHALL batch related chores into one spawn and SHALL require subagents to return a summary within a stated size.
3. On Claude, the installer SHALL set `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` and SHALL NOT pin the main session model.
4. Agents that take everything from the delegation prompt SHALL set `omitClaudeMd`; agents that write prose for people SHALL preload `prose-and-wording`.
5. The installer item SHALL move the legacy Kiro lifecycle rules file `~/.claude/rules/instructions.instructions.md` to a backup when it is detected. `workflows/spec-driven.md` already contains every methodology section of that file; its only extra content is a communication block superseded by `skills/communication-tone.md`, so nothing is folded.

### Requirement 8: Test-gated acceptance

**User Story:** As a user, I want an agent's turn to end only when the repo's checks pass, so that I do not receive broken work.

#### Acceptance Criteria

1. WHEN a repo's `.harness.toml` sets `verify` THEN the Stop and SubagentStop hooks SHALL run it after a turn that changed files.
2. IF the command fails THEN the hook SHALL block the stop and return only the failing part of the output, at most 60 lines.
3. WHEN the hook has blocked 3 times in a row in a session THEN it SHALL allow the stop and tell the lead to report the failure.
4. WHEN `verify` is unset THEN the hook SHALL NOT block.
5. The verify command SHALL have a timeout from config, default 600 seconds.

### Requirement 9: Workflows

**User Story:** As a user, I want ready-made fan-out workflows that I start myself, so that large reviews and refactors run in parallel without the harness launching them on its own.

#### Acceptance Criteria

1. The harness SHALL ship Claude Code workflows `pr-sweep` and `refactor-fanout`.
2. `pr-sweep` SHALL review each listed PR or diff with `reviewer` in parallel and return one consolidated report.
3. `refactor-fanout` SHALL split a refactor across worktrees with `refactor`, run `claim-verifier` on each result, and stop before any merge.
4. The overlay SHALL forbid the lead from starting a workflow unless the user asks for it by name.
5. Merging refactor output SHALL be a hard stop that needs the user's approval.

### Requirement 10: Session journal archive

**User Story:** As a maintainer, I want old session journals archived with a digest, so that agents read less while the audit chain stays verifiable.

#### Acceptance Criteria

1. docs-scaffold SHALL add `session archive [--keep N]`, default N=1.
2. WHEN archive runs THEN every session file except the newest N SHALL move byte-for-byte to `<ignore dir>/sessions/history/`.
3. Archive SHALL write `<ignore dir>/sessions/history/digest.md` with one block per archived file: start goal, entry count, final head and last action.
4. WHEN chain verification runs after an archive THEN the system SHALL follow links into `history/` and report the chain intact.
5. `session-syncer` SHALL run `session archive` then `session sync`; `session-logger` SHALL run `session log`.

### Requirement 11: Multi-tool rendering

**User Story:** As a user of several coding agents, I want the same roster rendered for each tool's native format, so that tiers mean the same thing everywhere.

#### Acceptance Criteria

1. The generator SHALL render agents per tool and profile into `harness/dist/<tool>/<profile>/` from the canonical files: Claude Code Markdown, Codex TOML, OpenCode, Cursor, Copilot `.agent.md`, Gemini CLI, Antigravity and Kiro Markdown.
2. A renderer SHALL emit `effort` only where the target supports it (Claude `effort`, Codex `model_reasoning_effort`) and SHALL omit it elsewhere.
3. WHERE a tier has no model in the profile THEN the renderer SHALL emit the target's inherit form or omit the model.
4. Every rendered agent file SHALL carry a harness marker so installers can recognize and remove it.
5. Codex SHALL receive the overlay through its `AGENTS.md`, its agents in `~/.codex/agents/`, and a verify gate through Codex hooks.
6. Tools without hooks SHALL receive the overlay with prompt-level instructions for the verify and Fable rules, and the docs SHALL list each tool's gaps.
7. Windsurf SHALL NOT receive harness files until its status is confirmed; OpenClaw SHALL receive documentation only.

### Requirement 12: Validation, tests and documentation

**User Story:** As a maintainer, I want the harness checked like the rest of the repo, so that releases stay consistent.

#### Acceptance Criteria

1. `skills/validate_skills.py` SHALL validate harness agents (required fields, allowed tiers and efforts, no `low`, unique names, description overlap) and profiles (every tier mapped or explicitly inherit, thresholds present).
2. Harness scripts SHALL use only the Python standard library and SHALL require Python 3.11 or later.
3. Unit tests SHALL cover mode computation, quota cache staleness, the Fable gate, the verify gate, rendering per tool, installer flag parsing, settings merge and uninstall, and session archive chain verification.
4. Bash scripts SHALL pass `bash -n`; PowerShell scripts SHALL be reviewed by reading, since PowerShell is not available on the build machine, and the report SHALL say so.
5. The docs SHALL gain a `harness` unit, decision records for the overlay and the config format, and updates to the system flow, installers unit, catalog, INDEX, README, INTEGRATIONS.md and STATUS.md.
6. The release SHALL be v1.1.0; commit, push and release SHALL wait for the user's approval.
