# Project Experience Index

> This file is for quickly searching past experience before a new task starts.
> Entries marked `[seed]` are preset reference cases and do not count as real completed projects.
> Real projects use date file names (for example `2026-05-16_*`); seed cases use `seed-*`.

## Statistics

- Real projects: 37
- Seed references: 17
- Total entries: 54
- Last updated: 2026-11-11

## By scenario

### APK / Android reverse engineering

- [2026-10-09 Offline licensing chain and embedded payload analysis of an Android APK](./2026-10-09_android-apk-offline-auth-flow.md)
- [2026-09-29 Comment targets and re-signed launch controls in an old Android client; keywords: native business identity, comment type mapping, signing control, real device acceptance boundary](./2026-09-29_android-native-comment-identity-signing-control.md)
- [2026-09-20 Full recovery of the iJiami packer dyncryptor RC4 variant + zlib decryption chain](./2026-09-20_ijiami-dyncryptor-rc4-variant-zlib-recovery.md)
- [2026-08-20 Removing server-driven ads from Flutter AOT (Blutter + equal-length string replacement)](./2026-08-20_apk-flutter-banner-ad-removal.md)
- [2026-05-15-cellular-pro-mumu-ksad-fragment-fix](./2026-05-15-cellular-pro-mumu-ksad-fragment-fix.md)
- [[seed] seed-008_apk-okhttp-ssl-pin-bypass](./seed-008_apk-okhttp-ssl-pin-bypass.md)

### Binary / firmware / CTF

- [2026-09-07 Static teardown of a Famicom Namco-163 strategy RPG ROM (iNES mapper19 / 6502 / recursive tracer / N163 audio / startup hardware check / stdlib CHR→PNG)](./2026-09-07_famicom-namco163-strategy-rom-teardown.md)
- [2026-09-17 Two-stage "wrapper + encrypted payload" structure of a Mir2-family thick client](./2026-09-17_mir2-thick-client-wrapper-encrypted-payload.md)
- [2026-09-29 Static triage of a stripped Go EXE + rustc native DLL (pclntab recovery, PE exports, Ghidra headless)](./2026-09-29_stripped-go-pclntab-rust-dll-triage.md)
- [2026-10-16 Full logic recovery of a Go+Wails usage dashboard (stripped, no symbols: manual pclntab/functab + byte-level string recovery)](./2026-10-16_wails-go-usage-dashboard-stripped-re.md)
- [2026-11-11 Static mapping of a heavily packed Windows PE (virtual sections / full-entropy payload / decoy IAT / entropy map)](./2026-11-11_windows-pe-packed-entropy-map.md)
- [2026-08-06_cortex-m-msc-firmware-self-keyed-rotate-xor](./2026-08-06_cortex-m-msc-firmware-self-keyed-rotate-xor.md)
- [2026-07-22 Analysis of an Electron Bytenode privileged update chain](./2026-07-22_electron-bytenode-privileged-update-chain.md)
- [2026-07-14_android-arm64-self-extract-source-recovery](./2026-07-14_android-arm64-self-extract-source-recovery.md)
- [2026-05-15_lumine-go-reverse](./2026-05-15_lumine-go-reverse.md)
- [[seed] seed-001_elf-packed-loader](./seed-001_elf-packed-loader.md)
- [[seed] seed-002_go-malware-stripped](./seed-002_go-malware-stripped.md)
- [[seed] seed-010_ctf-pwn-rop-x64](./seed-010_ctf-pwn-rop-x64.md)
- [[seed] seed-011_pcap-protocol-reverse](./seed-011_pcap-protocol-reverse.md)
- [[seed] seed-014_unity-il2cpp-reverse](./seed-014_unity-il2cpp-reverse.md)
- [[seed] seed-015_iot-firmware-uart](./seed-015_iot-firmware-uart.md)

### Web / API / penetration testing

- [2026-10-30 Passive reconnaissance of an encrypted API envelope site and a play-money rebuild; keywords: offline AES envelope decoding, polling to STOMP push, provably fair, multi-agent rebuild, audience/scope separation](./2026-10-30_js-encrypted-envelope-exchange-playmoney-rebuild.md)
- [2026-08-01 Contract-faithful local reconstruction of a Next.js CDK](./2026-08-01_nextjs-cdk-contract-faithful-local-reconstruction.md)
- [2026-08-01_pentest-encryption-oracle-public-template-sql-admin-takeover: .NET CMS generic encryption oracle, public ciphertext template consumer, complete STL/template parsing, raw SQL `UPDATE RETURNING`, official administrator verifier old/new password differential and isolated PostgreSQL cleanup loop](./2026-08-01_pentest-encryption-oracle-public-template-sql-admin-takeover.md)

- [2026-07-18_gin-juice-client-friction](./2026-07-18_gin-juice-client-friction.md)
- [2026-07-05_dsl-vm-captcha-reverse](./2026-07-05_dsl-vm-captcha-reverse.md)
- [2026-06-29_burp-mcp-full-test-and-fix](./2026-06-29_burp-mcp-full-test-and-fix.md)
- [2026-05-26_pentest-newapi-rate-limit-bypass](./2026-05-26_pentest-newapi-rate-limit-bypass.md)
- [2026-05-25_pentest-cf-access-sibling-subdomain-cookie-poisoning](./2026-05-25_pentest-cf-access-sibling-subdomain-cookie-poisoning.md)
- [2026-05-17_pentest-vue-spa-actuator-leak](./2026-05-17_pentest-vue-spa-actuator-leak.md)
- [2026-05-16_pentest-personalblog-fun-mass-assignment](./2026-05-16_pentest-personalblog-fun-mass-assignment.md)
- [[seed] seed-003_web-api-auth-bypass](./seed-003_web-api-auth-bypass.md)
- [[seed] seed-004_js-sign-webpack](./seed-004_js-sign-webpack.md)
- [[seed] seed-006_ssrf-cloud-metadata](./seed-006_ssrf-cloud-metadata.md)
- [[seed] seed-017_xxe-oob-exfil](./seed-017_xxe-oob-exfil.md)

- [2026-10-16 Using CDP to get the runtime evidence Playwright cannot (initiator call stack / arguments at breakpoints)](./2026-10-16_cdp-runtime-recovery-vs-playwright.md)
- [2026-10-16 Fidelity verification of a 1:1 replica needs three layers: implementation present → values consistent → **response structure consistent** (only the third layer caught field-level differences)](./2026-10-16_fidelity-verification-layering.md)
### Enterprise intranet / cloud security

- [[seed] seed-005_ad-certipy-esc1](./seed-005_ad-certipy-esc1.md)
- [[seed] seed-007_ntlm-relay-coercer](./seed-007_ntlm-relay-coercer.md)
- [[seed] seed-013_kerberoasting-spn](./seed-013_kerberoasting-spn.md)
- [[seed] seed-016_k8s-container-escape](./seed-016_k8s-container-escape.md)

### iOS reverse engineering

- [[seed] seed-009_ios-jailbr&#101;ak-detect-bypass](./seed-009_ios-jailbr%65ak-detect-bypass.md)

### Toolchain and environment

- [2026-09-03 Security boundary integration of multiple issues/PRs](./2026-09-03_issue-pr-security-boundary-integration.md)
- [2026-08-17 tool-index r2 fallback and unified powershell/pwsh child process entry](./2026-08-17_tool-index-r2-fallback-powershell-pwsh-host-fix.md)
- [2026-08-14 Review of a PR on Windows PowerShell native command exit codes](./2026-08-14_windows-powershell-native-exit-code-pr-review.md)
- [2026-08-08 Client-neutral structured routing PR integration](./2026-08-08_client-neutral-structured-routing-pr-integration.md)
- [2026-07-20_reverse-toolchain-windows-bootstrap](./2026-07-20_reverse-toolchain-windows-bootstrap.md)

- [2026-10-16 Chinese text directly adjacent to ASCII keywords breaks the \b word boundary (the .NET and Python engines are both affected)](./2026-10-16_cjk-adjacent-ascii-word-boundary-routing-failure.md)
- [2026-10-16 Triple transport layer pitfall when accessing overseas APIs from within China (Node fetch ignores the proxy / CF fingerprint / execFile corrupting UTF-8 through GBK)](./2026-10-16_cn-network-transport-triple-trap.md)
- [2026-10-16 Tool index .md/.json dual-copy drift, PowerShell 5.1 property assignment rollback, triple line ending pitfall](./2026-10-16_tool-index-dual-desync-and-scripting-traps.md)
- [2026-10-16 Six kinds of silent failure in a CDP forensics tool (navigation resets the Debugger domain / low script count raises no alarm / options not wired)](./2026-10-16_cdp-tooling-timing-and-option-traps.md)
- [2026-10-16 Operational pitfalls of CDP debugging sessions (temporary profile cleaned, login state lost / port LISTENING ≠ CDP)](./2026-10-16_cdp-session-profile-and-port-pitfalls.md)
### Other

- [2026-08-08 Open PR value triage and safe integration](./2026-08-08_pr-value-triage-and-safe-integration.md)
- [[seed] seed-012_log4shell-jndi-rce](./seed-012_log4shell-jndi-rce.md)

## Frequent success patterns (by technique)

### Client-neutral routing and supply chain gates

- [Isolated worktree, multi-PR ancestor loop, Git-blob AV review and the reference/executable CI boundary](./2026-09-03_issue-pr-security-boundary-integration.md)
- [Unified Resolve-ReverseHostExe child process entry, r2 .bat fallback, StrictMode-safe hashtable access](./2026-08-17_tool-index-r2-fallback-powershell-pwsh-host-fix.md)
- [Save the exit code right after the native command, reproduce on a real Windows PowerShell 5.1 host, pin the PR head](./2026-08-14_windows-powershell-native-exit-code-pr-review.md)
- [Single routing.json, multi-entry parity, pinned actual install commands](./2026-08-08_client-neutral-structured-routing-pr-integration.md)

### Custom firmware wrapping

- [1 KiB self-masked ROR/XOR, Cortex-M vector crib, cross-firmware verification](./2026-08-06_cortex-m-msc-firmware-self-keyed-rotate-xor.md)

### Cross-engine text matching and word boundaries

- [\b fails when CJK sits against ASCII, hitting .NET and Python alike; the "no space" coverage blind spot of benchmark cases](./2026-10-16_cjk-adjacent-ascii-word-boundary-routing-failure.md)

### Transport layer for accessing overseas APIs from within China

- [curl as the transport layer: reads the system proxy, passes the CF fingerprint, body through a temporary file to avoid GBK corrupting Chinese, windowsHide against pop-ups](./2026-10-16_cn-network-transport-triple-trap.md)

### Browser runtime forensics (direct CDP)

- [initiator.stack recovers the call origin, breakpoints in minified scripts need columnNumber, the order of enable and listeners](./2026-10-16_cdp-runtime-recovery-vs-playwright.md)

### Index and inventory consistency

- [Multi-format indexes must be checked item by item; PowerShell PSCustomObject property existence guard; binary read/write preserves line endings](./2026-10-16_tool-index-dual-desync-and-scripting-traps.md)

### Silent failures and cross-cutting capabilities

- [Collection operations need quantity plausibility checks; cross-cutting capabilities (navigation/triggers/logging) belong in a unified entry, not wired command by command](./2026-10-16_cdp-tooling-timing-and-option-traps.md)

### Operating browser debugging sessions

- [Do not put the profile in a temporary directory; port LISTENING ≠ CDP, check the Browser field with curl /json/version](./2026-10-16_cdp-session-profile-and-port-pitfalls.md)

### Replica fidelity acceptance

- [Three-layer verification: does it exist → is it right → **does it look the same**; the third layer needs real interface calls, GET only](./2026-10-16_fidelity-verification-layering.md)
### Android packer custom decryption chain

- [Manual dex overlay parsing + RC4 variant KSA/PRGA recognition + zlib decompression (iJiami dyncryptor)](./2026-09-20_ijiami-dyncryptor-rc4-variant-zlib-recovery.md)
### Triage of stripped Go / Rust binaries

- [pclntab function name recovery (no GoReSym), `go version -m` metadata, script parsing of the PE export table, Ghidra headless Java postScript](./2026-09-29_stripped-go-pclntab-rust-dll-triage.md)
### Go stripped symbol recovery and logic recovery

- [Manual pclntab/functab recovery (GoReSym failure branch), exact LEA+len string pairing, time constant triangulation](./2026-10-16_wails-go-usage-dashboard-stripped-re.md)
### Encrypted API envelopes and real-time protocol rebuilds

- [Locate the key in preamble code then decode offline, per-topic seq + bounded replay + REST snapshot, after-commit publishing](./2026-10-30_js-encrypted-envelope-exchange-playmoney-rebuild.md)

## Entity inverted index (by target feature)

### Wails v2 / Go-stripped Windows desktop applications

- [Recovering the Wails bindings/events interface surface, recognizing the OSCrypt (DPAPI+AES-GCM) credential chain, SQLite incremental scan position model](./2026-10-16_wails-go-usage-dashboard-stripped-re.md)

### Multi-host security skill routing package

- [Core/adapter boundary and selective integration of a large PR](./2026-08-08_client-neutral-structured-routing-pr-integration.md)

### Windows PowerShell supply chain bootstrap scripts

- [Unified powershell/pwsh child process entry, tool-index .bat fallback, pin gate StrictMode](./2026-08-17_tool-index-r2-fallback-powershell-pwsh-host-fix.md)
- [Exit codes distorted after native command output passes through the object pipeline](./2026-08-14_windows-powershell-native-exit-code-pr-review.md)

### Cortex-M USB MSC updater

- [Application/resident bootloader boundary and the virtual disk write chain](./2026-08-06_cortex-m-msc-firmware-self-keyed-rotate-xor.md)

### Local reverse engineering skill routing package (including localization fixes and execution layer bridging)

- [Chinese boundary defect in routing rules, R3 keyword gap and paired benchmark cases](./2026-10-16_cjk-adjacent-ascii-word-boundary-routing-failure.md)
- [Tool index dual-copy drift and PowerShell traps in the registration script](./2026-10-16_tool-index-dual-desync-and-scripting-traps.md)

### Bundled SPA (no source map)

- [CDP recovers runtime call stacks and breakpoint arguments](./2026-10-16_cdp-runtime-recovery-vs-playwright.md)

### In-house CDP forensics toolchain

- [Navigation resets the Debugger domain, low script counts are silently incomplete, valued options not registered (the same pitfall hit three times)](./2026-10-16_cdp-tooling-timing-and-option-traps.md)
- [Debugging profile cleaned from the temporary directory and the login state lost, 9222 held by the everyday Chrome causing a wrong verdict](./2026-10-16_cdp-session-profile-and-port-pitfalls.md)

### 1:1 website replica acceptance

- [Response structure differential: missing fields are invisible while the "implemented" and "values right" layers are both green](./2026-10-16_fidelity-verification-layering.md)
### iJiami packed APK

- [dyncryptor overlay manifest structure + RC4 variant stepping (i+=2 / j+=state[i]+1) + zlib to EOF](./2026-09-20_ijiami-dyncryptor-rc4-variant-zlib-recovery.md)
### Stripped Go EXE + rustc native DLL

- [pclntab function name recovery, Ghidra identifies rustc, native export RVAs/VAs](./2026-09-29_stripped-go-pclntab-rust-dll-triage.md)
### Sports exchange + live card table site (Angular front end, AES envelope API, score socket)

- [Public passive observation only; rebuild with an own brand and virtual chips, real-time control from the back office](./2026-10-30_js-encrypted-envelope-exchange-playmoney-rebuild.md)
### Windows commercial protection packer PE

- [Memory-restoring packer: 6 RawSize=0 sections + 60 MiB full-entropy payload + code block mapping table](./2026-11-11_windows-pe-packed-entropy-map.md)

## Usage

1. Before a new task starts, search by scenario category for similar records.
2. When a real project matches, reuse its verified flow and pitfall records first.
3. When a seed case matches, use it only as a method reference, not as a real success record.
4. After adding experience, update this index through the PR flow instead of changing the shared mainline directly.
