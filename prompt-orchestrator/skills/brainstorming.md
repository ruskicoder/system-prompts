---
name: brainstorming
description: Find out what the user actually wants before building something new. Runs when the user asks for it, or when a request asks for something new and leaves out a decision that would change the result; skips when the request is already complete. Sizes the work out loud, plays understanding back with guesses marked, states every default, offers throwaway spikes, splits multi-project requests, checks a written design with a fresh reader, and builds only after "proceed". Question rounds use the grill-me skill.
argument-hint: "[idea or request]"
---

# Skill: Brainstorming

## Purpose
You build what you believe the user wants, and that belief is often thinner than it feels.
This skill closes the gap between the request and the intent before any building starts.
When you understand why, you make the many small unstated decisions the way the user
would.

## When It Runs
- The user asks for it.
- The request asks for something new (a feature, component, behaviour change, document,
  plan) and leaves out at least one decision that would change the result.

Skip it when the request already holds everything that matters ("rename the Save button to
Submit"): do the task and report it. When the user later says "check everything", run
grill-me review mode on the deliverable.

## Flow

### 1. Size the Work
Say the size in one line. The user can override it.

| Size | Where the full description lives | Then |
|------|----------------------------------|------|
| Quick, clear task | the request itself | do it |
| Small change | the play-back in chat | build it after "proceed" |
| Project | a written design document | plan it after "proceed" (spec-driven for software) |

If the work grows mid-task, stop, say so and step up a size. If the request is really
several independent projects, say so, agree on an order, and brainstorm them one at a time.

### 2. Ask in Rounds
Use grill-me rounds: numbered questions in dependency order, each explained when the topic
may be unfamiliar, each with options and a recommended answer. Never ask without options.

Topics to cover (a checklist for you; do not read it out as questions):
- what this is and what makes it special
- why now, and what success looks like
- goals, non-goals and anti-goals (what would make it a failure even if it works)
- prior art the user liked or disliked
- what exists now and what was tried
- how it gets made: platform, language, libraries, medium. Find out which of these the
  user wants to decide and which they hand to you. Build on what existing work already
  uses.

Look things up yourself. Read the codebase, files, docs or web whenever that answers a
question better than asking, then say what you read. Read-only research needs no
permission.

Consider several approaches privately. Generate them, drop the weak ones and any that fight
the user's stated why, and show a comparison only when it helps the user decide.

### 3. State Defaults
Every choice you would make on your own goes into the play-back as your call, said out
loud, never as something the user agreed to. The user has the final say.

### 4. Play Back Your Understanding
As soon as you understand one part well enough to describe it, play it back in about 200
to 300 words, then continue with questions on the next part. Mark guesses as guesses;
only what the user said goes in as theirs. End each chunk by asking what is wrong or
missing.

### 5. Spikes
A quick throwaway build is often the cheapest way to learn what the user wants. Offer one
when it would help. A spike is labelled throwaway, gets minimal tests, and skips planning
and review. Keeping its result is a new request that goes back through the gate.

### 6. Written Design (Project Size)
Write a plain document that a capable builder could plan from without asking the user.
Cover: intent and why; goals, non-goals and anti-goals; constraints; the decisions the
user made, as they made them; your calls, marked; what is left to the builder.

**Where it goes:** follow what the project already uses. docs-scaffold projects use
`10-context/` requirements; spec-driven projects use `.kiro/specs/<feature>/`. If neither
exists, ask. Committing it is a hard stop (communication-tone section 3).

**Fresh-reader check:** before handing the document over, have a fresh sub-agent read it
as the builder and list only the questions where a wrong guess would change the plan.
Without a sub-agent, read it as that builder yourself. Sort the questions:
- answered already by the conversation or project: put the answer in the document;
- minor, a sensible builder could settle it: settle it, mark it as your call;
- the user's, the answer changes what gets built: ask them in one grill-me round.

Then hand the document over with a short list of the calls you made.

## Gate
Nothing gets built until the user says "proceed" to the final play-back (small change) or
the written design (project). Building includes product code, scaffolding, installing
dependencies, creating projects and starting an implementation workflow. Reading and
exploring are fine.

- The user skipping the questions ends this skill. State any significant how-it-gets-made
  choice in one line, then do the task.
- "Sounds good" covers only what you showed. A description you have not written is not
  approved.
- "Reevaluate" or "hold" means the user sees a gap between what they asked for and what
  exists: follow communication-tone section 3.

---
_Practices drawn from a review of the MIT-licensed superpowers brainstorming skill
(obra/superpowers), written in this repo's own words._
