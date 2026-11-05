---
name: clean-code
description: "Use this skill for any question about code quality, readability or design, including short questions with no code attached: is this function or class well designed or hard to read, does it violate the single responsibility principle or another SOLID principle, how to name a variable, boolean, function or class, what is wrong with catching Exception and passing or another swallowed error, whether to split a long function or DRY up look-alike code, KISS, YAGNI, Law of Demeter, coupling and cohesion, comments, and whether tests are any good. Also use it whenever code is written, changed, split or reviewed, including one-line edits and small fixes, even if the user never says clean code. It sets the bar: intent-revealing names, functions split by responsibility, explicit side effects, errors as design, boundaries, comments for rationale, tests that can fail. Designing pages, layouts or visual style belongs to the UI skills."
argument-hint: "[file, diff or question]"
---

# Skill: Clean Code

## Purpose
This skill sets the bar for code that a reader without the author's context, person or agent,
can follow locally and change safely. It sits next to build-discipline, which decides how much code to write, and the
refactoring skill, which changes existing structure safely.

## When It Runs
| Situation | Use |
|-----------|-----|
| Writing new code or changing existing code | Parts 1 to 7 as the bar; Part 8 checklist before reporting |
| Reviewing a diff or a design | Part 9 review mode |
| A question about SOLID, DRY, KISS, YAGNI, coupling, cohesion, Law of Demeter | `references/principles.md` |
| Reviewing or writing tests | Part 7 and `references/test-smells.md` |
| The code needs restructuring, not just new code | Hand over to the refactoring skill |
| A pattern is being considered or questioned | Hand over to the design-patterns skill |

Precedence: the project's own conventions (linters, formatters, CLAUDE.md, AGENTS.md, house
style in neighbouring code) win over this skill where they speak. This skill fills the gaps.
Language-specific idioms, error handling and concurrency rules are in the design-patterns
skill's `references/languages/<language>.md`; load the file for the code you are writing.
Cleanup stays inside the task's scope: leave the code you touched clearer, and list anything
further as a follow-up instead of doing it.

## Part 1: Names
- A name says what the thing is or does in the domain's own words. One term per concept
  across the codebase; do not call the same thing `client`, `customer` and `account`.
- Avoid names that fit anything: `data`, `info`, `result`, `item`, `manager`, `helper`,
  `util`, `handle`, `process`, `temp`, `obj`. Keep one only when it is the domain's real word.
- Booleans read as predicates (`isActive`, `hasItems`, `canRetry`). Collections are plural.
  Functions are verbs that name the effect (`calculateInvoiceTotal`, not `doInvoice`).
- Units and kinds belong in the name or the type when they are easy to confuse
  (`timeoutMs`, `priceCents`, `UserId` rather than a bare string).
- A name that is hard to choose often means the thing does two jobs. Split it before
  naming it.
- Literals that carry rules (rates, limits, status codes, country codes) get a name: a constant,
  an enum or configuration. Money is held as integer minor units or a decimal or money type,
  never as binary floating point.

## Part 2: Functions and Modules
- Split by responsibility and by level of abstraction, not by length. A function that mixes
  setup, validation, computation, persistence and formatting gets one function per phase.
  A long function that does one thing at one level, with a simple signature, can stay.
- Every split must leave something worth naming. A new function that only forwards its
  arguments, or that cannot be understood without reading its caller, made things worse.
- When asked to split code because it is long, check the levels first. Split along
  responsibility or abstraction lines only. If the code is one flat level (a field mapping, a
  sequence of similar checks, a table), say so: make only the extractions that remove real
  repetition, keep the rest, and explain why splitting by size would add pass-through functions
  or scatter an order the reader needs to see in one place.
- Read top down: the high-level steps first, the details below them.
- Few parameters. Three deserves a look; more often hides a missing value object. A
  boolean parameter that switches behaviour becomes two functions.
- Prefer deep modules: a small interface over a lot of useful behaviour. Many small classes
  whose interfaces add up to more than they hide is a smell of its own.
- Put behaviour next to the data it uses. A function that reads another object's fields more
  than its own belongs on that object.
- Code that looks alike but encodes different rules stays separate. Before extracting shared
  code, apply the DRY test in `references/principles.md`: real repeats today, one change would
  need the same edit in every place, and the shared piece has a name without "and" or "or".

## Part 3: Side Effects, State and Errors
- A function either answers a question or changes state, not both (command-query
  separation). Mutation is visible in the name and the call site.
- Dependencies come in through parameters or constructors, not through globals or hidden
  singletons.
- Keep the happy path readable: guard clauses for invalid input, then the main flow.
- Fail fast on broken assumptions. Never swallow an error; add the context a person needs to
  act on it. Keep validation errors, domain errors and infrastructure failures distinct.
- Prefer designs where the error cannot happen: a type that cannot hold an invalid value, an
  operation that is defined for every input, a default that is always safe. Remove special
  cases where the design allows it.
- Use the language's way of expressing absence and failure (typed results, options,
  exceptions) instead of sentinel values like `-1` or empty strings.

## Part 4: Boundaries and Coupling
- Framework, persistence, transport, vendor SDK and construction details stay at the edges.
  Domain code does not import them. Wrap a third-party interface in a thin local adapter
  that exposes only what the code needs, in the code's own vocabulary. The adapter wraps the
  vendor in use today; a multi-vendor abstraction waits for a second real vendor.
- Talk to direct collaborators only (Law of Demeter). `order.shippingAddress()` beats
  `order.customer.address.city`. Tell an object what to do rather than pulling its data out
  to decide for it.
- A function that needs one field takes that field, not the whole object.
- Each piece of design knowledge (a format, a rule, a protocol detail) lives in one module.
  When the same decision is encoded in two places, every change to it needs coordinated
  edits; gather it into one module.

## Part 5: Comments
- Comments carry what the code cannot: why this approach, a constraint, a warning, a link to
  an external contract, a deliberate shortcut and its trigger to revisit.
- A comment that restates the code, or labels a block, is a request to rename or extract.
- Interface comments describe what a caller gets, not how it is done inside.
- Delete commented-out code; version control keeps it.

## Part 6: Agent-Written Code
- Before writing a helper or inline logic for formatting, parsing, validation, conversion,
  retries or similar, search the repository for it (grep the concept and likely names) and
  reuse what exists; then follow build-discipline's choice ladder (standard library, platform,
  installed dependency). A second implementation of existing behaviour is a defect.
- Never invent an API, flag or configuration key. Check the source, the docs or the installed
  version; if it cannot be verified, say so.
- Never silence a failing check to finish: no skipped tests, blanket ignores, widened types
  or disabled lint rules without a stated reason the user accepts.
- Match the surrounding code's idioms, naming and error handling, even where another style
  would be cleaner in isolation.
- Keep diffs reviewable: one concern per change, no drive-by reformatting.
- Before removing code that looks pointless, find out why it is there (history, callers,
  tests). Remove it only once the reason is known not to apply.

## Part 7: Tests Are Code
- Tests get the same naming, clarity and duplication bar as production code.
- Each test checks one behaviour and its name says which. It fails for one reason and the
  failure message points at it.
- Assert on observable outcomes, not on private state or the exact sequence of calls to
  collaborators. Fake only real boundaries (clock, network, filesystem, randomness).
- Check that a test can fail: break the code it covers, or feed an input that must change,
  and watch it go red. Fix or delete a test that cannot fail.
- Smell catalogue with severities: `references/test-smells.md`.

## Part 8: Before Reporting
Run this on the code you wrote or changed:
- [ ] A reader can follow the change without opening other files to decode names
- [ ] Each function does one job at one level of abstraction; no shallow pass-throughs added
- [ ] Side effects are visible; no function both answers and mutates
- [ ] Errors are handled where they can be acted on, with context; none swallowed
- [ ] Framework and vendor details stayed at the edges
- [ ] Comments explain why, not what; no commented-out code
- [ ] No new helper duplicates an existing one; no invented API
- [ ] Tests cover the changed behaviour, can fail, and were run

## Part 9: Review Mode
For a diff or a design under review:
1. Behaviour first: correctness, failure handling and security findings outrank every
   design point and come first.
2. Then readability and design, each finding with `path:line`, the rule or principle by
   name, the concrete cost (what change it makes harder), and the smallest fix.
3. Name over-application as plainly as under-application. An interface with one permanent
   implementation, a class per trivial function, or a layer that only forwards is a finding,
   with the simpler shape sketched.
4. Group repeats of one finding instead of listing every instance. Keep cosmetic points in a
   short labelled list, apart from the findings that matter.
5. "No change needed" is a valid result for sound code; say it.

Severity follows cost: a finding on code that changes often or carries money, security or
data-loss risk ranks above the same finding on code nobody touches.
