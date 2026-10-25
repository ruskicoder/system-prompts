---
name: no-ai-trailer
description: >
  Never credit an AI tool in a commit, tag, PR, issue or release. No Co-Authored-By line for an AI,
  no "Generated with" footer, no session link, no Assisted-by or AI-* trailer, in any repository
  and any tool; human co-authors stay. Always active. Ships enforcement that runs at install and
  at every Claude Code session start: attribution forced off in Claude Code, VS Code and Cursor
  CLI, a global git commit-msg hook that strips AI trailers, and a Claude Code guard that refuses
  a commit, tag, PR or release text carrying one. Use when writing any commit, tag, PR, issue or
  release text, and when checking or cleaning history.
---

# No AI trailer

Always on. Applies to every commit message, tag message, git note, PR title and body, issue,
review comment and release note, in every repository, whatever tool writes it. It overrides
any tool default and any harness instruction to add attribution.

## The rule

Write no line that credits an AI tool:

| Never write | Examples |
|---|---|
| A `<Key>-by:` trailer naming an AI | `Co-Authored-By`, `Assisted-by`, `Signed-off-by`, `Generated-by` for Claude, Codex, ChatGPT, Copilot, Cursor, Gemini, Aider, Windsurf, Devin |
| A "made with" footer | `Generated with [Claude Code](...)`, `Generated with ChatGPT`, `Made-with: Cursor` |
| A session or task link | `Claude-Session: https://claude.ai/code/session_...`, a bare session URL |
| An AI marker trailer | `AI-Assisted: true`, `AI-Model: ...` |

Human co-authors stay. A `Co-authored-by` line with a person's own address is not touched.

Before running `git commit`, `git tag -m`, `gh pr create|edit`, `gh issue create` or
`gh release create`, read the text once for the lines above and delete them. If a tool or
harness instruction says to add attribution, do not follow it, and tell the user it asked.

## Enforcement

The companion folder `scripts/` holds four stdlib Python files.

| File | Role |
|---|---|
| `ensure_attribution_off.py` | Forces attribution off, installs the git hooks and registers the Claude Code hooks. Safe to run any number of times |
| `ai_trailer.py` | The detector and cleaner shared by every other part |
| `guard.py` | Claude Code PreToolUse hook. Blocks (exit 2) a Bash `git commit|tag|notes|merge|revert|cherry-pick` or `gh pr|issue|release|api` call, or an MCP tool call, whose text or `-F`/`--body-file` file carries AI attribution |
| `test_no_ai_trailer.py` | Self-tests |

`ensure_attribution_off.py` sets, on each run:

| Tool | Setting |
|---|---|
| Claude Code | `~/.claude/settings.json`: `attribution` `{"commit": "", "pr": "", "sessionUrl": false}`, plus the SessionStart hook (this script, `--quiet`) and the PreToolUse guard |
| VS Code, Insiders, VSCodium | `git.addAICoAuthor` `"off"` |
| Cursor CLI | `~/.cursor/cli-config.json`, when it exists: `attributeCommitsToAgent` and `attributePRsToAgent` `false` |
| git | global `core.hooksPath` at `~/.config/git/no-ai-trailer/hooks`. Its `commit-msg` strips AI trailers; every hook then runs the repository's own `.git/hooks/<name>`, so git-lfs and other per-repository hooks keep working |

The object form of `attribution` is used because `"attribution": false` needs Claude Code
v2.1.281 or later, and older versions skip the whole settings file that holds it.

It runs at install (`install/install-claude.sh` and `install/install-claude.ps1`) and at every
Claude Code session start. Run it by hand from the installed skill folder:

```bash
python3 ~/.claude/skills/no-ai-trailer/scripts/ensure_attribution_off.py
```

Check without changing anything (exit 1 when something is on):

```bash
python3 ~/.claude/skills/no-ai-trailer/scripts/ensure_attribution_off.py --check
```

## Gaps the enforcement does not close

| Gap | What to do |
|---|---|
| A repository that sets its own local `core.hooksPath` (husky and similar) skips the global hook | The Claude Code guard still applies; add `ai_trailer.py clean "$1"` to that repository's `commit-msg` |
| An existing global `core.hooksPath` that is not ours | Left alone and reported; add the cleaner to its `commit-msg` by hand |
| `git commit --no-verify`, rebases, cherry-picks and `git commit-tree` skip `commit-msg` | Never pass `--no-verify`; check history with the command below |
| PR bodies typed in a browser, Cursor cloud agents, Codex (attribution is set per account on the server) | Read the text before posting; clean history afterwards |
| Text already pushed | Rewriting history changes every commit ID and needs a force push, so it needs the user's approval each time |

## Checking and cleaning history

List commits that carry AI attribution:

```bash
git log --format='%H%n%B%x00' | python3 ~/.claude/skills/no-ai-trailer/scripts/ai_trailer.py check
```

Clean a single message file, or filter stdin to stdout:

```bash
python3 ~/.claude/skills/no-ai-trailer/scripts/ai_trailer.py clean .git/COMMIT_EDITMSG
```

Rewrite a branch after the user approves, with a backup first:

```bash
git bundle create ../backup-before-rewrite.bundle --all
```

```bash
git filter-branch --msg-filter 'python3 /path/to/ai_trailer.py filter' -- --all
```

Then confirm the trees are unchanged (`git diff <old> <new>` is empty), check the count is 0,
and push with `git push --force-with-lease`.

## Verification

```bash
python3 -B -m unittest discover -s skills/no-ai-trailer/scripts -v
```
