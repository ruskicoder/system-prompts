# Messaging and Integration Patterns

Load this when systems or services exchange messages or events. Names follow Hohpe and Woolf,
*Enterprise Integration Patterns* (pattern names and problem statements published under CC BY
at enterpriseintegrationpatterns.com), plus the messaging entries of the Azure catalogue.
Descriptions are our own. Modern brokers implement most of these: name the broker feature
before building one.

## First: should this be a message at all?

| Integration style | Use when |
|-------------------|----------|
| Remote call (REST, gRPC) | The caller needs an answer now, from one stable callee |
| Messaging | The caller can continue without the answer, work must survive outages, load must be buffered, or many parties react |
| Shared database | Avoid between separately owned services; acceptable inside one module |
| File transfer | Batch exchange with external parties |

A synchronous chain of three or more services on a write path is a warning sign: each hop
multiplies latency and failure.

## Message types

| Pattern | Meaning | Rule |
|---------|---------|------|
| Command message | "Do this" to one receiver | Imperative name (`ReserveStock`); one owner |
| Event message | "This happened" to any interested party | Past-tense name (`StockReserved`); immutable; the publisher does not know consumers |
| Document message | Data transfer without intent | Use for bulk or reference data |
| Request-reply | A request with a reply on another channel | Add a return address and a correlation identifier; set an expiry |
| Correlation identifier | Links replies, retries and related messages | Propagate with trace context |
| Message sequence | A large payload split into parts | Number the parts; reassemble with an aggregator |
| Message expiration | Data useless after a deadline | Set a time to live; drop or dead-letter expired messages |
| Format indicator | Consumers must know the schema version | Version field or schema id in a header |

Event design: thin events (id plus type) force consumers to call back; fat events carry state
and couple consumers to the schema. Choose per event, version every schema, and check
compatibility in CI before publishing a change.

## Channels

| Pattern | Use |
|---------|-----|
| Point-to-point channel | One consumer processes each message (work queue) |
| Publish-subscribe channel | Every subscriber gets its own copy (topic plus subscriptions or consumer groups) |
| Datatype channel | One message type per channel, so consumers know what arrives |
| Invalid message channel | Messages that cannot be parsed or validated go here instead of blocking |
| Dead letter channel | Messages that repeatedly fail processing go here, with an owner, alert, retention and redrive procedure |
| Guaranteed delivery | Persist messages so they survive broker and consumer restarts |
| Channel adapter / messaging bridge | Connect an application or another messaging system to the channel |
| Message bus | Shared infrastructure, common data model and command set for many applications |

## Routing

| Pattern | Use |
|---------|-----|
| Content-based router | Route by message content to one destination |
| Message filter | Drop messages a consumer does not want |
| Dynamic router | Destinations configured at runtime |
| Recipient list | Send to a computed list of destinations |
| Splitter / aggregator | Break a message into parts and recombine results, with completion and timeout rules |
| Resequencer | Restore order for messages that arrive out of order |
| Scatter-gather | Broadcast a request and aggregate the replies |
| Routing slip | The route travels with the message |
| Process manager | A stateful coordinator drives a multi-step process (orchestration; durable workflow engines implement it) |
| Message broker | Central routing hub decoupling senders from receivers |

Keep business rules out of routers and translators; they belong in services.

## Transformation

| Pattern | Use |
|---------|-----|
| Message translator | Convert between formats at the boundary |
| Envelope wrapper | Add or remove transport headers around a payload |
| Content enricher / content filter | Add missing data, or strip what the receiver must not see |
| Claim check | Store a large payload elsewhere and send a reference |
| Normalizer | Convert many formats of the same meaning into one |
| Canonical data model | One shared format between many systems; costly to evolve, use sparingly |

## Endpoints and consumers

| Pattern | Use |
|---------|-----|
| Messaging gateway / mapper | Hide messaging APIs behind domain-shaped interfaces |
| Transactional client | Receive, process and acknowledge in one unit, or use an outbox for sends |
| Polling consumer / event-driven consumer | Pull at your own rate, or receive pushes |
| Competing consumers | Several instances share one queue to scale processing |
| Selective consumer | Consume only messages matching criteria |
| Durable subscriber | Keep messages for a subscriber while it is offline |
| Idempotent receiver (idempotent consumer) | Processing a message twice has the same effect as once; dedupe by message or business id with a unique constraint or conditional write |
| Service activator | Connect a message to a service call |
| Priority queue | Process urgent messages first, with separate queues or priorities |
| Sequential convoy | Process related messages in order per group (session, partition key) without blocking other groups |

System management: control bus, wire tap, message history, message store, smart proxy, test
message and channel purger support operations and debugging.

## Reliability checklist (answer before writing integration code)
1. **Delivery guarantee**: at most once, at least once, or effectively once. Default to at least
   once plus idempotent receivers.
2. **Idempotency**: which key, stored where, for how long.
3. **Bad messages**: invalid-message and dead-letter paths, each with an owner, alert, retention
   and redrive procedure.
4. **Retries**: bounded attempts, backoff with jitter, transient versus permanent
   classification, downstream timeouts.
5. **Ordering**: total, per key, or none. Prefer per-key ordering through partition keys or
   message groups.
6. **Schema evolution**: a schema format and a compatibility check in CI.
7. **Observability**: trace context propagated; lag, age, throughput, failures, retries and
   dead-letter depth measured.
8. **Failure boundary**: what rolls back, what compensates, what can be replayed.

## Messaging anti-patterns
- Dual write: saving to the database and publishing to the broker as two steps. Use an outbox
  (or a transactional producer when the broker is the only store).
- Acknowledging before processing and committing state.
- Non-idempotent consumers under at-least-once delivery.
- Unbounded retries, no jitter, or retrying validation errors.
- A dead-letter queue nobody watches.
- One topic carrying many unrelated event types.
- Distributed two-phase commit across services.
- Using "eventual consistency" as a reason to skip timeouts, compensations or a process manager.
- Large payloads on the bus instead of a claim check.
- Unbounded queues, buffers, prefetch counts or consumer concurrency.
