---
name: ghidra-reverse
description: Use for free/open reverse engineering with Ghidra (headless or GUI), including decompile, cross-refs, and optional Ghidra MCP workflows when IDA is unavailable.
---

# Ghidra Reverse Engineering

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md`
2. `NOW`: confirm that **Ghidra** is needed (no IDA / open-source preference / batch headless)
3. `NEXT`: read `../tool-index.md` for the ghidra / ghidra-mcp paths
4. `NEXT`: missing tool → bootstrap `ghidra-mcp` (if the manifest supports it) or install Ghidra by the manual steps
5. `ACT`: import the sample → automatic analysis → export the decompilation of key functions

## When to use

- Main reverse engineering entry when there is no IDA license
- Batch headless analysis / decompilation in CI
- Ghidra script (Java/Python Jython/PyGhidra) automation
- Link with ghidriff in `binary-diff` / `patch-diff-exploit`

## Division of work with IDA

| Need | Preferred |
|------|------|
| Deep analysis with an existing IDA MCP | `ida-reverse/` |
| Open source / batch / teaching | **This skill** |
| Quick CLI reconnaissance only | `radare2/` |

## Workflow

### 1. Project and automatic analysis

```text
□ New Project → Import the file → Analyze (default analyzers)
□ Record the detected language/compiler and the base address
□ Mark the entry, export table and string xrefs
```

### 2. Key functions

```text
□ Trace back from strings / imported APIs
□ Reconstruct the algorithm in the Decompile window
□ Rename functions/variables; write Plate comments
□ Hand over to Frida/GDB when dynamic work is needed (dynamic chapter of reverse-engineering)
```

### 3. Headless (batch)

```bash
# Example: the analyzeHeadless path depends on the install; MUST take it from tool-index
analyzeHeadless /path/to/project Proj -import sample.bin -postScript ExportDecomp.py
```

### 4. MCP (if configured)

```text
□ Confirm the ghidra MCP port (commonly 8765; tool-index is authoritative)
□ Pull decompilation / xrefs with the MCP tools; guessing the port is forbidden
```

## Toolchain

| Tool | Purpose | Bootstrap |
|------|------|------|
| Ghidra | Main decompilation tool | Manual release / package manager |
| ghidra-mcp | AI bridge | bootstrap capability name `ghidra-mcp` |
| ghidriff | Patch diffing | See `patch-diff-exploit` |

## References

- `references/ghidra-cheatsheet.md`
- `../ida-reverse/` `../radare2/` `../binary-diff/`

## Routing context

**Upstream**: MASTER R22  
**Downstream**: dynamic verification → Frida/GDB; exploitation → `pwn-chain`  
**Sibling**: `ida-reverse` (commercial deep analysis)

## Task completion self-check

- [ ] Is it based on real Ghidra/tool-index paths?
- [ ] Did I record function addresses and renames?
- [ ] Are there reproducible steps?
- [ ] Checklist / journal?