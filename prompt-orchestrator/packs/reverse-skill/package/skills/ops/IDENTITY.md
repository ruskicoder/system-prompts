# reverse-skill Identity Statement (relative to Z3r0)

> This file fixes **who we are**. It absorbs Z3r0's ideas on evidence, scope, division of work and timelines, but does **not** become the Z3r0 platform.

## We are

| Dimension | reverse-skill |
|------|----------------|
| Form | **Skill routing package**: methodology + tool bootstrap for any AI client (Claude/Cursor/Codex…) |
| Entry | `RULES.md` → `MASTER-ROUTING` / `master-route.ps1` → sub-skill |
| Tool truth | `tool-index.md` + `bootstrap-manifest.json` (local paths, no guessing) |
| Evolution | Redacted experience written back to `field-journal/` |
| Output | Markdown reports + the local `work/<case>/` working directory (gitignored) |
| Deployment | `git clone` is enough; no mandatory PG/UI/Docker pool |

## We are not

| Z3r0 has | reverse-skill **deliberately does not build** |
|---------|---------------------------|
| React operations console | No |
| FastAPI control plane + WebSocket sessions | No |
| PostgreSQL evidence store | No |
| LightRAG service | No |
| Docker host pool / noVNC control proxy | No: (can **document** an optional sandbox profile) |
| Multi-agent process runtime | No: (only **role→skill mapping + handoff protocol**) |

## What we learn from Z3r0 (scaled-down implementation)

| Idea | reverse-skill form |
|------|-------------------|
| Authorization and project boundary | `ops/scope-contract.md` → `scope.md` per case |
| Evidence→Finding→Path | `ops/evidence-finding-path.md` + report templates |
| Specialist division of work | `ops/role-map.md` (Lead/cie/cpe/cre…→ skill) |
| Replayable | Append-only `work/<case>/timeline.md` |
| WorkItem/coverage | `workitems.md` + coverage checkboxes |
| Complete sandbox tooling | `ops/sandbox-profile.md` vs bootstrap-manifest |
| Egress control | `network_profile` field (offline/lab/authorized) |

## Distinctive features (must be kept)

1. **Three-axis routing + PRIMARY fast path** (target type / intent / toolchain)  
2. **bootstrap installs tools on demand** across Windows/Kali/Linux/macOS  
3. **MCP friendly** (IDA/Burp/jshook/anything-analyzer)  
4. **field-journal redacted evolution**  
5. **Obedience engineering**: ACTION REQUIRED / completion self-check / no fake stops  

## Healthy relation with Z3r0

```text
Z3r0 = red team operating system / team collaboration platform
reverse-skill = the agent's security work router + manual

Optional future: mount this package's skill content into Z3r0 sandbox-local skills
Current: works completely with zero Z3r0 dependency
```

## Relation to "800+ community micro-skills"

- Do **not** submodule giant skill libraries (poisoning surface and maintenance cost, see `skill-supply-chain.md`)  
- **Do** maintain `references/community-security-skills.md` as an index and borrowing rules  
- **Do** use `domain-coverage-map.md` to show: deep skills + routing > a pile of fragmented skills  
- Installing external skills: AST10 thinking + trust only curated sources (such as Trail of Bits curated)  
