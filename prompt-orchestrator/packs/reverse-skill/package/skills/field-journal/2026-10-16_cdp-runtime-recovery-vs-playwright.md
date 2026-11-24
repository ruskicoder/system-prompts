---
name: cdp-runtime-recovery-vs-playwright
description: Playwright scenarios cannot get the request initiator call stack; native CDP can. Includes 3 pitfalls such as setting breakpoints in minified scripts requiring a columnNumber
metadata:
  type: project
---

# Using CDP to Get the Runtime Evidence Playwright Cannot

**Date**: 2026-10-16
**Scenario category**: JS reverse engineering / traffic capture analysis
**Target**: `{target_domain}` (SPA, logged-in pages)

## Background

The existing capture capability is based on browser snapshots driven by Playwright scenarios. **Its own output states an honest boundary**:

> *Playwright scenario events **do not expose request initiator stacks**;
> receipt order does not prove causality.*

That is: **it cannot tell "which code in the page sent this request"**. And that is exactly the core need of the first phase of JS reverse engineering
(tracing the call origin).

## Core finding: switching to the native CDP domain is enough

The `Network.requestWillBeSent` event **carries** `initiator.stack.callFrames`,
including `functionName` / `url` / `lineNumber` / `columnNumber`. One test got a **14-level call stack**,
and the function names matched the source facade level by level (`<request wrapper> → <method alias> → <facade method> → … → <framework entry>`).

**This is not "a more advanced trick" but "the wrong observation channel was chosen"**: Playwright not exposing it ≠ the browser not providing it.

## Two other kinds of evidence only CDP can get

1. **Reading function arguments/return values at breakpoints**: set a breakpoint at the `fetch(` call in the request wrapper function,
   and when paused, read `scopeChain[0]` (local) to see the three arguments `method` / `path` / `opts` directly;
   this is the most direct answer to "how the parameters are generated".
2. **Source search and pinpointing in minified scripts**: fetch the full source with `Debugger.getScriptSource` and regex-search it locally,
   which is much faster than searching by eye in DevTools.

## Three pitfalls you will hit (all tested)

### Pitfall 1: XHR breakpoints **do not work on a fetch architecture**

`DOMDebugger.setXHRBreakpoint` **only applies to `XMLHttpRequest`**. Modern SPAs generally use `fetch`
⇒ the breakpoint is set, requests go out as usual, **0 pauses** (and no error, so it is easily misread as "this page has no requests").

**Countermeasure**: on fetch sites, "set the breakpoint by text inside the request wrapper function" (see pitfall 2).
Also, CDP has **no** `beforeXHR` instrumentation value (`Debugger.setInstrumentationBreakpoint`
only has the `beforeScriptExecution` family); copying it blindly fails silently.

### Pitfall 2: breakpoints in bundled scripts need **both lineNumber and columnNumber**

A bundle may have **only 8 lines in total, each hundreds of thousands of characters long**. Giving only `lineNumber` puts the breakpoint at the **start of the line**
(in the test it landed inside a Chinese string literal), and the variables read out have nothing to do with the target.

```js
// compute the in-line column from the text match position
const line = src.slice(0, idx).split('\n').length - 1;
const lineStart = src.lastIndexOf('\n', idx) + 1;
const column = idx - lineStart;                              // ★ required
await call('Debugger.setBreakpointByUrl', { url, lineNumber: line, columnNumber: column });
```

Read back `result.locations` to check whether CDP really accepted the position: **`locations.length === 0`
= no executable statement at that position** (most likely the match landed inside a string); use more distinctive text.

### Pitfall 3: call `Debugger.enable` **after registering the `scriptParsed` listener**

Enabling first makes Chrome **replay `scriptParsed` for the existing scripts all at once** while no listener exists yet
⇒ **0 scripts** received ⇒ the error "text not found in 0 scripts". Enabling again later **does not replay** (already enabled).
Criterion: the number of collected scripts is 0.

## Reusable patterns

**"Live window + trigger inside the window" must go into the same command**. CDP capture is live; requests completed before the window opens can never be captured;
and "please ask the user to act within the window" cannot be guaranteed by a script (the user agreed but acted outside the window = a wasted round; this project hit it).
Approach: add `--then <expression file> --then-after <seconds>` to window commands, and N seconds after the window opens, run the trigger expression over **the same CDP connection**
(commonly `location.reload()`, which brings the whole page initialization request chain).

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| XHR breakpoint paused 0 times | The target uses fetch, which XHR breakpoints do not cover | Set the breakpoint by text inside the request wrapper function instead | 30 min |
| The breakpoint read unrelated variables | A minified script line of 400,000 characters; giving only the line number put the breakpoint at the line start | Add `columnNumber` + read back `locations` to validate | 35 min |
| The error "text not found in 0 scripts" | `enable` came before listener registration and the replay was lost | Register `scriptParsed` first, then `enable` | 25 min |

## Improvement suggestions for this package

- If the execution surface of the `js-reverse` module depends on some external MCP, the documentation should **offer a direct CDP option in parallel**,
  so the whole route does not become unusable when that MCP is not ready.
- The module's `references/` is thin (12 files averaging about 271 B); the three pitfalls in this document are **certain to be hit**,
  so extracting them into a reference page is recommended.

## Evolution actions

- [x] Added pitfall records
- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation

## Environment information

- OS: win32 x64
- Tool versions: Chrome 155 / Node 26 (native WebSocket)
- Target platform/version: modern SPA (bundled output, no source map)

---

<!-- [Evolution statistics] New patterns this time: 2 (runtime call stack recovery / reading arguments at breakpoints) | Toolchain problems fixed this time: 3 -->
