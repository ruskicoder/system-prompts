# reverse-skill In-Package Security Audit (Executable Surface)

> 2026-09-03 re-review: extended to Git objects, payload identity, symlinks, the binary allowlist, GitHub Action pinning and Gradle Wrapper validation. See [Repository security review - 2026-09-03](SECURITY-REVIEW-2026-09-03.md).

> Date: 2026-08-02
> Scope: executable scripts and bootstrap manifests in `skills/**/scripts`, `skills/scripts`, `kali/scripts`, `burp-mcp-full`  
> **Excludes**: **teaching payload documents** such as `src-hunter` / payloader (their DROP and injection samples are methodology and are not executed automatically)

## Conclusion (overall)

| Level | Verdict |
|------|------|
| **Backdoor / active database deletion / disk formatting** | **Not found** |
| **Piped download and execute (curl\|sh / IEX DownloadString)** | **Not found** |
| **Hardcoded cloud keys / private keys** | **Not found** (the `sk-` / `BEGIN RSA` in documents are detection examples) |
| **Residual supply chain risk** | **Partly hardened (medium-low to low)**: `@latest` pinned; GitHub downloads support **manifest SHA256 + API digest** |

**Overall: the executable skill script surface currently shows no planted backdoor or "one-click database deletion" logic; dangerous deletions are limited to temporary tool reinstall directories and case output directories.**

### 2026-07-18 hardening (this commit)

| Item | Action |
|----|------|
| jshookmcp | `@latest` → `@0.3.4` |
| pentestswarm | `@latest` / docker `:latest` → `@v0.1.0` / `:v0.1.0` |
| jadx | pin `v1.5.6` + `assetSha256` |
| apktool | pin `v3.0.2` + `assetSha256` |
| bootstrap PS/sh | After download, `Assert-DownloadedFileIntegrity` / `verify_sha256`; manifest hash first, then the GitHub `digest`; on failure delete the file and abort |
| Releases without a pinned hash | Still installable, but print a **WARN** with the actual sha256 |

### 2026-08-02 security fixes

| Item | Fix |
|----|------|
| Kali quick setup | Resolve the sudo user home with `getent`, removed `eval` |
| Frida process listing | Use a `frida-ps` argument array, removed inline Python code concatenation |
| Burp MCP token | Atomic replacement through a restricted temporary file, POSIX file permissions fixed to `0600` |
| Burp MCP bridge | Parse MCP newline-delimited messages and reconnect on demand after Burp starts |
| Anything Analyzer MCP | bootstrap enables bearer auth by default and registers the credential through an optional host adapter |
| IDA MCP startup | End old processes one by one to avoid multi-PID argument expansion errors |

## Scan method

Search the executable extensions (`.ps1` / `.sh` / `.py` / `.js` / `.java`) for:

- `Invoke-Expression` / `IEX` / `FromBase64String` / `DownloadString`
- `curl|bash` / `wget|sh` piped execution
- `DROP DATABASE|TABLE`, `rm -rf /`, `Remove-Item ... C:\Windows`
- Reverse shell shapes (abuse of `/dev/tcp`, `TcpClient` connect-back)
- Hidden window starts (review the purpose)

Second round: manual reading of the download and delete paths in `bootstrap-reverse.ps1/.sh`, `mcp-bridge.js`, and the diagram and cryptography Python scripts.

## Findings

### 1. Delete operations (all expected cleanup, not database deletion)

| Location | Behavior | Risk |
|------|------|------|
| `bootstrap-reverse.ps1` `Expand-ArchiveIntoDirectory` | Deletes the target install directory before reinstalling; deletes `%TEMP%\reverse-bootstrap-*` | Tool install paths only, not user business data |
| `bootstrap-reverse.ps1` anything-analyzer | On failure `Remove-Item node_modules`, then `pnpm install` | Limited to the cloned tool repository |
| `apk-reverse/scripts/decode.*` | Cleans the jadx/apktool out directories of the task output | Limited to the task root |
| `case-init.ps1` | Cleans temporary directories | Temporary |
| `bootstrap-reverse.sh` | Same kind of temp and install target cleanup | Same as left |

**No** executable `DROP`/`TRUNCATE` logic against `C:\`, system directories or arbitrary database connection strings was **found**.

### 2. Network behavior (tool bootstrap, not C2)

| Location | Behavior | Notes |
|------|------|------|
| `bootstrap-reverse.ps1` | `api.github.com` fetches releases; `Invoke-WebRequest` downloads zip/jar | Repository names come from the **manifest allowlist** |
| `bootstrap-reverse.sh` | `curl` / `git clone` / `pipx` / `npm` | Same as above |
| `mcp-bridge.js` | Only `127.0.0.1:9876` HTTP to Burp | Local loopback |
| `ToolDiscovery.ps1` | Probes `http://host:port/mcp` | Health check |
| `kali/.../tool-discovery.sh` | `(echo >/dev/tcp/$host/$port)` | **Port probe**, not a reverse shell |

### 3. Hidden windows

| Location | Purpose |
|------|------|
| `bootstrap-reverse.ps1` `Start-Process ... -WindowStyle Hidden` | Starts `pnpm dev` in the background (anything-analyzer) |
| `ida-reverse/scripts/start.ps1` | Starts IDA-related processes (must stay in the background) |

These are service start patterns; no hidden download of malicious payloads was found.

### 4. "Dangerous words" in documents and payloads (not executed automatically)

**Markdown/JSON teaching material** such as `pentest-tools/src-hunter` and `attack-chain` contains SQL injection, `DROP` examples and log cleanup **red team methodology**.  
**Bootstrap and master-route never execute these automatically**; execution depends on an AI or a person choosing them inside an **authorized scope**.

Related constraints: `ops/scope-contract.md`, `ops/skill-supply-chain.md`, `field-journal/precedent-*.md`.

### 5. Residual supply chain risk (recommended future hardening, not a proven backdoor)

| Item | Risk | Recommendation |
|----|------|------|
| `@jshookmcp/jshook@0.3.4`, `pentestswarm@v0.1.0` in `bootstrap-manifest.json` | Tag drift / supply chain poisoning surface | Pin version numbers + checksums |
| GitHub release zip **without SHA256 verification** | A replaced release is hard to detect in time | Add `assetSha256` to the manifest and verify it in bootstrap |
| `npm install -g` / `pip` default sources | Inherent ecosystem dependency risk | Install only manifest capabilities; use private sources or lockfiles in production |

## Executable script inventory (audit baseline)

```
skills/scripts/*.ps1|*.sh + lib/ToolDiscovery.ps1
skills/apk-reverse/scripts/*
skills/radare2/scripts/*
skills/ida-reverse/scripts/*
skills/browser-automation/scripts/*
skills/diagram-generator/scripts/*.py
skills/case-review/scripts/*.py
kali/scripts/*
burp-mcp-full/mcp-bridge.js (+ Java extension source)
```

## Recommended ongoing checks

```powershell
# Quick health check of the executable surface (example)
rg -n "Invoke-Expression|FromBase64String|DownloadString|rm -rf /|DROP DATABASE" skills/scripts skills/*/scripts kali/scripts burp-mcp-full -g "*.ps1" -g "*.sh" -g "*.py" -g "*.js"
```

Before **executable scripts** of a new skill are merged, rerun this checklist; Markdown-only methodology changes do not require it.

## Sign-off

- Audit performed by: local static scan of the repository + manual review of key paths  
- Result: no backdoor / no automatic database deletion; supply chain hardening is listed as a follow-up improvement  
