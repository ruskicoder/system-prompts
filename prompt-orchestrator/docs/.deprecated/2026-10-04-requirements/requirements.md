---
deprecated: {date: 2026-10-04, from: .kiro/specs/docs-scaffold/requirements.md, reason: "Approved draft before user decisions: warn-only CLI, scaffold-type question only, ignore dir for temporary sessions, append-only session journal, manifest in JSON", superseded_by: none}
---

# Requirements Document

## Introduction

`docs-scaffold` is a prompt-orchestrator skill that creates and maintains a documentation tree serving as the single source of truth (SSOT) for a software project. The tree is designed for two readers at once: humans, who need a predictable layout and a clear reading order, and AI agents, who need a compact entry point, one topic per file, and machine-readable metadata so they can load only what a task needs.

The skill targets three failure modes of project documentation. Gaps are prevented by a manifest that declares which documents each unit must have, where every required slot is either filled, marked `todo`, or marked `n/a` with a reason. Staleness is detected by recording, per section of related documents, the code paths the section describes and the commit at which it was last verified; any later change to those paths flags the section. Duplication is prevented by giving every fact one home, separating current-truth documents from immutable dated work records, and keeping code-derived reference material in a machine-owned `_generated/` folder.

The skill is methodology-neutral and contains no client-, vendor-, or project-specific conventions, phase codes, or identifiers. It supports two deployment modes: standalone (documentation in its own repository) and embedded (documentation inside a code monorepo, alongside Kiro specs used for spec-driven development). Superseded or rejected specifications are preserved in a `.deprecated/` folder instead of being deleted. Export to office formats, multilingual documentation, and methodology profiles are out of scope.

### Glossary

- **Docs root**: the directory holding the documentation tree. Defaults to `docs/`; taken from project conventions when they define one.
- **Unit**: a module, application, or service documented under `30-units/<unit>/`, optionally grouped one level as `30-units/<domain>/<unit>/`.
- **Section**: a folder of 2 to 10 related documents that share one verification stamp (for example one unit folder, or `20-architecture/`).
- **Spec document**: a document of type `requirements`, `nfr`, `design`, `detail`, `interface`, or `test`, or any file inside a change folder.
- **Substantive change**: a change that alters meaning: behavior, scope, acceptance criteria, requirement IDs, interfaces, data definitions, values, or design decisions.
- **Minor change**: a change that does not alter meaning: typography, spelling, formatting, whitespace, or link-target repair. Git history is the audit trail for minor changes.
- **Work record**: a dated document under `70-work/` describing an investigation, change, test run, review, or release.
- **Validator**: the check tool distributed with the skill.

## Requirements

### Requirement 1: Skill packaging and distribution

**User Story:** As a maintainer of prompt-orchestrator, I want `docs-scaffold` to follow the repository's single-source skill model, so that every supported agent receives the same behavior without hand-maintained copies.

#### Acceptance Criteria

1. The skill SHALL have exactly one canonical source file at `skills/docs-scaffold.md` with valid `name`, `description`, and `argument-hint` frontmatter.
2. WHEN `python3 tools/generate_integrations.py` runs THEN the system SHALL emit `docs-scaffold` to every integration target the generator supports.
3. WHEN `python3 skills/validate_skills.py` runs THEN the system SHALL report zero failures for `docs-scaffold` and its generated copies.
4. The deprecation operation SHALL be part of `docs-scaffold` and SHALL NOT be a separate skill.
5. The validator SHALL be distributed with the skill to every integration target, so that a project using any supported agent can run it.
6. The skill, its templates, and the validator SHALL NOT contain client names, vendor names, project names, employee identifiers, internal URLs, or methodology-specific phase codes.

### Requirement 2: Initialization and mode selection

**User Story:** As a developer adopting the skill, I want the agent to explain the available modes and ask me which ones to use, so that the scaffold matches my project without silent defaults.

#### Acceptance Criteria

1. WHEN the skill is invoked in a project that has no `90-meta/manifest.yaml` under the docs root THEN the agent SHALL explain the deployment modes (`standalone`, `embedded`) and the enforcement modes (`warn`, `strict`) and SHALL ask the user to choose one of each before writing any file.
2. The agent SHALL NOT select a deployment mode or enforcement mode without an explicit user answer.
3. WHEN the user answers THEN the agent SHALL record `mode`, `enforcement`, `docs_root`, and `changes_dir` in `90-meta/manifest.yaml`.
4. IF the project conventions define a documentation root THEN the agent SHALL propose that path as `docs_root`; otherwise it SHALL propose `docs/`.
5. IF the docs root already contains files THEN the agent SHALL list the existing files that conflict with the scaffold and SHALL NOT overwrite or move any of them without user approval.
6. WHEN the project already has documentation THEN the agent SHALL recommend `warn` enforcement and SHALL state that `strict` can be enabled once the validator reports no errors.

### Requirement 3: Scaffold structure

**User Story:** As a reader, I want every project to share the same predictable layout, so that I can find any fact without searching.

#### Acceptance Criteria

1. WHEN initialization completes THEN the system SHALL create under the docs root: `README.md`, `INDEX.md`, `glossary.md`, `10-context/`, `20-architecture/`, `30-units/`, `40-verification/`, `50-operations/`, `60-decisions/`, `70-work/`, `80-guides/`, `90-meta/`, `_generated/`, and `.deprecated/`.
2. Every numeric prefix at the top level of the docs root SHALL be unique.
3. Live documents SHALL be at most three directory levels below the docs root.
4. `README.md` SHALL contain purpose, scope, folder map, reading order, and status legend, and SHALL be the single entry point for humans and agents.
5. Each top-level folder SHALL contain only the document types assigned to it in `90-meta/conventions.md`.
6. WHERE mode is `standalone` THEN the system SHALL create `70-work/changes/`; WHERE mode is `embedded` THEN the system SHALL use the configured `changes_dir` (default `.kiro/specs`) and SHALL NOT create `70-work/changes/`.
7. The docs root SHALL NOT contain secrets, credential files, or runnable project scripts; configuration SHALL be documented in `50-operations/configuration.md` with templates kept outside the docs root.

### Requirement 4: Document metadata

**User Story:** As an AI agent, I want every document to carry structured metadata, so that I can index, filter, and trust documents without reading them in full.

#### Acceptance Criteria

1. Every live document SHALL begin with frontmatter containing `id`, `type`, `status`, `owner`, and `summary`.
2. `type` SHALL be one of the values listed in `90-meta/conventions.md`.
3. `status` SHALL be one of `draft`, `approved`, `todo`, or `n/a`.
4. IF `status` is `n/a` THEN the document SHALL contain a non-empty `na_reason`.
5. `summary` SHALL be a single line.
6. WHERE a document satisfies or describes requirements THEN its frontmatter SHALL list the requirement IDs in `traces`.
7. Requirement IDs SHALL be stable and SHALL NOT be reused for a different requirement.
8. Every `id` SHALL be unique across live documents.

### Requirement 5: Completeness (no silent gaps)

**User Story:** As a project lead, I want missing documentation to be detected automatically, so that gaps are visible instead of silent.

#### Acceptance Criteria

1. `90-meta/manifest.yaml` SHALL declare the required document types for each unit kind.
2. WHEN the validator runs THEN it SHALL report every unit missing a required document.
3. WHEN the validator runs THEN it SHALL report every required document that is empty or has `status: n/a` without `na_reason`.
4. WHEN the validator runs THEN it SHALL report every requirement ID in `10-context/` that is not traced by at least one design document and at least one test document.

### Requirement 6: Section verification and staleness

**User Story:** As a maintainer, I want documentation to be flagged when the code it describes changes, so that stale documents are found before anyone relies on them.

#### Acceptance Criteria

1. Verification SHALL be recorded once per section, in the frontmatter of the section's `README.md`, as `sources` (code path globs) and `verified` (commit and date).
2. WHEN any file matching a section's `sources` has changed since `verified.commit` THEN the validator SHALL report that section as stale.
3. WHEN an agent re-verifies a section against the current code THEN it SHALL update `verified` to the current commit and date.
4. IF a section contains fewer than 2 or more than 10 documents THEN the validator SHALL warn and suggest merging or splitting.
5. WHERE mode is `standalone` THEN `sources` entries SHALL be qualified as `<repo>:<path>` and each repo SHALL be declared in the manifest with the environment variable that holds its local clone path.
6. IF a declared repo clone is not available locally THEN the validator SHALL report affected sections as `unverifiable` and SHALL NOT report them as passing.

### Requirement 7: Current truth versus work records

**User Story:** As a reader, I want current-state documents kept separate from historical records, so that I never mistake history for current behavior.

#### Acceptance Criteria

1. Documents in `10-context/` through `50-operations/` SHALL describe the system as it is at the current commit.
2. Work records in `70-work/` SHALL be named `YYYY-MM-DD-<slug>` and SHALL NOT be modified after their `status` is closed.
3. Decision records in `60-decisions/` SHALL be numbered sequentially and SHALL NOT be modified after acceptance, except to add a `superseded_by` reference.
4. `70-work/STATUS.md` SHALL be the only living progress ledger.
5. Test runs SHALL be recorded as `70-work/test-runs/YYYY-MM-DD-<unit|integration|system>-r<N>.md`, with repeated rounds as separate files.

### Requirement 8: Change specs and Kiro integration

**User Story:** As a developer using spec-driven development, I want change specs and current-truth documents to stay consistent, so that approved specs never describe outdated behavior.

#### Acceptance Criteria

1. Each change SHALL live in `<changes_dir>/<change-id>/` containing `requirements.md`, `design.md`, and `tasks.md`.
2. WHEN a change is implemented THEN the agent SHALL merge its lasting facts into the affected documents in `10-context/` through `50-operations/` and SHALL re-verify the affected sections.
3. WHERE mode is `embedded` THEN the agent SHALL offer to add a pointer to `README.md` of the docs root in `AGENTS.md`, `CLAUDE.md`, and a Kiro steering file, and SHALL ask before modifying any of those files that already exist.

### Requirement 9: Generated content

**User Story:** As a maintainer, I want code-derived reference material produced by tools, so that it never drifts from the code.

#### Acceptance Criteria

1. `_generated/` SHALL contain only machine-produced files and SHALL NOT be edited by hand.
2. WHEN the validator runs with its regenerate option THEN it SHALL rebuild `INDEX.md`, `_generated/traceability.md`, `_generated/health.md`, and `.deprecated/README.md`.
3. WHEN the validator runs without the regenerate option AND regenerating would change any generated file THEN it SHALL report the generated files as out of date.
4. `INDEX.md` SHALL list every live document with its `id`, `type`, `status`, and `summary`, and SHALL exclude `.deprecated/`.

### Requirement 10: Deprecation of specs

**User Story:** As a developer, I want wrong, mistaken, or changed specs preserved instead of deleted, so that the reasoning behind past decisions stays auditable.

#### Acceptance Criteria

1. WHEN a spec document is found to be wrong or mistaken, OR is about to receive a substantive change, THEN the agent SHALL deprecate the current version before editing or replacing it.
2. WHEN a change to a spec document is minor THEN the agent SHALL NOT deprecate it.
3. IF the agent cannot determine whether a change is substantive or minor THEN it SHALL ask the user before proceeding.
4. WHEN a document is deprecated THEN the agent SHALL move it to `.deprecated/YYYY-MM-DD-<slug>/`, keeping sibling files together when a whole spec folder is deprecated.
5. WHEN a document is deprecated THEN the agent SHALL add `deprecated` frontmatter containing `date`, `from` (original path), `reason`, and `superseded_by` (an `id`, or `none`).
6. WHEN a document is deprecated THEN the agent SHALL update every live link that pointed to it so that it points to the replacement, or SHALL remove the link and report it when there is no replacement.
7. Files in `.deprecated/` SHALL NOT be deleted or modified after the move.
8. Live documents SHALL NOT link into `.deprecated/`; deprecated documents MAY link to live documents.
9. Documents in `.deprecated/` SHALL be excluded from `INDEX.md`, ID-uniqueness checks, and coverage checks, and a replacement MAY reuse the deprecated document's `id`.

### Requirement 11: Validator behavior

**User Story:** As a developer, I want one command that checks the whole tree, so that documentation health can be enforced locally and in CI.

#### Acceptance Criteria

1. The validator SHALL run on Python 3.8 or later without third-party dependencies.
2. The validator SHALL check missing documents, silent gaps, stale sections, requirement coverage, broken links and trace IDs, duplicate IDs, out-of-date generated files, modified work records, modified decision records, modified deprecated files, and live links into `.deprecated/`.
3. WHERE enforcement is `warn` THEN the validator SHALL print all findings and exit with code 0.
4. WHERE enforcement is `strict` THEN the validator SHALL exit with a non-zero code when any error-level finding exists.
5. Each finding SHALL include severity, check name, file path, and a one-line fix hint.
6. The validator SHALL ship with an automated self-test covering each check.

## Out of Scope

- Export of documents to office formats.
- Multilingual documentation (English only).
- Methodology profiles, phase codes, or client-specific deliverable mappings.
