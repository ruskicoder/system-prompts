---
name: cdp-tooling-timing-and-option-traps
description: 'Six kinds of silent failure in a CDP forensics tool: navigation resets the Debugger domain, a low script count raises no alarm, options are not wired into some subcommands'
metadata:
  type: project
---

# Six Kinds of Silent Failure in a CDP Forensics Tool (All Exposed by One End-to-End Drill)

**Date**: 2026-10-16
**Scenario category**: other (quality problems in an in-house toolchain)
**Target**: local direct-CDP forensics scripts (not an external target)

## Background

Ran an "end-to-end drill" on an in-house CDP tool: not a formality, but a run against a real site of every capability it promises.
One drill exposed **6 defects**, **3 of them "silent failures"**: no error, no crash, just quietly wrong or incomplete results.

## Six defects

### High severity (silent failures)

**1. No alarm on a low script count → wrong conclusions**
When the page sat on a sub-route (`/notifications`, a 404 route), the SPA loaded only **10 scripts**, while a full load is **42**.
Search returned "**0 hits**" as usual; it looked like "this site does not have it", while in fact the scripts were not fully loaded at all.
**Fix**: warn explicitly when the number of collected http(s) scripts is low (<20), with the hint "return to the site home page before searching".

**2. Full-page navigation resets the Debugger domain → data from the old page**
When `Debugger.enable` runs and collection starts **before** navigation, you get the **old page's** scripts; the new page's `scriptParsed` events never arrive.
The tested symptom is highly misleading: the page **has navigated successfully** (`location` correct, `readyState=complete`, DOM normal),
but the script count is still the old page's 10, **with no error**.
**Fix**: the order must be "navigate first → wait for `Page.loadEventFired` → then enable + collect", implemented as a `--navigate <URL>` option.

### Medium severity

**3-4. Session capabilities "wired command by command" → something always gets missed**
`--then` (trigger inside the window) was wired into only 4 subcommands and missed `search_in_sources`;
`--navigate` was added only to the shared collection function, while `list_scripts` has its own implementation and does not go through that path.
**Symptom**: the option is accepted but **silently has no effect** (the argument is passed, the behavior does not change).
**Fix (structural)**: do not wire it command by command; move it to **unified preprocessing in the `main` flow**,
so every subcommand (including ones added later) gets the capability automatically. This one change eliminated both problem classes 3 and 4.

**5. Forgetting to register `VALUE_OPTS` when adding a valued option to the CLI**
Symptom: a value like "navigate to **true** first" appears in the log; the option degrades to a boolean, and its value is dropped as a positional argument.
**This project has hit the same pitfall three times** (`--host` / `--group` / `--navigate`).
**Fix**: make "which options take values" a data-driven set, with a hard comment above the set: "when adding an option, add it here too".

### Low severity (self-inflicted)

**6. Called an undefined helper function** (`sleep` exists in another file but not in this one).

## Reusable patterns

**"Silent failures" are far more dangerous than crashes**: a crash makes people stop and investigate right away;
a silent failure makes people **keep working on wrong results**, and the more "normal-looking" a conclusion is, the more easily it is trusted.
**Self-check criterion**: every "collection" operation should have a **plausibility check on quantities** (do the script count, entry count and byte count fall within the expected range? Warn on deviation).

**"Wiring command by command" is a design flaw, not an oversight**: when capabilities are added one command at a time, gaps grow with the number of commands.
Every "cross-cutting capability every subcommand should have" (logging, timeouts, navigation, triggers, authentication) belongs in a unified entry point.

## Improvement suggestions for this package

- If any tool in the package does "collect + search", the output should **always include the collection size** (such as `searching N scripts…`),
  so downstream readers can see at a glance whether N is absurd.
- A drill (end-to-end drill) should be a routine step of tool delivery: **merely running through is an illusion; running real data exposes the problems**.

## Evolution actions

- [x] Added pitfall records
- [ ] Updated the routing matrix / tool-index / bootstrap-manifest / sub-skill documentation

## Environment information

- OS: win32 x64 | Tool versions: Chrome 155 / Node 26 (native WebSocket)
- Target platform/version: modern SPA (bundled output, no source map)

---

<!-- [Evolution statistics] New patterns this time: 2 (silent failure criterion / unified wiring of cross-cutting capabilities) | Toolchain problems fixed this time: 6 -->
