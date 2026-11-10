---
id: decisions.canary-removal
type: adr
status: approved
owner: Do Dang Khoa
summary: "Remove the canary (line, probe, markers, reply and subagent hooks): the harness hooks return to 1.7.0. CI enforcement stays as an on-demand skill that gates only the rules the user picks."
superseded_by: none
---

# Decision

Approved by the leader on 2026-11-11. Supersedes sections 1 and 2.1 of decision 0005 (the canary). The CI part
of 0005 stays, changed as below.

## Context

The leader ran the canary in the TrekLink orchestrator session of 2026-11-10 night (Claude Code session
`415aaa12`, 15 replies with a canary line). Frame, letter and mode bar were right on every reply. The hook
raised 6 alarms:

| Alarm | Count | Cause |
|---|---|---|
| probe 7 answered wrong | 3 | marker 7 sits in `prose-and-wording`, which that session never loaded (0 occurrences in the transcript); the probe could not be answered |
| probe 4 and probe 6 answered wrong | 2 | the marker was in context; the reply guessed `(`; the work of those turns was not affected |
| no canary line, no reply contract | 1 | first reply of the session; corrected from the next reply |

Every alarm advised rotating a session that kept delivering. The line and the probe also cost tokens on every
turn, and the probe text adds to the context the canary was meant to protect.

## Decision

1. Remove the canary: `canary_gate.py`, `canary.toml`, the eight markers, the canary rule in communication-tone
   section 1, `harnessctl.py canary`, the status line segment, and the reply and subagent hooks. The installer
   registers the 1.7.0 hooks only and deletes the stale `canary.toml` and `canary_gate.py` from the installed
   harness home.
2. Keep no replacement reply hook. Rules are judged from results (diffs, PR text, CI on request), not from a
   token the model writes for a hook.
3. CI enforcement is a skill loaded on demand. `harnessctl.py ci-install` requires `--rules` (`all`, or rule ids
   and prefixes); every gate rule not named is installed as advisory. AGENT.md section L no longer makes every
   new rule need a registry entry and checker.
4. This repository's own workflow (`.github/workflows/prompt-orchestrator-ci.yml`) is unchanged.

## Consequences

- Drift is no longer signalled per reply. Context rotation is the user's call, read from the status line `ctx`.
- Reinstalling the harness removes the canary hooks from Claude Code and Codex settings.
