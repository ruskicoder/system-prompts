---
name: prose-and-wording
description: 'Wording rules for every document, comment, commit message, PR body and
  chat reply. Bans the em dash, banned openers, aphorism formulas, two-beat antithesis,
  unverified claims and fabricated precision. Addendum A bans the sentence-level AI
  patterns: inline-list colons, sweeping quantifiers, trailing conditions, back-reference
  pronouns, loose articles, X-not-Y contrast, dashes and comma splices. Always active.
  Use when writing or editing any prose, and when reviewing wording.'
---

<!-- Generated from skills/prose-and-wording.md by tools/generate_integrations.py. Edit the source file, not this one. -->

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

Split into two sentences. A colon works when the second clause explains the
first. Parentheses work for a true aside.

| Instead of | Write |
|---|---|
| `The rule is loaded — verify it drops traffic` | `The rule is loaded. Verify that the rule drops traffic` |
| `Two sites shared the defect — the second is worse` | `Two sites shared the defect. The defect is worse at the second site` |
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
| `Considerations` | `SNMP enforces authentication only` |

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

## Addendum A: Sentence-level AI patterns

The addendum covers body prose in chat replies, documents, code comments, commit messages, and PR and issue
text. Tables, captions, code, identifiers, quoted text and fixed sentences required by the governing template
or guideline are exempt.
Rule of repair: change sentence shape only. Keep every fact, item, condition, quantity and scope word.

### A1. No colon before an inline list
A colon that introduces a list inside a sentence is an AI pattern. Put the items first as a condition, then give
the main clause.

Before: Response data is generated once, when the session ends, for every result: success, error, user cancel and timeout.
After:  For success, error, user cancel and timeout, the response data is generated once when the session ends.

Applies also to label lines ("Base class of the workers: lifecycle, callback and thread posting.").
After:  Base class of the workers (lifecycle, callback and thread posting).

### A2. No sweeping quantifiers
Do not write "every", "any", "all", "each", "always", "never" as filler. Name the items instead.
Keep the quantifier only when the source states a universal rule, and keep it exactly in that case.

Before: The handler is called for every result.
After:  The handler is called for success, error and timeout.

### A3. Condition, time and place first
Put "During ...", "On ...", "When ...", "For ...", "If ..." at the start of the sentence, not after the main clause.

Before: The worker reads the records on the background thread.
After:  On the background thread, the worker reads the records.

### A4. No back-reference pronouns
Do not use "it", "them", "they", "this", "that" to point at a noun from the previous clause or sentence. Repeat
the noun, or merge the verbs on the same object.

Before: The controller then creates the worker for the request type and starts it.
After:  Then, the controller creates and starts the worker for the request type.

### A5. Sequence word at the start
Write "Then," or "After that," at the start of the sentence. Do not insert "then" between the subject and the verb.

### A6. Use articles sparingly
Do not open sentences with "A [noun]" for something the reader already knows. Use "the" for defined items. Drop
articles before names, identifiers and code terms.

Before: A cancel request received during initialization ends the session as cancelled.
After:  During initialization, the cancel request ends the session as cancelled.

### A7. No "X, not Y" contrast
State the positive fact only.

Before: The input screens are displayed by the external app, not by this app.
After:  The external app displays the input screens.

### A8. No dashes
Do not use em dashes, en dashes as punctuation, or " - " as a dash. Use a comma, a period or parentheses.
Parentheses hold a short list of nouns or a short aside with no verb inside.
Write a numeric range with a hyphen, as in 3 - 5 or 16 - 24 px. A hyphen between two numbers marks a range.

### A9. No comma splices or reversed fragments
Write one fact per sentence, in the order subject, verb, object, after any leading condition from A3. Do not chain
clauses with commas, and do not use inverted fragments ("Generated once, the data ...").

### Self-check before delivery
1. Search for ":" inside body sentences.
2. Search for every / any / all / each / always / never.
3. Search for sentences starting with or ending in it / them / they / this.
4. Search for em dashes, en dashes and " - " outside numeric ranges.
5. Search for ", not ".
6. Compare each rewritten sentence with its original. Item lists, conditions, numbers and negations must match.
