# Community Security Skill Ecosystem Comparison (2026-07)

> Sources retrieved: **2026-07-17**  
> Purpose: let reverse-skill **know what exists outside**, borrow as needed, and **not** merge giant external libraries wholesale into this package.  
> This package's identity: routing + tool bootstrap + evidence/scope contract + field-journal (see `ops/IDENTITY.md`).

## 1. High-value external repositories (learn from them, do not install blindly)

| Repository | Scale/positioning | Value to this package | Risk |
|------|-----------|------------|------|
| [trailofbits/skills](https://github.com/trailofbits/skills) | ToB security research Claude plugin marketplace | Quality benchmark for audit/vulnerability analysis/RE plugins | Install through the ToB marketplace; do not trust non-curated copies by default |
| [trailofbits/skills-curated](https://github.com/trailofbits/skills-curated) | Reviewed plugin list | Preferred over arbitrary community skills | Same as above |
| [Orizon-eu/claude-code-pentest](https://github.com/Orizon-eu/claude-code-pentest) | 6 pentest lifecycle skills + pure Python scripts | The recon→exploitation→report pipeline compares with our `attack-chain`+`pentest-tools` | Self-check the authorization boundary; scripts need a sandbox |
| [trilwu/secskills](https://github.com/trilwu/secskills) | 16 skills + 6 specialist subagents | The multi-role division compares with `ops/role-map.md` | Plugin form, differs from this package's monorepo |
| [Masriyan/Claude-Code-CyberSecurity-Skill](https://github.com/Masriyan/Claude-Code-CyberSecurity-Skill) | ~15–19 domain skills (including RE/OT/CSOC) | Domain coverage checklist | Less depth than this package's single-domain skills |
| [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) | **800+** skills · ATT&CK/NIST mapping | The **framework mapping** and domain catalog are worth referencing; do not depend on the whole library | Very large, huge maintenance and poisoning surface |
| [Eyadkelleh/awesome-skills-security](https://github.com/Eyadkelleh/awesome-claude-skills-security) | SecLists packaged as agent skills | Wordlist/payload entry | Overlaps with the seclists bootstrap |
| [securityfortech/awesome-security-skills](https://github.com/securityfortech/awesome-security-skills) | Curated list of security skills | Index for discovering new skills | List type, each entry needs an audit |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | Index of 1000+ cross-vendor skills | Discover official/community skills | Not security specific |
| [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | PR security review GitHub Action | Compares with our docs/report-side "change audit" scenario | A CI product, not RE routing |
| [agentskills.io](https://agentskills.io) | Agent Skills open standard | Align frontmatter/directory conventions | The standard itself has no offensive or defensive content |

### 1.1 Second retrieval round additions (searched again 2026-07-17)

| Repository / resource | Positioning | Where it lands in this package |
|-------------|------|----------|
| [trailofbits/skills](https://github.com/trailofbits/skills) plugins: `audit-context-building` `differential-review` `semgrep-rule-creator` `sharp-edges` `dwarf-expert` `burpsuite-project-parser` | Audit context, differential security review, dangerous APIs, DWARF, Burp project parsing | Compare against `ida-reverse`/`docs-generator`/audit workflows; **not** merged wholesale |
| [HexRaysSA/ida-claude-code-plugins](https://github.com/HexRaysSA/ida-claude-code-plugins) | Official IDA Claude plugins (including domain automation, marked unsafe) | Compare with the `ida-reverse` MCP path; unsafe plugins are disabled by default |
| [P4nda0s/reverse-skills](https://github.com/P4nda0s/reverse-skills) | IDA-NO-MCP: export decompilation, then analyze; rev-frida/dex-dump/u3d | Complements "offline export when MCP is unavailable" |
| [2389-research/binary-re](https://github.com/2389-research/binary-re) | triage→static(r2/Ghidra)→dynamic(QEMU/GDB/Frida)→synthesis | `reverse-engineering` phase gates are in `re-agent-workflow.md` |
| [incogbyte/android-reverse-engineering-claude-skill](https://github.com/incogbyte/android-reverse-engineering-claude-skill) | APK unpacking, endpoint extraction, adaptive Frida bypass | Compare with `apk-reverse`; dynamic scripts need scope |
| [OwenPawl/cerberus-re-skill](https://github.com/OwenPawl/cerberus-re-skill) | Apple-oriented Ghidra+LLDB+Frida triple loop | Reference for the macOS/iOS dynamic loop |
| [ljagiello/ctf-skills](https://github.com/ljagiello/ctf-skills) | CTF reverse/pwn; tools installed on demand | Compare with CTF-Sandbox + `pwn-chain` |
| [shuvonsec/claude-bug-bounty](https://github.com/shuvonsec/claude-bug-bounty) | /recon→/hunt→/validate→/report | Compare with `recon-pipeline.md` + the scope gate |
| [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) | Web payloads + a Prompt Injection chapter | `pentest-tools/payloads` first; LLM topics in `llm-security` |
| [HackTricks](https://hacktricks.wiki/) | Pentest methodology + **AI/MCP abuse** | See the MCP section of skill-supply-chain |
| [appsecsanta AI pentesting agents 2026](https://appsecsanta.com/research/ai-pentesting-agents-2026) | Architecture classification of 39+ open-source AI pentest agents | Multi-agent ≠ mandatory; we use role-map |
| Snyk evaluation "more skills ≠ better" | Skill stacking can lower audit quality | Reinforces the "deep skills + routing" strategy |

## 2. Security standards and threats (2025–2026)

| Source | Key points | Where it lands in this package |
|------|------|----------|
| [OWASP Agentic Skills Top 10](https://owasp.org/www-project-agentic-skills-top-10/) | Malicious skills, supply chain, permission abuse, memory poisoning and more | `ops/skill-supply-chain.md` |
| [Anthropic Agent Skills engineering article](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | Install only trusted sources; review scripts and dependencies | Same as above + bootstrap forbids guessing paths |
| Poisoning campaigns such as ClawHavoc (recorded by AST10) | Mass malicious skills in registries | One-click installs from unknown registries into this package are forbidden |

## 3. What this package has vs broad external coverage

| Domain | reverse-skill | Why we do not merge the common external libraries wholesale |
|------|---------------|--------------------------------|
| APK/JS/IDA/r2/firmware/pwn | **Deep** skills + scripts | Keep the depth bound to tool-index |
| Pentest/attack chain/SRC | pentest-tools + attack-chain + src-hunter | Orizon-style packages can serve as a methodology comparison |
| LLM/agent security | llm-security | AST10 strengthens the security of the skills themselves |
| Evidence/scope/roles | **ops/** (distinctive feature) | Most skill packages have no case contract |
| OT/ICS / pure GRC / fraud F3 | No standalone skill | Routing miss → propose a new skill or an external link; do not force it in |
| 800+ micro-skills | Not copied | MASTER routing + domain skills replace fragmentation |

## 4. Borrowing rules (MUST)

```text
1. Pulling a whole library of 800+ skills through a git submodule as a runtime dependency is forbidden
2. When borrowing: extract "phases/checklists/command patterns" into this package's references or an existing skill
3. External scripts: first inspect dependencies and network behavior in an isolated environment, then consider bootstrap-manifest
4. New scenarios: add a skill through CONTRIBUTING and update routing + the RULES keywords
5. Record the source URL + retrieval date (the format of this file)
6. Run the ops/skill-supply-chain.md checklist before installing/merging
7. At runtime load only the PRIMARY of MASTER-ROUTING (+ necessary secondary), to avoid skill stacking overload
```

## 4.1 "Borrowed outputs" already settled in this package (not external library dependencies)

| Output | Path |
|------|------|
| RE four phases | `reverse-engineering/references/re-agent-workflow.md` |
| Authorized reconnaissance | `pentest-tools/references/recon-pipeline.md` |
| Attack chain gates | `attack-chain/references/lifecycle-checklist.md` |
| Skill supply chain | `ops/skill-supply-chain.md` |
| Domain coverage | `references/domain-coverage-map.md` |

## 5. Suggested priorities (later iterations)

| Priority | Action |
|--------|------|
| P0 done | ops contract, MASTER routing, skill supply chain security document |
| P1 | Add pentest phase checklists to attack-chain references, compared against Orizon/ToB |
| P2 | Optional "external skill allowlist" configuration, not in the default path |
