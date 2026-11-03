# Design Principles

Load this when a decision or a review needs a principle by name. Every principle here is a
tool for one question: does this make the code easier to understand and cheaper to change?
Each entry gives the rule, how to spot a violation, and how to spot over-application. Check
both: over-application reads as careful design and is easy to miss in review.

## Complexity: what the principles fight

Complexity is anything in the structure that makes code hard to understand or change. It shows
up as three symptoms:

| Symptom | What it feels like |
|---------|--------------------|
| Change amplification | A simple change needs edits in many places |
| Cognitive load | A reader must hold many facts at once to change something safely |
| Unknown unknowns | A reader cannot tell what they need to know; nothing signals the gap, so it surfaces as bugs |

It has two causes: dependencies (code that cannot be understood or changed in isolation) and
obscurity (important information that is not visible). Reduce both by removing the thing, or by
hiding it behind an interface that is smaller than what it hides.

## SOLID

| Principle | Rule | Violation signs | Over-application signs |
|-----------|------|-----------------|------------------------|
| Single responsibility | A module has one reason to change: one actor or one concern drives its edits | Validation, rules, persistence and I/O in one class; a name with "and" or a vague noun (`Manager`, `Utils`); edits for unrelated reasons in its history | Logic that always changes together scattered over many one-method classes; a reader must open five files to follow one rule |
| Open/closed | Add new behaviour by adding code, not by editing stable code | A switch on a type code repeated in several places, edited for every new variant | Plugin points, registries and hooks for variation that does not exist |
| Liskov substitution | A subtype honours the contract of its parent: no stronger preconditions, no weaker guarantees, no surprise exceptions | Callers check the concrete type; an override throws "not supported"; a subclass ignores a parameter | Rarely over-applied; the risk is inheritance used where composition fits |
| Interface segregation | Clients depend only on what they use | A fat interface whose implementers stub half the methods; a test double that must fake ten methods to test one | One interface per method, multiplying types with no client asking for the split |
| Dependency inversion | Policy depends on abstractions it owns; concrete details are wired in at the edges | Domain code constructs its database client or HTTP client; tests need the real network | An interface for every class, including types with one permanent implementation and no test seam |

Before adding an abstraction in the name of any letter, name its second real use (a second
implementation that exists today, or a test double the tests need). No second use, no
abstraction.

## DRY: one place for each piece of knowledge
The rule is about knowledge, not text. Two pieces of code that look alike but encode different
decisions are not duplication; merging them couples things that will change apart.

Before extracting shared code, all three must hold:
1. The logic already appears in more than one real place (not a predicted one).
2. A change to the rule would need the same edit in every place.
3. The shared piece can be named without "and" or "or".

Any "no" means keep the copies. Undoing a wrong shared abstraction means splitting it again at
every caller.

Violation signs: the same rule, format, constant or protocol detail encoded in several modules;
a fix applied in one copy and missed in another. Over-application signs: a shared helper with
boolean parameters to serve callers that diverged; a base class whose subclasses override most
of it.

## KISS: the simplest design that meets the need
Prefer direct over indirect, flat over nested, explicit over generic, and the standard library
or platform over hand-rolled code. Of two correct solutions, take the one with fewer moving
parts. Judge simplicity by how quickly a reader understands the code: four plain lines can be
simpler than one dense line the reader must decode.

## YAGNI: build for the change that has arrived
No extension point, option, layer or abstraction for a need that is not required now or
concretely planned with an owner. The cost is paid today, and an abstraction designed from one
case often does not fit the second case when it arrives. Refactoring toward an abstraction once the second real case exists is cheap where every
caller can be changed; designing it from one case is not.

Exception: a published surface (library API, plugin contract, CLI flag, wire format) is
expensive to change later, so a documented extension point there counts as a real need.

Complexity that is always allowed: security, input validation at trust boundaries, error
handling, accessibility, measured performance needs, reliability, and the project's existing
architecture.

## Law of Demeter and tell, don't ask
A method calls only: itself, its own fields, its parameters, objects it creates, and services
it was given. It does not reach through one object to another.

Violation signs: chains like `a.b.c.d`; a test that mocks three levels deep to reach the code
under test; null checks at every step of a chain. Fix by asking the direct collaborator for what
is needed, or by moving the decision to the object that owns the data.

Not a violation: fluent builders and pipelines that return the same kind of object, and plain
data structures read by the code that owns them.

## Command-query separation
A function either returns information or changes state. A query called twice gives the same
answer and changes nothing. Where the language or a protocol needs both at once (pop, atomic
compare-and-set), name it so the mutation is obvious.

## Separation of concerns and cohesion
Group code by what it knows, not by when it runs. Modules carved by execution order (read,
then parse, then write) tend to spread one piece of knowledge, such as a file format, over all
stages. High cohesion means the parts of a module change together; low coupling means modules
change apart.

## Coupling: what must two pieces of code agree on
When a change forces a coordinated edit elsewhere, name the agreement. Common kinds, from
weakest and easiest to see to strongest and hardest to see:

| Agreement on | Example |
|--------------|---------|
| A name | Callers use a function's name; a rename tool finds them all |
| A type | Callers depend on a parameter's type |
| The meaning of a value | `status == 3` means cancelled in several places |
| The position of values | Positional arguments or tuple fields that must stay in order |
| An algorithm | Writer and reader both implement the same encoding or hash |
| The order of operations | `init()` must run before `load()`, enforced by nobody |
| Timing | Two threads or services must act within a window |
| Values that change together | Two constants that must stay equal |
| Identity | Two parts must hold the same object, not equal copies |

Weaken strong agreements that cross module or service boundaries: replace a magic value with a
named constant or enum, positional arguments with named ones, a hidden order with a type that
enforces it, duplicated algorithms with one shared implementation. Strong coupling inside one
cohesive module is acceptable. Aim for coupling that is visible and weak; removing all of it is
neither possible nor useful.

## Deep modules and information hiding
- A module's value is the behaviour it provides; its cost is the interface a caller must learn.
  Good modules hide a lot behind little.
- Private fields with a getter and setter for each hide nothing. Hiding is about whether a
  design decision escapes the module.
- Make the common case simple. Rare options get defaults so most callers never see them.
- Pull complexity down: the module's author handles the hard case once so every caller does not.
  A configuration option the code could compute itself pushes complexity onto every user.
- Each layer offers a different abstraction from the one below it. Adjacent layers with the same
  methods are pass-throughs.
- Design it twice: for an important interface, sketch two different shapes and compare before
  building one.

## Design red flags
Names for problems worth stating in a review. The smell map in the refactoring skill
(the refactoring skill's `references/smells.md`) lists techniques for most of them.

| Flag | What it looks like |
|------|--------------------|
| Shallow module | The interface is about as complex as the implementation |
| Information leakage | One design decision encoded in several modules |
| Temporal decomposition | Modules split by execution order, sharing knowledge across stages |
| Overexposure | The common path forces callers to learn rare options |
| Pass-through method | A method that only forwards to another with the same signature |
| Pass-through variable | A value threaded through layers that do not use it |
| Special-general mixture | Use-case-specific code inside a general mechanism |
| Conjoined methods | Two functions that cannot be understood without each other |
| Hard to name | No precise name fits; the concept is muddled or is two things |
| Hard to describe | A complete, short interface comment cannot be written |
| Non-obvious code | A first-time reader cannot follow it on a quick read |
