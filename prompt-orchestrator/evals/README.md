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
