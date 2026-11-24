# 2026-07-22 Analysis of an Electron Bytenode Privileged Update Chain

## Scenario classification

Binary analysis / Electron / Bytenode / update chain security audit

## Target overview

Completed a cross-layer reverse engineering of a Windows x86 Electron desktop application, from the NSIS installer, ASAR and Bytenode JSC to the native game SDK and the remotely rendered pages, confirming the privilege boundary, IPC capabilities and the update package trust model.

## Complete execution chain

1. Checked the SHA-256, Authenticode, manifest, sections, overlay and mitigations of the outer `{electron_app}` PE to confirm the installer type and elevation level.
2. Unpacked the NSIS read-only with 7-Zip, located the inner archive and rebuilt the file list; then extracted the original `app.asar`, keeping logical offsets, sizes and per-file hashes.
3. Identified Electron 22.0.0, Node 16.17.1 and Bytenode 1.5.7 from `package.json`, runtime resources and JSC strings; separated the original extraction directory from an existing modified directory.
4. Loaded `main.jsc` and `preload.jsc` in the `ELECTRON_RUN_AS_NODE=1` mode of the Electron shipped with the sample, solving the host Node/V8 ABI incompatibility.
5. Mocked Electron, network, file writes, archives, FFI, child processes and exit in the probe; recorded window options, 21 main-process IPC handlers, 29 preload bridge members and lifecycle callbacks.
6. Froze a static resource snapshot of `{remote_ui_domain}` and traced how the `updateUrl` returned by `https://{update_api_domain}/api/user/v1/check_ver` reaches the local `checkUpdates`.
7. Drove the update handler with a loopback HTTP fixture, confirming the URL acceptance, download, extraction and detached updater launch sequence; recorded the absent allowlist, hash, package signature and Authenticode checks each as "not observed in the controlled path".
8. Statically rechecked the exports, imports, strings, PE protections, signatures and key addresses of `{native_game_sdk}`, separating ABI forwarding, the callback FIFO, the state watchdog and the third-party platform install branch.
9. Used "conditional capability" wording for service, driver, hosts, root certificate, proxy and platform registry operations; capabilities are described only where call chain evidence exists, without inferring that this run executed them.
10. Produced the formal report, three data flow diagrams, structured IOCs, reproduction commands and an evidence index, and in the conclusion separated high-confidence static facts, controlled dynamic facts and the freshness boundary of the remote snapshot.

## Pitfall record

| Problem | Cause | Solution | Time |
|---|---|---|---|
| Loading JSC directly in the host Node failed | Bytenode bytecode is bound to a specific V8/Node ABI | Run in the RunAsNode mode of the sample's Electron | Medium |
| Timers and exit logic interfered with the results after starting the probe | The main process contains lifecycle callbacks, a watchdog and `process.exit` | Added `--run-timeouts` and mocked timers, exit and four kinds of app callbacks | Medium |
| The update handler must trigger network, disk write and child process paths at once | Enumerating handlers only proves registration, not data flow | Added an `--update-url` fixture that records parameters and side effects across the whole chain | Medium |
| The analysis directory contained existing modified artifacts | A modified ASAR/JSC would contaminate the original conclusions | Treat only `{sample_dir}` and `{extracted_original_dir}` as original evidence sources | Low |
| The status of dual-signed DLLs is easy to misjudge | Each signature's certificate, timestamp and current verification status may differ | Check each signature with `signtool verify /pa /all /v` | Low |
| Native strings show high-privilege system capabilities | Strings and imports do not mean the current path executed them | Combine with xrefs/call chains and mark them "conditional capability" | Medium |
| The remote UI keeps changing | The current chunks and API behavior are not permanently fixed assets | Save a dated resource snapshot, hashes and fetch time | Low |

## Toolchain findings

- The Electron shipped with the sample is the most stable ABI container for running Bytenode JSC; `ELECTRON_RUN_AS_NODE=1` runs the probe without starting the business GUI.
- Electron module mocks must cover `app.whenReady/on/quit`, `BrowserWindow`, `ipcMain.handle/on`, `shell`, `session` and `webContents`, otherwise only an incomplete registration surface appears.
- Update chain verification should record the input URL, request library, target file, extraction directory and final `spawn` arguments together to close the evidence loop from renderer to updater.
- PE signature audits should describe "certificate present", "certificate within its validity period", "trusted timestamp present" and "current chain verification succeeds" separately.
- For large third-party DLLs, partition capabilities by imports/exports and strings first, then recheck high-risk branches such as services, network, certificates and process creation at address level.

## Key code/commands

```powershell
$env:ELECTRON_RUN_AS_NODE = '1'
$env:__COMPAT_LAYER = 'RunAsInvoker'

& '{electron_exe}' '{probe_script}' '{main_jsc}' `
  --execute --exercise=all --run-timeouts --quiet `
  --out='{main_probe_json}'

& '{electron_exe}' '{probe_script}' '{main_jsc}' `
  --execute --exercise=all --run-timeouts `
  --update-url='http://127.0.0.1:{port}/update.zip' --quiet `
  --out='{update_probe_json}'

& '{electron_exe}' '{probe_script}' '{preload_jsc}' `
  --execute --exercise=bridge --quiet `
  --out='{preload_probe_json}'

signtool verify /pa /all /v '{native_game_sdk}'
```

## Improvement suggestions for this package

1. Add a Bytenode ABI decision tree to the Electron/JS reverse engineering route: after the host Node fails, prefer the RunAsNode mode of the target's Electron.
2. Add a general Electron mock coverage matrix and an IPC registration/call consistency check script.
3. Fix the checks in the updater audit template: URL constraints, transport protocol, manifest signature, package hash, signature chain, extraction traversal and final execution arguments.
4. Add mandatory separate columns for "conditional capability" and "observed behavior" to the report template, lowering the risk of over-inferring from imports/strings.

## Reusable patterns/script snippets

1. **Three trust boundaries**: original installer -> original ASAR/JSC -> remote page snapshot, each with its own hashes and timestamps.
2. **Separate the registration surface from the execution surface**: enumerate IPC/preload APIs first, then call high-risk handlers with mock fixtures and capture side effects.
3. **Update chain five-tuple**: `source URL -> downloader -> archive path -> extractor -> executable`, with evidence kept for every node.
4. **Native capability grading**: imports/strings are leads, xrefs/call chains are capability evidence, and only real dynamic events count as executed facts.
5. **Four-state signature model**: report signature presence, certificate validity period, timestamp and current trust verification separately.

## Evolution actions

- [x] Added pitfall records
- [x] Updated the experience index
- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation

## Environment information

- OS: Windows 11 x64
- Tool versions: Electron 22.0.0, Node 16.17.1, Bytenode 1.5.7, Python 3.12
- Target platform/version: Windows x86 / Electron desktop app

## Redaction requirements

This document keeps only general versions, API path structures, orders of magnitude and analysis methods. Sample names, publishers, real domains, case directories, hashes, configuration keys, tokens and user identifiers are replaced or omitted; no sample file is attached.

---
<!-- [Community contribution] When done, ask the user whether to open a PR to the main repository. The process is in CONTRIBUTE-BACK.md -->
