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

Isolated results on 2026-11-05 (Sonnet, one run per query): `ui-ux-philosophy` 18 of 18,
`design-patterns` 19 of 20 (the Adapter, Facade and Proxy comparison did not trigger), `clean-code`
14 of 18 (four short code-review questions did not trigger). A control run of the
`ui-ux-philosophy` set with an unrelated description (SQL migrations) triggered on none of the 10
UI queries and on the SQL query, so the mode measures the description.
