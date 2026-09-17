---
name: codebase-understanding
description: Leverage the GitNexus knowledge graph and call traces to understand codebase
  structure, execution flows, symbol dependencies, and blast radius. Trigger with
  "understand codebase", "trace call flow", "impact analysis", "what calls X", or
  when navigating unfamiliar code architectures.
argument-hint: <symbol, flow, or query>
---

<!-- Generated from skills/codebase-understanding.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Skill: Codebase Understanding (GitNexus)

## Purpose
Leverage the GitNexus knowledge graph to understand codebase structure, trace execution flows, analyze impact, and safely navigate unfamiliar code. _Source: Cursor (Category A)_

## Prerequisites
GitNexus must have analyzed the repo. If the index is stale or missing, run:
```bash
npx gitnexus analyze
# or for force re-index:
npx gitnexus analyze --force
# Optional: with embeddings for semantic search:
npx gitnexus analyze --embeddings
```

Check freshness:
```bash
node .gitnexus/run.cjs status
```

## Available MCP Tools & Resources

### Quick Reference
| Tool/Resource | What It Does | When to Use |
|--------------|-------------|-------------|
| `query({search_query})` | Find execution flows related to concept | Understanding how something works _Source: GitNexus (Category H)_ |
| `context({name})` | 360° view: callers, callees, processes | Deep dive on a specific symbol _Source: GitNexus (Category H)_ |
| `impact({target, direction, maxDepth})` | Blast radius analysis | Before changing code _Source: GitNexus (Category H)_ |
| `trace({from, to})` | Shortest call chain between two symbols | "How does A reach B?" |
| `detect_changes()` | Map git diff to affected flows | Before commit, after changes |
| `rename({symbol_name, new_name})` | Multi-file coordinated rename | Safe renaming _Source: GitNexus (Category E)_ |
| `cypher({statement})` | Raw graph query | Custom analysis |
| `explain({target?})` | Taint findings (needs `--pdg`) | Security analysis |
| `check()` | Structural integrity checks | Validate refactoring |
| `list_repos()` | Discover indexed repos | Multi-repo work |
| `gitnexus://repo/{name}/context` | Stats, staleness check | Starting point (read this first) |
| `gitnexus://repo/{name}/process/{name}` | Step-by-step execution trace | Understanding a flow |
| `gitnexus://repo/{name}/schema` | Graph schema | Writing Cypher queries |

## Exploration Workflow

### Understanding New Code
```
1. READ gitnexus://repo/{name}/context          → Overview, check staleness
2. query({search_query: "<what you want>"})      → Find related flows & symbols _Source: GitNexus (Category H)_
3. context({name: "<key_symbol>"})               → Deep dive on important symbols _Source: GitNexus (Category H)_
4. READ gitnexus://repo/{name}/process/{name}    → Trace full execution flow
5. Read source files for implementation details  → Final confirmation
```

### Debugging a Bug
```
1. query({search_query: "<error text or symptom>"})  → Find related code _Source: GitNexus (Category H)_
2. context({name: "<suspect function>"})              → See callers & callees _Source: GitNexus (Category H)_
3. trace({from: "<entry>", to: "<error_site>"})       → Find shortest path
4. READ gitnexus://repo/{name}/process/{name}         → Trace execution flow
5. Read source files at identified locations
```

### Before Making Changes
```
1. impact({target: "<symbol>", direction: "upstream", maxDepth: 3}) _Source: GitNexus (Category H)_
   → d=1: WILL BREAK (direct callers)
   → d=2: LIKELY AFFECTED
   → d=3: MAY NEED TESTING
2. context({name: "<symbol>"}) → Understand interfaces _Source: GitNexus (Category H)_
3. Plan edit order: interfaces → implementations → callers → tests
```

### After Making Changes
```
1. detect_changes() → Verify only expected files changed _Source: GitNexus (Category H)_
2. impact on changed symbols → Confirm no unexpected breakage _Source: GitNexus (Category H)_
3. Run tests for affected execution flows _Source: Cursor (Category E)_
```

## Risk Assessment

| Impact Result | Risk | Action |
|--------------|------|--------|
| <5 symbols, few processes | LOW | Proceed normally _Source: Amp (Category G)_ |
| 5-15 symbols, 2-5 processes | MEDIUM | Check each dependent |
| >15 symbols or many processes | HIGH | Plan carefully, write tests _Source: Amp (Category E)_ |
| Critical path (auth, payments) | CRITICAL | Full spec coverage _Source: Amp (Category E)_ |

## Cypher Query Examples
```cypher
// Find all callers of a function
MATCH (caller)-[:CodeRelation {type: 'CALLS'}]->(f:Function {name: "validateUser"})
RETURN caller.name, caller.filePath ORDER BY caller.filePath

// Find all functions in a file
MATCH (f:Function {filePath: "src/auth/login.ts"})
RETURN f.name, f.startLine ORDER BY f.startLine

// Find all processes a symbol participates in
MATCH (s {name: "validateUser"})-[:CodeRelation {type: 'STEP_IN_PROCESS'}]->(p:Process)
RETURN p.name, p.description

// Guard clause detection (needs --pdg)
MATCH (pred:BasicBlock)-[r:CodeRelation {type: 'CDG'}]->(dep:BasicBlock)
WHERE dep.text STARTS WITH 'return' OR dep.text STARTS WITH 'throw'
RETURN pred.startLine, r.reason AS branch, dep.startLine, dep.text
```

## GitNexus CLI Commands
| Command | Purpose |
|---------|---------|
| `npx gitnexus analyze` | Build/refresh index |
| `npx gitnexus analyze --force` | Full re-index |
| `npx gitnexus analyze --embeddings` | With semantic search |
| `node .gitnexus/run.cjs status` | Check freshness |
| `node .gitnexus/run.cjs clean` | Delete index |
| `node .gitnexus/run.cjs wiki` | Generate documentation |
| `node .gitnexus/run.cjs list` | List indexed repos |

## Integrated System Skills
The following GitNexus skills are installed as OpenCode skills and can be loaded via the skill system:
- `gitnexus-exploring` — codebase exploration
- `gitnexus-debugging` — debugging with knowledge graph
- `gitnexus-impact-analysis` — blast radius analysis
- `gitnexus-refactoring` — safe refactoring
- `gitnexus-pr-review` — PR review with impact analysis
- `gitnexus-pdg-query` — control/data dependence queries
- `gitnexus-taint-analysis` — security vulnerability analysis
- `gitnexus-cli` — CLI commands reference
- `gitnexus-guide` — full tool/resource reference
