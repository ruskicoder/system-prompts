# Agent Skill Supply Chain Security (distinctive feature of this package)

> Combined sources: OWASP Agentic Skills Top 10 (AST10), Anthropic Agent Skills security advice, public poisoning incidents (such as ClawHavoc, see the AST10 timeline)  
> Retrieved: 2026-07-17  
> Applies when installing/writing/merging **any** skill, MCP or bootstrap script

Static audit of this package's **executable script surface** (backdoors / database deletion / pipe execution): [`docs/PACKAGE-SECURITY-AUDIT.md`](../../docs/PACKAGE-SECURITY-AUDIT.md).

## 1. Why reverse-skill manages this separately

This package:

- Directs the AI to **run commands and bootstrap downloads**
- Touches the local machine and the network through MCP  
- Writes to field-journal / reports  

A malicious skill can cause: credential theft, persistent prompts, supply chain backdoors.  
We use **documentation gates + a tool source of truth** instead of building another skill app store.

## 2. Threat mapping (condensed AST10 approach)

| Risk class | Manifestation | This package's control |
|--------|------|----------|
| Malicious/poisoned skill | Induces exfil, writes memory/backdoors | Trust only this repository + external sources the user authorized in writing; read the external SKILL.md and scripts manually first |
| Excessive permissions | Indiscriminate `curl \| bash`, whole-disk reads | bootstrap only manifest capabilities; scope `network_profile` |
| Dependency poisoning | Malicious pip/npm packages | Prefer official releases; record versions in tool-index |
| Blind trust in MCP | Unaudited MCP servers | tool-index registration status + port probing; remote MCP not trusted by default |
| MCP/CLI auto-execution poisoning | A repository `.env` changes `CODEX_HOME` and similar so a malicious MCP runs at startup (HackTricks / CVE-type cases) | Do not trust default MCP configuration inside a repository; check env and the MCP list before starting the agent |
| Prompt injection into a skill | Hidden instructions in the SKILL body | Review the diff; "execution instructions hidden in HTML comments" are forbidden without the user |
| Scope drift | Skill induces wider scans / "fully automatic takeover from one domain" | ops/scope-contract: out_of_scope + auth; wild scanning without in_scope is forbidden |
| Skill stacking overload | Mounting too many skills at once causes missed findings (public evaluation observation) | Load only PRIMARY + necessary secondary (MASTER-ROUTING) |

## 3. MUST checklist for installing external skills

```text
□ Source: official org / audited list (such as ToB curated) / user-owned
□ Read every SKILL.md + scripts/* + package dependencies
□ No mysterious outbound connections, no default steps that read ~/.ssh / browser stores
□ On conflict with this package's routing: this package's MASTER-ROUTING + scope win
□ Do not copy into the monorepo unless it goes through CONTRIBUTING and redaction
□ Update skills/references/community-security-skills.md with the source and date
```

## 4. Boundary with bootstrap / MCP

| Action | Allowed | Forbidden |
|------|------|------|
| `bootstrap-reverse.ps1 -Capability X` | X ∈ bootstrap-manifest.json | Any new name without changing the manifest |
| Register an MCP | User confirmation + tool-index refresh | Silently writing a global MCP that points to an unknown URL |
| Run community one-click Python pentest tools | Authorized lab + after reading the source | Directly against production targets + unknown scripts |

## 5. Authors/contributors of this package

- New skill: CONTRIBUTING + ACTION REQUIRED + completion self-check  
- Citing community content: note the URL + date (this file / community-security-skills.md)  
- Suspicious behavior found: stop executing, tell the user, do not "try to bypass" automatically

## 6. Quick self-check (before each merge of external material)

```powershell
# List the script extensions that will come in
Get-ChildItem -Recurse -Include *.ps1,*.sh,*.py,*.js | Select-Object FullName
# Rough search for dangerous patterns (manual review, not exhaustive)
# Run in the external directory: Select-String -Pattern 'Invoke-WebRequest|curl .\||wget .\||~/.ssh|exfil'
```

## 7. Related

- Identity: `IDENTITY.md`  
- External directory: `../references/community-security-skills.md`  
- Authorization: `scope-contract.md` + `field-journal/precedent-auth.md`  
