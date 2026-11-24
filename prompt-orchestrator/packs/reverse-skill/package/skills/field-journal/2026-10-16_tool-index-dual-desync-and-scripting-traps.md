---
name: tool-index-dual-desync-and-scripting-traps
description: The two tool index copies .md/.json must stay in sync; in PowerShell 5.1, assigning a nonexistent property rolls back the whole block; a triple line ending pitfall
metadata:
  type: project
---

# Tool Index Dual-Copy Desync + Four Pitfalls of Scripted Maintenance

**Date**: 2026-10-16
**Scenario category**: other (toolchain maintenance / index consistency)
**Target**: the tool index of the local reverse engineering skill package

## Background

When registering "local tools not on PATH" (installed in a separate venv or a dedicated directory) in the tool index,
I wrote an idempotent script that changed only the human-readable `.md` copy. A later check found that **the machine-readable `.json` was not synced**.

## Defect 1: the `.md` and `.json` index copies are out of sync (misleading clients that read the json)

| Tool | `tool-index.md` | `tool-index.json` |
|---|---|---|
| Local JDK | `yes` | `available: false` |
| Dynamic analysis tools in a separate venv | `yes` | `available: false` |

**Why it is dangerous**: some agents read the **machine-readable** copy first ⇒ judge "tool not installed" ⇒ capabilities that are installed get skipped.
**Fix**: a script that changes the index must **update both copies at once** and run a consistency check at the end (compare the md `yes/no`
with the json `available` tool by tool).

## Defect 2: in PowerShell 5.1, assigning a **nonexistent property** of a PSCustomObject → the whole try block rolls back

When you assign a nonexistent property to an object produced by `ConvertFrom-Json`, PS 5.1 **throws immediately**
(`The property ... cannot be found on this object`), and since it is inside a `try` ⇒ **the whole sync rolls back**.

**Highly misleading symptom**: in the same batch of tools, A and B synced successfully and C failed. The reason is that **C appears in both the `tools` and
`capabilities` arrays**, and `capabilities` uses different field names (`tool_available` / `ready`,
not `available`) ⇒ the assignment blows up.

**Fix**: probe whether the property exists before assigning (the PS 5.1-safe approach):

```powershell
foreach ($c in $o.capabilities) {
  if ($c.name -ne $Name) { continue }
  if ($c.PSObject.Properties['tool_available']) { $c.tool_available = $true }
  if ($c.PSObject.Properties['ready'])          { $c.ready = $true }
}
```

## Defect 3: the triple line ending pitfall (the same patch was broken repeatedly)

| # | Scenario | Symptom | Fix |
|---|------|------|------|
| 1 | Read, modify and write the file in Python **text mode** | `git diff` becomes a giant **58 KB** patch (the whole file counts as changed) | **Binary read/write** (`open(p,'rb')` / `open(p,'wb')`), no line ending conversion |
| 2 | Source files created with a file writing tool are **CRLF**, while the project is all LF | Inconsistent with the rest of the project | Validate after writing and convert to LF |
| 3 | Global `core.autocrlf=true`, and `git apply` turns the target file into CRLF | After applying the patch, the line endings of the whole file change | `git -c core.autocrlf=false apply <patch>`, or simply **edit by hand** |

**Criterion**: the line counts shown by `git diff --stat` are wildly out of line with your actual change (for example 5 lines changed but 550 reported)
⇒ suspect line endings / BOM immediately, not the diff tool.

## Defect 4: the semantic trap of `find -size -1k` (false positives in statistics)

Counting "files smaller than 1KB" with `find ... -size -1k` **only matches 0-byte files**, because
`-size` counts in **blocks** and **rounds up**; a 146 B file counts as 1 block, which does not satisfy `< 1`.

**Fix**: use byte units, `-size -1024c`.
(In this case the error briefly led me to the wrong conclusion "the documents are generally thin", while in fact "overall there is substance, and only some modules are thin".)

## Reusable patterns

**Any index/inventory artifact that exists in more than one format must have a "consistency check" step**,
and the check must **compare item by item**, not just confirm that "both files exist".

**Scripts that modify files read and write in binary**, treating line endings as **data that must be preserved explicitly** rather than a runtime detail.

## Improvement suggestions for this package

- If `tool-index` must serve both people and machines, **keep only one copy as the single source of truth** (such as the json),
  and generate the other from a script; double writing always drifts.
- `refresh-tool-index` should support an "extra search paths" parameter (such as `%USERPROFILE%\Tools\**`),
  so tools installed in dedicated directories / venvs do not depend on manual bridging.

## Evolution actions

- [x] Updated tool-index (the two copies are now consistent)
- [x] Added pitfall records
- [ ] Updated the routing matrix
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation

## Environment information

- OS: Windows 10.0.22631
- Tool versions: PowerShell 5.1 / Node 26 / Git 2.45
- Target platform/version: local tool index (md + json copies)

---

<!-- [Evolution statistics] New patterns this time: 4 (dual index drift / PS assignment / line endings / find semantics) | Toolchain problems fixed this time: 4 -->
