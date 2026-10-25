---
name: prose-and-wording
description: >
  Wording rules for every document, comment, commit message, PR body and chat
  reply. Bans the em dash, banned openers, aphorism formulas, two-beat
  antithesis, unverified claims and fabricated precision. Always active. Use
  when writing or editing any prose, and when reviewing wording.
---

# Prose and wording

Always on. This is not a mode the user has to request. It applies to chat
replies, tracked documents, code comments, commit messages, PR bodies, issue
text and generated reports.

Ported from `enterprise-sleeper/_docs/11-conventions/09-prose-and-wording.md`.
The source, with the print and figure rules that belong to that repository
removed, is at `references/source-09-prose-and-wording.md`.

The reader is an operator looking for one specific thing, usually under time
pressure. Write for that.

## Hard rules

| Rule | Scope |
|---|---|
| No em dash `—` in prose | Everywhere |
| No en dash `–` as a clause separator | Everywhere |
| No generic openers | Everywhere |

An em dash inside a code fence, an inline code span, or a table cell used as a
"not applicable" placeholder is permitted. That is quoted content or data, not
prose. An em dash in quoted source text stays as written, because a quotation
is evidence.

### Replace the em dash

Join statements with a comma. Split into two sentences where the comma produces
a run-on. A colon works when the second clause explains the first. Parentheses
work for a true aside.

| Instead of | Write |
|---|---|
| `The rule is loaded — verify it drops traffic` | `The rule is loaded, verify it drops traffic` |
| `Two sites shared the defect — the second is worse` | `Two sites shared the defect. The second is worse` |
| `Hash a1bb75c5 — the pre-fix artifact` | `Hash a1bb75c5, the pre-fix artifact` |

### Banned openers

`Let's`, `In order to`, `It's worth noting`, `Needless to say`, `At the end of
the day`, `It goes without saying`, `Simply put`.

Delete the opener and start with the statement.

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

`Use X rather than Y` is an instruction. It is permitted.

### No unverified claims

State only what the repository or returned tool output supports. Where a claim
is carried forward but unproven, mark it inline:

```
(unverified) The modem bypass procedure restores service within five minutes.
```

Use `(unverified)`, `(untested)` or `(needs check)` followed by the claim. Add
the item to the repository's risk or pending register in the same edit. Do not
delete the claim, and do not silently promote it to fact.

### No fabricated precision

Do not quote a line count, a duration, a hash or a percentage that was not
measured. An unverified figure is worse than no figure, because it survives
into a decision.

## Structure

Headings name a feature or a fault. A heading that could sit on any document is
not a heading.

| Instead of | Write |
|---|---|
| `Overview` | `Boot order and passthrough` |
| `Additional notes` | `Upgrade removes both artifacts` |
| `Considerations` | `SNMP enforces authentication, not privacy` |

Break text into blocks a reader can scan. Prefer a table for anything
comparative, sequential with branches, or enumerable. Prefer a numbered list
for anything executed in order.

Commands are literal text on their own line. Never put a command and its
explanation on the same line.

Cut generic openers, restated context, and summaries of the paragraph above.

## Keep all context

Brevity applies to the wording, not to the content. Do not delete a procedure,
an evidence reference, a rationale, a configuration value or a correction in
the name of tone. Cut the words around the fact, keep the fact.

Where a section is long because the subject is complex, break it into
sub-headings and tables. Do not summarise it away.

## Ledger exemption

Append-only records, decision registers and change logs keep their full
narrative and reasoning. A compressed decision gets re-litigated later. The
wording rules still apply to them: em dashes, banned openers and aphorism
formulas are removed. Existing entries are corrected in place for wording only,
never for substance.

## Applying to existing documents

Bring a file to these conventions when you edit it for another reason. Do not
open a separate rewrite pass for a file you are not otherwise touching, unless
the user asks for exactly that.

## Checking

Repositories that carry the source convention run:

```bash
make prose
```

```bash
python3 tests/prose-conventions/run.py --verbose
```

Where no checker exists, grep before committing:

```bash
grep -rn '—' --include='*.md' .
```
