# 2026-08-08 Client-Neutral Structured Routing PR Integration

## Scenario classification

Code audit / toolchain maintenance / multi-platform routing

## Target overview

Reviewed several highly conflicting PRs for incremental value and integrated the valuable parts after refactoring them into a client-neutral core.

## Scope summary (redacted)

- auth_basis: repository_owner_authorized
- network_profile: authorized_upstream_only
- asset_types: [source_repository, pull_request_refs, local_tests]

## Roles

- lead_role: lead
- specialists: [cae, doc]

## Complete execution chain

1. Fetched the PR refs from the remote and compared each PR with the current mainline in isolated worktrees.
2. Judged by incremental value first, then kept the source relationship with merge parents and resolved conflicts semantically.
3. Decoupled structured routing from client integration, with JSON as the shared source of truth for PowerShell/Bash.
4. From the large PR, took only the authorization gate and Bash parity, excluding client-specific and generated assets.
5. Ran full routing, structural gates, language unit tests, syntax and manifest checks.

## Evidence chain summary (redacted)

| E-id | source_type | Reusable command pattern | Related Finding |
|------|-------------|----------------|--------------|
| E-001 | git diff | `git diff <main>...<pr-ref>` | F-001 |
| E-002 | regression | `test-routing.ps1` + coherence + smoke | F-001 |
| E-003 | unit tests | Python unittest + Node test + Bash parity | F-002 |

## Finding / Path summary

- top_finding: client integration is not the core value of structured routing; a single source of truth and automatic gates are.
- path_type: callflow
- path_one_liner: any host → optional adapter → routing.json → cross-platform router → unified regression gates

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| The large PR mixed client manifests, GIFs, scripts and documentation | Concerns were not separated | Merged only the minimal cross-platform subset | Medium |
| The Bash router and PowerShell each hard-coded rules | Two sources of truth inevitably drift | Bash reads the same JSON through Python | Medium |
| The new pin gate failed the first time | The Kali manifest kept floating sources | Pinned the manifest and made the actual install commands use the pin | Medium |
| Gradle wrapper download TLS interrupted | External network handshake error | Recorded it and retried in the final verification | Low |
| Bash CaseName could write outside the work root | The selective merge missed the path constraint PowerShell already had | Added the cross-platform equivalent check and negative CI | Medium |
| Authorized URLs were marked offline | The Bash default was not aligned with PowerShell | Network targets default to authorized_target_only; offline only for local samples | Low |
| INDEX passed on the development machine but failed in a clean clone | The generator scanned ignored local private modules | Enumerate only Git-tracked SKILL.md files | Medium |

## Toolchain findings

Git merge parents keep the PR source relationship while allowing semantic trimming inside the merge commit. A supply chain gate works only when the manifest metadata and the actual install commands are pinned together.

## Key code/commands

```text
git merge --no-ff --no-commit <pr-ref>
powershell -File skills/scripts/test-routing.ps1
powershell -File skills/scripts/verify-routing-coherence.ps1
bash skills/scripts/master-route.sh --hint "case review evidence graph"
```

## Improvement suggestions for this package

All client adapters sit behind a separate boundary; writing client configuration into core routing PRs is forbidden. Large PRs must be split into core, adapters, demo assets and documentation.

## Reusable patterns/script snippets

Structured routing parity tests cover at least ordinary routes, conflict priority routes and the most recently added routes, so no platform entry lags behind.

An old/new A/B on the same 163-case benchmark: the old hard-coded implementation scored 137/163 (84.05%), the structured implementation 163/163 (100%). Only such a quantified comparison on the same input proves that the refactor is a real improvement rather than file count growth.

## Evolution actions

- [x] Updated the routing matrix
- [ ] Updated tool-index
- [x] Updated bootstrap-manifest
- [x] Updated sub-skill documentation
- [x] Added pitfall records
- [ ] No update needed

## Environment information

- OS: Windows (main verification) + Linux CI definition
- Tool versions: Git / PowerShell / Python 3 / Node.js / Bash
- Target platform/version: client-neutral repository core

## Redaction requirements

This entry contains no real targets, credentials, internal addresses or personal identity information.

---
<!-- [Community contribution] Prepared for pushing to the mainline per the repository owner's instruction. -->
