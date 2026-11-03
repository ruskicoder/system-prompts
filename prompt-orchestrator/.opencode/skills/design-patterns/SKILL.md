---
name: design-patterns
description: 'Use this skill whenever a structural design decision comes up, even
  if no pattern is named: choosing or questioning a design pattern, making code extensible,
  reviewing the abstractions a diff adds, picking a UI architecture (MVC, MVP, MVVM,
  MVI, MVU, Redux, VIPER, TCA, BLoC; Jetpack Compose, SwiftUI, Flutter or React state),
  monolith versus microservices, event-driven or serverless design (Lambda, Functions,
  queues), messaging reliability (outbox, idempotent consumers, sagas), designing
  a network API (resources, pagination, errors, versioning), DDD and data-access patterns,
  concurrency, or the idiomatic form of a pattern in Java, Kotlin, Swift, Go, Rust,
  Python, TypeScript, C#, C++, Dart, Ruby or PHP. It names the force before any pattern,
  climbs a ladder from no change to a full pattern, applies a YAGNI gate, shows full,
  lighter and leave-it options with cost before editing, records the decision, and
  gives existing patterns a verdict.'
argument-hint: '[file, module, pattern name or question]'
---

<!-- Generated from skills/design-patterns.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Skill: Design Patterns

## Purpose
A pattern is a named answer to one question: what is going to change here, and what must stay
still while it changes? Applied to a real axis of change it makes the next variant cheap.
Applied to a guess it adds files, names and indirection that every reader pays for and that
the second real case often cannot use. This skill picks the lightest structure that absorbs the
change that actually exists, and says so when that structure is no pattern at all.

## When It Runs
| The request | Mode |
|-------------|------|
| What a pattern is, which one fits, how two compare | **Answer**: read the reference entries involved, answer, name the lighter form; no map, no edits |
| One place and a named pattern ("make this a Strategy") | **Targeted**: check counter-signals (Part 4), then apply or stop |
| One place, no pattern named ("this switch keeps growing") | **Targeted** with a one-row Refactor Map |
| A module, codebase or architecture to restructure | **Map**: Parts 1 to 6 |
| New code with a possible variation point | Parts 1 to 3, then a decision record (Part 7) |
| A diff or design that adds or uses patterns | **Review**: Part 8 |

The same method applies at every scale: a class, a screen, a module, a service, a system. Load
the reference for the scale and family the force belongs to (see References).

**Required first step for code in a specific language:** read
`references/languages/<language>.md` before answering, reviewing or proposing any form. Its
idioms (for example "accept interfaces, return concrete types" in Go, a function or dict instead
of Strategy classes in Python) replace the generic shape and belong in the answer.

Related skills: clean-code for code-level rules and principles, refactoring for the safe steps
that move code into a new shape (pin behaviour first, one hat per step), build-discipline for
the rule against speculative structure, system-design and architecture for service boundaries
and ADRs.

## Part 1: Name the Force
Start from the problem, never from the catalogue: picking a pattern first and then a place for
it produces structure with no force behind it. Answer these, in the code's own terms:

1. **What varies?** Which part will have a second, third, fourth version?
2. **Who wants it to vary?** A requirement, a third-party API, a customer tier, a platform, a
   test double. "It might be useful" is not a source.
3. **What must not move?** Which callers, contracts or stored data must survive untouched?
4. **When does it vary?** Build time, startup, per request, per user, mid-operation. Runtime
   variation and configuration-time variation call for different shapes.
5. **How many axes?** Two independent axes is one structure (Bridge), not two patterns stacked.

Write it as one sentence: "The payment provider varies per tenant, chosen at runtime, and the
checkout flow must not change." That sentence often names the pattern on its own.

When the request does not say what will change, ask one question with two or three concrete
guesses from the code. When running without a user, write the assumption at the top of the
output and mark it "to confirm".

If nothing varies, stop: direct code, plus a no-pattern decision (Part 7).

## Part 2: The Ladder
Stop at the lowest rung that removes the pain:

1. **Nothing**: the current code is fine for the change that is coming.
2. **Plain refactoring**: extract function, move function, introduce parameter object, a lookup
   table when the variants differ only in data.
3. **Language idiom**: a function or a map of functions, a closure, a generator, a sum type with
   exhaustive matching, a module. In dynamic and functional languages this is often the right
   form of Strategy, Command, Template Method and Iterator. `references/languages/<language>.md`
   lists the native form of each classic pattern; check it before rung 4.
4. **Lighter form**: the pattern's intent with fewer roles (one interface, no factory; a
   decorator function instead of a class hierarchy).
5. **Full pattern**: all the roles.

Check the framework and the codebase before rung 3: most frameworks already ship the common
patterns (middleware chains, dependency injection containers, event buses, template classes,
repositories). Use the existing mechanism; a hand-built copy is duplicated infrastructure to
maintain.

## Part 3: The YAGNI Gate
Rungs 4 and 5 must pass all four. Any failure means the lower rung wins and the decision says
when to revisit.

1. **Rule of three**: two variants exist today, and a third is concretely planned. One
   implementation plus a hypothetical is a guess.
2. **Named source**: point at the requirement, API, tenant or platform that forces the
   variation. "For flexibility" is not a source.
3. **Cost paid back**: the indirection (files, names, a longer path from symptom to cause,
   and on tight budgets runtime or binary size) buys more than it costs.
4. **Direct version is worse**: sketch the plain version. If it is clear and easy to change
   later, it wins.

On a published surface (library API, plugin contract, CLI flag, wire format) changing later
means a breaking release; weigh that in gate 3, and count a documented extension point as a
named source.

**"Make it extensible"** from a lead, a ticket or a user does not change the gate; it changes
the answer. Deliver a seam instead of an abstraction: separate what is stable from what would vary
as two plain functions or classes, say which pattern the seam becomes when the second real case
arrives, and explain that an interface designed from one case is the one the second case cannot
satisfy. If the requester still wants the abstraction now, it is their call: build it and record
the override.

## Part 4: Counter-Signals
Before applying a pattern, compare the code with the pattern's "Do not use when" line in
`references/catalog.md`. A matching counter-signal means the literal request and the better
result differ, which is a scope question under communication-tone. Stop before editing, even
if the user named the pattern: state the counter-signal, sketch the lighter form in a few lines, and ask
which they want. Once the user has seen the options and their cost, their choice wins over the
recommendation.

## Part 5: Refactor Map (Map mode, and Targeted mode with no pattern named)
The map is the one batch of scope questions that communication-tone allows before work starts:
options per row, a recommendation, one question where only the user can answer. Produce it
before any edit, then end the turn and wait for a choice. Keep at most seven hotspots; put the
rest under "Later". Line counts are estimates and say "about".

When the user has already closed scope ("apply the recommendations", "go ahead", or an
auto-decide grant that covers it), do not stop: apply the recommended rows and include the map
in the report. A row whose recommendation is a full pattern with a matching counter-signal
still waits for the user's yes.

```markdown
## Refactor Map: <scope>

**Diagnosis:** <why change is hard here today, one or two sentences>
**Force:** <the sentence from Part 1, or the assumption marked "to confirm">
**Constraints:** <public API, upstream merges, security rules, deadlines, or "none">
**Safety net:** <tests that exist> / <characterization tests to add first>

### 1. <hotspot> (`path:line`)
- **Signal:** <what the code shows>
- **A. Full pattern:** <pattern applied as ...>. Cost: <new files, about +N lines, indirection>
- **B. Lighter:** <idiom, lighter form or plain refactoring>. Cost: <...>
- **C. Leave it:** <the condition under which today's code is fine>
- **Recommendation:** <A, B or C>, because <reason tied to the force>
- **Question:** <one question only the user can answer, or "none">

### Not touching
- `path`: <signal that needs nothing, or off the path of the force>

### Bugs found
- `path:line`: <behaviour>. Pinned with a test, not fixed unless you say so. (Or "none".)

### Later
- <hotspots outside this map>

**Order:** <sequence and why>
**Reply with a choice per row (for example "1A, 2B, 3C") or "apply the recommendations".**
```

At architecture scale a row is a seam between modules or services (for example an
anti-corruption layer, an outbox, a module facade for a strangler migration); take its options
from the family reference.

A reply that leaves a row out means C for that row; restate the reading before editing.
Without a user, apply only rungs 1 to 4, leave full patterns for confirmation, and list the
open questions in the report.

## Part 6: Apply
Follow the refactoring skill for every row: pin behaviour first, one hat per step, the net run
after each step, every intermediate state green. Per row:
- Follow the catalogue entry's path; stop at the lighter form if the pain is gone and tell the
  user, continuing only if they chose the full form.
- One row per change set; never mix two rows. Tests for a new seam go with their row.
- A bug found on the way is pinned and listed, then fixed only on request in its own step.
- Commit only when the user or the approved plan allows it (communication-tone hard stops).

Report per row: what changed, the line delta, the test result, and what the next wave holds.

## Part 7: Decision Record
Never write "used the Strategy pattern" and stop. The force and the rejected alternative are
what stay useful later. In the chat, or in the spec or ADR for architecture-scale decisions:

```markdown
**Force:** <what varies, who wants it, when; or "none today">
**Choice:** <pattern, idiom or direct code>
**Rejected:** <the nearest alternative and why>
**Becomes a pattern when:** <the trigger, for a no-pattern choice>
```

Record no-pattern decisions as well: they tell the next person that the seam exists and what
would justify more.

## Part 8: Review Mode
For a diff, a design or an existing codebase:

1. Behaviour first: failures, missing error handling and security findings outrank design.
2. Give each pattern occurrence one verdict, judged by structure, not by class names:

| Verdict | Meaning |
|---------|---------|
| Sound | Intent, structure and trade-off fit a real force |
| Misapplied | The structure is real but the problem is wrong, roles are broken, or the abstraction leaks (a singleton as global mutable state, an observer with ordering assumptions) |
| Name only | Called `*Factory`, `*Strategy` or `*Adapter` without the structure; report it only when the name misleads or hides a smell |
| Over-engineered | Machinery with one variant and no force in sight: an interface with one implementation and no test seam, a factory for one product, a strategy with one strategy |
| Uncertain | Say what evidence would settle it |

3. Run the gate in reverse on each abstraction the change adds: can the author name the force?
   Do two variants exist today? Does the framework already provide it? Is the direct version
   really worse? Does it make testing easier or harder?
4. A request to remove an abstraction includes the smaller shape, sized in files and lines,
   and any public-contract change it implies.
5. Weigh severity by churn and risk: a misapplied pattern on a hot path or a money path ranks
   above the same thing in code nobody has touched in years. With shallow or squashed history,
   say so and judge by structure alone.

## Guardrails
- A pattern name supplies no guarantee by itself. Atomicity, idempotency, durability, thread
  safety, authorization and snapshot isolation need explicit mechanisms and tests.
- Define ownership and failure behaviour for wrappers, callbacks, histories and pools: cleanup
  survives exceptions, retries account for idempotency.
- Measure before applying performance patterns (Flyweight, caching proxies, object pools).
- Test the composition, not only each part: ordering, reentrancy, cycles, concurrent access,
  partial failure, empty histories, unknown keys, repeated restore or replay.
- A singleton hides a global dependency and shares state between tests. Prefer creating one
  instance at startup and passing it in.

## References (load on demand)
Load only what the force points to; most tasks need one family file and one language file.

| The force is about | Load |
|--------------------|------|
| Object creation, composition or behaviour inside a module | `references/catalog.md` (23 Gang of Four patterns, look-alikes) |
| UI state, screens, MVC, MVP, MVVM, MVI, MVU, Redux, VIPER, TCA, BLoC; Android, iOS, Flutter, React, server MVC; mobile offline-first | `references/presentation.md` |
| Layering, hexagonal, clean, modular monolith, microservices, event-driven, serverless, BFF, cells; reversibility of the decision | `references/architecture-styles.md` |
| Where business logic lives, ORM and data access, DDD aggregates, bounded contexts | `references/enterprise-and-ddd.md` |
| Failure between services, data across stores, gateways, deployment, observability, cloud security | `references/distributed-and-cloud.md` |
| Messages, events, queues, brokers, integration between systems | `references/messaging.md` |
| Threads, async tasks, shared state; pure functions, result types, pipelines | `references/concurrency-and-functional.md` |
| A network API: resources, errors, pagination, versioning, idempotency, long-running operations | `references/api-design.md` |
| Naming a recurring bad solution in code, design, architecture or performance | `references/anti-patterns.md` |
| The native form of a pattern in one language | `references/languages/` (`java`, `kotlin`, `swift`, `go`, `rust`, `python`, `typescript`, `csharp`, `cpp`, `dart`, `ruby`, `php`) |

Principles (SOLID, DRY, coupling) live in the clean-code skill's `references/principles.md`;
code smells and their techniques in the refactoring skill's `references/smells.md`.

## Checklist
- [ ] Force named in one sentence, or "none" with direct code
- [ ] Lowest working rung chosen; framework and codebase mechanisms checked first
- [ ] Rungs 4 and 5 passed all four gate questions
- [ ] Counter-signals checked; user saw options and cost before a full pattern
- [ ] Refactor Map produced before edits in Map mode
- [ ] Behaviour pinned; one row per change set; bugs pinned, not fixed in passing
- [ ] Decision recorded with the rejected alternative or the revisit trigger
