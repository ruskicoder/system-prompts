# Ruby and Rails

Authorities: the community Ruby Style Guide (rubystyle.guide, the basis of RuboCop's defaults),
the Rails guides and the Rails doctrine for Rails apps. RuboCop (with rubocop-rails where
relevant) in CI; the project's `.rubocop.yml` decides.

## Idioms that replace classic patterns

| Classic pattern | Ruby form |
|-----------------|-----------|
| Strategy, Command | Blocks, procs and lambdas; any object responding to `call` |
| Iterator | `each` with blocks and `Enumerable`; external iteration with `Enumerator` |
| Decorator | `SimpleDelegator` or module prepend; presenters in Rails views |
| Observer | Callbacks, `ActiveSupport::Notifications`, or explicit publish-subscribe |
| Singleton | A module with `module_function`, or the `Singleton` module where truly needed |
| Value object | `Data.define` (Ruby 3.2) for immutable values; `Struct` for simple records; do not extend them by subclassing |
| Template Method | Modules with hook methods, or blocks passed to a method |
| Duck typing | Depend on the messages an object responds to, not its class |
| Active record | Rails models (see `enterprise-and-ddd.md`); move heavy rules to plain objects when models grow |

## Style rules (from the community guide)
- `snake_case` methods, variables, files and directories; `CapitalCase` classes and modules;
  `SCREAMING_SNAKE_CASE` constants.
- Predicate methods end in `?` (no `is_` prefix); methods with a dangerous counterpart end in `!`
  only when a safe version exists.
- Guard clauses over nested conditionals; `if` and `case` as expressions returning values.
- No explicit `return` where it is not needed for flow; no explicit `self` except for writers.
- `unless` for simple negatives, never with `else`.
- Prefer `raise` over `fail`.
- No class variables (`@@`); use class instance variables or configuration objects.
- `# frozen_string_literal: true` where the codebase uses it.

## Errors
- Rescue specific exceptions; never rescue `Exception` (it traps signals and `exit`); a bare
  `rescue` catches `StandardError` only.
- Do not suppress exceptions or use `rescue` as a modifier to hide failures.
- No exceptions for flow control; no `return` from `ensure`.
- Define custom errors inheriting from `StandardError`, grouped under one module error.

## Rails structure
- Fat models and skinny controllers until models grow; then extract service objects, form
  objects, query objects and presenters with single responsibilities.
- Avoid callbacks that hide side effects across models; prefer explicit service calls.
- Background jobs (Active Job) for slow work; keep jobs idempotent.
- N+1 queries: `includes`, `preload`, and the strict-loading checks.

## Agent pitfalls
- Java-style getters and setters (use `attr_reader` and friends).
- `rescue Exception` or swallowing errors.
- Monkey-patching core classes in application code.
- Callbacks with side effects on external systems.
- `for` loops instead of `each`.
