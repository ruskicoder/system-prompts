# Java

Authorities: Bloch, *Effective Java* (third edition), the Java Language Specification and JEPs
for feature semantics, the Google Java Style Guide or the project's own style. Checkstyle,
Error Prone, SpotBugs or Sonar where the project uses them; the project's formatter decides
layout.

Assume the JDK the project targets; features below note the release where they became final.

## Idioms that replace classic patterns

| Classic pattern | Java form |
|-----------------|-----------|
| Strategy, Command | Functional interfaces and lambdas (`Function`, `Supplier`, a custom single-method interface) |
| Factory | Static factory methods (`of`, `from`, `valueOf`, `newInstance`) instead of constructors where naming or caching helps |
| Builder | A static nested builder for many optional parameters; records with compact constructors for plain data |
| Singleton | A single-element `enum` when one is required; prefer dependency injection |
| Value object | `record` (final in JDK 16) |
| State, Visitor | `sealed` interfaces (JDK 17) with records and pattern matching for `switch` (JDK 21), exhaustive without `default` |
| Template Method | A method taking lambdas for the varying steps; an abstract class only for real families |
| Observer | Listener interfaces, `Flow` publishers, or the framework's events |
| Iterator | `Iterable`, streams; avoid exposing internal collections |
| Decorator, Proxy | Wrapper classes; framework AOP and dynamic proxies where the framework provides them |

## Classes and types (Effective Java themes)
- Minimise mutability: final fields, no setters on value types, defensive copies of mutable
  inputs and outputs.
- Favour composition over inheritance; design classes for inheritance or make them final.
- Prefer interfaces to abstract classes for types; program to interfaces in signatures.
- Override `equals`, `hashCode` and `toString` together, or use records.
- Use enums instead of int constants; `EnumSet` and `EnumMap` for flags and maps.
- Generics without raw types; bounded wildcards for flexible APIs (producer `extends`,
  consumer `super`).
- Return empty collections or `Optional` instead of `null`; `Optional` for return values only,
  not fields or parameters.

## Errors
- Checked exceptions for recoverable conditions callers must handle; unchecked for programming
  errors. Do not use exceptions for control flow.
- Throw exceptions appropriate to the abstraction; wrap with the cause.
- Never swallow exceptions; never catch `Throwable` or `Error` in business code.
- try-with-resources for anything `AutoCloseable`.

## Concurrency
- Executors instead of raw threads; virtual threads (final in JDK 21) for high-concurrency
  blocking I/O; avoid pinning by not holding `synchronized` locks across blocking calls where
  the JDK version pins virtual threads.
- Prefer immutable data and `java.util.concurrent` types (`ConcurrentHashMap`, `CompletableFuture`,
  locks, atomics) to `wait`/`notify`.
- Structured concurrency (`StructuredTaskScope`) is a preview API in recent JDKs; use it only
  where preview features are enabled.
- Document thread-safety of public classes.

## Structure
- Packages by feature rather than by layer for larger codebases; package-private by default.
- Frameworks (Spring, Jakarta EE, Micronaut, Quarkus) already provide DI, transactions, AOP and
  templates: use them instead of hand-built factories and proxies.
- Constructor injection; no field injection in new code.

## Agent pitfalls
- Getters and setters generated for every field by default.
- `Optional.get()` without checking, or `Optional` as a field.
- Checked exceptions wrapped in `RuntimeException` without context.
- Static utility classes holding business logic.
- Interfaces for every service with one implementation (Spring proxies do not require them).
