# Concurrency and Functional Patterns

Load this when the force is about work running at the same time, shared state between threads
or tasks, or structuring logic as transformations of data. Use the language's own concurrency
model first (see the matching file in `languages/`); the patterns below name what those models
implement.

## Concurrency: choose the model before the primitive

| Model | Shape | Fits | Cautions |
|-------|-------|------|----------|
| Shared memory with locks | Threads share data guarded by mutexes | Small critical sections, existing threaded code | Deadlocks, contention, forgotten locks |
| Message passing / channels | Tasks own their data and communicate by sending messages | Go goroutines and channels, Erlang/Elixir processes, actor frameworks | Unbounded mailboxes, lost messages, backpressure |
| Async / await on an event loop | Cooperative tasks yield at I/O points | I/O-bound servers and clients (JavaScript, Python asyncio, C#, Rust async, Kotlin coroutines, Swift concurrency) | Blocking calls freeze the loop; CPU work needs a separate pool |
| Data parallelism | Split data, process chunks in parallel, combine | CPU-bound batch work | Overhead on small inputs; ordering of results |
| Immutable data | No shared mutable state at all | Functional cores, configuration, caches of values | Copy cost on large structures; use persistent structures |

## Concurrency patterns

| Pattern | Use | Cautions |
|---------|-----|----------|
| Thread pool / executor | Reuse a bounded set of workers for many tasks | Size from the workload (CPU-bound near core count; I/O-bound higher); bound the queue |
| Producer-consumer | Decouple producers from consumers with a bounded queue | Bound the queue so producers feel backpressure |
| Future / promise | A handle to a result computed later | Always handle failure and cancellation |
| Structured concurrency | Child tasks live inside a scope that waits for them and cancels them on failure | Prefer it wherever the language offers it (Kotlin coroutine scopes, Swift task groups, Python task groups and Trio nurseries; Java's `StructuredTaskScope` is a preview API) |
| Actor | An object that owns its state and processes one message at a time | Avoid synchronous request chains between actors (deadlock risk) |
| Active object | Method calls become requests queued to the object's own thread | Similar to an actor with a typed interface |
| Monitor object | Methods synchronised on one lock with condition waits | Keep critical sections short; never call out while holding the lock |
| Readers-writer lock | Many readers or one writer | Helps only when reads dominate and are long; can starve writers |
| Guarded suspension / balking | Wait until a condition holds, or return at once if it does not | Always wait in a loop that rechecks the condition |
| Reactor / proactor | Demultiplex I/O events to handlers (readiness or completion based) | Implemented by event loops (epoll, kqueue, IOCP, libuv, Netty, Tokio) |
| Thread-local storage | Per-thread state | Breaks with thread pools and async tasks that hop threads; prefer explicit context |
| Barrier / latch / semaphore | Coordinate phases, wait for N events, bound concurrency | Semaphores are a clean way to cap concurrent calls to a dependency |
| Double-checked locking | Lazy initialisation with a lock taken only once | Correct only with proper memory semantics (volatile or atomics); prefer the language's lazy initialiser |
| Pipeline / fan-out fan-in | Stages connected by channels; spread work and merge results | Close channels and propagate cancellation |

Rules for any concurrent code:
- Every task has an owner, a lifetime and a cancellation path. No fire-and-forget without a
  supervisor or an error handler.
- Bound everything: queues, pools, buffers, concurrency against each dependency.
- Prefer immutable messages and confined state to shared mutable state.
- Hold a lock for as little as possible; never do I/O or call unknown code while holding it.
  Acquire multiple locks in one global order.
- Propagate deadlines and cancellation through every layer.
- Test with race detectors and model checkers where the toolchain has them (`go test -race`,
  ThreadSanitizer for C, C++ and Rust, the `loom` crate for Rust), and with stress tests that
  vary timing.

## Functional patterns

| Pattern | Use |
|---------|-----|
| Pure functions | Same input, same output, no side effects; the default for business rules |
| Functional core, imperative shell | Pure logic in the middle, I/O at the edges; makes logic testable without fakes |
| Immutability | Values that never change; updates return new values |
| Higher-order functions | Pass behaviour as functions; replaces Strategy, Command and Template Method in most languages |
| Map, filter, reduce / pipelines | Express transformations as a chain of small steps |
| Algebraic data types and pattern matching | Sum types (sealed classes, enums with data, unions) plus exhaustive matching replace type switches and the Visitor pattern |
| Option / Maybe | Model absence explicitly instead of `null` |
| Result / Either and railway-oriented flow | Model expected failure as a value; chain steps that short-circuit on the first error |
| Composition and currying | Build functions from smaller ones; partial application for configuration |
| Memoisation | Cache results of pure functions; only for pure ones |
| Lazy evaluation / generators | Produce values on demand; streams over large data |
| Lenses / copy-with | Update nested immutable data without manual copying (records `with`, Kotlin `copy`, Immer) |

Cautions:
- Readability first: a chain of combinators a reader must decode is worse than a plain loop.
- Do not import monad libraries into a codebase whose idioms do not use them; use the language's
  native result and option types.
- Exceptions stay the right tool for truly unexpected failures in languages built around them.
