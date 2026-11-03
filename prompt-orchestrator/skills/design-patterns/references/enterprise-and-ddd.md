# Enterprise Application and Domain-Driven Design Patterns

Load this when the force is about where business logic lives, how it reaches the database, or
how a large domain is split and modelled. Names follow Fowler's *Patterns of Enterprise
Application Architecture* catalogue and Evans' *DDD Reference*; descriptions here are our own.
Most frameworks and ORMs already implement several of these: name what the framework provides
before building one.

## Organising domain logic

| Pattern | Shape | Fits | Move on when |
|---------|-------|------|--------------|
| Transaction script | One procedure per business operation, calling the database directly | Simple rules, CRUD, small apps | The same rules repeat across scripts |
| Table module | One class per table handling all its rows | Record-set-oriented platforms | Rarely chosen today |
| Domain model | Objects with behaviour and data that enforce the rules | Rich, changing rules worth testing without a database | The rules are thin: a domain model adds mapping cost for nothing |
| Service layer | Application operations that coordinate domain objects, transactions and security for each use case | Several clients (UI, API, jobs) share the same operations | A service per entity that only forwards to a repository is a pass-through |

An anemic domain model (data classes plus services holding all rules) is a valid transaction
script style when the rules are thin; it becomes a problem when rules exist but are scattered
across services and duplicated.

## Data source patterns

| Pattern | Shape | Fits | Cautions |
|---------|-------|------|----------|
| Table data gateway / row data gateway | An object that wraps SQL for a table, or for one row | Transaction scripts, thin data access | Keep SQL in one place |
| Active record | A row object that knows how to load and save itself and carries domain logic | Domain logic close to the schema; Rails, Laravel Eloquent, Django models | Couples the domain to the schema; heavy logic outgrows it |
| Data mapper | A separate layer moves data between domain objects and tables; the domain knows nothing of persistence | Domain model differs from the schema; Hibernate, EF Core, SQLAlchemy ORM | Mapping cost and ORM complexity |
| Repository | A collection-like interface for aggregates, hiding queries | Domain model with aggregates; testing without a database | Do not wrap an ORM repository in another; generic repositories with every query method leak persistence |
| Unit of work | Tracks changed objects and commits them in one transaction | Several objects change in one operation | The ORM session or `DbContext` usually is one already |
| Identity map | One in-memory object per database row within a session | Avoids duplicate objects and inconsistent updates | Provided by most ORMs |
| Lazy load | Load related data on first access | Large object graphs | N+1 queries: load eagerly what each use case needs |
| Query object | A query represented as an object or composable expression | Dynamic filters | Prefer the ORM's query builder |

Mapping patterns (identity field, foreign key mapping, association table, embedded value,
serialized LOB, single-table, class-table and concrete-table inheritance) are ORM configuration
choices: pick per entity by query needs and schema evolution, and prefer composition over deep
inheritance in tables.

## Other enterprise patterns

| Pattern | Use |
|---------|-----|
| Data transfer object (DTO) | Carry data across a process or API boundary; keep it free of behaviour; do not reuse it as the domain model |
| Remote facade | Coarse-grained interface over fine-grained objects to cut network round trips |
| Gateway | Wrap access to an external system behind an interface in your own terms (same idea as an adapter) |
| Separated interface / plugin | Define an interface in one package, implement it in another, wire it at configuration time |
| Service stub | Replace a slow or unavailable service in tests |
| Value object | Small immutable object compared by value (money, date range, email address) |
| Money | Amount plus currency, with rounding and allocation rules; never floating point for money |
| Special case | An object for the absent or exceptional case instead of `null` checks |
| Optimistic offline lock | Detect conflicting edits with a version number; the default for web apps |
| Pessimistic offline lock | Prevent concurrent edits by locking; only when conflicts are frequent and costly |
| Session state (client, server, database) | Choose by size, security and scaling: stateless servers favour client or database session state |

## Domain-driven design: tactical patterns

| Pattern | Rule |
|---------|------|
| Entity | Has identity that persists through changes; equality by identity |
| Value object | No identity; immutable; equality by value; put behaviour on it |
| Aggregate | A cluster of entities and value objects with one root that guards its invariants. Reference other aggregates by id. Change one aggregate per transaction; reach consistency with others through domain events |
| Domain event | A past-tense fact the domain cares about (`OrderPlaced`); raised by aggregates, handled inside or across contexts |
| Domain service | An operation that belongs to no single entity or value object; stateless; named in the domain language |
| Repository | One per aggregate root, returning whole aggregates |
| Factory | Creation of complex aggregates when constructors are not enough |
| Specification | A named, combinable business rule (`isOverdue.and(isHighValue)`); a predicate function is the lighter form |
| Module | Groups concepts by domain meaning, not by technical type |

Aggregate design: keep aggregates small; design them around true invariants, not around
navigation convenience; if two things can be consistent eventually, they belong in different
aggregates.

Supple design (from the DDD Reference): intention-revealing interfaces, side-effect-free
functions, assertions (state pre- and postconditions), standalone classes, closure of
operations, and declarative design. These match the clean-code skill's rules.

## Domain-driven design: strategic patterns

| Pattern | Use |
|---------|-----|
| Ubiquitous language | One vocabulary per context, used in code, tests and conversation |
| Bounded context | The boundary inside which a model and its language are consistent; usually aligns with a team and a deployable or module |
| Context map | The documented relationships between contexts |
| Partnership | Two teams succeed or fail together and coordinate closely |
| Shared kernel | A small shared model both teams change only together |
| Customer-supplier | The upstream team plans for the downstream team's needs |
| Conformist | The downstream team adopts the upstream model as is |
| Anti-corruption layer | The downstream team translates the upstream model at its boundary |
| Open host service and published language | The upstream offers a documented protocol and shared format for many consumers |
| Separate ways | No integration; duplicate instead |
| Big ball of mud | Name a tangled area honestly and wall it off |

Distillation: identify the core domain (where the business competes) and spend the best design
effort there; buy or use generic solutions for generic subdomains; keep supporting subdomains
simple.

When to use DDD at all: complex, changing business rules with domain experts available. For
CRUD or data pipelines, transaction scripts and plain data access are the better fit.
