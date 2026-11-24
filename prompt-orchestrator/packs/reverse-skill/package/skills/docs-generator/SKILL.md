---
name: docs-generator
description: |
  Creates task-oriented technical documentation with progressive disclosure. Use when writing READMEs, API docs, architecture docs, or markdown documentation.
  Also use this skill at the END of any completed reverse engineering, penetration testing, CTF, or security analysis task to generate a formal report in the user's project directory.
  Trigger keywords: write a report, write documentation, produce a report, writeup, technical documentation, report, documentation.
---

# Technical Documentation

## ACTION REQUIRED (execute right after reading)

1. `NOW`: confirm whether the current task falls within this skill's scope
2. `NOW`: read `../tool-index.md` and check tool availability and actual paths
3. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
4. `ACT`: enter the first step of the "Workflow" and execute it; do not stop at a confirmation state

For writing style, tone, and voice guidance, use `Skill(ce:writer)` with **The Engineer** persona.

## Security/reverse engineering task documentation output

After a reverse engineering/pentest/CTF/security analysis task completes, this skill produces the formal technical document in the **user's project directory**.

### When it triggers

1. A reverse engineering task completes with core conclusions (algorithm reconstruction, signature cracking, bypass plan and similar)
2. A penetration test completes with vulnerabilities found and verified
3. A CTF challenge is solved and the flag obtained
4. The user explicitly asks to "write a report/document/writeup"

### Template choice

| Task type | Template |
|---------|---------|
| APK/binary/so reverse engineering | `references/security-report-templates.md` → reverse engineering report |
| Penetration testing/vulnerability hunting | `references/security-report-templates.md` → penetration test report |
| CTF solving | `references/security-report-templates.md` → CTF Writeup |
| JS/web signature reverse engineering | `references/security-report-templates.md` → signature reverse engineering report |
| Malware / APT / virus analysis report | `references/security-report-templates.md` + **`references/vendor-report-rules.md`** |
| General technical documentation | `references/templates.md` → README / API documentation |

### Vendor report structure (Issue #65)

Formal security reports **MUST** read `references/vendor-report-rules.md` (take only the structure; do not copy vendor text). Choose a vendor flavor only when the task evidence or the user explicitly calls for it; regular reverse engineering and other tasks use `flavor = null`.

| Flavor / Overlay | When to use | Main reference skeleton |
|------------------|--------|------------|
| `malware` | Clearly malicious samples, trojans, signed-binary sideloading, phishing poisoning | Huorong style: overview → flow → sample analysis → incident response → IOC |
| `apt` | APT/campaign/group/multi-stage infection chain/industry targeting | Kaspersky Securelist style: summary → infection chain → investigation narrative → Interesting findings → technical analysis → detection and mitigation → IOC |
| `flavor = null` | Regular APK/ELF/PE/Mach-O reverse engineering, algorithm/firmware analysis, pentest / CTF / JS signatures | Original task template + Base common elements; no malware/APT-specific sections |
| thin `vuln` | The user explicitly asks for vulnerability/patch/CVE technical analysis | Overview → impact/reproduction → crash and patch analysis → protection advice (layered on null, not a third default full-text flavor) |

Principle: **templates should be few and precise**: only 2 vendor full-text flavors; `vuln` is only an optional thin overlay, with no third default full-text template.
Applies **together** with §0 Evidence→Finding→Path; on conflict the Evidence contract wins.

### Output standard

- **Output location**: the user's current project directory (not the skill package directory)
- **File name format**: `YYYY-MM-DD_[type]-[target short name]-report.md`
- **If the project has a `docs/` directory**: prefer placing it under `docs/`
- **Encoding**: UTF-8
- **Language**: follow the user's conversation language (a Chinese conversation gets a Chinese report, an English conversation gets an English report)

### Quality requirements

- Every code block must run directly or have clear context
- No placeholders/TODOs
- Key findings must be backed by evidence
- Reproduction steps must let a third party reproduce independently
- Replace sensitive information (real tokens, passwords, internal URLs) with placeholders
- **MUST** contain the Evidence → Finding → Path chain (see `../ops/evidence-finding-path.md` and template §0)
- **MUST** read `references/vendor-report-rules.md`: choose `malware` / `apt` or `flavor = null` (vulnerability tasks may add the thin `vuln` overlay); without a flavor, output only the original task template and the applicable Base elements, with no forced IOC/ATT&CK
- **SHOULD** reference the case `scope.md` / `timeline.md` (`../scripts/case-init.ps1`)

### Diagram integration

When generating a report, call the `diagram-generator` skill at suitable places to produce visual diagrams:

| Report type | Suggested diagrams | Diagram type |
|---------|---------|---------|
| Reverse engineering report | Function call relationship diagram, data flow diagram | Mermaid flowchart / sequenceDiagram |
| Penetration test report | Attack path diagram, network topology diagram | Mermaid flowchart / Graphviz |
| CTF Writeup | Solution flowchart | Mermaid flowchart |
| JS signature reverse engineering report | Request chain sequence diagram, algorithm flowchart | Mermaid sequenceDiagram / flowchart |

Diagrams are embedded in the report markdown as Mermaid code blocks so they render directly on GitHub/GitLab.

---

## Core Principles

### 1. Progressive Disclosure

Reveal information in layers:

| Layer | Content | User Question |
|-------|---------|---------------|
| 1 | One-sentence description | What is it? |
| 2 | Quick start code block | How do I use it? |
| 3 | Full API reference | What are my options? |
| 4 | Architecture deep dive | How does it work? |

**Warnings, breaking changes, and prerequisites go at the TOP.**

### 2. Task-Oriented Writing

```markdown
<!-- Bad: Feature-oriented -->
## AuthService Class
The AuthService class provides authentication methods...

<!-- Good: Task-oriented -->
## Authenticating Users
To authenticate a user, call login() with credentials:
```

### 3. Show, Don't Tell

Every concept needs a concrete example.

## Formatting Standards

- **Sentence case headings**: "Getting started" not "Getting Started"
- **Max 3 heading levels**: Deeper means split the doc
- **Always specify language** in code blocks
- **Relative paths** for internal links
- **Tables** for structured data with 3+ attributes

## Quality Checklist

- [ ] Code examples tested and runnable
- [ ] No placeholder text or TODOs
- [ ] Matches actual code behavior
- [ ] Scannable without reading everything
- [ ] Reader knows what to do next

## Anti-Patterns

| Problem | Fix |
|---------|-----|
| Wall of text | Break up with headings, bullets, code, tables |
| Buried critical info | Warnings/breaking changes at TOP |
| Missing error docs | Always document what can go wrong |

## Templates

For README, API endpoint, and file organization templates, see [references/templates.md](references/templates.md).

## Related Skills

- `Skill(ce:writer)` - Writing style, tone, and voice (load The Engineer persona)
- `Skill(ce:visualizing-with-mermaid)` - Architecture and flow diagrams


---

## On-Demand Bootstrap

This skill depends on no external tools and generates pure text. No bootstrap needed.

If diagrams need rendering for the report, it calls the `diagram-generator/` skill.

---

## Routing context

**Upstream entry**: every security/reverse engineering skill calls this skill automatically when its task completes
**How it triggers**:
- Automatic: runs as step 9 of the behavior chain after the task completes
- Manual: the user says "write a report", "produce documentation", "writeup"

**Sibling modules**:
- `apk-reverse/`: produces a reverse engineering report after APK reverse engineering
- `ida-reverse/`: produces a reverse engineering report after binary analysis
- `radare2/`: produces a reverse engineering report after CLI analysis
- `js-reverse/`: produces a signature report after JS signature reverse engineering
- `reverse-engineering/`: produces a reverse engineering report after general reverse engineering
- `field-journal/`: report content also serves as a data source for the evolution log

**Security report templates**: `references/security-report-templates.md`
**Vendor report rules**: `references/vendor-report-rules.md` (flavor: malware | apt | null; optional overlay: vuln)
**General document templates**: `references/templates.md`


## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Does the report contain Evidence / Finding / Path (ops contract)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
