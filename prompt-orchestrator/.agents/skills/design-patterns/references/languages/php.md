# PHP

Authorities: PHP-FIG standards (PSR-1, PSR-4 autoloading, PSR-12 and the PER Coding Style), the
PHP manual, PHP: The Right Way. PHP_CodeSniffer or PHP-CS-Fixer for style; PHPStan or Psalm for
static analysis at a strict level; PHPUnit or Pest for tests.

## Idioms that replace classic patterns

| Classic pattern | PHP form |
|-----------------|----------|
| Strategy, Command | Closures and first-class callables (`strlen(...)`, PHP 8.1); small interfaces for richer strategies |
| Factory | Static named constructors (`Money::fromCents()`); the framework container for object graphs |
| Builder | Named arguments (PHP 8.0) and constructor property promotion |
| Singleton | A container binding with shared lifetime, not a static instance |
| Value object | `readonly` properties (8.1) and `readonly` classes (8.2) |
| State, Visitor | Backed enums (8.1) with methods; `match` expressions |
| Decorator, Chain of Responsibility | PSR-15 middleware |
| Repository, Active record | Doctrine (data mapper with repositories) or Eloquent (active record): follow the framework in use |
| Iterator | Generators (`yield`) and `IteratorAggregate` |

## Language rules
- `declare(strict_types=1);` at the top of every file; type every parameter, property and
  return value; avoid `mixed` except at boundaries.
- Namespaces and PSR-4 autoloading through Composer; commit `composer.lock`.
- Constructor injection with interface type hints; do not use the container as a service
  locator inside business code.
- Enums instead of class constants for closed sets; `match` instead of `switch` for value
  mapping (strict comparison, no fall-through).
- Immutability for value objects with `readonly`; `with...()` methods return modified copies.

## Errors and security
- Exceptions, not error codes or `false` returns, for failures; catch specific exceptions;
  convert PHP warnings to exceptions in the framework's error handler.
- Database access through PDO or the ORM with bound parameters; never interpolate input into SQL.
- `password_hash` and `password_verify` for passwords; escape output in templates by default
  (Twig, Blade); validate input at the boundary.
- Keep queries out of templates: models or repositories for data access, views for
  presentation.

## Agent pitfalls
- Missing `strict_types` and untyped arrays passed everywhere (use typed DTOs).
- Business logic in controllers or templates.
- Static facades or global helpers inside domain code where injection is clearer (follow the
  framework's own conventions where it relies on facades).
- Suppressing errors with `@`.
- String-built SQL.
