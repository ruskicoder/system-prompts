# Dart and Flutter

Authorities: Effective Dart (dart.dev: style, documentation, usage, design), the Flutter
architecture recommendations (see `presentation.md`), the `lints` and `flutter_lints` packages.
`dart format` decides layout; `dart analyze` with the recommended lint set runs in CI.

## Idioms that replace classic patterns

| Classic pattern | Dart form |
|-----------------|-----------|
| Strategy, Command | Functions and function types; avoid one-member abstract classes when a function will do |
| Utility class | Top-level functions and constants instead of classes with only static members |
| Builder | Named parameters with defaults; cascades (`..`) instead of returning `this` for chaining |
| Factory | `factory` constructors and named constructors (`Point.fromJson`) |
| Singleton | A top-level final instance or a factory constructor returning a cached instance; prefer injection |
| State, Visitor | `sealed` classes with exhaustive `switch` expressions and patterns (Dart 3) |
| Value object | Immutable classes with `final` fields and `const` constructors; generated with freezed or built_value in Flutter apps |
| Observer | `Stream`, `ChangeNotifier`/`Listenable` in Flutter view models |
| Mixin | `mixin` for shared behaviour; prefer pure `mixin` or pure `class` over `mixin class` |

## Design rules (Effective Dart)
- Names: consistent terms; the most descriptive noun last; non-imperative verb phrases for
  booleans (`isEnabled`, `canClose`), positive forms; imperative verbs for side-effect methods;
  no `get` prefix; `to___()` copies and `as___()` views.
- Privacy with a leading underscore; group related classes in one library.
- Class modifiers (`final`, `base`, `interface`, `sealed`) to state how a class may be extended
  or implemented; do not extend or implement classes not designed for it.
- `final` fields and `const` constructors where possible; getters for field-like reads without
  side effects.
- Type annotations on public APIs, fields and uninitialised variables; not on initialised
  locals. `Object?` instead of `dynamic` unless dynamic dispatch is intended.
- Named parameters instead of positional booleans; inclusive start and exclusive end for ranges.
- Return empty collections and streams, not nullable ones; `Future<void>` for async members that
  produce nothing.
- Override `hashCode` with `==`; avoid custom equality on mutable classes.

## Errors and async
- Throw `Exception` implementations for recoverable conditions and `Error` subclasses for
  programming mistakes; never catch `Error` to continue.
- Every `Future` is awaited or explicitly ignored with `unawaited` (lint `unawaited_futures`).
- Cancel stream subscriptions and dispose controllers in Flutter `dispose`.
- Isolates for CPU-heavy work (`Isolate.run`, `compute` in Flutter).

## Flutter specifics
- No business logic in widgets; widgets render state from view models; commands for user actions.
- `const` widgets where possible; split large build methods into widgets, not helper methods
  returning widgets.
- Repositories and services injected (provider, get_it or the codebase's choice), with fakes in
  tests.

## Agent pitfalls
- Classes with only static members.
- `dynamic` everywhere and unchecked JSON maps passed deep into the app.
- Unawaited futures and leaked stream subscriptions.
- Business logic and network calls inside `build`.
