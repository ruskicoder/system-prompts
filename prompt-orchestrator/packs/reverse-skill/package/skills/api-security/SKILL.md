---
name: api-security
description: Use for authorized security assessment of REST, GraphQL, WebSocket, or SOAP APIs, including discovery, authentication, authorization, rate-limit, and CI/CD testing.
---
# API Security Testing

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md` to confirm that this skill's operations are authorized routine operations
2. `NOW`: confirm whether the current task falls within the scope of this skill
3. `NEXT`: read `../tool-index.md` and verify tool availability and actual paths
4. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
5. `ACT`: enter step one of the "Workflow" and execute it; do not stop at confirmation

> Covers every protocol: REST / GraphQL / WebSocket / SOAP
> 10-phase methodology, from discovery to CI/CD integration

## When to use

- REST API security testing (OpenAPI/Swagger driven or blind)
- GraphQL security audit (introspection, batch queries, alias overloading)
- WebSocket security testing
- JWT / OAuth 2.0 authentication testing
- BOLA/IDOR/BFLA authorization vulnerability detection
- API rate limit bypass and DoS testing

## 10-phase test process

### Phase 1: API discovery and reconnaissance

```text
Active discovery:
□ Vespasian: headless browser crawl → automatically generates OpenAPI 3.0 / GraphQL SDL specs
□ Entropy --discover: extract endpoints from robots.txt + JS files
□ Kiterunner / ffuf: brute-force undocumented endpoint paths
□ Check common paths: /swagger.json, /openapi.json, /graphql, /api-docs

GraphQL introspection (three attempts):
  1. Standard introspection query
  2. Reduced query (bypasses a WAF that blocks the full query)
  3. Query only __schema { types { name } } (minimal probe)
```

### Phase 2: Authentication testing

```text
JWT analysis (jwt_tool / Burp):
□ alg:none attack: change the header to "alg":"none" and empty the signature
□ Key confusion: RS256 public key → HS256 symmetric key
□ Weak HMAC key brute force: jwt_tool -C -d wordlist.txt
□ Expiry/claim tampering: modify the exp/iat/sub/role claims
□ kid injection: ../../etc/passwd → HMAC signature bypass

OAuth 2.0:
□ redirect_uri manipulation → authorization code leak
□ CSRF via a missing state parameter
□ Token leaks in the Referer header
□ Missing PKCE detection

GraphQL authentication:
□ mutation through a GET request bypasses authentication (CSRF)
□ Batch query authentication bypass
```

### Phase 3: Authorization testing (BOLA/IDOR/BFLA)

```text
BOLA (object-level authorization bypass):
□ Iterate numeric IDs: /user/1 → /user/2 → /user/3
□ Iterate UUIDs
□ Iterate usernames/emails
□ Burp Autorize: two-session replay comparison

BFLA (function-level authorization bypass):
□ Regular user calls administrator APIs
□ HTTP method switching: GET → PUT → PATCH → DELETE
□ API version downgrade: /v2/admin → /v1/admin
□ Bulk operation injection: {"users": [1,2,3]} → {"users": [1,2,3,admin_id]}

Tools: Burp Autorize, AuthMatrix, Entropy (malicious_insider persona)
```

### Phase 4: GraphQL specifics

```text
Introspection leak → information exposure detection
Alias overloading → 100+ alias DoS
Batch queries → 10+ simultaneous query DoS
Field duplication → __typename × 500
Directive overloading → recursive @skip/@include
Circular queries → deeply nested introspection recursion
Field suggestions → information leak through error messages
GraphiQL/Playground exposure → public IDE risk
GET mutations → CSRF risk
Tracing/debug mode → metadata leak

Tools: FireTail, Escape DAST, api.sh (Phases 1-3)
```

### Phase 5: REST input validation

```text
□ HTTP method switching: GET→POST→PUT→DELETE→OPTIONS→PATCH
□ Content-Type tampering: JSON→XML→multipart
□ NoSQL injection: {"username": {"$gt": ""}}
□ SSRF via URL parameters: webhook URL/avatar URL/import URL
□ XXE in XML endpoints
□ Parameter pollution: /api?role=user&role=admin
□ Mass assignment: add is_admin: true to the request body
```

### Phase 6: Business logic and differential testing

```text
□ Entropy compare: diff v1 vs v2 API → status code changes/removed fields/latency regressions
□ Multi-role workflow testing: admin/user/readonly permission matrix
□ Coupon/points/price manipulation
□ Race conditions: concurrent requests to test TOCTOU
```

### Phase 7: WebSocket testing

```text
□ Endpoint discovery
□ Message injection (payload injection, prototype pollution)
□ Oversized message handling
□ Type confusion
□ Cross-site WebSocket hijacking (CSWH)
```

### Phase 8: Rate limiting and DoS

```text
□ Rate limit bypass via headers: X-Forwarded-For, X-Real-IP
□ Path variants: /api/ → /api → /Api/ → /API/
□ Slowloris low-bandwidth exhaustion
□ GraphQL batch query deep-nesting DoS
□ IP rotation testing (ProxyCat proxy pool)
```

### Phase 9: Data exposure

```text
□ Excessive response data: compare what the API returns with what the UI shows
□ Pagination enumeration: ?page=1&limit=10000
□ Information leak through error messages: stack traces/internal paths/SQL errors
□ GraphQL nested traversal to reach unauthorized data
□ OpenAPI spec exposes sensitive endpoints
```

### Phase 10: CI/CD integration

```text
□ Entropy --ci --watch: rerun automatically when the spec changes
□ Escape DAST: block builds automatically by severity threshold
□ Persist findings as regression tests
□ StackHawk (developer first, ZAP core)
```

## Toolchain

| Tool | Purpose | Source |
|------|------|------|
| Vespasian | Traffic → OpenAPI/GraphQL spec | GitHub: praetorian-inc/vespasian |
| Entropy | LLM-generated attack scenarios, 5 personas | GitHub: arjinexe/entropy-chaos |
| Escape DAST | Business logic security testing | escape.tech |
| api.sh | 8-phase all-protocol attack pipeline | GitHub: Sharon-Needles/api |
| FireTail | 12 GraphQL-specific tests | firetail.ai |
| jwt_tool | Comprehensive JWT testing | GitHub: ticarpi/jwt_tool |
| Burp Autorize | Two-session authorization comparison | Burp BApp Store |

## References

- `references/rest-graphql-testing.md`: REST + GraphQL in-depth testing
- `references/jwt-oauth-testing.md`: JWT + OAuth security testing


## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
