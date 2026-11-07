---
name: thesis-defense
description: "Prepare a team for a capstone or thesis defence: build a question bank from the team's own documents (register, Reports 1 to 6, SRS, SDD, slides), run a consistency check that the register, reports, slides and demo agree on scope, features, numbers, names and roles, map every registered function to a demo step ('demo exactly what you registered'), assign each question to the member who built that part, and rehearse answers in a short, evidence-first shape. Use when preparing for a defence, review or committee presentation, generating likely examiner questions, checking documents against each other or against the demo, planning a demo script, or running a mock defence."
argument-hint: "[documents folder or files] [questions | consistency | demo | mock]"
---

# Thesis and capstone defence

A committee tests two things: that the product is what the team registered, and that each member
understands the part they claim. Most lost marks come from contradictions between documents, a
demo that shows something other than the registered scope, and answers that wander. This skill
prepares for all three from the team's own files. Never invent a fact, number or feature to fill
an answer: an answer the team cannot back is worse than "we did not test that".

## Modes

| Mode | Input | Output |
|---|---|---|
| `consistency` | All submitted documents, slides, demo script | Contradiction table and fixes |
| `questions` | The documents, the member list with their parts | Question bank with owner and source per question |
| `demo` | The register and the demo plan | Function-to-demo map with fallbacks |
| `mock` | The question bank | A mock defence: one question at a time, answer review |

A bare `/thesis-defense` runs `consistency`, then `demo`, then `questions`.

## 1. Consistency check

Extract these facts from every document and compare them across documents:

| Fact | Where it appears |
|---|---|
| Project name, team members, roles, supervisor | Register, every report cover, slides |
| Problem statement and target users | Register, Report 1, slides |
| Function list (each registered function) | Register, SRS use cases, SDD components, demo script |
| In-scope and out-of-scope items | Register, Report 1, slides |
| Technology stack and versions | Register, SDD, code (`package.json`, firmware build files) |
| Numbers: users, nodes, range, latency, cost, test counts | Every report, slides |
| Terms and abbreviations | Every document's first use |
| Schedule and milestones | Register, progress reports |

Report as a table: fact, value per document, verdict (consistent, contradiction, missing), fix
(which value is verified and which documents change). A value is verified when the code, a test
log or a decision record supports it; when none does, the team decides before the defence and
every copy changes to match.

## 2. Demo what you registered

Map each registered function to the demo:

| Registered function (register wording) | SRS ID | Demo step | Who drives it | Data or device needed | Fallback |
|---|---|---|---|---|---|

Rules:

- Every registered function has a demo step, or a written reason it is not shown and where the
  evidence is (a test report, a recording).
- The demo shows registered functions first, in register order. Extras come after, labelled as
  extras.
- Use the register's names on screen and in speech. If the app says "Trip" and the register says
  "Event", the committee hears two features.
- A fallback for every step that depends on hardware, network or a third-party service: a
  recording made on the real system, with its date, and a statement that it is a recording.
- Rehearse on the defence room's network and power conditions, with the devices charged and the
  accounts logged in.

## 3. Question bank

Generate questions from the documents, section by section. For each section ask:

| Kind | Question shape |
|---|---|
| What | What does this component do? What exactly is in scope? |
| Why | Why this technology, protocol or design and not the obvious alternative? |
| How measured | How did you measure this number? On what setup, how many runs? |
| Limits | What happens when it fails (no signal, battery low, node lost)? What did you not test? |
| Ownership | Which part did you build? Walk through its code or circuit. |
| Consistency | Report 2 says X, the demo shows Y. Which is right? |
| Process | How did the team split work, review code, track tasks? How was AI used? |

For each question record: the question, the source (document and section), the member who
answers, the evidence they cite (table, test, commit, file), and a model answer that has passed
the anti-AI check in section 4. Every member
needs questions on their own part; a committee often asks a member about code they did not write.
Prepare for that with a one-minute overview of every part.

On AI use: answer what the team's AI-use statement says, plainly. If tools were used for language
editing or code assistance, say so, and show that the member can explain the result without them.

## 4. Answer shape

1. The direct answer in the first sentence: "Yes", "No", "[n] nodes", "LoRa, because...".
2. The evidence: the table, test or code that shows it.
3. The limit, if there is one: "We tested up to [d] m. Range beyond that is untested."

Stop there. No restating the question, no "that's a great question", no tour of related
features. If the answer is unknown: "We did not measure that. We would test it by...". Under 45
seconds for most answers.

| Weak answer | Strong answer |
|---|---|
| "That's a great question. Our system is designed with reliability in mind, leveraging a robust mesh architecture that ensures messages are delivered in a variety of conditions..." | "In our field test, [k] of [n] messages arrived at the base within [t] s over [h] hops. The failed messages were sent when [cause from the test log]. Table [x] in Report [y]." |

Fill every bracket from the team's own test log, report or code before rehearsal. A bracket the
documents cannot fill stays open and becomes "We did not measure that", never an estimate.

Every written answer goes through the anti-AI check before the team rehearses it: model answers
in the question bank, the one-minute overviews, review notes from the mock defence, the AI-use
answer and the slides. The check is `draft_scan.py` from `concision-and-logic` with
`--genre professional`, the logic table in that skill, and the tells table in
`academic-writing`. An answer with a tell or an unsupported claim is rewritten before anyone
learns it.

## 5. Mock defence

Ask one question at a time from the bank, starting with the highest-risk ones (contradictions,
untested limits, ownership). After each answer, review it against the answer shape: did the first
sentence answer, was evidence cited, was the length under 45 seconds of speech (about 110 words).
Run the anti-AI check on every written review note and revised answer. Record weak answers for
another round.

## Checklist before the defence

- [ ] Consistency table has no open contradiction.
- [ ] Every registered function maps to a demo step or a documented reason.
- [ ] Every member has rehearsed questions on their own part and an overview of the others.
- [ ] Every number in the slides is in a report, and every number in a report has its test.
- [ ] Fallback recordings exist and are dated.
- [ ] The AI-use answer matches the team's written statement.
- [ ] Every written answer, every overview and every slide passed the anti-AI check in section 4:
      no tells, no unsupported claims, no bracket left filled with a guess.

## Related skills

`academic-writing` (fixing the documents the check flags), `concision-and-logic` (tightening
answers and slides), `grill-me` (question rounds with the leader on open decisions).
