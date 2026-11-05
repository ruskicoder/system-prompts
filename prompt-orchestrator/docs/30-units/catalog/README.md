---
id: units.catalog
type: section
status: draft
owner: unassigned
summary: "Canonical skills and workflows."
kind: module
sources: [skills/*.md, workflows/*.md]
verified: {commit: 3798e1c, date: 2026-11-05}
---

# catalog

## Purpose
The single source of every skill (`skills/*.md`) and workflow (`workflows/*.md`) that the generator distributes to each supported agent.

## Responsibilities
- One markdown file per entry, with frontmatter `name`, `description` (at most 1024 characters), optional `argument-hint` and `license`, optional vetting fields `origin` (`in-house` or `third-party`), `vetting` (`pending`, `passed` or `rejected`) and `vetted` (date), a `# ` title and at least one `## ` section.
- Optional companion files (scripts, templates) live in a sibling folder named after the skill, for example `skills/docs-scaffold/`; the generator copies them next to each generated `SKILL.md`.
- `skills/communication-tone.md` is the single communication rule (status block, settle scope then execute in one pass, hard stops, report every change, interrupt and resume); `skills/build-discipline.md` holds build and task-type rules; `workflows/third-party-vetting.md` gates outside content; `skills/brainstorming.md` and `skills/grill-me.md` clarify new work before building (question rounds with options, play-back, proceed gate, review mode); `skills/prose-and-wording.md` holds the always-on wording rules; `skills/no-ai-trailer.md` bans AI attribution in commits, tags, PRs, issues and releases and enforces it.
- UI work: `skills/ui-flow-and-layout.md` (entity homes, lifecycle as a state machine, one primary action per state, list and detail anatomy, version-dependent settings, every view state, flow map deliverable), `skills/design-accessibility-review.md` (WCAG 2.2 AA: evidence rules, four passes, the 55 A/AA criteria, component checklists), `skills/design-heuristics-audit.md` (ten heuristics, 0 to 4 severity, prove then vet) and `workflows/ui-review-loop.md` (inspect, fix, re-verify a running UI). build-discipline's Feature rules and spec-driven's design phase require the flow map and the WCAG 2.2 AA target for UI work. These were re-authored in-house from practices reviewed during third-party vetting on 2026-11-02.
- Refactoring: `skills/refactoring.md` (two hats, pin behaviour first with characterization tests, preparatory refactoring, smell to technique loop, refactor or sprout or strangle, reference-aware moves) with on-demand references `skills/refactoring/references/smells.md` and `legacy.md`; build-discipline's Refactor rules and the harness `refactor` agent point to it. Re-authored in-house from refactoring skills vetted on 2026-11-02.
- Code design: `skills/clean-code.md` (names, functions split by responsibility rather than length, command-query separation, errors as design, boundaries, comments for rationale, rules for agent-written code, review mode) with on-demand references `skills/clean-code/references/principles.md` (complexity, SOLID with over-application signs, DRY, KISS, YAGNI, Law of Demeter, coupling kinds, deep modules, design red flags) and `test-smells.md`; `skills/design-patterns.md` (name the force, five-rung ladder, YAGNI gate, counter-signals, Refactor Map before edits, decision record, verdicts for existing patterns) with references under `skills/design-patterns/references/`: `catalog.md` (23 Gang of Four patterns, look-alikes), `presentation.md` (UI architectures, Android, iOS, Flutter, React guidance), `architecture-styles.md` (including serverless practice), `enterprise-and-ddd.md`, `distributed-and-cloud.md`, `messaging.md`, `concurrency-and-functional.md`, `api-design.md`, `anti-patterns.md` and `languages/` (12 language idiom files), each grounded in the primary source it names. build-discipline, refactoring, review-software-architecture and code-quality-testing link to them. Re-authored in-house from skills vetted on 2026-11-02.
- Issues: `skills/issue-checker.md` sweeps open issues beside each PR review (last-speaker classification into resolved, stale report, leader-only, unanswered, waiting or nothing to do; fixes counted only when merged into the project's done branch; code located and read through GitNexus or `git grep` before answering; close only on checked evidence; one closing question; holding reply plus leader queue; per-repo counts; `act` mode only under a standing grant, `draft` otherwise). Re-authored in-house from issue-triage skills vetted on 2026-11-05.
- Entries are listed in `INTEGRATIONS.md` and `tools/registry.json` (both generated).
- Platform prompt-size caps (an 8,000-byte main-prompt limit in Codex, `MAX_SKILL_PROMPT_BYTES` in `codex-rs/ext/skills/src/render.rs`; 20,000 characters for M365 Copilot declarative-agent skills) are platform limits, not repo rules. Skills keep the content they need; never compact or truncate necessary instructions to fit a cap ([decision 0001](../../60-decisions/0001-platform-prompt-size-caps.md)). `references/*.md` in the companion folder remains an option for optional detail.

## Code
`skills/*.md`, `workflows/*.md`

## Entries with embedded tooling

| Entry | Tooling | Verification |
|---|---|---|
| `skills/docs-scaffold.md` | Companion folder `skills/docs-scaffold/scripts/` (CLI and self-tests) | `python3 -B -m unittest discover -s skills/docs-scaffold/scripts -v` |
| `skills/no-ai-trailer.md` | Companion folder `skills/no-ai-trailer/scripts/`: `ensure_attribution_off.py` (settings, global git hooks, Claude Code hooks; run by `install/install-claude.*` and at every session start), `ai_trailer.py` (detector and cleaner), `guard.py` (PreToolUse guard), self-tests | `python3 -B -m unittest discover -s skills/no-ai-trailer/scripts -v` |
| `skills/refactoring.md` | Companion folder `skills/refactoring/references/` (smell to technique map, legacy techniques), loaded on demand | Not applicable |
| `skills/clean-code.md` | Companion folder `skills/clean-code/references/` (principles, test smells), loaded on demand | Not applicable |
| `skills/design-patterns.md` | Companion folder `skills/design-patterns/references/` (pattern families and `languages/`), loaded on demand | Not applicable |
| `skills/prose-and-wording.md` | Companion folder `skills/prose-and-wording/references/` (source convention, print rules removed) | Not applicable |
| `skills/human.md` | Companion folder `skills/human/`: `scripts/human_tool.py` dispatcher over the scanner, preservation, suggestion, harvest, voice and loop modules, plus `references/*.md` (contract, catalog, structure, workflows, voice, style, tools) | `python3 -B -m unittest discover -s skills/human/scripts -v` |

