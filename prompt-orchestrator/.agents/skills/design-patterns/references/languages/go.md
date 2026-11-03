# Go

Authorities: Effective Go (official baseline, written before generics and modules), Go Code
Review Comments (official review checklist), Google Go Style Guide (normative), Go Doc Comments.
`gofmt` decides formatting; `go vet` and a linter set (golangci-lint) run in CI. The project's
own conventions win where they differ.

## Idioms that replace classic patterns

| Classic pattern | Go form |
|-----------------|---------|
| Strategy, Command, Template Method | A function value or a small interface with one method |
| Factory | A `NewThing(...)` constructor function returning a concrete type |
| Builder | Functional options (`NewServer(addr, WithTimeout(d))`) or a config struct |
| Decorator, Chain of Responsibility | Middleware: `func(http.Handler) http.Handler` composed in order |
| Adapter | A type that implements the consumer's small interface around a third-party client |
| Observer | Channels, or a slice of callbacks guarded by a mutex |
| Iterator | `range` over slices, maps, channels, and range-over-func iterators (`iter.Seq`) since Go 1.23 |
| Singleton | A package-level value initialised once (`sync.Once` when lazy); prefer passing it in |
| Visitor | A type switch over a closed set of types |
| Inheritance | Composition and struct embedding; interfaces satisfied implicitly |

## Interfaces and types
- Accept interfaces, return concrete types. Define interfaces in the consuming package, small
  (often one method), and only when a second implementation or a test needs them.
- Make the zero value useful where possible (`sync.Mutex`, `bytes.Buffer`).
- Pointer receivers when in doubt; value receivers for small immutable types; do not mix them on
  one type. Receiver names short and consistent, never `this` or `self`.
- No stutter: `bytes.Buffer`, not `bytes.BytesBuffer`. Package names short, lower case, no
  `util`, `common` or `helpers`.
- Initialisms keep one case: `ServeHTTP`, `appID`, `userURL`.

## Errors
- Errors are values: return `error` as the last result and handle it at once; indent the error
  path and keep the happy path at the left margin.
- Never discard an error with `_` without a comment explaining why.
- Wrap with context using `fmt.Errorf("load config: %w", err)`; inspect with `errors.Is` and
  `errors.As`. Error strings are lower case with no trailing punctuation.
- No in-band errors: return `(value, error)` or `(value, ok)` instead of `-1` or `""`.
- `panic` only for programmer errors that cannot be handled; never for normal failure.

## Concurrency
- Pass `context.Context` as the first parameter; never store it in a struct; respect
  cancellation in every blocking call.
- Every goroutine has a clear exit; no goroutine blocks forever on a channel. Use
  `errgroup` or a `sync.WaitGroup` to wait and collect errors.
- Prefer synchronous APIs; let callers add concurrency.
- Share memory by communicating where it fits; a mutex is fine for protecting a small struct.
- Bound concurrency (worker pools, semaphores); close channels from the sender side only.
- Run tests with `-race`.

## Structure and testing
- Table-driven tests with subtests (`t.Run`); failure messages in `got X, want Y` order.
- `internal/` packages for code that must not be imported from outside the module.
- `golang-standards/project-layout` is a community collection, not an official standard; start
  flat and add packages when they earn it.
- `crypto/rand` for secrets, never `math/rand`.

## Agent pitfalls
- Declaring interfaces next to their only implementation "for testability".
- Java-style getters (`GetName`) and deep package hierarchies.
- Ignoring returned errors, or logging and returning the same error (double handling).
- Starting goroutines without cancellation or a wait.
- Over-using generics where an interface or a concrete type is clearer.
