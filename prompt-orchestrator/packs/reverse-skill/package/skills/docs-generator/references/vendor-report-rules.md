# Vendor Report Rules (professional vendor report structure overlay)

> Issue #65 problem 2.  
> **Take only the structure and writing rules; copying any vendor report body, charts, real IOC instances or long passages is forbidden.**  
> This file is an **overlay**: it does not replace the task templates in `security-report-templates.md`, and it does not weaken §0 Evidence→Finding→Path.

Structure references (public samples, skeleton only):

| Flavor | Main reference | Scenario |
|--------|--------|------|
| `malware` | Huorong Security virus/technical analysis reports | Clearly ordinary trojans, signed-binary sideloading, phishing poisoning, malicious samples |
| `apt` | Kaspersky Securelist / APT campaign reports (such as MATA) | APT, group campaigns, multi-stage infection chains, industry targeting |

Principle: **templates should be few and precise**: only 2 vendor full-text flavors (`malware` / `apt`) + Base common elements + an **optional thin overlay** (such as `vuln` vulnerability technical analysis). Regular reverse engineering, pentest, CTF and JS reports keep their task templates and are not disguised as malware reports by default; `vuln` is **not** a third default full-text flavor.

---

## 0. When to enable

When `docs-generator` produces a **security** report (reverse engineering / malware / end of a pentest / the user explicitly asks for a "professional report" or "vendor style"), it **MUST** read this file. Choose a vendor flavor only when task evidence or an explicit user request supports it; otherwise use `flavor = null` and only layer the common professional elements onto the original task template.

| Signal | Flavor / Overlay |
|------|------------------|
| APT / group / campaign / multi-stage C2 / industry targeting / ICS / spear-phishing campaign | `apt` |
| Clearly malicious samples, trojans, info stealing, signed-binary sideloading, spoofed sites | `malware` |
| The user explicitly asks for vulnerability/patch/CVE technical analysis, or the task evidence is OS/component vulnerability research | `flavor = null` + **thin overlay `vuln`** (see §3b) |
| Regular APK/ELF/PE/Mach-O reverse engineering, algorithm analysis, firmware analysis, penetration testing, CTF, JS signatures | `flavor = null`; use the original task template and the minimal set of common professional elements |

When the user explicitly asks for "Kaspersky/APT style", "Huorong/virus report style" or "vulnerability technical analysis style", that overrides the automatic choice.  
**Forbidden**: putting ordinary malware/APT/regular reverse engineering into the `vuln` outline by default.

---

## 1. Common professional elements (Base)

Apply these Base elements by report type. Elements marked **MUST** cannot be omitted; flavor-specific elements must not appear in unrelated tasks just to fill the template. When nothing applies, use `n/a` and explain why.

| # | Element | Requirement |
|---|------|------|
| G1 | Executive summary / overview | **MUST**: 3–8 sentences: what was analyzed, the most serious conclusion, impact surface, recommended actions |
| G2 | Scope and authorization | **MUST**: link to the case `scope.md` (see template §0.1) |
| G3 | Evidence→Finding→Path | **MUST**: see `security-report-templates.md` §0 and `skills/ops/evidence-finding-path.md` |
| G4 | IOC table | **MUST** for `malware` / `apt`; other tasks include it only when relevant indicators exist |
| G5 | Recommendations / response | **MUST** for `malware` / `apt`: at least 1 actionable recommendation; other tasks follow the original task template |
| G6 | Appendix metadata | **SHOULD**: tools and versions, sample hashes, complete reproduction commands |
| G7 | ATT&CK mapping | **MUST** (under `apt`; when no technique applies, `n/a` + reason); **SHOULD** for other tasks |

### 1.1 Minimum IOC table columns

```markdown
| Type | Value | Context | First/last seen | Source evidence | Confidence |
|------|----|--------|---------------|----------|--------|
| file_sha256 / file_md5 / domain / ip:port / url / mutex / path / registry | … | Where it was found | YYYY-MM-DD / n/a | E-id | high/med/low |
```

### 1.2 Copyright and safety boundaries

- Do not paste paragraphs or captions from vendor PDFs/web pages as your own analysis.
- Use placeholders for real tokens, internal URLs and customer identifiers.
- Do not output directly exploitable attack step details against unauthorized targets (follow the case scope / RULES).

---

## 2. Flavor: `malware` (Huorong style · explicit choice)

**Narrative goal**: let the reader understand within 5 minutes "what it is → where it came from → what the sample does → how to respond → which IOCs exist".

### 2.1 Recommended section order

```markdown
# [Title: one-sentence threat characterization]

> Analysis date / analyst / sample identifier (hash)

## 1. Overview
(G1: discovery channel, disguise technique, core technical points, whether products can detect it; write n/a if unknown)

## 2. Attack / infection flow
(Flowchart: Mermaid or a step list; matches Path `path_type=attack`)

## 3. Sample analysis
### 3.1 Sample provenance
### 3.2 Static analysis
(**MUST** include import table / basic identity Evidence: E-imports or equivalent; see the radare2/ida/malware hard gates)
### 3.3 Dynamic analysis / behavior
(n/a + reason when dynamic conditions are unavailable)
### 3.4 Core findings (Findings table or numbered list, with evidence_ids)

## 4. Incident response
(Act only within the authorized scope: first confirm the scope and preserve evidence such as samples, memory, process tree, network connections and logs, then isolate the host; only after approval by the person in charge terminate processes, quarantine/remove files, check hosts/startup items, run a full scan and recheck. Do not delete files before evidence is preserved.)

## 5. Summary
(Risk reminders and prevention for ordinary users/operations staff)

## 6. IOC information
(G4 table)

## 7. Evidence chain summary
(§0: E / F / P / Timeline; can merge with §3.4 without dropping fields)

## 8. Appendix
(Tool versions, reproduction commands, script paths)
```

### 2.2 Writing style

- Chinese-speaking users get Chinese by default; conclusions first, then details.
- Layer the static analysis by "component/stage" and avoid unstructured long log pastes.
- Response steps must be independently executable; filler such as "raise security awareness" is forbidden.

---

## 3. Flavor: `apt` (Kaspersky Securelist style)

**Narrative goal**: tell the campaign-level story clearly: who attacked whom with which chain and when, how the investigation progressed, how the components divide the work, and what defenders can use to detect it.

### 3.1 Recommended section order

```markdown
# [Campaign/cluster name]: [one-sentence impact]

> Date / team / industry and regional scope (if known)

## 1. Executive summary
(G1: time window, victim profile, entry point, family/cluster attribution, duration, most important conclusion)

## 2. The infection chain
(By stage: delivery → exploit/loader → main trojan → post-exploitation/theft; state "limited visibility" clearly for unknown stages
matching the Path; a chain diagram is recommended)

## 3. Incident investigation
(Investigation narrative: key turning points, internal proxy/C2 traits, how the scope widened; attach the Timeline)

## 4. Interesting findings
(3–7 non-obvious points, each attached to an E-id / F-id where possible)

## 5. Technical analysis
### 5.1 Component overview table (loader / trojan / stealer / …)
### 5.2 Per-component behavior and configuration
### 5.3 Static key points (including import table/packing/persistence Evidence)
### 5.4 Network and C2
(An ATT&CK table G7 can be attached)

## 6. Detection and mitigation
(Detection ideas / hunting leads / mitigation priority; no empty slogans)

## 7. IOC
(G4; grouped by type)

## 8. Evidence chain summary
(§0 fields)

## 9. Appendix
(Sample list and hashes, tool versions, referenced public identifiers; do not copy external report text)
```

### 3.2 Writing style

- Be honest about the timeline and "visibility limits".
- Interesting findings ≠ a repeated overview; write the anomalies that were truly key in the investigation.
- Analyze components with a table first: role / persistence / C2 / dependencies, then expand.

---


## 3b. Thin overlay: `vuln` (vulnerability technical analysis · optional)

> Issue #65 supplement. The structure references the outline of public "OS/component vulnerability technical analysis" reports; **take only the section skeleton**; copying PoC packets, exploitation details or unauthorized attack steps from screenshots/body text is forbidden.  
> **Not** a third default vendor full-text flavor; layer it only for vulnerability research tasks or on explicit user request.

**Narrative goal**: the reader quickly sees "who is affected → how to confirm/reproduce (within authorization) → root cause and patch diff → how to mitigate".

### Suggested section order

```markdown
## 1. Vulnerability overview
### 1.1 Impact scope (version/component/configuration preconditions)
### 1.2 Vulnerability reproduction (authorized environment; steps repeatable by a third party; no weaponization tutorial tone)

## 2. Vulnerability analysis
### 2.1 Crash / anomaly analysis (Evidence: crash logs, trigger conditions)
### 2.2 Patch analysis (diff/guard conditions/fix points, attach E-*)
### 2.3 PoC or trigger analysis (only existing material within the authorized scope; explaining the protocol/input construction layers is enough)

## 3. Protection advice
### 3.1 Mitigations (configuration/mitigation switches and similar)
### 3.2 Official patch and verification

## 4. Evidence → Finding → Path (can be merged into each section or a separate table)
```

### Hard constraints

- **MUST** scope/authorization: reproduction and PoC extension against unauthorized targets are forbidden
- **MUST** E/F/P: reproduction, crash and patch conclusions all attach evidence_ids
- **MUST NOT** use `vuln` as the default shell for malware/APT
- **MUST NOT** copy exploit code or complete weaponization steps from external reports/screenshots
- IOC table: only when network/file indicators exist; otherwise n/a or omit

---
## 4. Hookup with the existing task templates

| Task template (`security-report-templates.md`) | Overlay method |
|------------------------------------------|----------|
| 1. Reverse engineering report | Default `flavor = null`, keep the original "static/dynamic/reproduction" skeleton and hard-gate Evidence such as the import table; apply §2 only to clearly malicious samples |
| 2. Penetration test report | `flavor = null`; add the applicable G1–G3 from Base, align the attack path with the §0 Path, no forced IOC |
| 3. CTF Writeup | `flavor = null`; keep the original challenge, approach and reproduction structure, no forced IOC/ATT&CK |
| 4. JS/web signature reverse engineering | `flavor = null`; use the original overview → locating → algorithm → reproduction skeleton, no malware overlay |
| Malware / APT specific | Explicitly choose the `malware` or `apt` full-text skeleton |

**Conflict resolution**: the §0 Evidence chain fields and the scope gate **always win**; a flavor only changes narrative order and the professional shell and must not remove E/F/P.

---

## 5. Selection pseudocode

```
if user_requests_kaspersky or apt or threat_campaign:
    flavor = apt
elif user_requests_huorong or vir_report or explicit_malware:
    flavor = malware
else:
    flavor = null  # original task template + applicable Base elements
overlay = null
if user_requests_vuln_tech_report or cve_patch_analysis:
    overlay = vuln  # thin only; never a third default full flavor
emit(base_report)
if flavor in (malware, apt):
    emit(report with flavor outline)
elif overlay == vuln:
    emit(report with vuln thin outline)
```

---

## 6. Completion checklist (self-check at the end of the report)

- [ ] A flavor is chosen, or explicitly "task template + minimal set"
- [ ] The G1 overview exists and is not empty talk
- [ ] §0 E/F/P fields are complete
- [ ] `malware` / `apt` reports have an IOC table (or n/a + reason)
- [ ] `malware` / `apt` reports have actionable recommendations/response
- [ ] Tasks without a flavor were not given malware/APT-specific sections
- [ ] vuln enabled only for vulnerability tasks; contains the overview/analysis/protection skeleton and E/F/P; no unauthorized PoC weaponization
- [ ] No pasted vendor text, no placeholders/TODOs
- [ ] Hard-gate Evidence such as the import table is in the static/technical analysis (if this task included binary analysis)

---

## 7. Source register

- Kaspersky Securelist, “Updated MATA attacks industrial companies in Eastern Europe”: <https://securelist.com/updated-mata-attacks-industrial-companies-in-eastern-europe/110829> (structure reference; accessed 2026-08-11)
- Huorong Security public technical article entry: <https://www.huorong.cn/> (site entry; accessed 2026-08-11. Register the specific article URL, title and access date when actually citing)
- ATT&CK technique ids serve only as normalized mappings and must be backed by this task's Evidence; do not carry IOCs from external reports into the current report automatically.

---

## 8. Non-goals

- No additional full-text templates for Mandiant/CrowdStrike/Qi An Xin and others (the two flavors + the optional thin overlay already cover common needs).
- Do not promote `vuln` to a default full-text flavor alongside malware/apt.
- Do not crawl vendor sites automatically to fill reports.
- Do not lower the Evidence contract or the authorized scope because of a flavor.
