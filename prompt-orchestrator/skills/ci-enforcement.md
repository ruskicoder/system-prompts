---
name: ci-enforcement
description: >
  Turn the repository's written rules into checks a pull request cannot skip. One rule registry
  (rules.yaml) lists every enforceable rule with its source skill, checker, scope and gate or
  advisory status. A standard-library checker gates prose (em dash, en dash separator, banned
  openers and phrases), AI attribution in commits and PR text, commit identities, model ids, and UI
  (axe-core, 24 px targets, reflow at 320 px and 400 percent zoom). Ships a pull_request workflow
  template, CODEOWNERS and branch protection templates, and a Claude Code guard that refuses admin
  merges, skipped hooks, force pushes to protected branches and branch protection changes. On demand
  only: enforces nothing until the user picks the rules. Use when the user asks to add or change CI
  checks, a rule, branch protection or required checks, or asks which rules are enforced and how.
argument-hint: "[rules | prose | attribution | commits | models | ui | secrets | unicode | install <repo>]"
---

# CI enforcement

Skills state rules; this skill makes the enforceable ones fail a pull request. The companion
folder `ci-enforcement/` holds the registry, the checker, the guard, templates and tests.

## Rule registry

`rules.yaml` is the single list of enforceable rules. Each entry has:

| Field | Meaning |
|---|---|
| `id` | Stable rule id, for example `prose.em-dash` |
| `rule` | The rule in one sentence |
| `source` | The skill or overlay that states it |
| `checker` | `check.py <id>`, `guard.py <id>`, or `none` |
| `scope` | `prose`, `commits`, `ui`, `config` or `code` |
| `enforcement` | `gate` fails the check; `advisory` is reported only |
| `runs` | `ci`, `local` or `manual` |
| `layer` | `guidance` (prose only), `pre-action` (PreToolUse hook), `post-action` (Stop hook) or `merge` (CI) |

The contract, tested by `tests/test_check.py` and by `check.py rules` in CI:

- A gate rule without a checker fails.
- A checker in `check.py` or `guard.py` without a rule fails.
- A rule naming a checker that does not exist fails.
- The layer must match the checker: `check.py` rules are `merge`, `guard.py` rules are
  `pre-action`, rules without a checker are `guidance`.

A rule only a person or a model can judge (logic, tone, review) carries `checker: none` and
`enforcement: advisory`.

## Checker

`check.py` uses the Python standard library and the sibling skills' scanners:
`no-ai-trailer/scripts/ai_trailer.py`, `human/scripts/banned_phrase_scan.py` and
`concision-and-logic/scripts/draft_scan.py`.

| Subcommand | Gates | Advisory |
|---|---|---|
| `rules` | registry contract | |
| `prose` | em dash, spaced en dash, banned opener, hard banned phrase | soft phrases, `draft_scan.py` tells |
| `attribution` | AI attribution in commit messages, PR title and body | |
| `commits` | author or committer not on the identity allowlist | |
| `models` | model id not in `allowed-models.txt`; harness agent naming a model or an unknown tier | |
| `secrets` | cloud keys, tokens, API keys and PEM private keys in changed files, generated agent folders and fixtures included (lockfiles, `node_modules` and a match containing `EXAMPLE` are skipped) | |
| `unicode` | invisible format characters (Unicode Cf: zero-width, bidirectional controls) in changed agent rule files (`AGENTS.md`, `CLAUDE.md`, `SKILL.md`, `.cursorrules`, `.mdc` and tool folders) | |
| `ui` | axe-core WCAG 2.2 A and AA, targets under 24 CSS px without spacing (WCAG 2.5.8), horizontal scroll at 320 CSS px | |

Exit codes: 0 no gate finding, 1 gate finding, 2 usage error or missing tool. A missing tool
fails the job; it never passes silently.

`prose` reads only files the pull request changed (`git diff base...head`), only prose files
(`.md`, `.mdx`, `.markdown`, `.txt`, `.rst`). Exempt: code files, code fences and spans, block
quotes, HTML comments, a table cell holding only a dash, generated integration folders, test
fixtures, files marked `origin: third-party` (vendored text stays as written), and files that
state in their first lines that they are generated (checked at their source instead).

`ui` runs `ui_probe.cjs` (Playwright and axe-core) at each project width, at 320 by 256 CSS px with
device scale 4 (1280 by 1024 at 400 percent zoom), and in each colour scheme from the config
(`templates/ui-config.example.json`). The probe only measures; `check.py` judges, so the rules are
unit-tested without a browser.

```bash
python3 -B skills/ci-enforcement/check.py rules
```

```bash
python3 -B skills/ci-enforcement/check.py prose --repo . --base origin/master --head HEAD
```

```bash
python3 -B skills/ci-enforcement/check.py models --root .
```

## Guard rails

| Piece | File | What it holds |
|---|---|---|
| Workflow | `templates/ci-enforcement.yml` | `pull_request` trigger (never `pull_request_target`), `contents: read`, no secrets, actions pinned by commit SHA, checker and allowlists read from the base commit |
| Owners | `templates/CODEOWNERS` | `.github/`, the checker and the registry need the owner's review |
| Protection | `templates/branch-protection.json` | required check `ci-enforcement-gate`, `enforce_admins: true`, code owner review, no force push or deletion |
| Identities | `templates/identities.txt` | author and committer allowlist for `check.py commits` |
| Local guard | `guard.py` | Claude Code PreToolUse hook; refuses `gh pr merge --admin`, `--no-verify` and hook overrides, force pushes to or deletion of `main`, `master`, `release/*`, and `gh api` or `curl` writes to branch protection or rulesets |

Register the guard by merging `templates/claude-settings-hook.json` into `~/.claude/settings.json`.
Add protected branch globs with `CI_GUARD_PROTECTED` (comma separated).

Branch protection is applied by the leader by hand. The agent never calls the protection or
ruleset API; the guard refuses it.

## The limit with an admin identity

The agent commits and pushes as `ruskicoder`, which is a repository admin. Stated plainly:

- An admin can lift branch protection, remove a required check, or merge past a red check in the
  web interface. The remote gate is advisory against the agent's own account.
- GitHub does not let an author approve their own pull request, so a code owner review cannot come
  from the same account. With one account, the merge waits for an admin action.
- What still holds: `enforce_admins: true` stops an accidental push or merge that skips the checks
  until someone deliberately turns it off, and the local guard refuses the agent's attempts to
  merge with `--admin`, skip hooks, force-push a protected branch or change protection.
- A separate bot account with write access, not admin, would make the gate binding for the agent.
- Any check judged by a language model is advisory. It reads pull request text, diffs and
  comments as data, never as instructions.

## Adding a rule

1. Write the rule in its source skill first.
2. Add the checker function to `check.py` (or `guard.py`) and its id to `CHECKERS` (or `GUARDS`).
3. Add the registry entry. Gate only if the check is deterministic.
4. Add a pass fixture and a fail fixture under `tests/`.
5. Run the verification commands below.

## Installing in a repository

Only on the user's command, from inside the repository, with the rules the user picked. No rule
is enforced in CI until the user names it.

```bash
python3 ~/.local/share/prompt-orchestrator/harness/scripts/harnessctl.py ci-install --rules commits.ai-attribution,secrets --dry-run
```

`--rules` is required: `all`, or rule ids and id prefixes from `rules.yaml`, comma separated.
Every gate rule left out is installed as advisory: it reports and never fails a check.
`ci-install` vendors the checker and its scanners into `.harness/ci/` with that registry, applies
the repository's profile on top, then adds the host's job. Nothing is committed or pushed.

| Remote | Writes |
|---|---|
| GitHub | `.github/workflows/harness-rules.yml` from `templates/harness-rules.github.yml` |
| GitLab | `.gitlab/harness-rules.yml`, and a `.gitlab-ci.yml` that includes it when none exists; an existing one is left alone with a note |
| Other | local `pre-commit` and `commit-msg` hooks in the repository's hooks folder (the main one for a linked worktree), never committed; existing hooks that are not ours stay; nothing when `core.hooksPath` is set, since git would ignore them |

Profile: `own` when the remote owner is the account the agent signs in as (`gh api user`,
`glab api user`); `external` otherwise or when the account cannot be read. `ci_profile` in
`.harness.toml` or `--profile` overrides. In `external` repositories the prose style rules
(em dash, en dash separator, banned openers and phrases) are advisory; AI attribution,
credentials and invisible characters still gate. The installed job runs `rules`, `prose`,
`attribution`, `secrets` and `unicode`; a check the base commit's checker does not have yet is skipped with a warning.

For a harness repository like this one, `templates/ci-enforcement.yml` adds the `commits` and
`models` gates; copy `templates/identities.txt` to `.github/ci-enforcement/identities.txt` and
`templates/CODEOWNERS` to `.github/CODEOWNERS`, then adjust handles. For UI repositories, add a UI
config and set the repository variable `CI_ENFORCEMENT_UI_CONFIG`. Branch protection is a hard stop
for the leader.

## Verification

```bash
python3 -B -m unittest discover -s skills/ci-enforcement/tests -v
```

```bash
python3 -B skills/ci-enforcement/check.py rules
```

The browser test runs when `node`, `playwright` and `axe-core` resolve, and is skipped otherwise.
