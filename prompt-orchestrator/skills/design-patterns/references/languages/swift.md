# Swift

Authorities: the Swift API Design Guidelines (swift.org), The Swift Programming Language,
Apple's SwiftUI and Observation documentation, the Swift concurrency documentation. SwiftLint or
swift-format where the project uses them.

## Idioms that replace classic patterns

| Classic pattern | Swift form |
|-----------------|------------|
| Strategy | A protocol with value-type conformers, or a closure |
| State, Visitor | Enums with associated values and exhaustive `switch` |
| Factory | Static factory methods named `make...`; failable or throwing initializers for validation |
| Builder | Initializers with default parameter values; result builders for DSLs |
| Singleton | `static let shared` where the platform demands one instance; otherwise inject |
| Observer | `@Observable` models in SwiftUI; `AsyncSequence` and `AsyncStream`; Combine in existing code |
| Decorator, Adapter | Protocol extensions and wrapper types; property wrappers for repeated property behaviour |
| Iterator | `Sequence` and `IteratorProtocol`; lazy sequences |
| Value object | `struct` (value semantics by default) |
| Template Method | Protocol with default implementations in an extension |

## API design (from the Swift API Design Guidelines)
- Clarity at the point of use is the first goal; read the call site, not the declaration.
- Include the words needed to avoid ambiguity (`remove(at:)`), omit needless words, and name
  parameters by role, not by type.
- Methods without side effects read as nouns (`distance(to:)`); methods with side effects read as
  imperative verbs (`sort()`). Mutating and non-mutating pairs: `sort()` and `sorted()`,
  `formUnion(_:)` and `union(_:)`.
- Booleans read as assertions (`isEmpty`); protocols describing what something is are nouns,
  capabilities end in `-able`, `-ible` or `-ing`.
- Argument labels: omit when arguments cannot be usefully distinguished (`min(a, b)`); label a
  first argument that starts a prepositional phrase; label all others.
- Every declaration gets a one-sentence documentation summary.

## Types, errors and memory
- Prefer `struct` and `enum`; use `class` for identity, shared mutable state or framework needs;
  mark classes `final` unless designed for inheritance.
- Protocol-oriented design: small protocols, composition, generics with `some` and `any`
  chosen deliberately (`some` for static types, `any` only when values of different types must
  mix).
- Errors: `throws` (typed throws where the error set is closed) and `do`/`catch`; `Result` for
  stored or callback results; optionals for simple absence. Avoid `try!` and force unwraps
  outside tests and proven invariants.
- Avoid retain cycles: `[weak self]` in escaping closures that capture an owner; delegates
  `weak`.

## Concurrency
- `async`/`await` with structured tasks (`async let`, task groups); avoid detached tasks unless
  the work truly must outlive its caller.
- Actors protect mutable state; `@MainActor` for UI state; value types and `Sendable` for data
  crossing isolation boundaries. Enable strict concurrency checking (the Swift 6 language mode).
- Respect cancellation (`Task.checkCancellation()`, `Task.isCancelled`).

## SwiftUI state (see `presentation.md`)
- `@Observable` models, owned with `@State` by the view that creates them, shared through the
  environment, bound with `@Bindable`. A separate view model layer is optional, not required.

## Agent pitfalls
- Force unwraps (`!`) and `try!` in production paths.
- Classes where structs fit; deep class inheritance.
- `ObservableObject` and `@Published` in new code targeting iOS 17 and later, where
  `@Observable` applies.
- Ignoring Sendable and actor isolation warnings.
- Massive view controllers or views holding networking and persistence code.
