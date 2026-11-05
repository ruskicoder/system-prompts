# ui-ux-philosophy evals

`evals.json` holds two behaviour cases.

1. A review of `files/devices/`: a Devices list screen (`DevicesPage.tsx`, `devices.css`) with 14
   planted violations (hover-only row actions, an action that shifts between rows, tabs ordered
   by clicks, a placeholder as label, a colour-only clickable status, a routine "Are you sure?",
   a permanent delete without undo, an "Error 500" toast, "No devices" while loading, stacked
   banners, two primary buttons, a div as sort header, a scroll jump after save) and two correct
   components that `notes.md` describes, which must not be reported.
2. Four product-owner requests that each collide with a rule (hide unavailable actions, tabs
   ordered by use, confirm every save, 16 px icon buttons).

Run each case with `claude -p` in a scratch copy of `files/devices/` (case 1) or an empty folder
(case 2), tools limited to Read, Glob and Grep, user settings off (`--setting-sources project`),
with the skill under test saved as `INSTRUCTIONS.md` and the prompt prefixed with "Read
INSTRUCTIONS.md in this folder first and follow it." Run the baseline without `INSTRUCTIONS.md`
and without the prefix. Grade each run against `expectations`; a partial counts as a fail. Run
one case at a time and only with 3 GB of memory available.

`trigger.json` holds queries for `skills/skill-creator/scripts/run_eval.py`.

## Results (2026-11-05, Sonnet, user settings off)

| Run set | Case 1 (15) | Case 2 (4) |
|---|---|---|
| Baseline, no skill, 3 runs | 14, 13, 14 | 3, 3, 3 |
| Skill, round 1 | 14, 15, 14 | 4, 4, 4 |
| Skill, final (after two fixes) | 15, 15, 15 | 4, 4, 4 (round 2) |

Round 1 missed the confirmation or undo for a status transition (now rule "The status as the
state control" 4) and once reported a component the fixture marks as reviewed (now the review
line in the skill's opening). Trigger: `trigger.json` with only this skill installed and user
settings off, 3 runs per query: 10 of 10 positives triggered 3 of 3, 8 of 8 negatives 0 of 3.
The stock `run_eval.py` reports 0 triggers here, because it runs with user settings (the real
skill and global skills compete with its temporary copy) and stops at the first tool call that is
not Skill or Read.
