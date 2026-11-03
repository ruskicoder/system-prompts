# Kotlin

Authorities: Kotlin coding conventions (kotlinlang.org), the coroutines guide, Android Kotlin
style guide and coroutine best practices for Android code. ktlint or detekt in CI; the project's
`.editorconfig` decides formatting.

## Idioms that replace classic patterns

| Classic pattern | Kotlin form |
|-----------------|-------------|
| Strategy, Command | Function types and lambdas; `typealias` for repeated function types |
| Builder | Named and default arguments; `apply {}` for configuration; type-safe builder DSLs where a DSL pays off |
| Factory | Top-level or companion factory functions with descriptive names (`fromJson`), instead of many constructor overloads |
| Singleton | `object` declarations; prefer injected instances where tests need control |
| State, Visitor | `sealed` classes or interfaces with exhaustive `when` |
| Value object | `data class` or `@JvmInline value class` for single-field wrappers |
| Decorator, Adapter | Interface delegation with `by`; extension functions for adapting APIs |
| Observer | `Flow` (cold) and `StateFlow` / `SharedFlow` (hot) |
| Iterator | Sequences (`sequence {}`) and collection operations |
| Template Method | Higher-order functions taking the varying steps |

## Language rules (from the coding conventions)
- `val` by default; read-only collection interfaces (`List`, `Set`, `Map`) in signatures.
- Default parameters instead of overloads; named arguments for same-typed or boolean parameters.
- Expression forms of `if`, `when` and `try`; `if` for two branches, `when` for three or more.
- Prefer a property to a function when it is cheap, does not throw and returns the same result
  for the same state.
- Extension functions for operations mainly on one type, with restricted visibility.
- Explicit types for public API return values and for properties initialised from Java
  platform types; explicit visibility in libraries.
- Scope functions (`let`, `run`, `with`, `apply`, `also`) chosen for readability, not nested
  several levels deep.

## Null safety and errors
- Model absence with nullable types; avoid `!!` except where a null is a proven bug, with a
  message via `requireNotNull` or `checkNotNull`.
- `require` for argument checks, `check` for state checks, `error` for impossible branches.
- Exceptions for unexpected failures; for expected failures return a sealed result type or
  `Result` within a module, not across public APIs that callers will forget to inspect.
- Do not catch `CancellationException` without rethrowing it.

## Coroutines and concurrency
- Structured concurrency: launch in a scope tied to a lifecycle (`viewModelScope`,
  `lifecycleScope`, a scope owned by the component); never `GlobalScope`.
- Suspend functions are main-safe: move blocking or CPU work with `withContext`; inject
  dispatchers instead of hard-coding `Dispatchers.IO` so tests can replace them.
- Expose `Flow` and suspend functions from data and domain layers; collect with lifecycle-aware
  collectors in UI.
- `supervisorScope` when one child's failure must not cancel its siblings.
- Shared mutable state: confine it to one coroutine, or protect it with `Mutex` or atomics.

## Agent pitfalls
- Java-style getters, setters and builders.
- `!!` sprinkled to silence the compiler.
- `GlobalScope.launch` and fire-and-forget coroutines.
- Mutable collections exposed from classes (`MutableList` properties).
- Catching `Exception` around suspend calls and swallowing cancellation.
