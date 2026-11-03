---
name: refactoring
description: Behaviour-preserving restructuring of existing code. Pin behaviour with tests before touching anything, keep two hats (restructure or change behaviour, never both in one step), make the change easy before making the easy change, map smells to the smallest technique, move symbols with reference-aware tools, and choose between refactor, sprout and strangle instead of a rewrite. Use for "refactor", "clean up", "untangle", "make this easier to change", legacy code without tests, or before a feature that is awkward to add.
argument-hint: "[file, module or goal]"
---

# Skill: Refactoring

## Purpose
Refactoring changes the shape of code and nothing else. Done well it makes the next change
cheap; done carelessly it is a rewrite with no safety net and a misleading name. This skill
keeps structure work and behaviour work apart, proves behaviour stayed the same, and picks the
smallest move that gets the code where it needs to be.

## When It Runs
| Situation | Path |
|-----------|------|
| A feature is awkward to add | Preparatory refactoring, then the feature (Part 3) |
| Code is hard to read or change, tests exist | Smell to technique loop (Part 4) |
| Code has no tests, or tests are thin | Pin behaviour first (Part 2), then Part 4 |
| A subsystem is too large to restructure in place | Refactor, sprout or strangle (Part 5) |
| A rename or move spans many files | Reference-aware moves (Part 6) |
| Long multi-file restructuring | Delegate to the harness `refactor` agent or the `refactor-fanout` workflow |

Build-discipline's Refactor rules apply throughout: define the behaviour boundary first, move
one ownership boundary at a time, preserve public interfaces, failure behaviour and ordering,
and keep every intermediate state building and green.

## Part 1: Two Hats
- **Structure hat**: rename, extract, inline, move, split. Observable behaviour does not change
  and the tests stay green the whole time without edits to their expectations.
- **Behaviour hat**: new or changed behaviour, with its test written first.
- Wear one hat per step. If a test expectation had to change, the step changed behaviour: it
  was not a refactoring. Undo it, or relabel it and give it its own test and its own commit.
- A bug found while refactoring is pinned as it is, the refactoring finishes, then the fix lands
  as its own step that moves the pinned expectation. When the correct behaviour is unclear, ask
  in one line; fix only the unambiguous part and state the assumption.

## Part 2: Pin Behaviour First
No net, no refactor.

- **Tests exist**: run them now and show the result. Confirm they exercise the code you will
  touch; coverage is a map of gaps, not a score to hit.
- **No tests**: write characterization tests that record what the code does today, bugs
  included. Feed varied inputs, capture outputs, assert those outputs. For large outputs, use a
  snapshot or approval-style test (the project's own tool, or a plain file comparison).
- **No runner available**: a small script that runs the pinned cases and exits non-zero on drift
  is a valid net. If the code cannot run here at all, say the net is unverified.
- **Untestable code**: the first refactoring is creating a seam (see `references/legacy.md`),
  done with the smallest possible edit, then the tests.
- Fake only real boundaries (clock, network, filesystem, database, randomness). Mask
  non-determinism (timestamps, generated ids, ordering) so the net does not fail on noise.
- Never delete, skip or loosen a failing test to finish a refactoring.

**When there is no time**: if pinning costs less than the refactoring (usually true for pure
logic), pin and refactor. If it costs more than the deadline allows, do not restructure: add
the new behaviour with sprout or wrap (`references/legacy.md`), record the debt, and move on.
Restructuring without a net because time is short is not an option.

| Excuse | Answer |
|--------|--------|
| "No time for tests" | Then there is no time to refactor; sprout and leave the old shape alone |
| "I can see it is equivalent" | Pure code is the cheapest to pin; pin it |
| "I will add tests after" | Tests written after pin the new behaviour, breakage included |
| "The fix is tiny, it can ride along" | A reviewer cannot separate it, and a revert drops the wrong half |

## Part 3: Make the Change Easy, Then Make the Easy Change
Before a feature, ask what makes it awkward: a long function, a hidden dependency, logic in the
wrong place, a misleading name. Fix that under the structure hat with tests green, then add the
feature under the behaviour hat. After the feature lands, clean what the change itself left
behind. Reject a patch that mixes a large functional change with unrelated structural churn.

## Part 4: Smell to Technique Loop
1. Name the smell in the code you need to change (`references/smells.md` maps each smell to
   candidate techniques; load it only when you need it).
2. Pick the smallest technique that removes it. Prefer local moves (rename, extract, inline)
   over new abstractions; introduce a pattern only when a second real case demands it, and
   then through the design-patterns skill (force, ladder, YAGNI gate).
3. Apply it in small, reversible steps, running the net after each step.
4. Stop when the change you came for is easy. Do not polish code nobody needs to touch.

When not to refactor: code that works and will not change; code you cannot pin; a request whose
real goal is a rewrite (that is an architecture decision, see Part 5).

## Part 5: Refactor, Sprout, or Strangle
| Situation | Choice |
|-----------|--------|
| Local mess, can be pinned | Refactor in place |
| New behaviour into risky untested code, no time to pin | Sprout (new tested unit called from the old code) or wrap (decorate the old behaviour) |
| A subsystem too large or risky to restructure in place | Strangler fig: build the new path behind a routing seam, move one capability at a time, keep both live, delete the old path when it carries no traffic |
| Pressure for a big-bang rewrite | Decline it as a refactoring; it is an architecture decision for the user, with its own spec |

A strangler migration names its deletion date and its routing check up front. A strangler
that never removes the old path is permanent double maintenance. Prove equivalence with a
parallel run or differential test (same inputs, old and new outputs compared) before routing
traffic. Details: `references/legacy.md`.

## Part 6: Reference-Aware Moves
Renames and moves across files change every caller. Use the strongest tool available, in order:
1. The agent's language-server tool (find references, rename symbol) when the harness has one.
2. The code graph (GitNexus `impact` and `rename`) when the repository is indexed.
3. A structural search and rewrite tool such as ast-grep for pattern-shaped changes. It matches
   syntax trees, not text; on Linux call the binary `ast-grep`, since `sg` is a system command.
   Test the rule on sample code before running it across the tree.
4. Plain text search only as a last resort, with every match reviewed by hand, including
   strings, configuration, docs and generated files.

Before the move, list the references and the public surface affected; after it, build, run the
net, and search again for the old name.

## Part 7: Checkpoints and Reporting
- A checkpoint is a green state that could be shipped. Keep each step small enough to review in
  its diff.
- Commit only when the user or the approved plan authorizes commits (communication-tone hard
  stops); the harness `refactor` agent commits on its own worktree branch.
- Report each step: smell, technique, files, net result before and after, and any behaviour
  question left open.

## Checklist
- [ ] Behaviour boundary stated; net exists and was run before the first edit
- [ ] Every step under one hat; no test expectation changed in a structure step
- [ ] Smallest technique chosen; no speculative abstraction
- [ ] Cross-file renames and moves done with a reference-aware tool and searched again after
- [ ] Every intermediate state builds and is green; no test deleted or skipped
- [ ] Found bugs pinned, then fixed in their own step
- [ ] Strangler migrations have a routing check and a deletion date
