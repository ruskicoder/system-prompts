# Contract-Faithful Local Reconstruction of a Next.js CDK Order Center

> Date: 2026-08-01
>
> Scenario: web / API / JS reverse engineering and local reconstruction
>
> Redaction: target domains and ports use standard placeholders; credentials, CDKs, order identifiers and private paths keep only their categories, without original values

## Scenario classification

Web / API / JS reverse engineering

## Target overview

Built a four-source evidence chain for a Next.js single-page order center ("entry snapshot, static bundles, runtime pages, public OpenAPI") and, without connecting to the real payment, worker and check services, rebuilt a runnable local project with the same information architecture, the same browser request shapes, the same response projections and the same order state semantics.

## Scope summary (redacted)

- auth_basis: the user provided the entry and asked for analysis and an equivalent local implementation
- network_profile: read-only rechecks of the public entry and the public OpenAPI; builds and acceptance all point to the loopback address
- asset_types: [web, frontend_js, public_openapi, screenshot, local_source]
- fixture_profile: synthetic CDKs, synthetic credentials, synthetic payment links, deterministic worker/check/payment adapters

## Roles

- lead_role: lead
- specialists: [cre, doc]

## Complete execution chain

1. Pinned the entry HTML, response headers, public OpenAPI and SHA-256, reusing the existing static packages and browser evidence.
2. Extracted routes, request body fields, headers, Storage keys, polling intervals, conditional rendering and the state vocabulary from the main page bundle.
3. Modeled the page's internal legacy API and the public v1 API separately with their own serializers, avoiding field drift from a shared DTO.
4. Computed desktop geometry, mobile breakpoints, card hierarchy, control states and copy baselines from runtime full-page screenshots, the DOM and CSS.
5. Built a canonical domain model, a CDK ledger and a deterministic state machine; external capabilities are taken over by the `CHECK_FN`, `PAYMENT_PROVIDER` and `WORKER_GATEWAY` fixture adapters.
6. Reduced credentials and payment links at request time to digests, types and safety hints immediately; the persistence model has no slot for the original values.
7. Ran contract tests for single, batch, detail, cancel, resubmit, pagination, dual authentication and the OpenAPI documentation.
8. Verified the visuals with desktop and mobile browser screenshots; formed the delivery evidence from the production build, interface smoke tests, secret scanning and re-verification after unpacking.

## Evidence chain summary (redacted)

| E-id | source_type | Reusable command pattern | Related conclusion |
|------|-------------|----------------|----------|
| E-001 | network/file | `curl -D headers -o page https://{target_domain}/<entry>; shasum -a 256 page` | Framework entry and timestamp baseline |
| E-002 | frontend_js/openapi | `rg 'sessionStorage|/api/|productType|customerToken' {formatted_chunk}`; `jq '{info,paths,securitySchemes}' openapi.json` | Legacy requests, states, browser storage and the v1 contract |
| E-003 | runtime_visual/local_qa | `chromium --headless ...; screenshot + DOMRect`; `npm test && npm run build && BASE_URL=... npm run smoke` | Desktop/mobile geometry, conditional rendering and the local contract loop |

## Finding / Path summary

- top_finding: the page's internal legacy API and the public v1 API share business semantics but differ in request fields, authentication entries and response projections, so the reconstruction needs "one domain model, two boundary serializers".
- path_type: callflow
- path_one_liner: form input -> page field mapping -> legacy Route Handler -> canonical service -> fixture adapters/ledger -> legacy serializer -> polling render.

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| Building interfaces only from route names still left page fields blank | The legacy and v1 response fields are not the same DTO | Derived the serializers from the property read points in the bundle and ran contract tests on both boundaries separately | ~45 min |
| The initial page form and the bound form were mixed together | Several cards, hints, buttons and lists render conditionally | Pinned the unbound baseline first, then built an interaction matrix by CDK/order state | ~30 min |
| The batch interface must express both partial success and ledger consistency | Promoting a single item error to a batch-wide exception loses the original page's per-item result semantics | Parse item by item, produce created/duplicate/failed in order within one store mutation, validate the ledger at the end and persist atomically | ~35 min |
| Ambiguity between documented required fields and property names | The OpenAPI and the page's internal call surface evolve independently | Kept the specified fields while recognizing compatible aliases at the boundary; the report lists the basis of the ruling separately | ~15 min |
| Visuals looked close but vertical error kept accumulating | Small deviations in card padding, line-height and gap add up | Constrained by full page height, main column width and key DOMRects, with section-by-section screenshot regression | ~40 min |
| Fixture hint text broke the identical first screen | Implementation notes were mixed directly into the product UI | Kept the UI at the evidence baseline, put fixture notes in the README; inputs still use deterministic examples | ~15 min |

## Toolchain findings

- The property read points in static bundles are better than the interface paths themselves for recovering response DTOs.
- Layering legacy/v1 serializers keeps page compatibility and public API stability at the same time.
- `fullPage` screenshots must be combined with viewport width, total page height and DOMRects; plain pixel similarity is amplified by font anti-aliasing.
- Batch orders should keep per-item created/duplicate/failed results; deduplication, capacity deduction and ledger validation belong in the same mutation, with a single atomic file replacement at the end.
- Secret scanning should cover source code, the runtime store, test logs and the unpacked directory of the final archive, not only the Git working tree.

## Key code/commands

```bash
# Static call surface and state fields
rg -n 'customerToken|productType|upiExpiresAt|customerResubmitCount|sessionStorage' {formatted_chunk}

# Public API structure
jq '{openapi,info,paths:(.paths|keys),security:.components.securitySchemes}' openapi.json

# Local quality gate
npm run lint
npm test
npx tsc --noEmit
npm run build
BASE_URL=http://127.0.0.1:{port} npm run smoke
```

## Improvement suggestions for this package

1. Add a "dual serializers for the legacy UI API and the public API" checklist to `js-reverse`.
2. Add a "visual baseline geometry table" and an "initial/bound/order state matrix" to the report template.
3. Add batch partial success with atomic persistence, dual authentication OR, OpenAPI schema/actual response consistency and scanning of the unpacked delivery package to the QA template.

## Reusable patterns/script snippets

1. **Four-source cross-check**: the entry snapshot locates the version, static bundles recover the call surface, the runtime recovers conditional rendering, the OpenAPI recovers the public contract.
2. **One core, two projections**: the canonical domain keeps state and ledger unified, and the legacy/public serializers keep the boundaries faithful.
3. **Initial state first, then the state matrix**: lock down the unbound first screen, then verify bound, created, in progress, completed, cancelled and resubmitted.
4. **Reduction at request time**: raw input is converted to SHA-256, type and mask as soon as it enters the service; logs and the store receive only the reduced results.
5. **Second verification of the delivery package**: unpack the archive into a new directory, reinstall, test and build, so leftovers in the working directory cannot hide problems.

## Evolution actions

- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation
- [x] Added pitfall records
- [ ] No update needed

## Environment information

- OS: macOS
- Tool versions: Node.js 24, Next.js 16.2.12 App Router, React, TypeScript 5.9.3, Chrome/Playwright
- Target platform/version: Next.js App Router / React / OpenAPI 3.1

## Final acceptance record

- ESLint, TypeScript 5.9.3, Next.js 16.2.12 production build: passed.
- Node test: 8/8 passed.
- HTTP smoke: 15 contract groups passed.
- Playwright: 11 state/viewport screenshots, 10 assertion groups passed; the browser console and page errors are both empty.
- The 1440 px initial page and the baseline are both 1440×1294; RGB MAE 2.301148, share of pixels within the 5-per-channel threshold 0.945085.

## Redaction recheck

- [x] Target domain replaced with `{target_domain}`
- [x] Original CDKs, order numbers, tokens, cookies, JWTs and payment links not written
- [x] Real IPs, ports and local private paths not written
- [x] Run commands use `{port}` and placeholders
- [x] Delivery experience keeps only methods, structures and verification patterns

---
<!-- [Community contribution] When done, ask the user whether to open a PR to the main repository. -->
