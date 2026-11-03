# Python

Authorities: PEP 8 (style), PEP 20 (the Zen of Python), PEP 257 (docstrings), PEP 484 and later
typing PEPs, the standard library documentation. A formatter (Black or Ruff format) and a linter
(Ruff, Flake8, Pylint) decide style; a type checker (mypy or Pyright) runs in CI for typed code.

## Idioms that replace classic patterns

| Classic pattern | Python form |
|-----------------|-------------|
| Strategy, Command | A function or callable passed in; a dict from key to function |
| Template Method | A function taking the varying steps as callables; an abstract base class only when a family of classes exists |
| Factory | A module-level function or a `@classmethod` alternative constructor (`from_json`) |
| Builder | Keyword arguments with defaults, or a `dataclass` with defaults |
| Singleton | A module (modules are imported once); pass instances explicitly where tests need control |
| Iterator | Generators (`yield`) and generator expressions; `itertools` |
| Decorator (GoF) | Wrapper objects, or function decorators (`@functools.wraps`) for cross-cutting behaviour |
| Observer | A list of callbacks, or signals in the framework in use |
| Visitor | `match` statements (3.10+) or `functools.singledispatch` |
| Interface | `typing.Protocol` for structural typing; `abc.ABC` when a shared base implementation helps |
| Value object | `@dataclass(frozen=True)` or `NamedTuple` |
| Resource guard | Context managers (`with`, `contextlib.contextmanager`) |

## Data and types
- `dataclasses` (or attrs, or Pydantic at I/O boundaries) for records; do not hand-write
  `__init__` and `__eq__` for plain data.
- Type hints on public functions; `Protocol` over inheritance for dependencies; `Optional` or
  `X | None` made explicit; avoid `Any` except at untyped boundaries.
- Enums (`enum.Enum`, `StrEnum`) instead of magic strings.
- Compare to `None` with `is` / `is not`; test sequence emptiness by truthiness; use
  `isinstance` rather than comparing types.

## Errors
- Exceptions derive from `Exception`; name them with an `Error` suffix.
- Catch specific exceptions; never a bare `except:`. Keep `try` blocks minimal.
- Chain with `raise NewError(...) from err` to keep the cause.
- Ask forgiveness rather than permission (EAFP) for races like file access; check first (LBYL)
  when the check is cheap and the failure would be confusing.
- No `return`, `break` or `continue` inside `finally` (it silently swallows exceptions).
- Release resources with `with`.

## Concurrency
- I/O-bound: `asyncio` with task groups (3.11+) for structured concurrency, or threads for
  blocking libraries; never call blocking functions inside a coroutine (use `asyncio.to_thread`).
- CPU-bound: processes (`concurrent.futures.ProcessPoolExecutor`, multiprocessing), or native
  extensions; the global interpreter lock limits threads for CPU work in default CPython builds.
- Bound queues and semaphores for concurrency against dependencies.

## Structure and naming
- `snake_case` functions, variables and modules; `CapWords` classes; `UPPER_CASE` constants; a
  leading underscore for internal names.
- No mutable default arguments: write `def f(items=None)` and then
  `if items is None: items = []`.
- Functions over classes when there is no state; modules as the unit of organisation.
- `def` instead of assigning a lambda to a name.

## Agent pitfalls
- Java-style class hierarchies, getters and setters (use attributes, `@property` when logic is
  needed).
- Swallowing exceptions with `except Exception: pass`.
- Mutable default arguments.
- Building strings for SQL or shell commands (use parameters and `subprocess` argument lists).
- Untyped `dict` payloads passed deep into the code instead of dataclasses.
