# C++

Authorities: the C++ Core Guidelines (isocpp, MIT-style licence; rule ids cited below), the
standard library reference, the project's chosen standard (C++17, 20, 23). clang-format for
layout; clang-tidy (with `cppcoreguidelines-*` and `modernize-*` checks), sanitizers and
warnings-as-errors in CI.

## Idioms that replace classic patterns

| Classic pattern | C++ form |
|-----------------|----------|
| Strategy | Templates and concepts (static), `std::function` or a virtual interface (dynamic), lambdas |
| Command | Lambdas or `std::function` stored in queues |
| State, Visitor | `std::variant` with `std::visit`, or an enum class with `switch` (Enum.3) |
| Factory | Functions returning `std::unique_ptr<Base>` (ownership explicit, R.20) or values |
| Builder | Aggregate initialisation with designated initialisers (C++20), or a builder returning by value |
| Singleton | A function-local static (thread-safe initialisation); prefer passing references (I.3 avoid singletons) |
| Resource guard | RAII types with destructors (R.1); `std::lock_guard`/`std::scoped_lock` for locks (CP.20) |
| Iterator | Ranges and standard iterators; range-based `for` |
| Observer | Callbacks with explicit lifetime management (`std::weak_ptr` or tokens that unregister) |
| Template Method | Non-virtual interface idiom, or CRTP for static polymorphism |

## Resources and ownership
- Manage every resource through an owning object with a destructor (R.1); no explicit `new`
  and `delete` (R.11); no `malloc`/`free` (R.10).
- Raw pointers and references never own (R.3, I.11); `std::unique_ptr` for exclusive ownership,
  `std::shared_ptr` only when ownership is truly shared (R.20, R.21).
- Take smart pointers as parameters only to express lifetime semantics (R.30); otherwise take
  `T&`, `const T&` or `T*` (F.7). Pass cheap types by value, others by `const&` (F.16).
- Prefer scoped objects to heap allocation (R.5); `std::span` and `std::string_view` for
  non-owning views, never outliving their source.

## Classes
- Rule of zero: let members manage resources so the class needs no special members (C.20); if
  you define or delete one of copy, move or destructor, handle them all (C.21).
- `class` when there is an invariant, `struct` for independent data (C.2); minimise exposed
  members (C.9); no `protected` data (C.133).
- Base class destructors public and virtual, or protected and non-virtual (C.35); polymorphic
  classes suppress public copy and move (C.67).
- Immutable and `const` by default (Con.1, Con.2); avoid implicit conversion operators (C.164).
- Always initialise objects (ES.20); prefer `{}` initialisation (ES.23); avoid casts (ES.48).

## Errors
- Throw exceptions to signal failure to perform a task (E.2), only for errors (E.3); purpose-made
  exception types (E.14); throw by value, catch by reference (E.15).
- `noexcept` where throwing is impossible or unacceptable (E.12), and on move operations.
- In codebases that disable exceptions, use `std::expected` (C++23) or an equivalent result type
  consistently, with RAII still handling cleanup (E.25).

## Concurrency
- Avoid data races (CP.2); minimise shared writable data (CP.3); never use `volatile` for
  synchronisation (CP.8).
- RAII locks only (CP.20); `std::scoped_lock` for several mutexes (CP.21); never call unknown
  code while holding a lock (CP.22); keep critical sections short (CP.43); name your lock guards
  (CP.44); wait on condition variables with a predicate (CP.42).
- `std::jthread` with stop tokens (C++20) over raw `std::thread`; run ThreadSanitizer in CI.

## Agent pitfalls
- Raw owning pointers and manual `delete`.
- `shared_ptr` by default where `unique_ptr` fits.
- Returning references or views to locals or temporaries (F.43).
- C-style casts and arrays where `std::array`, `std::span` or containers fit.
- Undefined behaviour from uninitialised variables, signed overflow, or out-of-bounds access;
  build tests with AddressSanitizer and UndefinedBehaviorSanitizer.
