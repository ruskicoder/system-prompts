# architecture-diagrams evals

`evals.json` holds two behaviour cases.

1. Plan from code: `files/plan/system.md` describes a small system (web and mobile apps, a NestJS
   backend with Prisma and a BullMQ queue, an MQTT broker, LoRa gateways and trackers, PostgreSQL,
   Redis, three third parties, one called from the browser) and lists backend modules that do not
   belong in an overview. 11 expectations: overview level, inventory from code, reading direction,
   third-party column, the browser-side call, runtime nesting, request and response pairs, edge
   labels, print-size font arithmetic, nesting depth, sketch and check before showing.
2. Review a figure: `files/review/fig.drawio` carries eight planted defects (a router edge, a "uses"
   label, labels on edges, a double-headed arrow, an edge through three frames and a title, a third
   party on the wrong side, three nesting levels, 9 px text, text that does not fit). The lint
   script sits beside it; four of the defects are outside what the lint can see. 11 expectations.

Run each case with `claude -p` in a scratch copy of its `files/` folder, user settings off
(`--setting-sources project`), tools Read, Glob and Grep (case 2 adds Bash so the lint can run),
with the skill under test saved as `INSTRUCTIONS.md` and the prompt prefixed with "Read
INSTRUCTIONS.md in this folder first and follow it." The baseline runs without `INSTRUCTIONS.md`.
Grade each run against `expectations`; a partial counts as a fail. Release bar (HARNESS.md
section 5): no failure repeats across runs, every expectation passes in at least 2 of 3 runs.

`trigger.json`: 18 queries for `skills/skill-creator/scripts/run_eval.py --isolated`.
