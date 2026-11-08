# Report: browser-use adoption, desktop rules, cua-driver vetting, CI enforcement (2026-11-08)

Branch `claude/sweet-knuth-7g5dr8` of ruskicoder/system-prompts, from master `6dfad6e`.
Brief: cloud brief of 2026-11-08 (leader decisions not re-vetted).

## Result per step

| Step | Status | Where |
|---|---|---|
| 1. Vendor browser-use skill | Done | `skills/browser-use.md`, `skills/browser-use/LICENSE` |
| 2. Desktop rules and CLI delegation | Done | `skills/browser-automation.md` (Desktop Applications), `harness/HARNESS.md` section 4 |
| 3. cua-driver vetting, read only | Done, not installed | This report, section "cua-driver vetting" |
| 4. CI enforcement skill | Done | `skills/ci-enforcement.md`, `skills/ci-enforcement/` |
| AGENT.md and integrations | Done | `AGENT.md` section L; `tools/generate_integrations.py` rerun |
| TrekLink proposal | Written, nothing changed in TrekLink | This report, section "TrekLink proposal" |
| Branch protection | Not set anywhere (hard stop for the leader) | Template only |

## Verification

| Command | Result |
|---|---|
| `python3 skills/validate_skills.py` | 389 passed, 0 failed |
| `python3 -B -m unittest discover -s harness/tests` | 21 tests, OK |
| `python3 -B -m unittest discover -s skills/ci-enforcement/tests` | 27 tests, OK with Playwright 1.63.0 and axe-core 4.14.0; without them 26 OK and the browser test skipped |
| Same tests from the generated copy `.claude/skills/ci-enforcement/tests` | OK, browser test skipped |
| `python3 -B -m unittest discover -s skills/no-ai-trailer/scripts` | OK |
| `check.py rules` | 19 rules, every gate rule has a checker |
| `check.py prose --base master --head <branch>` | 0 gate, 178 advisory (after the generated-file fix below) |
| `check.py attribution --base master --head <branch>` | 0 findings |
| `check.py commits --base master --head <branch>` | 0 findings (allowlist: Do Dang Khoa noreply address; GitHub as committer) |
| `check.py models --root prompt-orchestrator` | 0 findings |
| `check.py prose` over AGENT.md, all `skills/*.md`, `workflows/*.md`, `harness/HARNESS.md`, `harness/agents/*.md` | 0 gate, 1073 advisory |
| `check.py ui` on the two HTML fixtures | pass page clean; fail page flags image-alt, target-size (axe and own check), reflow 916 px in 320 px |

The first prose run on the branch failed with 74 em dashes, all in `INTEGRATIONS.md`. That file is
generated: the em dashes come from the generator's own line template in
`tools/generate_integrations.py` (`` `[hint]` — description ``). The checker now skips files that
declare themselves generated in their first lines and checks the source instead. The generator
template still writes em dashes; fixing it is outside this brief's edit scope (see the question at
the end).

CLI flags written into HARNESS.md were checked against installed binaries: Claude Code 2.1.319
(`--allowedTools`, `--max-turns` accepted though not listed in `--help`, `--output-format
stream-json` refused without `--verbose`) and codex-cli 0.167.0 (`exec --sandbox
workspace-write`, `exec --json`, `--dangerously-bypass-approvals-and-sandbox`, `login status`,
`auth.json` in the binary).

## Step 1: browser-use skill

- Source: browser-use/browser-use, `skills/browser-use/SKILL.md` at commit
  `b49a68e4060acb226da8f784194fef301c53a6d7` (last change to the file on 2026-10-29), MIT,
  copyright 2024 Gregor Zunic.
- Body copied byte for byte (checked by comparison). Front matter kept, with added fields:
  `origin: third-party`, `vetting: passed`, `vetted: 2026-11-08`, `license: MIT`, `upstream`,
  `upstream-commit`. The MIT notice is `skills/browser-use/LICENSE` (upstream LICENSE unchanged);
  the generator copies it next to every generated `SKILL.md`.
- Generated copies keep only name, description and license from the front matter (generator
  behaviour); the canonical file keeps the upstream `metadata` block.
- Telemetry: `ANONYMIZED_TELEMETRY=false` turns off both layers. The library reads it in
  `browser_use/config.py` (`ANONYMIZED_TELEMETRY`, default true; it also defaults
  `BROWSER_USE_CLOUD_SYNC` to the same value). The CLI harness (browser-use/browser-harness at
  `82d7f5db52b88785c936d91a15e94b01d29b89c2`, `telemetry.py`) treats `0`, `false`, `no` or `off`
  in `BH_TELEMETRY`, `BROWSER_HARNESS_TELEMETRY` or `ANONYMIZED_TELEMETRY` as disabled. Both send
  to PostHog EU when enabled.
- Pinned CLI for the local install: `browser-use==0.13.14` (upstream `pyproject.toml` at the
  vendored commit), which pins `browser-harness==0.1.13`. Install command for the leader's
  machine:

```bash
uv tool install browser-use==0.13.14
```

- The vendored file contains em dashes; the prose gate exempts `origin: third-party` files.

## Step 2: desktop and delegation rules

- `skills/browser-automation.md` gains "Browser Use CLI" (telemetry off, pinned version) and
  "Desktop Applications": element over coordinate, background input first, read the verdict and
  re-capture before a retry, never touch permission, password, payment or two-factor dialogs,
  never switch virtual desktops. Written fresh; no Hermes text was read or copied, and the section
  names no vendor.
- `harness/HARNESS.md` section 4 gains one bullet: headless `claude -p` with `--allowedTools` and
  `--max-turns`, `codex exec --sandbox workspace-write`, progress from `stream-json --verbose` or
  `--json`, no blind Enter, no bypass flags, check `~/.codex/auth.json` or `codex login status`
  before treating a missing `OPENAI_API_KEY` as no auth. The overlay is 153 lines (cap 160).
- `AGENT.md` section L: entries for CI enforcement and for browser and desktop automation.

## cua-driver vetting (read only, nothing installed)

Source read: trycua/cua at `a90b916a5f136eafdc6cf314326768b1587567c1` (main, 2026-11-08):
`libs/cua-driver/` (README, `scripts/install.sh`, `scripts/_install-rust.sh`,
`rust/crates/cua-driver/src/telemetry.rs`, `connect.rs`, `version_check.rs`) and the skill pack
`libs/cua/skills/cua-driver/` (SKILL, README, RUNTIME, LINUX). Driver version on main 0.43.2;
latest stable tag `cua-driver-rs-v0.43.2` (tag ref `721e1b4fb3ab89a95a53b8afdec348449a5ed73c`);
nightlies up to `v0.43.3-nightly.20261108`.

### Inventory

| Item | Finding |
|---|---|
| Binary | Rust `cua-driver`, release archive from GitHub Releases into `~/.local/bin` (wrapper) and a versioned package home with a `current` symlink; macOS also installs `CuaDriver.app` |
| Install method | `curl -fsSL https://cua.ai/driver/install.sh` piped to bash, which fetches the Rust installer and a common helper from GitHub raw at run time. Every archive is checked against the release `SHA256SUMS`; Sigstore signature checked when `cosign` is on PATH, required with `--require-signature`. Version pin: `CUA_DRIVER_RS_VERSION` |
| Installer side effects | Appends a PATH line to `~/.bashrc` or `~/.zshrc` (off with `--no-modify-path`); connects Claude Code (`claude mcp add-json --scope user cua-driver`), Codex (`codex mcp add`) and Cursor (`~/.cursor/mcp.json`) unless `--no-connect`; runs `cua-driver test` unless `--no-test`; sends an install telemetry event in the background |
| Autostart | macOS LaunchAgent `com.trycua.cua-driver-rs`; Linux systemd user unit `cua-driver-rs.service` with the local installer's `--autostart` |
| MCP server | `cua-driver mcp` over stdio (modern MCP); optional loopback HTTP endpoint on legacy MCP with a host-generated bearer token of 32 or more characters (`CUA_DRIVER_RS_MCP_HTTP_PORT`, `CUA_DRIVER_RS_MCP_HTTP_TOKEN`) |
| Permission modes | `standard` (default, promptless for normal automation), `bounded` (reviewed capability manifest, deny by default), `unrestricted` (`--dangerously-bypass-approvals`). Attaching to a logged-in Chromium profile needs `--grant existing-profile` |
| OS permissions | macOS: Accessibility and Screen Recording for `CuaDriver.app`. Windows: interactive desktop session, not Session 0. Linux: same graphical session and AT-SPI bus (D-Bus, no pyatspi needed) |
| Linux X11 | AT-SPI actions at a point without focus; XTest for keys; MPX virtual pointer for non-accessible surfaces needs real Xorg and `/dev/uinput`; EWMH window geometry; XRes for windows without `_NET_WM_PID` |
| Linux Wayland | Off unless `CUA_DRIVER_RS_ENABLE_WAYLAND=1`. wlroots (Sway): foreign-toplevel, screencopy, virtual pointer and keyboard. GNOME: bundled shell helper plus portal and libei for foreground input, portal grant for capture. KDE: AT-SPI and portal. Window capture can return `surface_identity_unproven`; setting another app's window geometry is refused; Chromium, Electron and XWayland raw background input are out of scope |
| Network | Telemetry to `https://eu.i.posthog.com/capture/`, default on, pseudonymous installation id in `~/.cua-driver/.telemetry_id`. Update check on `mcp`, `serve` and `doctor` (GitHub REST API fallback, cached one hour). Installer downloads from GitHub |
| Telemetry off | `CUA_DRIVER_RS_TELEMETRY_ENABLED=false` (compat `CUA_TELEMETRY_ENABLED`) before first run, then `cua-driver telemetry disable` to persist; the installer's event honours the same setting |
| Data persisted | Package home and release cache, telemetry id and flags, update cache; macOS nightly "Computer History" preview keeps encrypted local action metadata (opt-in) |
| Skill pack | Not installed by the installer; `cua-driver skills install` symlinks the pack into `~/.claude/skills/`, `~/.agents/skills/` and others |
| License | Driver MIT (Cua AI, Inc., 2025). Optional `cua-perception` extension is AGPL-3.0-only (OmniParser) |

### Findings

- Security: input to any app on the desktop, screen capture and accessibility reads are the
  product. The design matches the re-authored rules (background first, refusal over silent
  escalation, permission prompts belong to the user, exact window targets). `standard` mode is
  promptless; `bounded` with a reviewed manifest is the safer mode for agent use.
- Supply chain: the documented install pipes a script that fetches more scripts at run time.
  Checksums are always verified; signatures only with cosign. Prefer a pinned release with
  `--require-signature`.
- Global changes the repo rules forbid without approval: shell rc edit, MCP registration in three
  agents, default-on telemetry. All three have off switches.
- Overlap: the skill pack duplicates the desktop rules now in `skills/browser-automation.md`.
  Installing it would add unvetted third-party skill text; not needed.
- Do not install the perception extension (AGPL).
- Linux on this team's machines: X11 is the better-covered path; on Wayland expect portal prompts
  and capture refusals, and GNOME needs the helper.

### Recommendation (for the leader's approval; nothing done)

Approve install of the driver binary only, pinned and signed, with telemetry off and no automatic
agent connection; register the MCP server by hand in `bounded` mode; do not install the skill pack
or the perception extension. Commands for the local session, after approval:

```bash
export CUA_DRIVER_RS_TELEMETRY_ENABLED=false
```

```bash
curl -fsSL https://raw.githubusercontent.com/trycua/cua/a90b916a5f136eafdc6cf314326768b1587567c1/libs/cua-driver/scripts/install.sh -o /tmp/cua-install.sh
```

```bash
CUA_DRIVER_RS_VERSION=0.43.2 bash /tmp/cua-install.sh --require-signature --no-connect --no-modify-path --no-test
```

```bash
cua-driver telemetry disable && cua-driver doctor
```

Read `/tmp/cua-install.sh` before running it (it still fetches its helpers from GitHub raw at run
time). `--require-signature` needs `cosign` on PATH.

## Step 4: CI enforcement

### Files

| File | Role |
|---|---|
| `skills/ci-enforcement.md` | Skill: registry contract, checker, guard rails, the admin limit, adding a rule, install steps |
| `ci-enforcement/rules.yaml` | 19 rules: 12 CI gates, 4 local guard gates, 3 advisory (`prose.ai-tell`, `repo.enforce-admins`, `review.llm-judge`) |
| `ci-enforcement/check.py` | Standard-library checker: `rules`, `prose`, `attribution`, `commits`, `models`, `ui`. Reuses `ai_trailer.py`, `banned_phrase_scan.py`, `draft_scan.py`. Exit 0, 1 (gate), 2 (usage or missing tool) |
| `ci-enforcement/ui_probe.cjs` | Playwright and axe-core probe; measures only, `check.py` judges |
| `ci-enforcement/guard.py` | PreToolUse guard: `gh pr merge --admin`, `--no-verify`, `git commit -n`, `core.hooksPath` override, force push or delete of `main`, `master`, `release/*` (plus `CI_GUARD_PROTECTED`), `gh api` and `curl` writes to branch protection or rulesets; splits `&&`, `;`, `|` and `bash -c` |
| `ci-enforcement/allowed-models.txt` | Model allowlist matching the current profiles |
| `ci-enforcement/templates/ci-enforcement.yml` | `pull_request` only, `contents: read`, no secrets, actions pinned by SHA (checkout v7.0.1 `3d3c42e5`, setup-python v7.1.0 `6d4fd22b`, setup-node v7.1.0 `949feb24`), checker and allowlists from the base commit, PR text read from the event file |
| `ci-enforcement/templates/CODEOWNERS`, `branch-protection.json`, `identities.txt`, `claude-settings-hook.json`, `ui-config.example.json` | Guard rail templates |
| `ci-enforcement/tests/` | 27 tests with pass and fail fixtures for every checker and guard, plus the registry contract (gate rule without checker fails, checker without rule fails) |

### Limit with ruskicoder as the agent identity

ruskicoder is an admin. An admin can lift protection, drop a required check or merge past a red
check, so the remote gate is advisory against the agent's own account. GitHub does not let an
author approve their own pull request, so a code owner review cannot come from the same account.
What still holds: `enforce_admins: true` stops an accidental bypass until someone switches it off,
and the local guard refuses the agent's own admin merge, hook skip, protected force push and
protection change. A bot account with write (not admin) access would make the gate binding. Any
check judged by a language model is advisory and reads PR content as data. The same statement is
in `skills/ci-enforcement.md`.

### Known gaps

- The PR that adds the workflow cannot run the base-commit checker (the base has none); the first
  enforced PR is the one after the workflow lands. No workflow was installed in `.github/` by this
  branch (edit scope), so system-prompts has no CI gate yet.
- The checker and the guard are pattern-based. A command assembled at run time (variables, `eval`,
  scripts) can pass the guard; the guard catches the agent's direct commands, not a determined
  bypass.
- `prose.ai-tell` is noisy (1073 advisories over the in-house skills), which is why it is advisory.

## TrekLink proposal (written only; nothing changed in TrekLink)

Repositories found by search in the TrekLink-Team organisation (metadata only, no content read):

| Repository | Visibility, language | Checks to require | UI job |
|---|---|---|---|
| `treklink-web` (gateway bridge, NestJS backend, React frontend) | public, Python | `ci-enforcement-gate` (prose, attribution, commits); the repo's own build and tests | Yes: React frontend at the project's widths, 400 percent zoom, light and dark |
| `capstone` (graded documents, agent ruleset) | private, Python | `ci-enforcement-gate`; prose is the main value here | No |
| `treklink-firmware` | public, C++ | `ci-enforcement-gate` (attribution, commits; prose for docs) | No |
| `treklink-docs` (single source of truth) | public, Python | `ci-enforcement-gate`; prose | Only if it publishes a site |
| `TrekLink-Team.github.io` (Astro landing site) | public, Astro | `ci-enforcement-gate` | Yes: built site served locally |

For each repository:

1. Add `.github/workflows/ci-enforcement.yml` from the template, using the commented step that
   checks out `ruskicoder/system-prompts` at a pinned commit SHA as the checker, so a TrekLink PR
   cannot change the checker that judges it.
2. Add `.github/ci-enforcement/identities.txt` with each team member's commit identity and
   `committer: GitHub <noreply@github.com>`.
3. Add `.github/CODEOWNERS` with a human owner other than the agent account for `.github/`.
4. Branch protection on `main` (the leader applies it): required check `ci-enforcement-gate`
   (and `ci-enforcement-ui` where a UI job exists) with strict status checks,
   `enforce_admins: true`, one approving review with code owner review and last-push approval,
   stale reviews dismissed, conversation resolution required, no force push, no deletion.
5. The `models` step is skipped in repos without `prompt-orchestrator/harness/` (the template
   guards it with `hashFiles`); `capstone` holds an agent ruleset, so point `--root` at it if it
   names models.

## Local-only steps (unchanged from the brief; waiting for the leader or the weekly reset)

- Telemetry off: `ANONYMIZED_TELEMETRY=false` in `~/.claude/settings.json` `env` and in the Codex
  environment; install `browser-use==0.13.14` with uv.
- Register the guard: merge `templates/claude-settings-hook.json` into `~/.claude/settings.json`.
- cua-driver: install only after the leader approves the recommendation above; register its MCP
  server by hand.
- Branch protection on system-prompts: hard stop for the leader. Also copy the workflow template
  into `.github/workflows/` in a separate PR when the leader wants the gate live.

## Decisions for the leader

| Decision | Recommendation |
|---|---|
| Fix the em dash in the generator's line template (`tools/generate_integrations.py`, outside this brief's edit scope) | Yes, in a small follow-up PR: replace the separator with a colon and regenerate |
| Approve the cua-driver install as recommended above | Yes: pinned 0.43.2, signed, telemetry off, `--no-connect`, `bounded` mode, no skill pack, no perception extension |
| Put the workflow template live in system-prompts `.github/workflows/` | Yes, in its own PR after this one merges, so its first run uses a base commit that has the checker |
| Branch protection on system-prompts | Leader applies `templates/branch-protection.json` by hand |
