# Passive Reconnaissance of a Public Exchange + Live Table Game Site and a Play-Money Rebuild with "Full Real-Time Control from the Back Office"

> Date: 2026-10-30
>
> Scenario: Web / JS reverse engineering (R3 js-reverse) + real-time protocol analysis + local rebuild (multi-agent swarm)
>
> Redaction: target domains, brands, accounts, tokens and encryption keys appear only as placeholders or category descriptions; no raw captures are included.

## Scenario classification

JS signing/encryption envelope + traffic capture analysis + local rebuild

## Target overview

Public passive observation only: extracted the information architecture, API shapes and real-time cadence of a sports exchange (match odds / bookmaker / fancy) plus live card table (dt20 / teen20 / lucky7 and so on) site,
then rebuilt it with an own brand and virtual chips (no real money involved): a Next.js player front end + a Next.js admin console + a Spring Boot Modulith back end.
Requirement: the back office can control all front-end content and the back-end betting logic in real time.

## Scope summary (redacted)

- auth_basis: public_passive_observation (no authorization from the site; active testing excluded)
- network_profile: read-only browsing of public pages + public demo login; recorded through CDP with a separate Chrome profile
- asset_types: [web, frontend_js, encrypted_api_envelope, websocket_score_feed, screenshot]

## Roles

- lead_role: lead (coordinator)
- specialists: [cie (bundle/realtime analysis), cre (product/odds math), ui-analyst, several implementation workers]

## Complete execution chain

1. master-route chose R3; case-init recorded `public_passive_observation` and out_of_scope (no scanning, no brute force, no payments); capture started only after case-guard passed.
2. Recording with a separate Chrome profile + CDP (port isolation): first the logged-out home page to pass CF, then 22 static routes, the sports list, 5 events and 11 card tables; single long tasks used detached scripts to avoid the 10-minute tool timeout.
3. Every interface response is an AES envelope; the key is hidden in obfuscated preamble code. Wrote an offline decoder (sending no extra requests to the live site) to batch-decode the recorded traffic.
4. Derived the real-time cadence statistically from the decoded samples: odds polled about every 500 ms, card tables about every 700 ms, scores over a separate socket (revision/baseRevision increments). Designed STOMP push + per-topic seq + a Redis replay buffer + REST snapshot fallback on that basis.
5. Evidence E-001..E-009 got SHA-256 + review_case `--verify-hashes --strict` passed (Gate G1); anonymized copies landed in the project Docs.
6. Specifications first: backend-contract (module table + migration number ranges + build isolation), realtime (envelope/replay/authentication), casino (provably fair algorithm + cross-language test vectors), domain-model, PRD, then handed out to workers.
7. Several workers implemented in parallel (identity/wallet/cms/realtime/admin/sportsbook/casino + two front ends); the coordinator independently re-verified each one (isolated build directory, Testcontainers, real HTTP + real JWT) and committed module by module.
8. Phase 7: fan-out load test with 2,000 STOMP subscribers; security self-review S-01..S-08b all fixed with regression tests; Playwright e2e covers "back office action -> takes effect on the front end without refresh"; measurable visual consistency checks per the must-match rules from recon.

## Evidence chain summary (redacted)

| E-id | severity | status | source_type | Reusable command pattern | Related Finding |
|------|----------|--------|-------------|----------------|--------------|
| E-003 | n/a | observed | network | `node recorder.mjs --cdp 9333 --out runs/r03 --routes routes.txt` (passive CDP recording) | F-001 |
| E-006 | n/a | validated | file | `node decode.mjs runs/r03/*.json --key-from preamble.js > decoded.ndjson` (offline envelope decoding) | F-002 |
| E-008 | n/a | observed | runtime_visual | `node crawl.mjs --tables tables.txt --shots 1440,390` (UI baseline + token sampling) | F-004 |

## Finding / Path summary

- top_finding: the site's "real time" is actually high-frequency polling plus an AES envelope; the rebuild switches to push (STOMP + seq + replay), cutting latency from polling-period level to sub-second, with direct control from the back office.
- path_type: callflow
- path_one_liner: back office action -> module service (audit written in the same transaction) -> after-commit publish -> Redis seq/buffer/fan-out -> STOMP -> front end merges by seq, gaps go through REST replay or snapshot.

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| Workers went long without writing to disk and lost context after session interruptions | Large tasks were conceived in one go; sessions got paused or interrupted | Required "write to disk by slice" (migration -> domain -> controller -> tests); after an interruption, start a new worker and state clearly "finish and verify on the existing files, do not rewrite" | ~1 h cumulative |
| `adm` in the JWT (= may enter the back office) was treated as "platform administrator", letting the agent layer read platform-wide data without authorization | One boolean carried two layers of semantics, "audience" and "data scope" | Split into `console()` (audience) and `globalScope()/canReach()/scopePath()` (scope); wrote an HTTP regression test that "old code must fail" before fixing | ~40 min |
| Front-end and back-end field names differ (marketId/selectionId/limits/delaySec vs id/minStake/betDelaySec) | The UI guessed fields from the specification first, the back end named them after its own domain | Put a single wire normalizer in the shared SDK that both front ends go through; unit tests use real back-end samples | ~25 min |
| Parallel builds overwrote each other's target/ | Several workers ran mvn at the same time | Give each worker a separate build directory through an environment variable (such as `{build_dir_env}=target-<name>`) | ~15 min |
| Player login/accepting the rules incremented the optimistic lock version by 1, causing occasional 409s on an immediately following back office lock | Entity saves were used for "bookkeeping" updates | Bookkeeping fields switched to native targeted UPDATEs that leave version alone; added a regression test | ~15 min |
| Next keeps the hidden DOM of the previous route, so e2e selectors hit two elements | Client-side route cache | Restrict assertions to `:visible`; use different test ids for repeated desktop/mobile components | ~10 min |

## Toolchain findings

- CDP attached directly to a separate logged-in profile passes CF more easily than a new headless instance and does not pollute the everyday browser.
- Node 22 ships WebSocket: a dependency-free STOMP 1.2 framer is enough for a 2,000-connection load test, p99 182 ms, 0 lost.
- Spring Modulith ModularityTests effectively block direct cross-module access; the shared kernel holds port interfaces (FeatureFlags, ApprovalGateway, RealtimePublisher).
- Provably fair: HMAC-SHA256 byte stream + rejection sampling (no modulo bias) + reverse Fisher-Yates. Java and browser-side TS are aligned card by card with the same test vectors, and e2e recomputes the hash and the deal in the browser.

## Key code/commands

```
# evidence integrity
python skills/case-review/scripts/review_case.py {case_root} --verify-hashes --strict
# isolated build + selected tests
{build_dir_env}=target-<name> ./mvnw -q -Dtest='ModularityTests,<Module>IntegrationTest' test
# full gate (including e2e)
scripts/verify.sh --e2e
# fan-out load test
node tools/load/ws-load.mjs --url ws://{remote_host}:{port}/ws --topic /topic/site-config --clients 2000 --trigger ./publish.sh
```

## Improvement suggestions for this package

- The R3 route could add an "encrypted API envelope" sub-branch: locate the key in the preamble code first and decode offline, avoiding extra requests to the target.
- The case-init template could add out_of_scope defaults for "rebuild tasks" (do not copy brand/assets/copy, do not connect real money payments).
- For multi-agent scenarios, add a hard step to the role-map: "the coordinator must independently re-verify worker output" (isolated build directory + real HTTP tests).

## Reusable patterns/script snippets

- Separate "audience vs scope": `console()` decides only whether one may enter the back office; data queries always go through `globalScope()/canReach()/scopePath()`.
- Real-time push trio: a monotonic seq per topic + a bounded Redis buffer (200 entries / 10 min) + gap replay or `{reset:true}` to trigger a REST snapshot.
- After-commit publishing: rolled-back changes are never broadcast; audit writes use `Propagation.MANDATORY` in the same transaction as the business logic.

## Evolution actions

- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation
- [x] Added a pitfalls record (this entry)
- [ ] No update needed

## Environment information

- OS: macOS (colima 4 CPU / 6 GB)
- Tool versions: Node 22, JDK 21, Spring Boot 4.1, Next.js 16, Postgres 17, Redis 7, Playwright (system Chrome)
- Target platform/version: public Web (Angular front end + encrypted JSON API + score socket), captured on 2026-10-29

---
<!-- [Evolution statistics] New patterns this time: 3 | Toolchain problems fixed this time: 0 -->
<!-- [Community contribution] The user agreed; PR submitted per CONTRIBUTE-BACK.md -->
