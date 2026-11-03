# Rust

Authorities: the Rust API Guidelines (checklist codes such as C-CASE, C-GOOD-ERR, C-NEWTYPE),
The Rust Programming Language, the Rustonomicon for `unsafe`, Clippy lints. `rustfmt` decides
formatting; `cargo clippy -- -D warnings` and `cargo test` run in CI.

## Idioms that replace classic patterns

| Classic pattern | Rust form |
|-----------------|-----------|
| Strategy | A generic parameter bounded by a trait (static dispatch), a trait object `Box<dyn Trait>` when the set is open at runtime, or a closure |
| Command | A closure (`Box<dyn FnOnce()>`) or an enum of commands |
| State | An enum with exhaustive `match`, or the typestate pattern (each state a type, transitions consume `self`) |
| Visitor | `match` over an enum; a visitor trait only for open sets such as AST crates |
| Builder | A builder type with `fn field(mut self, v) -> Self` and a final `build()` returning `Result` when validation can fail (C-BUILDER) |
| Factory | Associated constructor functions (`new`, `with_capacity`, `from_*`) (C-CTOR) |
| Iterator | Implement `Iterator`; expose `iter`, `iter_mut`, `into_iter` (C-ITER) |
| Decorator | A wrapper type implementing the same trait, or middleware layers (tower `Layer`) |
| Singleton | `static` with `OnceLock` or `LazyLock`; prefer passing a handle |
| Observer | Channels (`std::sync::mpsc`, `tokio::sync::broadcast`) or callback vectors |
| RAII resource guard | `Drop`; destructors must not fail (C-DTOR-FAIL) |

## Types and API design
- Newtypes for distinct meanings (`struct UserId(u64)`) and custom types instead of `bool` or
  `Option` arguments that hide meaning (C-NEWTYPE, C-CUSTOM-TYPE).
- Make invalid states unrepresentable with enums and typestate.
- Private struct fields for future flexibility (C-STRUCT-PRIVATE); sealed traits when outside
  implementations must be prevented (C-SEALED).
- Implement common traits eagerly where they make sense: `Debug`, `Clone`, `PartialEq`,
  `Default`, `Display`, `From` and friends (C-COMMON-TRAITS, C-CONV-TRAITS).
- Accept the most general input that works (`&str`, `impl AsRef<Path>`, `impl IntoIterator`);
  let callers decide on copying and allocation (C-CALLER-CONTROL, C-GENERIC).
- No out-parameters; return tuples or structs (C-NO-OUT).
- Naming: `as_` (cheap borrow), `to_` (expensive conversion), `into_` (consumes self) (C-CONV);
  no `get_` prefix for plain getters (C-GETTER).

## Errors
- `Result<T, E>` for recoverable errors, `panic!` only for bugs and broken invariants.
- Propagate with `?`; never `unwrap` or `expect` in library code paths that can fail at runtime;
  `expect("reason")` only where failure is impossible and the reason says why.
- Libraries define error enums implementing `std::error::Error` and `Display` (C-GOOD-ERR),
  often with `thiserror`; applications may aggregate with `anyhow` or similar and add context.
- Document error, panic and safety conditions in rustdoc sections (C-FAILURE).

## Ownership and concurrency
- Borrow by default, clone deliberately; reach for `Rc`/`Arc` and interior mutability only when
  ownership cannot be expressed statically.
- `Send` and `Sync` bounds where types cross threads (C-SEND-SYNC); `Arc<Mutex<T>>` for shared
  state, channels for hand-off.
- Async: one runtime per binary; never block inside async code (use `spawn_blocking`); hold no
  `std::sync::Mutex` guard across `.await`.
- `unsafe` only with a `// SAFETY:` comment stating the invariant, in the smallest block, behind
  a safe API.

## Agent pitfalls
- `.clone()` everywhere to silence the borrow checker.
- `unwrap()` in production paths.
- `Box<dyn Trait>` where a generic or an enum would do.
- `Rc<RefCell<...>>` graphs translated from object-oriented designs.
- Stringly-typed errors (`Result<T, String>`) in libraries.
