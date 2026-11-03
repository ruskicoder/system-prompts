# API Design Patterns

Load this when designing or reviewing an interface that other programs call over a network:
HTTP/JSON, gRPC, GraphQL or webhooks. Sources: Google API Improvement Proposals (AIP, CC BY
4.0), RFC 9457 (problem details), the Azure asynchronous request-reply pattern. Library and
in-process interfaces follow the clean-code skill and the language file instead.

An API is a published surface: every name, field and status code becomes a contract that is
expensive to change. Apply the YAGNI gate to new fields and endpoints, and the compatibility
rules below to every change.

## Choosing a style

| Style | Fits | Cautions |
|-------|------|----------|
| Resource-oriented HTTP (REST style) | Public and partner APIs, CRUD-shaped domains, cacheable reads | Model resources and standard methods first; custom actions only when a standard method does not fit |
| gRPC / RPC | Internal service-to-service calls, streaming, strict schemas | Browser clients need a proxy; versioning by package |
| GraphQL | Many client types needing different shapes of a rich graph | Query cost limits, N+1 resolvers, caching and authorization per field |
| Webhooks | Notifying external parties of events | Sign payloads, retry with backoff, let receivers deduplicate, document ordering (usually none) |
| Asynchronous messaging | Internal events between services | See `messaging.md` |

## Resource-oriented design
- Name resources as nouns in a hierarchy (`/publishers/{id}/books/{id}`); collections plural.
- Standard methods: Get, List, Create, Update (partial, with a field mask or merge semantics),
  Delete. Custom methods (`:cancel`, `:archive`) for operations that do not map to them.
- Use HTTP semantics as defined: safe `GET`, idempotent `PUT` and `DELETE`, `POST` for create
  and custom actions, correct status codes (`201` with the new resource, `204`, `404`, `409`,
  `412`, `422` or `400`, `429`).
- Resource ids are opaque strings to clients; do not expose database sequence ids as meaning.

## Errors
- One error shape everywhere. On HTTP, use problem details (RFC 9457, media type
  `application/problem+json`) with `type`, `title`, `status`, `detail`, `instance` plus
  extension members such as a machine-readable error code and field violations.
- Messages are for developers; codes are for programs. Never leak stack traces, SQL or internal
  hostnames.

## Pagination
- Every List method paginates from the first release; adding it later breaks clients.
- Cursor (token) pagination: request `page_size` and `page_token`; response `next_page_token`,
  empty only at the end of the collection. Tokens are opaque, not merely base64 of an offset,
  and grant no authorization. Cap `page_size` at a documented maximum instead of erroring.
- Offset pagination only for small, stable collections where users jump to page numbers.

## Filtering, ordering and partial responses
- One documented filter syntax; validate it and reject unknown fields.
- Document a default ordering; ordering keys must be stable for pagination.
- Field masks or sparse fieldsets for large resources.

## Idempotency and concurrency
- Let clients send a request id or idempotency key on create and other non-idempotent calls;
  store the key with the result and replay the result for repeats within a window.
- Optimistic concurrency with `ETag` and `If-Match` (or a version field); return `412` on a
  stale write.

## Long-running operations
- Return `202 Accepted` with a status resource or operation id; the client polls it (or gets a
  callback) until done, then reads the result. Include progress and a cancel method when
  meaningful. This is the asynchronous request-reply pattern.

## Versioning and compatibility
- Additive changes are compatible: new optional fields, new endpoints, new enum values (if
  clients were told to tolerate unknown values).
- Breaking changes need a new major version: removing or renaming fields, changing types or
  meaning, tightening validation, changing defaults.
- Version in the path or package (`/v1/`, `myapi.v1`) for major versions; keep at least one
  previous major version running through a documented deprecation period.
- Clients and servers ignore unknown fields (tolerant reader).
- Contract tests (consumer-driven where consumers are known) and schema diff checks in CI.

## Security and operations
- Authenticate every call; authorize per resource, not only per endpoint.
- Validate input at the boundary against the schema; limit payload sizes.
- Rate limit per client with `429` and `Retry-After`; publish limits.
- Correlation id in and out; log method, resource, status and latency, never secrets or tokens.
- Publish the schema (OpenAPI, protobuf, GraphQL SDL, AsyncAPI) from the source of truth and
  keep examples in it tested.

## API anti-patterns
- Verbs in resource paths for standard operations (`/getUsers`).
- `200 OK` with an error in the body.
- Unbounded list endpoints.
- Chatty APIs that need many calls per screen (consider aggregation or a BFF).
- Leaking the database schema as the API.
- Breaking changes without a version.
- Booleans that will grow into states (`isActive` becoming active, suspended, deleted): use an
  enum from the start when more states are foreseeable.
