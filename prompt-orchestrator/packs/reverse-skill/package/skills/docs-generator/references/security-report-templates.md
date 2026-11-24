# Security/Reverse Engineering/Pentest Technical Document Templates

This file provides document templates for security projects such as reverse engineering, penetration testing and vulnerability analysis. After the task completes, the AI should create a document in the user's project directory and fill in the matching template.

---

## 0. Evidence Chain (every security report MUST contain it)

> Full contract: `skills/ops/evidence-finding-path.md`  
> Case directory: `work/<case>/` (`case-init.ps1`)

The report body **MUST** contain the following sections (they can be merged into "Core findings", but no field may be omitted):

### 0.1 Scope summary
- Link to `scope.md`: `auth` / `in_scope` / `network_profile`
- No scope → the task must not be declared complete

### 0.2 Evidence
At least 1 entry, fields: `E-id` / `source_ref` / `repro_command` / `content_hash|n/a`

### 0.3 Findings
Each entry: `F-id` / `severity|n/a_re` / `evidence_ids` / `confidence` / `location` / `status`

### 0.4 Path
At least 1 `P-id`: `path_type=attack|callflow|solve`; steps can attach E/F

### 0.5 Timeline summary
Link to `timeline.md` or embed the 3–10 key appended entries

---

---

## 0.6 Vendor structure overlay (professional vendor report structure)

> Full rules: `references/vendor-report-rules.md` (Issue #65)  
> **MUST** read it and choose a type when producing a formal security report; **take only the structure; copying vendor text/IOC instances is forbidden**.

| Flavor / Overlay | Scenario | Skeleton in one sentence |
|------------------|------|------------|
| `malware` | Clearly malicious samples/ordinary trojans/signed-binary sideloading | Huorong style: overview → flow → sample analysis → incident response → IOC |
| `apt` | APT/campaign/multi-stage chain | Kaspersky style: summary → infection chain → investigation → Interesting findings → technical analysis → detection and mitigation → IOC |
| `flavor = null` | Regular reverse engineering/pentest/CTF/JS signatures | The task template in this section + the applicable Base common elements |
| thin `vuln` | Vulnerability/patch/CVE technical analysis (explicit) | Overview → impact/reproduction → crash and patch analysis → protection advice |

**Common element (G1–G7) summary**: G1 executive summary MUST · G2 Scope MUST · G3 E/F/P MUST · G4 IOC MUST only for `malware`/`apt` · G5 recommendations MUST for `malware`/`apt`/`vuln` · G6 appendix SHOULD · G7 ATT&CK MUST for `apt`

Type choice and section order follow `vendor-report-rules.md`; on conflict with §0.1–0.5, **the Evidence contract wins**.

## 1. Reverse engineering report template

```markdown
# [Target name] Reverse Engineering Analysis Report

> Analysis date: YYYY-MM-DD
> Analyst: [AI / human]
> Toolchain: [jadx / IDA / radare2 / Frida / ...]

## 1. Target overview

| Attribute | Value |
|------|---|
| File name | |
| File type | APK / ELF / PE / Mach-O / ... |
| Size | |
| MD5 | |
| SHA256 | |
| Package name/entry | |

## 2. Analysis goals

<!-- The core questions this reverse engineering work must answer -->

## 3. Static analysis

### 3.1 Basic information
<!-- Architecture, compiler, protection mechanisms, string traits -->

### 3.1.1 Import table / dependencies (MUST for binaries)
<!-- Write the E-imports / E-triage-imports summary; record Evidence even on failure, skipping is forbidden -->

### 3.2 Key functions/classes
<!-- List the key logic located, with code snippets -->

### 3.3 Crypto/signing algorithms
<!-- If crypto is involved, state the algorithm, key source and parameter construction -->

## 4. Dynamic analysis

### 4.1 Hook records
<!-- Targets and results of Frida / xposed / other hooks -->

### 4.2 Runtime behavior
<!-- Network requests, file operations, process behavior -->

## 5. Core findings

<!-- List the key conclusions with numbers -->

1. ...
2. ...
3. ...

## 6. Reproduction steps

<!-- Let others reproduce your analysis results -->

```bash
# Key commands
```

## 7. Open questions

<!-- Points not fully resolved -->

## 8. Attachments

<!-- Hook scripts, decryption code, screenshots and similar -->
```

---

---

## 1b. Malware / APT report (vendor flavor)

When the task is malware analysis, a virus report or APT/campaign analysis, **do not** hand in only the "reverse engineering" skeleton above; regular reverse engineering tasks keep the original template and do not pick a vendor flavor automatically:

1. Read `vendor-report-rules.md` and choose `malware` or `apt`
2. Output in the matching section order
3. Still **MUST** contain the §0 Evidence chain; the `malware` / `apt` flavors also **MUST** contain the IOC table
4. Static analysis of binary samples **MUST** contain import table Evidence (consistent with the radare2/ida/malware hard gates)

## 1c. Vulnerability technical analysis report (thin `vuln` overlay)

When the task is an **OS/component vulnerability, patch comparison, CVE technical analysis**, or the user explicitly asks for a "vulnerability technical analysis report":

1. Read `vendor-report-rules.md` §3b and use the thin `vuln` section order (**not** the malware/apt full-text flavor)
2. **MUST** contain: impact scope, reproduction within authorization or an explicit n/a, crash/root cause or patch diff Evidence, protection/patch advice
3. **MUST** contain §0 Evidence→Finding→Path
4. **MUST NOT** extend the PoC against unauthorized targets or copy weaponization details of external exploits

## 2. Penetration test report template

```markdown
# [Target] Penetration Test Report

> Test date: YYYY-MM-DD
> Test scope: [URL / IP / application name]
> Authorization status: [authorized / CTF / learning environment]

## 1. Executive summary

<!-- One paragraph: what was tested, what was found, risk level -->

## 2. Test scope

| Item | Details |
|------|------|
| Target | |
| Test type | Black box / gray box / white box |
| Test time | |
| Tools | |

## 3. Findings summary

| # | Vulnerability name | Risk level | Status |
|---|---------|---------|------|
| 1 | | High/medium/low/info | Verified/pending confirmation |

## 4. Vulnerability details

### 4.1 [Vulnerability name]

**Risk level**: high / medium / low

**Description**:

**Impact**:

**Reproduction steps**:

1. ...
2. ...
3. ...

**Evidence**:

```
<!-- Request/response/screenshot/payload -->
```

**Fix recommendation**:

## 5. Attack path

<!-- If there is a complete attack chain, draw the path -->

```
Entry → information gathering → exploitation → privilege escalation → goal reached
```

## 6. Tools and environment

| Tool | Version | Purpose |
|------|------|------|
| | | |

## 7. Summary of fix recommendations

| Priority | Recommendation |
|--------|------|
| P0 | |
| P1 | |
| P2 | |

## 8. Appendix

<!-- Complete payloads, scripts, configuration files and similar -->
```

---

## 3. CTF writeup template

```markdown
# [Competition] - [Challenge] Writeup

> Category: Web / Reverse / Pwn / Crypto / Misc / Forensics
> Difficulty: Easy / Medium / Hard
> Points: N pts
> Solve time:

## Challenge description

<!-- Original challenge description -->

## Approach

### Step 1: information gathering
<!-- What was observed -->

### Step 2: vulnerability/breakthrough point
<!-- What key point was found -->

### Step 3: exploitation
<!-- How it was exploited -->

## Key code/payload

```python
# exploit code
```

## Flag

```
flag{...}
```

## Pitfall record

<!-- Detours taken -->

## Knowledge points

<!-- Knowledge points this challenge involves, for later review -->
```

---

## 4. JS/web signature reverse engineering report template

```markdown
# [Site/application] Signature Parameter Reverse Engineering Report

> Analysis date: YYYY-MM-DD
> Target endpoint: [URL]
> Signature field: [field name]

## 1. Target request

```http
POST /api/xxx HTTP/1.1
Host: example.com

param1=xxx&sign=<target field>
```

## 2. Locating process

### 2.1 Breakpoint/hook method
<!-- How the signature generation point was found -->

### 2.2 Call stack
<!-- Key call chain -->

## 3. Algorithm reconstruction

### 3.1 Algorithm type
<!-- HMAC-SHA256 / AES / custom / ... -->

### 3.2 Parameter construction
<!-- Which fields take part in the signature, ordering rules, separators -->

### 3.3 Key source
<!-- Hard-coded / returned by an API / derived from a timestamp / ... -->

## 4. Local reproduction code

```javascript
// Node.js reproduction
```

## 5. Verification result

<!-- Compare the signature generated by the reproduction code with the real request -->

## 6. Anti-scraping/risk control notes

<!-- Rate limits, device fingerprints, environment detection and similar -->
```

---

## 5. Document output standard

### Output location

- Documents go to the **user's current project directory** by default (not the skill package directory)
- File name format: `YYYY-MM-DD_[type]-[target short name]-report.md`
- If the user's project has a `docs/` directory, prefer placing it under `docs/`

### When to output

The AI calls this skill automatically to produce documentation at these moments:

1. A reverse engineering task completes with core conclusions
2. A penetration test completes with vulnerabilities found and verified
3. A CTF challenge is solved and the flag obtained
4. The user explicitly asks to "write a report/document"

### Quality requirements

- Every code block must run directly or have clear context
- No placeholders/TODOs (if a part really is unfinished, mark it "to be completed" and explain why)
- Key findings must be backed by evidence (command output, screenshot description, code snippets)
- Reproduction steps must let a third party reproduce independently
