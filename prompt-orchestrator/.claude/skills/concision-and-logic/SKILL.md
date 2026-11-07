---
name: concision-and-logic
description: 'Cut verbosity and check the reasoning of any English draft, whichever
  model or person wrote it: answer first, a length budget, a claim-by-claim support
  check, the logic faults fluent drafts hide (unsupported universals, non sequiturs,
  scope shifts, restated premises, mixed-level lists, unrequested options), and the
  shape-level AI tells of GPT, Claude and Gemini drafts. Bundles a standard-library
  scanner for universals, verdict sentences, meta-notes, parentheses, importance flags
  and hedge stacks, plus a dated research reference of tells per model family. Use
  when a draft is too long, rambles, yaps, reads as AI-written, ''sounds like Gemini
  or ChatGPT'', or when asked to tighten, shorten, check the logic or argument, or
  review a report, email or form before it is sent. Use it on the request alone, before
  the draft is pasted or opened: ''this draft'', ''this answer'' or ''this paragraph''
  with no text attached yet still needs it.'
argument-hint: '[file path or text] [--genre academic|professional]'
---

<!-- Generated from skills/concision-and-logic.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Concision and logic check

A draft can be grammatical, polite and well formatted and still say little, or say something
that does not follow. This skill finds both. It runs on any draft, from any model or person,
before `human` and after the genre skill (`academic-writing` or `professional-writing`).

Order for a document that will be submitted or sent:

1. Genre skill: `academic-writing` for graded or scientific documents, `professional-writing`
   for emails, platform notes, PR and issue text, and reports to a supervisor.
2. This skill: length, logic, shape-level tells.
3. `human` (audit, then rewrite only confirmed spans).
4. `prose-and-wording` checks (em dash, openers, aphorisms, antithesis).

## Rules

1. **Answer first.** The first one or two sentences carry the main point: the result, the
   decision, the request. Background follows only if the reader needs it to act.
2. **One job per sentence.** A sentence states one fact, one claim with its support, or one
   request. Split a sentence that does two.
3. **Every claim has support you can point to**: a measurement, a test, a citation, a file, a
   decision record. A claim without support is cut, marked `(unverified)`, or turned into a
   question for the owner. Never invent support.
4. **Name the members instead of quantifying over them.** "Every figure is configurable" and
   "any node can relay" hide which figures and which nodes. List them, or state the condition
   under which the claim holds.
5. **State scope as a list, not as a verdict.** Replace "X is in scope, and Y is not" with an
   In scope / Out of scope list or table.
6. **No notes about the text.** Delete "note that", "this means", "as mentioned above", "the
   following section describes", "sample values". Put a value's status in a table column
   (`Default`, `Measured`, `Planned`).
7. **Parentheses for references, units, abbreviations and short codes only.** Anything that needs a
   verb inside the brackets becomes its own sentence or a table cell.
8. **Show the consequence instead of announcing importance.** Cut "this matters", "crucially",
   "plays a key role"; give the number, failure or cost that makes it matter.
9. **One hedge per uncertainty, tied to its cause.** "Results from 3 nodes may not hold for 20"
   instead of "this may potentially provide some indication".
10. **No unrequested options, previews, recaps or outlooks.** One answer when one was asked.
    No "Here is a breakdown", no closing summary of what the reader just read, no "looking ahead"
    unless the plan is already decided.
11. **Keep the content.** Concision cuts words around facts, never the facts, the procedure, the
    evidence or a limitation (prose-and-wording, Keep all context).

## Length budget

Set the budget before editing, from what the reader needs:

| Text | Budget |
|---|---|
| Platform note, submission comment, chat status | 1 to 3 sentences |
| Email or message to a supervisor | Under 150 words; the request in the first two lines |
| PR or issue body | What changed, why, how it was checked; one short paragraph or list each |
| Answer to a factual question | The answer, then at most one sentence of support |
| Report section | Set by the template; within it, no sentence that a reader could delete without losing a fact |

A draft over budget is cut by deleting sentences that carry no fact, then merging sentences that
repeat a fact. Shortening every sentence evenly produces staccato, not concision.

## Logic check

Run this on every paragraph that argues, compares, scopes or concludes. It is a manual check:
the scanner below does not test logic. It cannot find a non sequitur, a scope shift, a restated
premise, a mixed-level list or any other fault in the table below; only reading the claims in
order finds them. Write each claim on its own line, then fill the table:

| Claim | Support (where) | Follows from the previous claim? | Fault |
|---|---|---|---|

Faults to look for:

| Fault | Sign | Fix |
|---|---|---|
| Unsupported universal | "every", "any", "all", "always", "never" with no list or proof | List the members or state the condition |
| Non sequitur | "Therefore", "so", "as a result" joining claims with no causal link | Give the missing step, or remove the connective |
| Scope shift | Evidence about one component, claim about the whole system | Narrow the claim to what was tested |
| Restated premise | The conclusion repeats the introduction in other words | Replace with the actual result, or cut |
| Mixed-level list | A goal, a tool and a risk in one bullet list | One level per list; split or regroup |
| Parallel bullets with no relation | Bullets that need "because", "unless" or "so" between them | Write them as sentences with the real connective |
| False dichotomy | "Either we use X or the system fails" | Name the other options or the evidence that rules them out |
| Correlation as cause | "After adding caching, users were happier" | Name the measurement and the confounders, or soften to what was observed |
| Contradiction across documents | A number, name or scope that differs between sections or documents | Pick the verified value and fix every copy |
| Circular definition | "A checkpoint is a point where hikers check in" | Define by function and boundary |

Gopen and Swan's reader-expectation principles help with sentences that are correct but hard to
follow: put old, linking information at the start of a sentence and the new point at the end;
keep the subject close to its verb ("The science of scientific writing", *American Scientist*,
1990).

## Scanner

`scripts/draft_scan.py` (next to this file) is standard-library Python 3:

```bash
python3 <skill-dir>/scripts/draft_scan.py draft.md --genre academic
```

```bash
python3 <skill-dir>/scripts/draft_scan.py - --genre professional < note.txt
```

It prints JSON (`metrics`, `counts`, `notes`, `findings` with line, category, severity, match,
sentence and advice) and exits 1 when it flags anything. Categories: `universal`, `verdict`,
`meta`, `importance`, `summary`, `hedge`, `copula`, `participle-tail`, `ai-vocab`, `dash`,
`parenthesis`, `long-sentence`. Severity is `normal`, or `low` for a parenthesis under four words
that is not a citation, number or abbreviation. Code fences, inline code and block quotes are
skipped. Every finding is a candidate: a quoted requirement, a definition that really is
universal, or a citation in parentheses stays.

The scanner tests wording, not reasoning. A draft it passes can still hold a non sequitur, a
scope shift, a restated premise or a mixed-level list. Run the logic check above on every draft
that argues or concludes, whatever the scanner reports. Self-tests:

```bash
python3 -B -m unittest discover -s <skill-dir>/scripts -v
```

## Before and after

Examples come from the TrekLink registration form (2026-11-07). Bracketed values stand for the
team's own figures.

| Before | After |
|---|---|
| Every figure is a configurable parameter. | The check-in interval and the overdue threshold are set per event by the organiser. Table 4 gives the defaults. |
| Any rented node can serve as a temporary relay checkpoint. | A rented node relays messages while it is powered and within [range] of another node. |
| Targeted firmware enhancements made during the capstone are in scope and credited, and re-architecting the mesh stack is not. | In scope: the firmware changes listed in Section 4.2. Out of scope: replacing the mesh protocol stack. |
| Note that the thresholds below are sample values. This means that the organiser can change them. | The organiser sets these thresholds per event. Table 4 lists the defaults. |
| This matters because hikers frequently lose signal in mountainous terrain, highlighting the need for a dependable offline solution. | On the [route] survey, [n] of [m] hikers lost phone signal for more than [t] minutes. The app therefore queues check-ins offline. |
| Here is a breakdown of the key benefits: offline support, Firebase, safety. | The app works without phone signal. Check-ins sync to Firebase when the mesh reaches a gateway. |

## Output

For a review, return a findings table (sentence, fault or tell, fix) followed by the revised text
with only the flagged sentences changed. For a rewrite request, return the revised text and a
one-line count of what changed (sentences cut, merged, rewritten). State which scanner findings
were left as they are and why.

## Reference

`references/ai-tells-by-model.md`: tells of the GPT, Claude and Gemini families with an example
and a fix for each, the shared tells, and dated sources (Kobak et al. 2025, Reinhart et al. 2025,
Liang et al. 2023, Weber-Wulff et al. 2023, Wikipedia's Signs of AI writing, Graphite 2026,
YapBench 2026). Load it when diagnosing a draft or when asked which model a pattern comes from.
