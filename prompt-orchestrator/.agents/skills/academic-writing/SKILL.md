---
name: academic-writing
description: 'Write and revise scientific, thesis and capstone documents in plain,
  precise English: university capstone reports (FPT SEP490 register or registration
  form, Reports 1 to 6, SRS, SDD, final thesis), papers, related-work sections and
  abstracts. Claims backed by evidence, real citations only with every DOI and URL
  checked (bundled Crossref checker), IEEE or APA reference lists, terms defined once
  and used consistently, requirement wording, related-work comparison, and removal
  of the AI tells graders notice (universal claims, verdict sentences, parenthetical
  asides, meta-notes, importance flags, era vocabulary of GPT, Claude and Gemini).
  Use when drafting, rewriting, reviewing or grading any academic or capstone document,
  adding references, or when a report reads as AI-generated.'
argument-hint: '[document or section] [--style ieee|apa]'
---

<!-- Generated from skills/academic-writing.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Academic writing

For documents a lecturer, supervisor or committee grades: capstone registration forms, progress
reports, SRS and SDD documents, theses, papers. The reader checks three things: is each claim
true, can the team show where it comes from, and did the team write it. This skill serves all
three. It does not try to beat AI detectors: they misclassify non-native English writers
(Liang et al., 2023) and are not reliable (Weber-Wulff et al., 2023). The aim is a document
whose every sentence the team can defend at the defence.

Pipeline for a submitted document: this skill, then `concision-and-logic` (length, logic,
scanner), then `human` (audit, then rewrite only confirmed spans), then the `prose-and-wording`
checks. Defence preparation from the finished documents is `thesis-defense`.

## Hard rules

1. **No claim without evidence.** Each factual sentence rests on a citation, a measurement from
   the team's own tests, a design section, or a decision the team made and can name. Mark
   anything else `(unverified)` and raise it with the writer; never smooth it into fact.
2. **Real references only.** Follow `references/citations.md`: open the source, find the
   supporting passage, run `scripts/check_refs.py` on the reference list. A reference that fails
   is removed, with the claim it supported. Never invent an author, title, year, DOI or page.
3. **One style, applied exactly.** IEEE or APA 7 as the template requires; formats in
   `references/citations.md`.
4. **Define each term once, then keep it.** First use: the full term and its abbreviation,
   "Software Requirements Specification (SRS)". After that, the same word every time. Do not
   rotate synonyms (node, device, unit, beacon) for one thing; a reader assumes four words name
   four things.
5. **No AI tells.** The tells graders notice are in the next section. Run the scanner from
   `concision-and-logic` on every draft.
6. **The team's words and the team's facts.** Keep the writer's terms, numbers, names and scope.
   Add no feature, result, user count or partner the writer did not give. A rewrite that
   reads better but claims more is a failed rewrite.
7. **Disclose AI use as the course requires.** If the course or school policy asks for an AI-use
   statement, write it plainly: what tool, for what (language editing, translation), and that the
   team checked every claim. Do not hide use the policy asks to be declared.

## The tells graders notice

Full list per model family, with sources, in
`<skills-dir>/concision-and-logic/references/ai-tells-by-model.md`. The ones found in the
TrekLink register (2026-11-07):

| Tell | Before | After |
|---|---|---|
| Universal claim | Every figure is a configurable parameter. | The check-in interval and the overdue threshold are set per event by the organiser (defaults in Table 4). |
| Universal capability | Any rented node can serve as a temporary relay checkpoint. | A rented node relays messages while it is powered and within range of another node. |
| Two-clause verdict | Targeted firmware enhancements made during the capstone are in scope and credited, and re-architecting the mesh stack is not. | In scope: the firmware changes listed in Section 4.2. Out of scope: replacing the mesh protocol stack. |
| Parenthetical aside | A loss can be reported (by the hiker or, where applicable, by the organiser) from any working state (see Table 2). | A loss can be reported from any of the six working states. The hiker or the organiser reports it. |
| Meta-note | Note that the values below are sample values. This means that they can be changed. | The organiser sets these values per event. Table 4 lists the defaults. |
| Importance flag | This matters because safety is crucial in remote areas. | Give the fact that makes it matter, with its source. |
| Corrective frame | A successful demo does not by itself establish field readiness. | The demo covered [n] nodes over [d] m. Range above [d] m is untested. |
| Era vocabulary | The system leverages a robust, multifaceted architecture. | Name the components and what each does. |

## Sentences

- Subject and verb early; the new information at the end of the sentence (Gopen and Swan, 1990).
- Past tense for what the team did ("We measured latency on 3 nodes"); present tense for what the
  system does and for established facts ("The gateway forwards packets to Firestore").
- "We" for the team's actions is acceptable in capstone reports and most engineering venues; use
  the passive only when the actor is unknown or irrelevant. Follow the template if it forbids
  "we".
- Numbers with units and a space: "2 s", "400 m", "20 %" (or "20%" if the template uses it; be
  consistent).
- Articles and plurals: check "the", "a" and plural "s" in every sentence. These are the most
  common slips for writers whose first language has no articles, Vietnamese included, and a
  grammar tool catches most of them.
- One idea per sentence. A sentence over about 35 words usually holds two.

## Requirements (SRS)

Each requirement is one sentence that can be tested:

| Before | After |
|---|---|
| The system should be fast and user-friendly. | FR-12: The app shall show the hiker's last check-in within 3 s of opening the event screen. |
| The system must handle all users. | NFR-3: The backend shall serve 200 concurrent hikers per event with a median response under 500 ms. |

- "shall" for a requirement, "should" for a goal, "will" for a statement of fact or intent; never
  mix them inside one requirement.
- An ID, one behaviour, a measurable condition, the actor. No "and/or", no "etc.", no "user
  friendly", "fast", "robust", "seamless" without a number.
- If the template follows a standard, follow it: ISO/IEC/IEEE 29148 for requirements, IEEE 1016
  for software design descriptions.

## Related work

- Group by approach (mesh messaging apps, satellite messengers, check-in services), not by paper.
- For each group: what it does, with a citation; how it differs from the team's system on a
  stated dimension (works without phone signal, cost per hiker, needs a guide). A comparison
  table with the same columns for every product is often clearer than prose.
- The gap is a fact you can show ("none of the four apps in Table 1 alerts a base station without
  a phone or satellite signal"), not a claim of novelty ("no existing solution addresses...").
- Do not write "many researchers have studied" or "extensive research exists" without the
  citations that show it.

## Abstracts and the register

A registration form or abstract answers, in this order and in one sentence each where possible:
the problem and who has it, what the team builds, how it works at the level a reader needs, what
is in scope and out of scope (as a list), and how success will be measured. No outlook, no
importance claims, no notes about the form itself.

## Review checklist

Run before handing the draft back:

- [ ] Every factual sentence has its evidence, or is marked `(unverified)`.
- [ ] `check_refs.py` ran on the reference list and reports every line `ok`. It checks every DOI
      and URL on a line. A line with neither is reported `unchecked, no identifier`: verify that
      source by hand, by ISBN or standard number, and record how. A `network` error is not a
      pass: run the check again where Crossref is reachable.
- [ ] Every source was opened and contains the passage the citing sentence relies on. A DOI
      that resolves and a URL that answers do not show this.
- [ ] One citation style, applied to every entry; every in-text citation has an entry and every
      entry is cited.
- [ ] Each term and abbreviation defined once, then used without synonyms.
- [ ] `draft_scan.py --genre academic` run; each remaining finding has a reason to stay.
- [ ] No universals without a list or condition, no verdict pairs, no meta-notes, no
      parenthetical asides with verbs.
- [ ] Numbers, names, scope and feature lists match the team's other documents (see
      `thesis-defense` consistency check).
- [ ] `human` audit run; only confirmed spans changed.
- [ ] No em dash in prose; no en dash as a clause separator.

## Output

For a review: a findings table (location, problem, fix), then the revised section with only the
flagged sentences changed, then the list of references removed or still unverified. For a draft:
the text, its reference list, and the checker's summary line.

## Reference files

| File | Read when |
|---|---|
| `references/citations.md` | Adding, checking or formatting references (IEEE, APA 7) |
| `scripts/check_refs.py` | Verifying a reference list: `python3 <skill-dir>/scripts/check_refs.py refs.md`. Needs network. Self-tests: `python3 -B -m unittest discover -s <skill-dir>/scripts -v` |
| `<skills-dir>/concision-and-logic/references/ai-tells-by-model.md` | Diagnosing tells per model family, with sources |
