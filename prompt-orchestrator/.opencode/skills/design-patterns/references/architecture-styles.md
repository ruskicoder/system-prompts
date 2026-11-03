# Architecture Styles

Load this when the force is about the shape of a whole application or system: how code is
layered, how parts are deployed, how they communicate. Technology choices, service boundaries
and the decision record belong to the system-design and architecture skills; this file routes
a force to a style and lists what each style costs.

## Choose by reversibility first
Spend design effort in proportion to how expensive a decision is to undo:

| Cost to reverse | Examples | How to decide |
|-----------------|----------|---------------|
| Cheap | Folder layout, layer order inside one deployable, where a module lives | Decide quickly; move later |
| Moderate | Repository versus direct ORM use, module boundaries, read models inside one database | Decide with evidence; revisit at milestones |
| Expensive | Splitting into services, event sourcing, multi-tenancy model, public plugin API, primary data store | Written decision with rejected alternatives (architecture skill), ideally after a spike |

## Code organisation styles (inside one deployable)

| Style | Shape | Fits | Costs and cautions |
|-------|-------|------|--------------------|
| Layered (n-tier) | Presentation, application or service, domain, data access; each layer calls the one below | CRUD-heavy apps, small teams, most framework defaults | Changes cut across all layers; watch for layers that only forward (pass-through) |
| Hexagonal (ports and adapters) | The application core defines ports; adapters implement them for UI, database, messaging, other systems | Domain logic worth protecting from frameworks; many external systems; test without infrastructure | One adapter per real external system; do not add ports for things that never vary |
| Onion and Clean Architecture | Concentric layers with dependencies pointing inward to the domain; use cases in an application ring | Same as hexagonal; teams that want explicit use-case objects | Ceremony for small apps: a use case class per CRUD operation that only forwards is a smell |
| Vertical slices | Code grouped by feature (request, handler, data access per slice) rather than by layer | Feature teams, apps where features change independently | Shared rules need a home; duplication across slices must be watched (DRY test in clean-code) |
| Modular monolith | One deployable split into modules with explicit public interfaces and owned data | The default for a new product and most teams; a path to services later | Needs enforced boundaries (build modules, architecture tests), or it decays into a ball of mud |
| Microkernel (plug-in) | A small core plus plug-ins discovered through a contract | Products with third-party or optional extensions (IDEs, browsers, tools) | The plug-in contract is a published surface: version it |
| Pipes and filters | Independent processing steps connected by a data stream | ETL, compilers, media and document processing | Error handling and ordering across steps need explicit design |

## Distribution styles (across deployables)

| Style | Shape | Adopt when | Costs and cautions |
|-------|-------|------------|--------------------|
| Monolith | One deployable, one database | One or a few teams; product still being discovered | Scaling is all-or-nothing; keep it modular |
| Service-based | A few coarse services, often one shared database | Some deployment independence without splitting data | Shared schema couples services; plan ownership |
| Microservices | Many independently deployable services around business capabilities, each owning its data | Several teams need independent release cadence and the organisation can run distributed tracing, versioned contracts and eventual consistency | Network failure modes, data consistency, operational load; a distributed monolith (services that must deploy together) is the common failure |
| Event-driven | Components publish facts; others react (see `messaging.md`) | Loose coupling and independent scaling matter more than one traceable flow | Flow is harder to see; needs correlation ids, idempotent consumers, dead-letter handling |
| Space-based | Replicated in-memory data grid processing units, asynchronous persistence | Extreme and spiky concurrency (ticketing, auctions) | Complex and costly; rarely the right first choice |
| Serverless | Functions triggered by events on a managed runtime, plus managed services | Spiky or low-volume workloads, glue and integration code, scheduled jobs, event processing | Cold starts, execution limits, vendor coupling, distributed debugging; see the section below |
| Backends for frontends | One backend per client type, owned with that client | Web, mobile and partner clients need different shapes or release cycles | Duplication between BFFs; shared logic stays in downstream services |
| Cell-based / deployment stamps | Independent copies of the whole stack, each serving a subset of tenants or regions | Blast-radius limits, data residency, very large tenant counts | Routing layer and fleet operations; cross-cell queries become hard |

Default: a modular monolith. Split a module into a service when its boundary has proved stable
and a concrete force demands it (independent scaling, release cadence, isolation, compliance),
not while the boundary is still being discovered. Decomposition by business capability or
subdomain is the starting point for any split; decomposition by technical layer is not.

## Serverless practice
Sources: AWS Well-Architected Serverless Lens and Lambda best practices; Azure Functions best
practices. The rules apply to any functions platform.

**Design**
- Keep functions short-lived and single-purpose; think in concurrent requests, not total
  requests.
- Share nothing in memory between invocations that matters for correctness: the execution
  environment may be reused or discarded at any time. Durable state goes to a store; workflow
  state goes to a state machine or durable orchestration.
- Orchestrate multi-step workflows with a state machine or durable functions (Step Functions,
  Durable Functions, Workflows), not by functions calling functions in code. Use choreography
  (events) between independent services and orchestration inside one business process.
- Avoid long-running functions; split work or move it to a workflow or a container service.
- Never let a function invoke itself, directly or through a trigger it writes to, without a
  guard; runaway recursion multiplies cost.

**Correctness**
- Delivery is at least once: every handler is idempotent. Validate and deduplicate at the start
  of the handler, keyed by an event or business id.
- Use partial batch responses for stream and queue sources so only failed records retry.
- Keep the function timeout below the queue's visibility timeout, or a message still being
  processed becomes visible again and is delivered twice.
- Bound retries, use backoff with jitter, and route poison messages to a dead-letter queue.
- Every dead-letter queue has a named owner, an alarm on its depth and a redrive procedure; a
  review flags any of the three that is missing.

**Performance and cost**
- Create SDK clients and connections outside the handler so warm invocations reuse them; never
  store user data or request data in that reused scope.
- Right-size memory by measurement (memory also sets CPU on Lambda); load test to set timeouts.
- Respect downstream limits: reserved concurrency or queue-based load levelling in front of
  databases and APIs that cannot scale with the function.
- Treat cold start as a measured problem: provisioned or always-ready instances, smaller
  packages, lazy loading.

**Security and operations**
- One least-privilege role per function; no wildcard actions or resources.
- Secrets from a secret manager, not plain environment variables or code.
- Structured JSON logs, metrics emitted through logs (embedded metric format or equivalent),
  distributed tracing, alarms on errors, throttles, duration and queue age.
- Infrastructure as code (SAM, CDK, Serverless Framework, Bicep, Terraform); delete unused
  functions.

**Serverless anti-patterns**: function chains calling each other synchronously; a monolithic
function routing every endpoint (sometimes acceptable as a deliberate "lambda-lith", but decide
it); shared mutable global state used as a cache of user data; unbounded concurrency against a
relational database; retries without idempotency.
