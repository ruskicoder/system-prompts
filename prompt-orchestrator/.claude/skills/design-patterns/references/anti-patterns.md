# Anti-Patterns

Load this to name a recurring bad solution in a review, or to check a design before building it.
Each entry gives how to recognise it and the direction out. Code-level smells and their
refactoring techniques are in the refactoring skill's `references/smells.md`; design red flags in
the clean-code skill's `references/principles.md`; messaging and API anti-patterns in
`messaging.md` and `api-design.md`.

Many anti-patterns began as reasonable choices that stopped fitting. Name each with evidence
(`path:line`, a metric, an incident) and propose the smallest move out.

## Code and design

| Anti-pattern | Recognise it by | Way out |
|--------------|-----------------|---------|
| God object | One class or module knows and does most things; most changes touch it | Extract classes by responsibility, one at a time (refactoring skill) |
| Big ball of mud | No discernible structure; everything depends on everything | Wall it off, define module boundaries at the edges, strangle inward |
| Spaghetti code | Control flow jumps unpredictably; deep nesting, flags, gotos | Decompose conditionals, extract functions, introduce state machines where state is implicit |
| Lava flow | Dead or half-understood code nobody dares remove | Find its callers and history; pin behaviour; delete what is unused |
| Golden hammer | One familiar tool or pattern applied to every problem | Name the force first (design-patterns Part 1); compare at least two options |
| Cargo cult | Structure copied without knowing why (layers, patterns, config) | Ask what each element buys; remove what buys nothing |
| Copy-paste programming | The same logic duplicated with small edits | DRY test in clean-code; extract once the duplication is real knowledge |
| Magic numbers and strings | Unexplained literals carrying rules | Named constants, enums or configuration |
| Boat anchor | Code kept "in case we need it" | Delete it; version control remembers |
| Poltergeist | Short-lived objects that only pass calls along | Inline them |
| Speculative generality | Hooks and abstractions for imagined needs | YAGNI gate; inline back to direct code |
| Singleton as global state | Mutable shared state reachable from anywhere | Pass the instance in; scope it explicitly |
| Anemic model with scattered rules | Rules duplicated across services around data-only classes | Move each rule next to the data it governs, or accept transaction scripts deliberately |
| Primitive obsession | Ids, money, units as bare strings and numbers | Value objects |
| Error hiding | Caught and ignored exceptions, empty catch blocks | Handle, rethrow with context, or let it fail |
| Premature optimisation | Complexity added for speed nobody measured | Measure first; keep the simple version until a profile says otherwise |

## Architecture

| Anti-pattern | Recognise it by | Way out |
|--------------|-----------------|---------|
| Distributed monolith | Services that must be deployed together; synchronous chains on every request | Merge back, or redraw boundaries by capability and move to asynchronous integration |
| Shared database between services | Several services write the same tables | One owner per table; others use its API or events |
| Entity services | One service per noun (`CustomerService`, `OrderService`) with no behaviour of its own | Boundaries by business capability or subdomain |
| Chatty services | Many fine-grained calls per user action | Coarser APIs, aggregation, data replication through events |
| Microservices first | A new product split into services before the domain is understood | Modular monolith first; split proven boundaries |
| Layer skipping or leaking | UI code querying the database; domain importing framework types | Enforce dependency direction with architecture tests or module boundaries |
| Configuration as code without types | Behaviour driven by unvalidated config files | Schema-validated configuration; fail at startup on bad config |
| Vendor lock-in by accident | Vendor SDK types spread through domain code | Adapters at the boundary; accept lock-in deliberately where it pays |

## Distributed and performance (Azure performance antipatterns and related)

| Anti-pattern | Recognise it by | Way out |
|--------------|-----------------|---------|
| Busy database | Business logic in stored procedures doing heavy processing | Move processing to the application tier; keep the database for data |
| Busy front end | Request threads doing heavy work | Move work to background jobs or queues |
| Chatty I/O | Many small network or storage requests | Batch, aggregate, cache |
| Extraneous fetching | Reading more data than needed (`SELECT *`, whole objects for one field) | Project only needed fields; paginate |
| Improper instantiation | Creating and disposing shared clients per request (HTTP, database, SDK clients) | One long-lived instance per process or pool |
| Monolithic persistence | One store for data with very different access patterns | Choose stores per access pattern where the cost is justified |
| No caching | Repeatedly computing or fetching stable data | Cache-aside with invalidation and limits |
| Noisy neighbour | One tenant consumes shared resources | Per-tenant quotas, throttling, bulkheads, stamps |
| Retry storm | Many layers retry the same failure at once | One retry budget, backoff with jitter, circuit breakers |
| Synchronous I/O | Blocking threads on I/O in a server | Asynchronous I/O end to end |
| N+1 queries | One query per item in a loop | Eager loading or a batched query |
| Unbounded resources | Queues, pools, caches or concurrency with no limit | Explicit limits and backpressure |

## Process
| Anti-pattern | Recognise it by | Way out |
|--------------|-----------------|---------|
| Big-bang rewrite | Replacing a working system in one release | Strangler fig with a deletion date (refactoring skill) |
| Analysis paralysis | Design that never converges | Timebox, decide by reversibility, spike the risky part |
| Design by committee | Every option kept to please everyone | One owner decides with a written record |
