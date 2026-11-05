# ui-ux-philosophy evals

`evals.json` holds three behaviour cases.

1. A review of `files/devices/`: a Devices list screen (`DevicesPage.tsx`, `devices.css`) with 14
   planted violations (hover-only row actions, an action that shifts between rows, tabs ordered
   by clicks, a placeholder as label, a colour-only clickable status, a routine "Are you sure?",
   a permanent delete without undo, an "Error 500" toast, "No devices" while loading, stacked
   banners, two primary buttons, a div as sort header, a scroll jump after save) and two correct
   components that `notes.md` describes, which must not be reported.
2. Four product-owner requests that each collide with a rule (hide unavailable actions, tabs
   ordered by use, confirm every save, 16 px icon buttons).
3. A review of `files/contract/`: a contract request wizard and record view
   (`ContractRequestPage.tsx`, `ui.css`) with 15 planted violations (a two-column form, unmarked
   optional fields, a Reset button, Back that clears the form, the organization asked twice, a
   disabled submit without a reason, an "OK" submit, errors in `window.alert`, a static
   "Loading..." for a long quote, a loud red Cancel, a preselected data-sharing checkbox, a
   restarting countdown, an invisible edit mode, a Ctrl+S-only save, tabs that wrap and mix
   links) and two reviewed components that `notes.md` describes, which must not be reported.

Run each case with `claude -p` in a scratch copy of `files/devices/` (case 1), `files/contract/`
(case 3) or an empty folder (case 2), tools limited to Read, Glob and Grep, user settings off (`--setting-sources project`),
with the skill under test saved as `INSTRUCTIONS.md` and the prompt prefixed with "Read
INSTRUCTIONS.md in this folder first and follow it." Run the baseline without `INSTRUCTIONS.md`
and without the prefix. Grade each run against `expectations`; a partial counts as a fail. Run
one case at a time and only with 3 GB of memory available.

`trigger.json` holds queries for `skills/skill-creator/scripts/run_eval.py`.

## Results (2026-11-05, Sonnet, user settings off, 3 runs per case)

| Run set | Case 1 (16) | Case 2 (4) | Case 3 (16) |
|---|---|---|---|
| Baseline, no skill | 14, 13, 14 (of 15, before #16 was added) | 3, 3, 3 | 14, 13, 15 |
| Skill, final (round 7) | 15, 16, 15 | 4, 4, 4 | 16, 16, 16 |

Rounds 1 to 6 closed these systematic misses, each seen in every run of a round: no confirmation
or undo for a status transition, a reviewed component reported as a finding, a consequence copied
from the skill's own dialog example, a target-size verdict that ignored the WCAG 2.5.8 spacing
exception, and invented requirements and unmeasured figures (now the Findings Evidence block). In
round 7 every expectation passes in at least 2 of 3 runs; the two misses are single-run slips (one
run named the wrong shifting button, one called edits reversible without marking it). The audit of
round 7 found no unmeasured figure, no small-target verdict without a neighbour check and no wrong
WCAG statement.

Trigger, `run_eval.py --isolated`, 3 runs per query: 10 of 10 positives triggered 3 of 3, 8 of 8
negatives 0 of 3.
