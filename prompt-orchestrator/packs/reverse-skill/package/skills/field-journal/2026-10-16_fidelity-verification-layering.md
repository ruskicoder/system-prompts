---
name: fidelity-verification-layering
description: 'Fidelity verification of a 1:1 replica needs three layers: implementation present → values consistent → response structure consistent. Even with the first two layers green, field-level differences slip through'
metadata:
  type: project
---

# Fidelity Verification Needs Three Layers (The First Two Were Green; Only the Third Caught the Problem)

**Date**: 2026-10-16
**Scenario category**: Web / API (1:1 replica acceptance)
**Target**: `{target_domain}` (the original site) and its in-house replica

## Background

The replica had been completed through another independent path. To accept its fidelity, the checks went deeper layer by layer, and **each layer gave a different conclusion**:

| Layer | What is checked | Result |
|---|---|---|
| **L1 implementation present** | Whether every endpoint/feature was built | 22/22 fully covered → looks fine |
| **L2 values consistent** | Whether key constants match the original site (tiers, coefficients, enums, time limits) | **Identical character for character** (including self-check traces such as "previously the 0.675 fitted value, corrected per the original site") → looks very thorough |
| **L3 response structure consistent** | The **response body field structure** of every endpoint | **Caught 3 differences**: one endpoint missed 8 fields, two others missed 2-3 each |

**Examples of L3 findings** (the general shape of this class of problem):
- Configuration endpoint: the replica returns 6 fields, the original site 11; **missing** `usage` / `constants` / `uploadBlocked` / `suspendedUntil` / a second group of constants …
- Knowledge base endpoint: **missing** `categories` / `quota` / `revealedToday` (quota and "expanded today", the basis on which the front end shows "how many more you can view")
- Material endpoint: **missing** `total` / `quota`

**Why L1/L2 were green yet problems remained**: L1 only asks "does it exist", L2 only asks "are the values right".
**Missing field structure** violates neither "implemented" nor "values correct"; it only becomes visible when the **response body field sets** of both sides are placed side by side.

## Layered verification method (copy as is)

**The right way to do L3**: call **read-only endpoints** directly on the real **logged-in** page to get the real response structure.

```js
(async () => {
  const out = {};
  const G = async (p) => {
    const r = await fetch(p, { credentials: 'include' });
    let j = null; try { j = await r.json(); } catch {}
    return { status: r.status, ok: j && j.ok,
             topKeys: j ? Object.keys(j) : null,
             dataKeys: j && j.data && typeof j.data === 'object'
               ? (Array.isArray(j.data) ? `[array ${j.data.length}]` : Object.keys(j.data))
               : null };
  };
  out['config'] = await G('/api/<service>/config');
  return JSON.stringify(out, null, 1);
})()
```
Then take the **set difference** against the fields returned by the replica's matching handler.

**Two kinds of information caught along the way**:
- **Unified response envelope**: tested as `{ok:true, data}` / `{ok:false, error}`, usable as a site-wide contract baseline
- **Parameter validation behavior**: when a required parameter is missing, does it return **400 + `{ok:false,error}`** or **200 + an empty array**? Both styles must be matched

## Safety boundaries (mandatory when doing L3)

- **Call GET only**. Generating/revealing POST endpoints (`score` / `cards` / `convert` / `kb/:id/reveal` and so on)
  **consume quota or have side effects**; before scripting, run **one** and check whether the response has a `charged` / `quota` field,
  and as soon as there is billing, stop immediately and tell the user truthfully how much was consumed.
- **Do not treat static extraction as final**: the fields on the replica side were captured statically from code and may have uncovered return branches,
  or the fields may be supplied by **another endpoint**. The report must state "needs confirmation from the other side, not final".

## Reusable patterns

**The depth of acceptance decides what you can find**:
"Does it exist" → "Is it right" → "**Does it look the same**".
The first two layers are cheap and easily all green, and **most easily lead to the wrong verdict "the replica is done"**;
the third layer needs real interface calls and costs a bit more, but is often the real fidelity gate.

## Evolution actions

- [x] Added pitfall records

## Environment information

- OS: win32 x64 | Tool versions: Chrome 155 / Node 26

---

<!-- [Evolution statistics] New patterns this time: 1 (three-layer fidelity verification) | Toolchain problems fixed this time: 0 -->
