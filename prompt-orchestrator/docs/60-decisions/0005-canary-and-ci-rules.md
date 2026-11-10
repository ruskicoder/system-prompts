---
id: decisions.canary-and-ci-rules
type: adr
status: draft
owner: Do Dang Khoa
summary: "Proposed: a braille-frame canary with reply letter, bracket probe and context shade, direct reply checks and rotation thresholds, core rules installed as CI checks on GitHub and GitLab on command, and vetted checks from the HyperDev bundle."
superseded_by: none
---

# Decision

Status: sections 1 and 2 approved by the leader on 2026-11-10 and implemented on branch
`claude/feat-canary-ci-rules-3e49ca`; section 3 is deferred to a later pull request by the leader's decision of the same day. **Agreed** marks the leader's
decisions from the grill rounds of 2026-11-10.

## Context

- Long sessions drift from the system prompt. Adherence falls as instruction count and context length grow
  (IFScale, arXiv 2507.11538; Chroma "Context Rot", 2025). Retrieval is weakest in the middle of a long context and
  strongest at its start and end ("Lost in the Middle", arXiv 2307.03172).
- A practitioner "canary" is a trivial rule obeyed in every reply. Known limits: it proves only that one rule
  survived, and the model can copy it from its own earlier replies.
- Claude Code and Codex Stop and SubagentStop hooks receive `last_assistant_message`. A PostToolUse hook on the
  `Agent` tool can add context to the parent session after a subagent returns. UserPromptSubmit can add context on
  every prompt in both tools (code.claude.com/docs/en/hooks; Codex hook guides for v0.150 and later).
- Claude Code strips block-level HTML comments from CLAUDE.md on load, so markers inside comments never reach the
  model.
- Rules that must hold belong in deterministic checks; prose is guidance (OpenAI "Harness engineering", 2026).
  This repository runs no rule checks on pull requests today.
- PR #2 (open, merges cleanly) adds a rule registry `rules.yaml`, `check.py`, `guard.py` and a workflow template.
- The HyperDev bundle (`ignore/vetting/hyprDev-vetted-v0.4.zip`) holds docs and one skill, no licence. Its ideas are
  re-authored below; no text or code is copied. The unredacted guide names `iced-tea-relax/hyper-pack`; on
  2026-11-10 that repo and the guessed sibling repos return 404 to the leader's account (private or absent). The
  organization's two public repos are MIT forks of `can1357/oh-my-pi` and `stablyai/orca`. The author's public
  `baka3k/agent-skills` (commit `ced7e09`) holds the HyperDev skill kit: no LICENSE file despite an MIT claim in its
  README, ClaudeKit-like naming of unproven origin, installers that overwrite `~/.cursorrules`. The author granted MIT use by
  message on 2026-11-09. Its debugging references copy obra/superpowers (MIT). On 2026-11-10 the four
  re-author candidates were A/B tested against our skills (48 runs): no quality gain at 20 to 68 percent more cost
  per run, so the leader rejected the whole kit.

## Decision

### 1. Canary

**Agreed:** glyph layout, no emoji, rule home in `skills/communication-tone.md` section 1 with a pointer from AGENTS.md
section K, rule in every generated integration with hook checks in Claude Code and Codex, never block.

Line 1 of every main-session reply, alone on its line. The layout follows the Claude Code working line (a moving
frame, then state), with frames the user can order by eye.

```
⣄ ▅ ▒ [c]
```

| Position | Glyphs | Meaning | Who checks |
|---|---|---|---|
| 1 frame | `⡀` `⣀` `⣄` `⣤` `⣦` `⣶` `⣷` `⣿`, then `⡀` again | Braille cell filling like water: bottom row first, left then right, one dot per reply; the full cell marks the wrap | You, by dot count; the hook, exactly the next frame; any frame after startup, resume, clear or compaction |
| 2 mode bar | `▇` `▅` `▃` `▁` | Surplus, Normal, Conserve, Critical | The hook: must equal the mode the harness computed |
| 3 context shade | `○` `░` `▒` `▓` `█` | Context fill: under 60, 60 to 64, 65 to 69, 70 to 74, 75 percent and over | The hook: must equal the value it injected this turn |
| 4 letter | `a` to `z`, then `a` again | Reply order | You, at a glance: a jump from `c` to `f` shows |
| 4 bracket | `()` `[]` `{}` `<>` around the letter | This turn's probe answer from the rule files | The hook: must match the marker it asked for |

Every glyph above was checked against Unicode `emoji-data.txt` and has no Emoji property. Claude Code's own spinner
frames were dropped because they are hard to order by eye, and its `✳` frame carries the Emoji property.

**Agreed, probe.** Eight visible marker lines sit spread across the core files: the start, 25, 50 and 75 percent and
the end of AGENTS.md, plus one each in communication-tone, prose-and-wording and HARNESS.md. Each reads like
`> canary marker 3: [`. Markers must be visible text, since Claude Code strips HTML comments. The rule names no marker
values. Each prompt the hook injects `canary probe 3, ctx 66`, and the reply must show `▒` and a `[ ]` bracket. The
bracket changes every reply but follows no cycle: a predictable bracket could be produced without reading the rules.
A wrong bracket names the region of the rules that dropped out. A random guess passes one time in four, so a dead
region escapes three turns in a row about 1.6 percent of the time. `harnessctl.py canary rotate` re-draws the
marker shapes.

**Agreed, direct reply checks.** The Stop hook also scans the reply for real breaks: em dash in prose, en dash as a
separator, banned openers, emoji, and a missing Asked, Done, State or Next part after work. Breaks are reported with
the canary result.

**Agreed, context pressure.** The status line caches the context percentage it already reads.

| Context fill | Shade | Hook action |
|---|---|---|
| under 60 percent | `○` | None |
| 60 to 64 | `░` | Note: rotation is near |
| 65 to 69 | `▒` | Strongly suggest rotating; continue while the task is unfinished |
| 70 to 74 | `▓` | Rotate once the current task is done |
| 75 and over | `█` | Rotation is mandatory. A large task finishes its current step cleanly, writes a handoff, then rotates without waiting |

Rotation means a handoff note and a fresh session: `hand_off_to_session` in the desktop app, the handoff prompt for a
new CLI session elsewhere. Long sessions rot context even below these levels, so shorter sessions are the default
advice.

**Agreed, on a miss:** the hook reports to the user in one `systemMessage` naming the failed glyph or rule and
suggests rotating the session. No re-injection, no block, no rewrite. The CLI status line shows canary health, for
example `canary ok` or `canary 2 miss`.

**Verified, subagents see the rules:** on 2026-11-10 a Claude Code 2.1.317 subagent reported a marker held only in
the project's `CLAUDE.md`, so the subagent probe can be answered.

**Agreed, subagents:** a subagent report starts with its probe answer only, the bracket around `a`, for example `[a]`. SubagentStart injects
the probe; a SubagentStop hook checks the report; a PostToolUse hook on the `Agent` tool tells the orchestrator, which
ends that subagent and starts a fresh one.

**Agreed, off switch:** on by default. `canary off` in a prompt turns it off for that session.
`canary = false` turns it off for a project in `.harness.toml`, or globally in the harness user config.

A live canary means the session is probably on track. It never counts as proof that a rule was followed.

### 2. Core rules as CI checks

**Agreed:** fold PR #2 into this work as one PR; GitHub Actions and GitLab CI; `ci-install` runs only on the user's
command; files are written and left uncommitted; gating splits by rule type; "own" means the remote owner is the
agent's own account, anything else is external, and `ci_profile` in `.harness.toml` overrides.

Every rule in the registry gets a `layer`:

| Layer | Enforced by | Example |
|---|---|---|
| guidance | Prose only | Tone, depth of answers |
| pre-action | PreToolUse hook | No `--no-verify`, no admin merge |
| post-action | Stop hook | Canary, direct reply checks, verify command |
| merge | CI job | No em dash in changed docs, no AI attribution in commits |

Install flow, when the user commands `harnessctl.py ci-install` in a repo:

1. Detect the host from the remote: GitHub writes `.github/workflows/harness-rules.yml`; GitLab writes
   `.gitlab/harness-rules.yml` and a `.gitlab-ci.yml` that includes it when none exists. An existing
   `.gitlab-ci.yml` is left alone with a note naming the include line.
2. Vendor the checker, its three scanners and a profiled `rules.yaml` into `.harness/ci/` (the scanners keep their
   folder layout so `check.py` finds them). Commit and push stay hard stops; the command lists the files it wrote.
3. Repos on any other host get local `pre-commit` and `commit-msg` hooks in `.git/hooks` (never committed) running the
   same `check.py`. Nothing CI-related is written.

Ownership: the owner in the remote URL is compared with the account the agent authenticates as (`gh api user` or
`glab api user`). Rule sources merge in order: global core rules shipped with the harness, then project rules from
`.harness.toml [rules]`.

| Rule type | Own repos | External repos |
|---|---|---|
| AI attribution, secrets, invisible Unicode in rule files | gate | gate |

The secrets (`secrets.pattern`) and invisible character (`unicode.invisible`) checkers were added to `check.py`
for these gates, each with pass and fail tests.
| Prose style (em dash, banned openers) | gate | advisory |

- Templates: GitHub uses the `pull_request` trigger only, read-only permissions, no secrets, actions pinned by SHA;
  GitLab uses merge request pipelines with no protected variables.
- Every finding prints the rule id, `file:line` and the fix, so the agent can act on CI output directly.
- CI checks code quality and the merge-layer rules only. The canary is an in-session signal for the user and the
  lead's subagent checks; CI does not check it. `harnessctl.py canary check` verifies the marker lines locally.
- With the leader's account as the AI identity, an admin can lift branch protection, so the remote gate stays
  advisory against that account. The local guard still holds.

### 3. Checks re-authored from the HyperDev bundle

**Agreed:** vet all six with pros, cons and alternatives; the leader decides after comparing. Research 2026-11-10;
the leader's selection is open.

| ID | Catches | Pros | Cons | Proposed verdict |
|---|---|---|---|---|
| H1 script decides done | Unverified "done" claims | `verify_gate.py` already does it; its tree fingerprint rejects stale passes | A repo without `verify` passes silently; covers only what `verify` runs | Keep with changes |
| H2 repeat counter | Same-command retry loops | PostToolUse receives `tool_input` and `tool_response` in both tools; cheap | A low threshold flags legitimate retries; state must persist between hook runs | Keep with changes, modelled on the OpenHands stuck detector |
| H3 machine gates | Rules claimed as enforced but not wired | One `layer` field, testable | A per-workflow gate list checks prose structure and breaks on edits | Keep `layer` with a wiring test, drop the gate list |
| H4 disposition ledger | Findings dropped without a decision | Fixed vocabulary, checkable | A schema proves form, not that "accepted" was fixed | Keep with changes, SARIF vocabulary plus required evidence |
| H5 plan ID cross-check | A requirement with no test | Deterministic | Four ID prefixes are heavy; an empty TEST satisfies it | Defer; later a REQ to TEST lint only |
| H6 diff against plan | Edits outside the planned files | Catches Bash writes that path hooks miss | False alarms on lockfiles, generated files and fair discoveries | Keep with changes, warn only |

Changes behind the verdicts:

- **H1.** Warn when a repo has no `verify` command. Make required CI status checks the merge authority. Keep
  `claim-verifier` for claims no script covers.
- **H2.** Key the counter on a hash of command, output and tree fingerprint, so "no change" is measured. Threshold 3
  to 4 repeats, plus alternating pairs. The OpenHands stuck detector uses 4 identical action and observation pairs,
  3 repeated errors and 6 alternating cycles (docs.openhands.dev/sdk/guides/agent-stuck-detector). Warn once per
  streak through `additionalContext`.
- **H3.** A test maps every `pre-action` rule to a registered PreToolUse matcher, every `post-action` rule to a Stop
  hook and every `merge` rule to a CI job. Codex documents tool hooks as a guardrail, not a complete enforcement
  boundary, so an unverified `layer` would overclaim.
- **H4.** Use SARIF 2.1.0 suppression statuses (`accepted`, `underReview`, `rejected`) plus `justification`. Map
  `unresolved` to `underReview` and keep `partially_accepted` as an extension. Every disposition except
  `underReview` needs evidence (a commit SHA or `file:line`) that the script resolves.
- **H5.** Spec Kit's `/speckit.analyze` checks coverage as an LLM prompt, not a script. A regex lint proves only
  that an ID exists. Revisit after H3 and H6.
- **H6.** Compute the changed set with the `git status` code from `verify_gate.py`. Match against `FILE-` globs with
  an always-allowed set (lockfiles, tests, changelog). Warn and ask the agent to justify or amend the plan.

## Alternatives

- Fixed token canary (`[po]`): rejected, copied from history in long sessions.
- Claude spinner frames with a workflow verb (`✻ Diagnosing…`): dropped, the frames are hard to order by eye and
  the verb adds length.
- A bracket that cycles in a fixed order: rejected, the model could predict it without reading the rules.
- Block and rewrite on a miss: rejected, hides the drift the canary exists to show.
- Re-injecting rules on a miss: rejected by the leader; rotating the session clears the drift instead of feeding it.
- Emoji canary: rejected, `communication-tone.md` section 10 bans emoji, and Codex on Windows mishandles non-ASCII
  Stop hook input (openai/codex#23784).
- Markers in HTML comments: rejected, Claude Code strips them before the model sees the file.
- LLM-judged rule review in CI: advisory at most; it treats PR content as data and cannot gate.
- Installing the HyperDev stack: rejected for now, no licence, plain HTTP MCP without auth, needs Neo4j, Qdrant and
  three models.

## Consequences

One PR that folds in PR #2:

1. Done: `.github/workflows/prompt-orchestrator-ci.yml` runs the generator drift check, `validate_skills.py`, every
   unit test suite, and the rule gate (registry, prose, attribution, secrets, invisible characters, identities,
   model ids) on pull requests.
2. Done: the canary rule in communication-tone, eight markers from `harness/canary.toml`, `canary_gate.py`, the
   subagent path, the off switch, the status line health segment, `harnessctl.py canary`, and tests.
3. Done: `harnessctl.py ci-install` for GitHub and GitLab, ownership detection, the local git hook fallback, and tests.
4. Deferred: the HyperDev checks, chosen in a later pull request. The harness is reinstalled on the leader's
   machine after this change merges.
