# Pattern Catalogue

Load only the rows the force points to. Each row gives the force the pattern absorbs, what the
code looks like when the pattern would help, the counter-signal that says do not use it, and
the lighter form to offer as option B. Treat the classic diagrams as roles, not as a list of
classes to create: language features often merge several roles into one.

## Creational

| Pattern | Force it absorbs | Signals in code | Do not use when | Lighter form |
|---------|------------------|-----------------|-----------------|--------------|
| Factory Method | Which concrete product to create varies by context, while the workflow around creation stays fixed | `new ConcreteX` scattered in a workflow that otherwise does not care which X | One product type; the caller can simply pass the object in | Pass a constructor or creation function as a parameter |
| Abstract Factory | Several related objects must come from the same family (per vendor, platform, theme) | Code that mixes products from different families by mistake; parallel `if vendor ==` blocks | One family, or families never mixed | A module or record of creation functions per family |
| Builder | Construction has many optional parts, steps, or validation across fields | Constructors with long parameter lists, telescoping overloads, half-built objects | Named or default arguments already make construction clear | Named arguments with defaults; a plain options record validated once |
| Prototype | Copying a configured object is cheaper or clearer than building it again | Repeated setup to produce near-identical objects | Objects are cheap to build; deep-copy semantics are unclear | A copy function with explicit overrides |
| Singleton | One instance per process must be enforced and shared | A global accessor (`getInstance()`) called from many places | The default case: it hides a dependency and makes tests share state; use it only when the platform allows exactly one instance | Create one instance at startup and pass it in; a module-level instance where the language makes modules singletons |

## Structural

| Pattern | Force it absorbs | Signals in code | Do not use when | Lighter form |
|---------|------------------|-----------------|-----------------|--------------|
| Adapter | A third-party or legacy interface does not match what the code needs | Vendor SDK types and calls spread through domain code | The interfaces already match; one call site | A thin wrapper function in the code's own vocabulary |
| Bridge | Two dimensions vary independently and subclasses multiply (N by M) | Class names that combine two axes (`PdfReportEmail`, `CsvReportSlack`) | Only one axis actually varies | Composition: pass the second dimension in as a parameter |
| Composite | Callers must treat a single item and a tree of items the same way | Recursive code that checks "is this a group?" everywhere | The structure is flat, or leaves and groups need different operations | A recursive function over a plain tree data structure |
| Decorator | Optional behaviour (retry, logging, timing, caching, auth) wraps a call in combinations | Flags and `if` blocks for cross-cutting concerns inside core logic | One fixed wrapper; the behaviour belongs in the class itself | A higher-order function or the framework's middleware |
| Facade | Callers repeat the same sequence of calls into a complex subsystem | The same five-call setup copied across call sites | The subsystem is already simple; the facade would only forward | One function for the repeated sequence |
| Flyweight | Memory grows with many objects that share most of their state | A measured memory problem from duplicated immutable data | No measurement shows a problem | Intern or cache the shared values |
| Proxy | Access to an object needs lazy loading, caching, access control or a remote hop, behind the same interface | Callers doing their own lazy init or permission checks before every use | The control is needed in one place only | Lazy initialisation or a check at the single entry point |

## Behavioural

| Pattern | Force it absorbs | Signals in code | Do not use when | Lighter form |
|---------|------------------|-----------------|-----------------|--------------|
| Chain of Responsibility | A request passes through an ordered, configurable set of handlers, any of which may stop it | A long `if` sequence of checks that grows and is reordered | The order is fixed and short | A list of functions run in order until one returns a result |
| Command | Actions must be queued, logged, retried, scheduled or undone | Operations that need history or replay but are plain method calls | No queueing, history or undo is needed | A closure or a data record describing the action |
| Interpreter | A small, stable grammar must be evaluated many times | Hand-parsed mini-languages with growing special cases | The grammar is large or changing; a parser library or existing format fits | A table-driven evaluator, or an existing expression library |
| Iterator | Traversal of a collection must not expose its internal structure | Callers index into internals or copy the collection to walk it | The language's built-in collections already do it | A generator or the language's iteration protocol |
| Mediator | Many components call each other directly after events, tangling dependencies | Each component holds references to most of the others | Two or three components with simple links | One coordinating function or an event dispatcher |
| Memento | State must be saved and restored without exposing internals | Undo built by copying public fields out and back in | State is a plain immutable value already | Keep previous immutable values in a list |
| Observer | One change must notify a growing, open-ended set of dependents | A function that calls every dependent by name and is edited for each new one | One or two fixed dependents; ordering between dependents matters | A list of callbacks; the framework's event mechanism |
| State | Behaviour depends on a status, and transitions are spread across `if` chains | The same `switch (status)` in many methods; illegal transitions possible | Two or three states with simple, local logic | A transition table or enum with exhaustive matching |
| Strategy | A caller or configuration selects one of several interchangeable algorithms | A growing `switch` selecting an algorithm by key | One algorithm; the variants differ only in data | A function parameter or a map from key to function; a lookup table for data-only variation |
| Template Method | Variants share a fixed sequence of steps and differ in some steps | Copied workflows that differ in two lines | Inheritance would be the only reason for the class hierarchy | A function that takes the varying steps as function parameters |
| Visitor | Many operations run over a stable set of node types | Type switches over the same node types repeated for each operation | The set of node types changes often | Exhaustive pattern matching over a sum type |

## Look-alikes

| Candidates | What decides |
|------------|--------------|
| Adapter / Decorator / Proxy | Adapter changes the interface; Decorator keeps it and adds behaviour; Proxy keeps it and controls access or lifecycle |
| Adapter / Facade | Adapter makes one interface fit another; Facade offers a simpler entry over many operations |
| Bridge / Adapter | Bridge is designed up front around two independent axes; Adapter fixes an existing mismatch |
| Bridge / Strategy | Bridge separates two whole hierarchies that vary independently; Strategy swaps one algorithm |
| Factory Method / Abstract Factory | Factory Method varies one product; Abstract Factory supplies several related products from one family |
| Strategy / State | Strategy is chosen by the caller or configuration; State follows the object's own evolving mode and its legal transitions |
| Strategy / Template Method | Strategy composes a whole algorithm in; Template Method fixes the skeleton and varies steps |
| Strategy / Command | Strategy is an interchangeable algorithm; Command is a request with its own execution lifecycle (queue, log, undo) |
| Facade / Mediator | Facade simplifies calls from outside into a subsystem; Mediator owns the coordination among peers |
| Composite / Decorator | Composite holds zero or more children in a part-whole tree; Decorator wraps exactly one component |
| Observer / Mediator | Observer broadcasts to whoever subscribes; Mediator decides who reacts and how |
| Visitor / Iterator | Visitor dispatches an operation per node type; Iterator controls traversal order and position |
