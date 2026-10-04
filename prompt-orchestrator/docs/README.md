---
id: readme
type: readme
status: draft
owner: unassigned
summary: "Entry point: purpose, scope, folder map, reading order."
---

# Documentation

## Purpose
<!-- What this documentation covers and who reads it. -->

## Scope
<!-- In scope / out of scope. -->

## Folder map
| Folder | Holds |
|---|---|
| `10-context/` | Overview, requirements (REQ-n), non-functional requirements (NFR-n), constraints |
| `20-architecture/` | Whole-system structure, data model, interfaces, cross-cutting concerns |
| `30-units/` | One folder per module, app, or service |
| `40-verification/` | Test strategy and test environments |
| `50-operations/` | Deploy, configuration, runbooks |
| `60-decisions/` | Numbered decision records (immutable once approved) |
| `70-work/` | Dated work records (immutable once closed) and `STATUS.md` |
| `80-guides/` | Onboarding, how-tos, examples |
| `90-meta/` | Conventions, manifest, locks |
| `_generated/` | Machine-owned output; never edit |
| `.deprecated/` | Preserved wrong or superseded specs; never link here |

## Reading order
1. This file, then `glossary.md`.
2. `10-context/overview.md`, then `20-architecture/system.md`.
3. The unit folders you work on, then `70-work/STATUS.md`.

## Status legend
`draft` written, not reviewed. `approved` reviewed, current. `todo` known gap. `n/a` not applicable (with `na_reason`). `closed` finished work record (locked).
