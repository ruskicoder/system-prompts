---
name: autosetup
description: Set the harness plan profile (Claude Max or Pro, Codex Plus, API, free) from the live account plan or the user's choice, write it to the user config, and re-render agents for that plan. Use when the user runs /autosetup, changes plan, or the harness tag says no profile is set.
argument-hint: "[profile name, for example claude-max]"
---

# Skill: Autosetup (harness plan profile)

Plans change, and no local file names the plan, so the harness never guesses it. This skill
sets it on request. Scripts live in the harness home: `~/.local/share/prompt-orchestrator/harness/scripts/`
on Linux and macOS, `%LOCALAPPDATA%\prompt-orchestrator\harness\scripts\` on Windows. Below,
`CTL` means `python3 <that folder>/harnessctl.py`.

## Steps

1. If the user gave a profile name (`/autosetup claude-max`), skip to step 4 with source `user`.
2. Detect the plan:
   - Claude: if a usage tool is available (in the Claude desktop app it is the session usage tool
     that reports `plan` and its windows), call it, then pass its JSON output to
     `CTL usage --provider claude --json '<output>'`. The command caches the 5-hour, weekly and
     weekly Fable windows and prints the suggested profile.
   - Codex: run `CTL codex-discover`. It reads the plan type and the model list from
     `codex app-server` and fills the `codex-plus` profile.
3. If no source answered, ask the user which plan they are on, with options from `CTL profiles`
   (`claude-max`, `claude-pro`, `codex-plus`, `api`, `free`), recommending the detected one if any.
4. Write it: `CTL set-profile --provider <claude|codex> --profile <name> --source <usage-tool|codex|user>`.
   This also re-renders the installed agents so their model fields match the plan.
5. Report the mode tag and tier mapping that `CTL show` prints, in two or three lines. For
   `codex-plus`, list the available models and ask whether the user wants different models per
   tier; if yes, edit the `[tiers]` table in the installed `profiles/codex-plus.toml` and run
   `set-profile` again.

## Rules

- Never call undocumented quota endpoints.
- For a one-session switch without writing to disk, tell the user to type `harness profile: <name>`.
- The frontier tier (Fable) still runs only on the user's explicit command, whatever the profile.
