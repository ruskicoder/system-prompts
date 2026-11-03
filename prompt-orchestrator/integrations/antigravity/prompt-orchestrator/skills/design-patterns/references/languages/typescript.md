# TypeScript and JavaScript

Authorities: the TypeScript Handbook (including "Do's and Don'ts"), the TSConfig reference,
MDN for JavaScript semantics, the ECMAScript specification. The project's formatter (Prettier,
Biome) and linter (ESLint with typescript-eslint, Biome) decide style. New TypeScript code runs
with `strict` enabled.

## Idioms that replace classic patterns

| Classic pattern | TypeScript form |
|-----------------|-----------------|
| Strategy, Command | Functions; a `Record<Key, Handler>` map |
| State, Visitor | Discriminated unions with a `kind` field and exhaustive `switch` checked with `never` |
| Factory | Plain functions returning objects or class instances |
| Builder | Object literals with optional properties; `satisfies` to check them against a type |
| Singleton | An ES module export (modules evaluate once per realm); pass dependencies explicitly where tests need control |
| Observer | `EventTarget`, Node `EventEmitter`, framework signals or stores |
| Iterator | Generators, `for...of`, async iterators with `for await` |
| Decorator (GoF) | Higher-order functions wrapping functions; framework decorators only where the framework uses them |
| Adapter | A function or module translating a vendor SDK into your own types |
| Interface | `interface` or `type` describing shape (structural typing); classes only when state and behaviour belong together |

## Types
- Primitive types `string`, `number`, `boolean`, `symbol`, `object`, never the boxed `String`,
  `Number` and friends.
- `unknown` instead of `any`; narrow with type guards. `any` only during migration, with a lint
  rule against new uses.
- Callbacks whose result is ignored return `void`; callback parameters are not optional unless
  callers really may omit them.
- Union types instead of overloads that differ in one parameter's type; optional parameters
  instead of overloads that differ only in trailing parameters; order overloads specific first.
- Model impossible states out: unions over flag combinations; branded types for ids where
  mixing them is a real risk.
- Validate untrusted data at runtime at the boundary (zod, valibot or equivalent) and derive the
  static type from the schema; a type assertion (`as`) is not validation.
- Prefer `readonly` and `as const` for data that must not change.

## Errors and async
- Throw `Error` subclasses, never strings; include the cause (`new Error(msg, { cause })`).
- Every promise is awaited, returned or explicitly handled; enable the floating-promise lint.
- `Promise.all` for independent work, `Promise.allSettled` when partial failure is acceptable;
  pass `AbortSignal` for cancellation.
- Do not mix callbacks and promises in one API.

## Structure
- ES modules; named exports over default exports for easier refactoring; no barrel files that
  create cycles or slow builds.
- Keep framework code (React components, Express handlers) thin over plain functions.
- Strict null checks: handle `undefined` explicitly; use optional chaining and nullish
  coalescing (`??`), not `||`, when `0` or `""` are valid values.

## Agent pitfalls
- `any` and `as` casts to silence the compiler.
- Classes with only static methods (use a module).
- Enums where a union of string literals is simpler (keep enums if the codebase uses them).
- Unhandled promise rejections and `forEach` with `async` callbacks.
- Copying server data into global client state instead of a data-fetching cache.
