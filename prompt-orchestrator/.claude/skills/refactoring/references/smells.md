# Smell to Technique Map

Load this when Part 4 of the refactoring skill needs a technique. Each row names a smell, how to
spot it, and the smallest moves that usually remove it. Start with the first technique listed;
reach for the later ones only if it does not fit. Design red flags such as information leakage
and shallow modules are described in the clean-code skill's `references/principles.md`, test smells in
the clean-code skill's `references/test-smells.md`, and judging existing patterns in the
design-patterns skill (review mode).

## Bloaters

| Smell | Signs | Techniques, smallest first |
|-------|-------|----------------------------|
| Long function | Scrolls off the screen, comments that label sections, many locals | Extract function per labelled section; replace temp with query; split loop; decompose conditional |
| Large class or module | Many fields used by different method groups, many reasons to change | Extract class per field group; extract module; move function to where its data lives |
| Long parameter list | Many parameters, several always passed together | Introduce parameter object; preserve whole object; replace parameter with query |
| Primitive obsession | Strings or numbers that carry rules (ids, money, units, status codes) | Replace primitive with value object; replace type code with subclasses or a lookup |
| Data clumps | The same few values travel together | Extract class or record for the clump, then move behaviour onto it |

## Change preventers

| Smell | Signs | Techniques |
|-------|-------|------------|
| Divergent change | One module changes for unrelated reasons | Split phase; extract class per reason |
| Shotgun surgery | One change touches many modules | Move function and move field to gather the logic; inline class that only forwards |
| Information leakage | One design decision (a format, a rule) encoded in several modules | Gather the knowledge into one module; merge the modules if no small interface can hold it |
| Parallel hierarchies | Adding a subtype here forces one there | Move behaviour so one hierarchy refers to the other, then collapse |

## Conditionals and control flow

| Smell | Signs | Techniques |
|-------|-------|------------|
| Complex conditional | Nested `if`, flags, repeated checks | Decompose conditional; consolidate conditional; guard clauses for special cases |
| Repeated switch on type | The same switch in several places | Replace conditional with polymorphism, or a lookup table when behaviour is data |
| Null checks everywhere | Defensive checks for the same absent value | Introduce special case (null object) |
| Flag arguments | Boolean parameters that select behaviour | Remove flag argument by splitting the function |

## Dispensables

| Smell | Signs | Techniques |
|-------|-------|------------|
| Duplicated code | Same or near-same logic in several places | Extract function; slide statements to line up near-duplicates first; pull up method |
| Dead code | Unreached branches, unused exports and parameters | Remove it, after a reference search and a test run |
| Speculative generality | Hooks, parameters and abstractions nobody uses | Collapse hierarchy; inline function or class; remove parameter |
| Comments that explain unclear code | Comment restates what the code should say | Rename; extract function with the comment's meaning as its name |
| Lazy element | A class or function that adds a name and nothing else | Inline it |
| Pattern with one variant | An interface with one implementation and no test seam, a factory for one product, a strategy with one strategy | Inline the abstraction back to direct code; record when it would return (design-patterns skill, Part 7) |

## Couplers

| Smell | Signs | Techniques |
|-------|-------|------------|
| Feature envy | A function uses another module's data more than its own | Move function next to that data |
| Inappropriate intimacy | Two modules reach into each other's internals | Move function and field; extract a shared module; hide delegate |
| Message chains | `a.b().c().d()` across objects | Hide delegate; extract function at the end of the chain |
| Middle man | A class that only forwards | Remove middle man; inline |
| Global or hidden state | Functions read or write globals or singletons | Encapsulate variable; pass the dependency in (a seam) |

## Naming and data

| Smell | Signs | Techniques |
|-------|-------|------------|
| Mysterious name | A name that needs a comment or a guess | Rename variable, function or field (reference-aware, Part 6) |
| Mutable data shared widely | Many writers, hard-to-track changes | Encapsulate variable; separate query from modifier; replace derived variable with query |
| Temporary field | A field set only in some paths | Extract class for the field and its users; introduce special case |
