---
name: cjk-adjacent-ascii-word-boundary-routing-failure
description: When Chinese text sits directly against an ASCII keyword, the \b boundary silently fails and routing falls back; the .NET and Python engines are both affected
metadata:
  type: project
---

# Chinese Text Directly Adjacent to ASCII Keywords Breaks the \b Word Boundary (Silent Fallback in the Routing Layer)

**Date**: 2026-10-16
**Scenario category**: other (tool/routing layer defect, not target reverse engineering)
**Target**: the local reverse engineering skill routing package itself (not an external target)

## Background

When the router was called with real Chinese task descriptions, tasks that clearly belonged to a specific route fell into `fallback` (the generic catch-all).
The official regression benchmark was fully green (178/178), so the defect was not in the rule content but in the **matching semantics**.

## Root cause

In both `.NET` (PowerShell `-match`) and Python 3 `re`, `\w` **includes CJK characters** for Unicode strings,
so when "a Chinese character sits directly against an ASCII keyword", `\b` (word boundary) **has word characters on both sides ⇒ no boundary ⇒ the assertion fails**:

```
Input: a Chinese sentence meaning "analyze whether this APK is packed", written with no spaces around APK
  The preceding CJK character (\w) and "a" (ASCII, \w) are adjacent ⇒ not a word boundary
  \bapk\b fails ⇒ none of the rules for that route match ⇒ falls to the catch-all
```

**Why the benchmark missed it**: all 103 existing Chinese cases **separated** ASCII keywords **with spaces** (such as "Android APK packed" written with spaces),
never covering the real input habit of "Chinese characters directly adjacent". **The benchmark's coverage blind spot is more worth recording than the defect itself.**

## Quantification

| Engine | Before fix | After fix |
|------|--------|--------|
| PowerShell (.NET Regex) | 11/20 correct | 18/20 |
| Python (used by the bash routing entry) | **0/8 correct** | **8/8** |

Both platforms read the same rule file ⇒ one fix covers both. The remaining 2 mismatches are **kept on purpose**:
bare `so` / `elf` (without a dot) do not match; adding them would hit common English words.

## Fix

Replace every `\b` in `must` / `mustAll` / `exclude` with an **ASCII-only boundary assertion**:

```
\bX\b   ->   (?<![A-Za-z0-9_])X(?![A-Za-z0-9_])
```

Key points:
- **Only touch regex fields**; keep `\b` in `note` (descriptive text) as is (that is prose, not a regex).
- When deciding whether a given `\b` is a leading or trailing boundary, **look at the left neighbor first**: if the left neighbor is an ASCII word char ⇒ trailing boundary;
  otherwise, if the right neighbor is a word char ⇒ leading boundary. In testing, an implementation that "looks at the right neighbor first" misjudged cases like `ad\b.?cs`, so `.` failed to match.
- After the change, run the regression benchmark (this time 178 → 197, still all green).

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| JSON invalid after replacement | On disk the regex `\b` is **3 characters** (escaped backslash + b); replacing it as 2 characters eats the `\` | Match the 3-character sequence in binary/exact mode | 20 min |
| Huge diff after editing the file | Python text mode read/write converted the line endings | **Binary read/write**, no line ending conversion | 15 min |
| Benchmark all green but functionality broken | Benchmark cases do not match real input habits (with spaces vs without) | Added 15 "no space" cases to lock in the regression | 10 min |

## Reusable patterns

**The criterion for "benchmark all green ≠ functionally correct"**: sample a run with **real user wording** (not test case wording).
In this case the characteristic of the real wording was "no spaces between Chinese and English". Any system that does text matching should ask:
"Are my test inputs and real user inputs the same at **token boundaries**?"

## Improvement suggestions for this package

- Benchmark cases should explicitly include "both spellings of the same keyword (with spaces / adjacent)" as **paired cases**, to avoid a false green from one-sided coverage.
- If upstream adopts this, the rule layer should use `(?<![A-Za-z0-9_])` instead of `\b` throughout, because this package targets users who **mix Chinese and English**.
- `references/` could add a page on "Unicode word boundary traps" (including the JS side of the same problem: JS `\w` is ASCII-only, so the JS implementation **does not** have this bug; the inconsistent behavior across the three engines is itself a trap).

## Evolution actions

- [x] Added pitfall records
- [x] Updated the routing matrix (filled the R3 keyword gap in sync)
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation

## Environment information

- OS: win32 x64
- Tool versions: PowerShell 5.1 / Node 26 / Python 3.10-3.14
- Target platform/version: local routing package v1.0.1

---

<!-- [Evolution statistics] New patterns this time: 1 (cross-engine Unicode word boundaries) | Toolchain problems fixed this time: 1 -->
