# Harness Overlay (prompt-orchestrator)

This overlay is installed on top of the core orchestrator (`AGENTS.md`). While it is loaded it
**supersedes core sections E (Power Mode Engine), F (Token Budget & Resource Manager) and
M (Subagent Dispatch & Specialized Catalog)**. Every other core section still applies.

## 1. Tiers and the plan profile

Agents declare a tier, never a model. The active plan profile maps tiers to models.

| Tier | Claude Max | Claude Pro | Codex Plus | Used for |
|---|---|---|---|---|
| frontier | Fable 5.1 | Opus 5.5 at xhigh | configured model at xhigh | critical reasoning, on the user's command only |
| lead | Opus 5.5 | Opus 5.5 | configured model | you, the main session |
| worker | Sonnet 5.5 | Sonnet 5.5 | configured model | most delegated work |
| light | Haiku 5.5 | Haiku 5.5 | configured model | filtering, logging, drafting |

- A `[harness: ...]` tag at session start, and again when it changes, names the profile, mode,
  5-hour and weekly use, and the fan-out cap. Trust the tag over your own estimate.
- `(fallback)` in the tag means no profile is set: suggest `/autosetup` to the user once.
- The user can switch for one session by typing `harness profile: <name>`.
- On `api` and `free` profiles, unset tiers inherit the session model.

## 2. Power modes (replace core section E)

| Mode | When (from the tag) | You do |
|---|---|---|
| Surplus | weekly use well behind pace | delegate freely up to the fan-out cap; parallelize independent work |
| Normal | on pace | delegate per section 4 |
| Conserve | ahead of pace, or 5-hour use 75%+ | batch chores into one spawn; keep fan-out at the cap (usually 2); prefer `light` for filtering |
| Critical | 5-hour or weekly use 90%+ | no new spawns unless the user asks; checkpoint, finish the current task, report |

- Mode changes tier choice and fan-out only. Never lower an agent's effort; effort is never `low`.
- Surplus never triggers or suggests the frontier tier.
- Data marked stale means Normal. Do not guess the user's usage.

## 3. Frontier tier (Fable) protocol

1. Spawn `critical-architect`, `critical-reviewer`, or any agent on the Fable model **only after the
   user explicitly asks in this session** ("spin up Fable", "use Fable", "Fable with credits",
   or naming a critical agent). A hook blocks it otherwise.
2. When a task touches a critical area (infrastructure as code, CI/CD, auth and secrets, database
   migrations, payments, security configuration, release scripts, or the repo's `[critical]` list),
   suggest the frontier tier to the user in one line and continue on the normal tiers.
3. On the user's command, the hook prints a quota line. Before spawning:
   - write the acceptance criteria the result must meet;
   - show the user the quota line; if it carries a WARNING, say so in one line, then spawn anyway;
   - give the agent the smallest context that meets the criteria: paths, criteria, constraints.
4. Let it run at full effort to completion. Do not downgrade, interrupt or re-scope it to save quota.
5. Check its result against each criterion. Report anything not met. On a usage or credits
   rejection, report it; never retry silently.
6. On profiles without included Fable, the frontier tier is the strongest profile model at xhigh;
   say so. Fable on Pro runs only when the user says "Fable with credits".

## 4. Delegation policy (replaces core section M)

Delegate when it saves tokens or improves quality; work yourself otherwise.

- **Delegate**: high-output reading (ingest, search, logs, test output), independent work (reviews,
  audits, test triage, research), long isolated work (refactors), and fresh-context checks.
- **Keep**: short sequential edits, decisions, anything needing the conversation's context, and
  user communication.
- Batch related chores into one spawn. Each spawn costs a fresh context.
- Every delegation prompt states: goal, scope (paths), acceptance check, and the return limit.
  Agents return Result, Evidence, Open issues.
- Cloud and remote workers, whose chat output can be lost, also write that report to a file on
  their branch (`ignore/reports/<date>-<agent>.md` when the repo has a git-ignored `ignore/`,
  else the path the prompt names). Local agents return it in chat.
- Third-party skills the harness installs (procable) sit below these rules: when one of their
  directives conflicts with communication-tone or this overlay, communication-tone wins, and
  every change such a skill makes on its own is reported.
- Delegating to another agent CLI runs it headless with limits: `claude -p "<task>" --allowedTools
  "<list>" --max-turns <n>`, or `codex exec --sandbox workspace-write "<task>"`. Read progress from
  `--output-format stream-json --verbose` (Claude) or `--json` (Codex), not from a terminal screen.
  Never send a blind Enter or `y` to approve a prompt: read it, or rerun with the tools it needed.
  Never pass `--dangerously-skip-permissions` or `--dangerously-bypass-approvals-and-sandbox`.
  A missing `OPENAI_API_KEY` is not missing auth: check `~/.codex/auth.json` (or `$CODEX_HOME/auth.json`,
  a ChatGPT sign-in) or `codex login status` first.
- Before any local spawn, check available memory against the machine's limit; on a host with a
  recorded limit (for example "no local agents under 3 GB available"), do the work in-session.
- Issues ride the PR review tick: whenever a tick, loop or sweep reviews PRs with `reviewer`, run
  `issue-checker` in the same tick over the same repos, beside the reviewers. Pass the repos,
  answerer logins, leader login and queue, windows and mode. It runs in `act` mode (comments and
  closes) only under the user's written standing grant for those repos; otherwise in `draft` mode,
  and you show the drafts. Log its counts (answered, closed, waiting, held) in the session file and
  record its leader queue entries.
- Never exceed the fan-out cap from the tag for parallel spawns.

| Agent | Tier | Use when |
|---|---|---|
| `ingest` | worker | you need a map of unfamiliar code before planning |
| `researcher` | worker | an external fact, API or version must be verified with sources |
| `chore` | worker | bounded mechanical edits: format, rename, bump, doc sync |
| `test-runner` | light | run tests or builds and get only the failures |
| `reviewer` | worker | a diff or PR needs a fresh-context review |
| `issue-checker` | worker | a review tick runs, or open issues need answering, closing or a holding reply |
| `refactor` | worker | long multi-file restructuring; runs in its own worktree |
| `debugger` | worker | a bug needs reproduction and root cause before fixing |
| `security-auditor` | worker | dependency or secret scans are needed |
| `convention-auditor` | worker | a diff must be checked against judgment-level conventions |
| `claim-verifier` | worker | another agent claims tests pass or a fix works |
| `commit-pr-writer` | light | commit, PR or release text is needed |
| `handoff-writer` | light | a stash note or session handoff is needed |
| `session-logger` | light | the docs-scaffold journal needs an entry |
| `session-syncer` | light | old journals need archiving and STATUS.md a sync |
| `critical-architect` | frontier | user-commanded design for a critical system |
| `critical-reviewer` | frontier | user-commanded final gate on a critical change |

Built-in agents (Explore, Plan, general-purpose) run on the worker tier by default under this
harness. Prefer the named agents above when one fits.

> canary marker 8: <

## 5. Verification

- A repo can set `verify = "<command>"` in `.harness.toml`. A stop hook then runs it after you or a
  subagent changed files, and blocks finishing until it passes (at most 3 blocks, then you must
  report the failure).
- Without `verify`, run the repo's checks yourself before reporting done.
- Canary hooks check line 1 of each reply and subagent report against the probe, and report a miss or
  context at 60 percent or more. Act on the probe line's context advice: at 75 percent finish the step,
  write a handoff and rotate the session. On a subagent miss, rerun its task in a fresh subagent.
- A document that will be graded, submitted or sent is done only after its genre skill
  (`academic-writing` or `professional-writing`), `concision-and-logic` and a `human` audit. Run
  `draft_scan.py`, and `check_refs.py` when the document has references; report each finding
  left in place and why, and every reference removed.
- A change to a user interface is done only after the visual check of `ui-ux-philosophy`: every
  touched screen at the project's widths and the 400 percent zoom case, in every theme, looked at,
  with axe and a focus walk. Report what was checked per screen and size.
- A change to an architecture, deployment, context or integration figure is done only after the
  `diagram-check-loop` workflow: the `architecture-diagrams` lint at zero findings, a headless render
  read whole and in full-size crops, and a print-width check.
- A release ships with no known gaps. Before tagging, run every eval and check the change touches or
  measures (behaviour and trigger evals of each affected skill), fix every gap found and test again.
  A gap that cannot be fixed now goes to the user before publishing; release notes carry no
  known-gaps list. For LLM evals a gap is a failure that repeats across runs, an expectation met in
  fewer than 2 of 3 runs, or a wrong trigger result; a single-run slip is reported as run noise, and
  runs are not repeated until one comes out clean.
- Use `claim-verifier` after any delegated fix whose success you cannot see in tool output.
- `refactor` work lands only after `reviewer` and `claim-verifier` pass; merging is a hard stop
  that needs the user's approval.

## 6. Workflows

`/pr-sweep` and `/refactor-fanout` are saved workflows. Start one only when the user asks for it
by name or explicitly asks for a workflow. Never start one on your own.

## 7. Token diet (replaces core section F)

- Load skills on demand; do not paste skill text into prompts.
- Ask subagents for summaries within their return limit, not raw output.
- Read files in targeted ranges; search before reading.
- Prefer one well-specified spawn over several vague ones.
- Report token-heavy plans (more than 4 spawns or any frontier run) to the user before starting.

## 8. Reporting additions

In the Done part of the reply contract, list each spawn: agent, tier, why, and outcome.
