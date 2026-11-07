# Skill evals

Behaviour and trigger evals for skills whose quality cannot be shown by the validator alone.
The folder is outside `skills/`, so the generator does not ship it to users.

- `<skill>/evals.json`: behaviour cases in the skill-creator schema
  (`skills/skill-creator/references/schemas.md`), with fixtures under `<skill>/files/`. Grade
  each run against `expectations`.
- `<skill>/trigger.json`: queries with `should_trigger`, for
  `skills/skill-creator/scripts/run_eval.py`.

Trigger run (from `prompt-orchestrator/skills/skill-creator`, after `python3 tools/generate_integrations.py`
has produced `.claude/skills/<skill>/SKILL.md`):

    python3 -m scripts.run_eval --eval-set ../../evals/design-patterns/trigger.json \
      --skill-path ../../.claude/skills/design-patterns --runs-per-query 3 --num-workers 1 --model sonnet

Each run starts `claude -p` processes; on machines with a memory limit for local agents, keep
`--num-workers 1` and run only when the limit allows.

## Isolated trigger mode

Use `--isolated` for any measurement you report. The stock mode writes a temporary command into the
project's `.claude/commands/`, runs `claude -p` with the user's settings and stops at the first tool
call that is not `Skill` or `Read`. With always-on user skills (for example communication-tone and
prose-and-wording) answering first, it reports 0 triggers even when the real skill is installed. On
2026-11-05 it scored `ui-ux-philosophy` 0 of 10 positives; the isolated mode scored 10 of 10 positives
and 0 of 8 negatives.

    python3 -m scripts.run_eval --isolated --eval-set ../../evals/ui-ux-philosophy/trigger.json \
      --skill-path ../../.claude/skills/ui-ux-philosophy --runs-per-query 3 --num-workers 1 --model sonnet

Same arguments and JSON output as the stock mode. Per run it:

1. Copies the skill folder once at start into a snapshot, so a later `generate_integrations.py` run
   cannot change what the run reads. The generator deletes and rewrites `.claude/skills/`, so do not
   run it while an eval is in progress. With `--description`, the snapshot carries that description.
2. Makes a temporary project holding only `.claude/skills/<skill>/`, and runs
   `claude -p <query> --output-format stream-json --verbose --setting-sources project --tools Skill Read Glob Grep`
   there, with `CLAUDECODE` removed from the environment.
3. Counts a hit when an assistant `tool_use` named `Skill` has an input containing the skill name, and
   stops at the hit, at the `result` event, or at the timeout (default 120 s; 30 s in stock mode).
4. Kills the process and deletes the temporary project.

Before each run the script waits until `MemAvailable` reaches `--min-available-mb` (default 3072, set 0
to disable) and fails the run after an hour of waiting. Run only the skill under test: description
changes mean editing the source skill, regenerating, then running again.

Unit tests for the SKILL.md parser: `python3 -B -m unittest discover -s skills/skill-creator/scripts -v`.

Isolated results on 2026-11-05 (Sonnet): before tuning, one run per query, `ui-ux-philosophy` 18 of
18, `design-patterns` 19 of 20 and `clean-code` 14 of 18. After the v1.6.1 description changes, three
runs per query: `clean-code` 18 of 18 and `design-patterns` 20 of 20, every positive triggering 3 of 3
and every negative 0 of 3. A control run of the `ui-ux-philosophy` set with an unrelated description
(SQL migrations) triggered on none of the 10 UI queries and on the SQL query, so the mode measures
the description.

## Writing skills (2026-11-07)

`academic-writing/evals.json` reviews a register excerpt with ten planted tells (two universals, a
scope verdict, a parenthetical aside, two meta-notes, an importance flag with a participle tail and
an era word) and a reference whose DOI does not resolve, plus a request for real IEEE references.
`academic-writing`, `professional-writing`, `thesis-defense` and `concision-and-logic` each have a
`trigger.json`.

Behaviour cases added on 2026-11-07, each with a planted defect and checkable expectations:

- `concision-and-logic/evals.json` (4 cases): a progress note with a scope shift, a non sequitur,
  a mixed-level list and a restated conclusion, which the scanner cannot find; an email over the
  150-word budget with its request at the end; a paragraph with a long aside, a short
  `(configurable)`, an unsupported universal and two parentheses that must stay; a Gemini answer
  with unrequested options.
- `professional-writing/evals.json` (4 cases): an email with a parenthetical aside and a request
  with no date, where the date must not be invented; a FAP note whose table holds targets, not
  measurements; a PR description requested to "sound impressive"; a status update with a verdict
  pair and a hedged next step.
- `thesis-defense/evals.json` (4 cases): four documents that disagree on node count, coverage,
  check-in interval, a term and two roles; a demo plan that skips F3 and shows an extra first; a
  test log that has no battery figure; an AI-use answer that must match the written statement.

Deterministic checks on the fixture: `draft_scan.py --genre academic` flags all ten tells.
`check_refs.py` has 11 offline self-tests (fake Crossref and HTTP); on 2026-11-07 Crossref and
doi.org were blocked by the session's network policy, so live runs reported both references
`unchecked`, not `fail`.

### Results, 2026-11-07 (Sonnet, 3 runs per query or case)

Trigger runs used `--isolated`. Behaviour runs used `claude -p` in a throwaway project holding
the four writing skills plus `human` and `prose-and-wording`, with Skill, Read, Glob, Grep,
Bash, Write and Edit allowed. A separate Opus call graded each expectation against the
transcript, the final reply and the files written. The em-dash expectations were checked by
script. A gap is an expectation met in fewer than 2 of 3 runs.

| Skill | Trigger (queries correct) | Behaviour (expectation-runs met) |
|---|---|---|
| academic-writing | 12 of 12 | 39 of 39 |
| concision-and-logic | 9 of 9 | 82 of 84 |
| professional-writing | 10 of 10 | 71 of 75 |
| thesis-defense | 9 of 9 | 67 of 69 |

No gap remains. The first runs found these, each fixed and its case run again:

- Trigger: concision-and-logic 0 of 6 positives, professional-writing 4 of 7, academic-writing
  6 of 8 at worst. The model asked for the missing text instead of loading the skill. Each
  description now says to load it on the request alone.
- academic-writing case 1 and concision-and-logic case 3: fixture defects. An uncited
  reference and an off-topic citation were rightly removed. The fixtures were corrected.
- concision-and-logic case 3: an expectation narrower than rule 7 of the skill; aligned.
- professional-writing: paraphrases widened a fact and a status update kept its thank-you line
  (rules 4 and 9).
- thesis-defense: fallbacks without a date, evidence left out of the spoken answer, the anti-AI
  scan skipped, and an AI-use answer that opened with a count (sections 2 and 4).

Every `professional-writing` and `thesis-defense` case was run again on 2026-11-07 after the last
skill edits (49d9f55, 0f60004), 3 runs each, Sonnet, in a throwaway project holding the same six
skills, with skills enabled (the run records each `Skill` call; `--disable-slash-commands` turns
skills off and must not be passed). Graded by hand per expectation, em dashes by script:

| Skill | Case 1 | Case 2 | Case 3 | Case 4 | Total |
|---|---|---|---|---|---|
| professional-writing | 8, 8, 8 | 5, 5, 5 | 6, 6, 6 | 6, 6, 6 | 75 of 75 |
| thesis-defense | 6, 6, 6 | 6, 6, 5 | 6, 6, 6 | 5, 4, 5 | 67 of 69 |

The two misses are single-run slips: one demo map gave undated recordings as fallbacks for F2, F4
and F5, and one AI-use answer offered to walk through "the backend code I wrote", which the
statement does not support.
