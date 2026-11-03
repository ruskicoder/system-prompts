# Distributed and Cloud Patterns

Load this when the force crosses a process or network boundary: failure between services,
data spread over stores, traffic routing, deployment, observability or trust boundaries.
Names follow the Azure Architecture Center catalogue and microservices.io; descriptions are our
own and apply to any cloud or on-premises platform. Messaging patterns are in `messaging.md`;
whole-system styles in `architecture-styles.md`.

Assume the network is unreliable, latency is not zero, and every remote call can fail, time out
or succeed twice. Each pattern below answers one of those facts and adds its own costs.

## Resilience

| Pattern | Force | Use | Cautions |
|---------|-------|-----|----------|
| Timeout | A slow dependency must not hold resources forever | Every remote call gets a deadline, propagated downstream | Set it from measured latency, below the caller's own deadline |
| Retry | Transient faults clear on their own | Retry idempotent operations with exponential backoff and jitter, bounded attempts | Never retry permanent errors; one retry budget per call chain, or retries multiply into a retry storm |
| Circuit breaker | A failing dependency keeps being called | Open after repeated failures, fail fast, probe with half-open | Pair with retry; expose state in metrics |
| Bulkhead | One overloaded dependency drains shared resources | Separate pools (threads, connections, instances) per dependency or tenant | Pool sizing needs load data |
| Rate limiting | A client would exceed a downstream quota | Control your own consumption to stay under limits | Coordinate across instances |
| Throttling | Callers overload your service | Reject or degrade excess requests with clear signals (`429`, `Retry-After`) | Per tenant where tenants differ |
| Queue-based load levelling | Spiky load would overwhelm a service | A queue absorbs bursts; consumers drain at a steady rate | Clients must accept asynchronous completion |
| Compensating transaction | A multi-step operation fails part way and steps cannot roll back | Undo completed steps with business-level compensations | Compensations can fail too: make them idempotent and retryable |
| Health endpoint monitoring | Orchestrators and load balancers need liveness and readiness | Separate liveness (process alive) from readiness (dependencies usable) | Health checks must be cheap and must not cascade failures |
| Leader election | One instance must coordinate | Elect a leader through a lease in a coordination service | Leases need fencing tokens so a stale leader cannot write |

## Data management

| Pattern | Force | Use | Cautions |
|---------|-------|-----|----------|
| Database per service | Services must change and scale independently | Each service owns its data; others go through its API or events | Cross-service queries need composition or read models |
| Shared database | Splitting data is not yet worth it | Several modules share one schema with clear table ownership | Schema changes couple deployments |
| Saga | A business transaction spans services | Sequence of local transactions with compensations, orchestrated or choreographed | Isolation is lost: design for intermediate states |
| Transactional outbox | A state change and its event must both happen or neither | Write the event to an outbox table in the same transaction; relay it to the broker (polling publisher or transaction log tailing) | Consumers still deduplicate |
| CQRS | Reads and writes have different shapes or loads | Separate read models from the write model | Read models lag; start inside one database before separate stores |
| Event sourcing | History of changes is a requirement, or state must be rebuilt | Store events as the source of truth; derive state by replay; snapshots for speed | Event schema versioning, replay cost and every reader changes; an audit table often suffices |
| Materialized view | Queries need a shape the store does not offer | Precompute views from one or more stores | Staleness; rebuild procedure |
| API composition | A query needs data from several services | A composer calls each and joins in memory | Latency and partial failure |
| Cache-aside | Repeated reads of slow data | Read through the cache, load on miss, invalidate on write | Stale data, stampedes on expiry; the cache is never the source of truth |
| Index table | Queries filter on fields the store does not index | Secondary index tables | Keep them consistent on write |
| Sharding | One store cannot hold the data or the load | Partition by a key with even distribution | Cross-shard queries and rebalancing; choose the key from access patterns |
| Expand and contract | Schema or contract must change without downtime | Add the new form, migrate readers and writers, remove the old form later | Two releases at least; track the removal |

## Routing and gateways

| Pattern | Use |
|---------|-----|
| Gateway routing | One endpoint routes to several services |
| Gateway aggregation | One request fans out to several services and returns one response |
| Gateway offloading | Shared concerns (TLS, auth, rate limits) handled at the gateway |
| Backends for frontends | One gateway or backend per client type |
| Ambassador | An out-of-process helper makes network calls for a service (retries, TLS, monitoring) |
| Sidecar | A helper process deployed beside each service instance (proxy, log shipper, config agent) |
| Service discovery | Clients or a router find instances through a registry; most platforms provide it |
| Strangler fig | Route capability by capability from a legacy system to the new one (refactoring skill, `legacy.md`) |
| Anti-corruption layer | Translate another system's model at your boundary |

## Deployment and operations

| Pattern | Use |
|---------|-----|
| Externalised configuration | Configuration outside the build artefact, per environment |
| Deployment stamps | Independent copies of the stack per tenant group or region |
| Geode | Each regional node can serve any client, with replicated data |
| Blue-green and canary | Switch or shift traffic to a new version with fast rollback |
| Feature flags | Separate deploy from release; every flag has an owner and a removal date |
| Static content hosting | Serve static assets from storage and a CDN, not from app servers |
| Compute resource consolidation | Pack related small workloads into one compute unit to cut cost |
| Scheduler agent supervisor | Coordinate a distributed workflow with a supervisor that detects and recovers failed steps |

## Observability

| Pattern | Use |
|---------|-----|
| Structured logging and log aggregation | JSON logs with request and correlation ids, collected centrally |
| Distributed tracing | Propagate trace context (W3C `traceparent`) across every hop |
| Application metrics | Rate, errors, duration per endpoint; saturation per resource; queue age and depth |
| Audit logging | Who did what to which record, kept apart from debug logs |
| Exception tracking | Errors grouped and alerted with context |
| Log deployments and changes | Correlate incidents with releases and config changes |

## Security patterns

| Pattern | Use |
|---------|-----|
| Federated identity | Delegate authentication to an identity provider (OIDC, SAML); do not store passwords yourself |
| Gatekeeper | A hardened front that validates and sanitises requests before they reach private services |
| Valet key | Give clients a short-lived, scoped token for direct access to one resource (pre-signed URL) |
| Access token | Pass identity between services as a signed token; validate it at every service |
| Least privilege | Each component gets only the permissions its job needs |
| Quarantine | Check external artefacts (packages, images, models) before the workload consumes them |

Audits of existing code go through the security-audit-codebase skill.

## Choosing and combining
- Start from the failure or constraint in front of you (a dependency that fails under load, a
  store that cannot keep up), never from the catalogue.
- Common pairings: retry with circuit breaker; queue-based load levelling with competing
  consumers; saga on compensating transactions; outbox with idempotent consumers; gateway
  routing, aggregation and offloading behind one endpoint.
- Every pattern here adds moving parts that must be operated. Inside one process and one
  database, most of them are unnecessary.
