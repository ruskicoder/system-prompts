# C# and .NET

Authorities: .NET Framework Design Guidelines (detailed API rules), the C# coding conventions
on Microsoft Learn (an example set adopted from the runtime and Roslyn styles, not an
authoritative list), the .NET runtime coding style. `.editorconfig` plus Roslyn analyzers
enforce style; nullable reference types enabled for new code.

## Idioms that replace classic patterns

| Classic pattern | C# form |
|-----------------|---------|
| Strategy, Command | `Func<>` and `Action<>` delegates or lambdas; an interface when the strategy has several members or state |
| Factory | Static factory methods; DI container registrations (`Microsoft.Extensions.DependencyInjection`) for object graphs |
| Builder | Object initializers and `required` / `init` properties; fluent builders for complex configuration (as in `WebApplication.CreateBuilder`) |
| Singleton | A DI registration with singleton lifetime, not a static instance |
| Observer | Events and `IObservable<T>`; channels (`System.Threading.Channels`) for producer-consumer |
| Decorator, Chain of Responsibility | ASP.NET Core middleware and `DelegatingHandler` for HTTP clients; decorator registration in DI |
| Iterator | `IEnumerable<T>` with `yield return`; `IAsyncEnumerable<T>` with `await foreach` |
| Value object | `record` and `record struct` (value equality) |
| State, Visitor | Pattern matching with `switch` expressions over records or sealed hierarchies |
| Unit of work, Repository | EF Core `DbContext` and `DbSet<T>` already implement both; do not wrap them by default |

## Language rules (from the conventions)
- Use current language features: language keywords for types (`string`, `int`), string
  interpolation, raw string literals, collection expressions, file-scoped namespaces, `using`
  declarations, `using` directives outside the namespace.
- `var` only when the type is obvious from the right-hand side.
- Catch only exceptions you can handle; no catching `System.Exception` without a filter; use
  specific exception types; rethrow with `throw;` to keep the stack.
- `async`/`await` for I/O; avoid blocking on tasks (`.Result`, `.Wait()`); consider
  `ConfigureAwait(false)` in library code; accept and pass `CancellationToken`.
- LINQ for collection manipulation with meaningful query variable names; watch the
  `IQueryable` versus `IEnumerable` boundary, which changes where the query runs.
- `Func<>`/`Action<>` instead of custom delegate types.

## Types and errors
- Nullable reference types on; treat warnings as errors in new projects.
- Records for immutable data; `required` members instead of long constructors for data types.
- Exceptions for exceptional conditions; `TryParse`-style methods (`bool TryX(out T)`) where
  failure is common and expected.
- `IDisposable`/`IAsyncDisposable` with `using`; never rely on finalizers for cleanup.

## Structure (ASP.NET Core and services)
- Constructor injection; options pattern (`IOptions<T>`) for configuration; `HttpClient`
  through `IHttpClientFactory`, never created per request.
- Minimal APIs or controllers kept thin; validation at the boundary; problem details for errors.
- Avoid service-locator use of `IServiceProvider` inside business code.

## Agent pitfalls
- `async void` outside event handlers.
- `.Result` and `.Wait()` causing deadlocks or thread starvation.
- New `HttpClient` per call (socket exhaustion).
- Generic repository wrappers over EF Core.
- Catching `Exception` and logging without rethrowing or handling.
