---
name: grill-me
description: Interview the user in rounds until every decision behind a plan, design
  or deliverable is settled. Numbered questions in dependency order, each explained
  when the topic may be unfamiliar, each with options and a recommended answer that
  "yes" accepts. Facts are looked up, never asked. Review mode checks a finished deliverable
  against what was agreed. Use when the user says "grill me", "check everything",
  or when the brainstorming skill hands over its question rounds.
argument-hint: '[plan, idea or deliverable to grill] [review]'
license: MIT (adapted from Matt Pocock's grilling skill). Complete terms in LICENSE.txt
---

<!-- Generated from skills/grill-me.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Skill: Grill Me

## Purpose
Reach a shared understanding with the user before anything is built, and confirm after
delivery that the result matches it. Questions are cheap; building the wrong thing is not.

Runs only when the user asks for it ("grill me", "check everything", "grill me on the
result") or when the brainstorming skill hands over its question rounds. It never starts
on its own during ordinary work.

## The Design Tree
Map the plan as a tree of decisions. Each decision branches into the decisions that depend
on it. The **frontier** is every open decision whose prerequisites are already settled:
the questions you can ask now without guessing at answers you have not heard.

## Rounds
1. Ask the whole frontier in one round. Number the questions across the session
   (Q1, Q2, ...).
2. Wait for the answers.
3. Recompute the frontier. Settled decisions unblock the ones that depended on them.
4. A question that depends on another question still open in this round belongs to a later
   round.
5. Repeat until the frontier is empty.

## Question Format
Every question carries options. Never ask an open question with nothing to choose from.

```
**Q1. <short title>**
<one or two sentences of context when the topic may be unfamiliar: what it is and why the
choice matters>
- (a) <option>: <consequence>
- (b) <option>: <consequence>
- (c) Something else, in your own words

Recommended: (a). <one-line reason>
```

- Put the recommended option first and word the question so "yes" accepts it.
- Two to four options. Always allow "something else".
- No emojis.

## Facts Versus Decisions
- Facts are your job. When a question needs a fact from the code, files, docs or the web,
  look it up before asking. Use a sub-agent where one is available, or your own tools
  otherwise. Ask the rest of the frontier while a lookup runs; only the questions that
  depend on it wait.
- Decisions are the user's. Put each one to the user and wait.
- Say every default you would apply out loud: the user can only reject a default they
  have heard. The user has the final say.

## Done
The session is done when the frontier is empty: every branch visited, nothing silently
assumed. Play back the full set of decisions. Act only after the user says "proceed". On
"reevaluate" or "hold", follow communication-tone section 3.

## Review Mode
Triggered by "check everything", "grill me on the result" or `review`.

1. List every decision agreed for the deliverable.
2. Next to each, show what was delivered and the evidence (file and line, test output,
   command result).
3. Mark each one: matches, differs, or cannot verify.
4. Grill the user only on the items that differ or cannot be verified, using the rounds
   and format above.
5. Fix what the answers require, re-verify, and report per communication-tone.

## Relationship to Other Rules
- communication-tone Phase 1 decides when scope questions are needed at all. This skill
  defines how to ask them when the user wants a full session.
- The brainstorming skill uses these rounds for new ideas.

---
_Adapted from the `grilling` skill in mattpocock/skills (MIT, Copyright (c) 2026 Matt
Pocock): restructured, with an explain-then-options question format, a tool fallback for
lookups, a proceed gate and review mode added. See LICENSE.txt._
