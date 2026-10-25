---
title: "Prose and Wording Conventions"
chapter: "11-conventions/09"
last_verified: 2026-09-15
doc_revision: 2026-09-15
scope: "Every tracked document, every generated book, every commit message"
---

# Prose and Wording Conventions

These rules apply to every tracked document in this repository, to the three generated
books, and to commit messages. They are enforced by `make prose`, which runs inside
`make all`.

The reader is an operator. The operator is looking for one specific thing, usually
under time pressure. Write for that.

## Hard rules, machine-enforced

| Rule | Enforcement |
|---|---|
| No em dash `—` in prose | `make prose` fails |
| No en dash `–` as a clause separator | `make prose` fails |
| No generic openers | `make prose` fails |

An em dash in a table cell used as a "not applicable" placeholder is permitted, because
it is data rather than prose. An em dash inside a code fence or an inline code span is
permitted, because it is quoted content.

### Replace the em dash

Join statements with a comma. Split into two sentences where the comma produces a
run-on.

| Instead of | Write |
|---|---|
| `The rule is loaded — verify it drops traffic` | `The rule is loaded, verify it drops traffic` |
| `Two sites shared the defect — the second is worse` | `Two sites shared the defect. The second is worse` |
| `Hash a1bb75c5 — the pre-fix artifact` | `Hash a1bb75c5, the pre-fix artifact` |

### Banned openers

`Let's`, `In order to`, `It's worth noting`, `Needless to say`, `At the end of the
day`, `It goes without saying`, `Simply put`.

Delete the opener and start with the statement.

## Hard rules, review-enforced

These are not reliably detectable by regex. A checker that guesses produces false
positives, and a check that cries wolf gets ignored.

### No aphorism formulas

Do not write a memorable line in place of an accurate one.

| Instead of | Write |
|---|---|
| `A ledger that doubles as a TODO list is neither` | `Open items live in the risk register. The change log stays append-only` |
| `A predicate that can match non-diagram text is a predicate that lies` | `Validate the predicate against real output before trusting its result` |

### No two-beat antithesis

Do not use the `not X, but Y` shape as a rhetorical device. State what is true.

| Instead of | Write |
|---|---|
| `This is not a preference, it is a requirement` | `This is a requirement` |
| `Not a rendering bug, an authoring choice` | `The dark fill comes from a style directive in the source` |

`Use X rather than Y` is an instruction, not antithesis. It is permitted.

### No unverified claims

State only what the repository or returned host output supports. Where a claim is
carried forward but unproven, mark it inline:

```
(unverified) The modem bypass procedure restores service within five minutes.
```

Use `(unverified)`, `(untested)`, or `(needs check)` followed by the claim. Add the
item to [`03-pending-and-risk-register.md`](../00-project-context/03-pending-and-risk-register.md)
in the same edit. Do not delete the claim, and do not silently promote it to fact.

### No fabricated precision

Do not quote a line count, a duration, a hash, or a percentage that was not measured.
An unverified figure is worse than no figure, because it survives into a decision.

## Structure

Headings name a feature or a fault. A heading that could sit on any document is not a
heading.

| Instead of | Write |
|---|---|
| `Overview` | `Boot order and passthrough` |
| `Additional notes` | `Upgrade removes both artifacts` |
| `Considerations` | `SNMP enforces authentication, not privacy` |

Break text into blocks a reader can scan. Prefer a table for anything comparative,
sequential with branches, or enumerable. Prefer a numbered list for anything executed
in order.

Commands are literal text on their own line. Never put a command and its explanation
on the same line.

Cut generic openers, restated context, and summaries of the paragraph above.

## Keep all context

Brevity applies to the wording, not to the content. Do not delete a procedure, an
evidence reference, a rationale, a configuration value, or a correction in the name of
tone. Cut the words around the fact, keep the fact.

Where a section is long because the subject is complex, break it into sub-headings and
tables. Do not summarise it away.

## Ledger exemption

[`10-change-log.md`](../10-change-log.md) and
[`02-decisions-register.md`](../00-project-context/02-decisions-register.md) are
append-only records. They are exempt from the brevity rules above and keep their full
narrative and reasoning. A compressed decision gets re-litigated later.

The wording rules still apply to them. Em dashes, banned openers, and aphorism formulas
are removed. Existing entries are corrected in place for wording only, never for
substance.

## Print documents

Removed from this copy. The print, typography, cover and figure rules are specific to
the source repository and do not apply here.

## Applying this to existing documents

The mechanical rules were applied repository-wide on 2026-09-15. Structural rewriting
happens per chapter, when that chapter is next edited for another reason (D-187).

When editing any document, bring it to these conventions before committing. Do not
open a separate rewrite pass for a file you are not otherwise touching.

## Checking

```bash
make prose
```

```bash
python3 tests/prose-conventions/run.py --verbose
```

The checker reports file, line, and the matched text. It exits non-zero on any
violation.
