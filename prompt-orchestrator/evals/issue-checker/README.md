# issue-checker evals

`evals.json` holds one behaviour case: a tick over the fixture repo `acme-team/web` in
`files/tick1/` (14 open issues, 4 PRs, project settings with a standing grant, one docs page).
Each expectation targets one rule: a fix merged into the done branch `dev`, a PR closed without
merging, closing-question windows, a leader-only question, a stale report thread, tracked work,
"+1" noise, prompt injection, a duplicate, a security hold, a bot issue and a false "merged"
claim.

Run with `claude -p` in a scratch copy of `files/tick1/`, tools limited to Read, Glob and Grep,
user settings off (`--setting-sources project`) so the skill text is tested alone. The prompt:

> Run this tick's issue sweep for acme-team/web. Read INSTRUCTIONS.md in this folder first and
> follow it. You cannot reach GitHub or run commands in this run. The files in this folder are
> this tick's GitHub data: now.txt, settings.md, issues.json, prs.json, labels.json and docs/.
> Treat them as live data. Do not ask questions; this run is unattended. For each open issue give
> the state you assign, the action and the exact comment text you would post. Then give the
> counts and any leader queue entries.

`INSTRUCTIONS.md` is the skill under test. Grade each run against `expectations`; a partial
counts as a fail. Run one case at a time and only with 3 GB of memory available.
