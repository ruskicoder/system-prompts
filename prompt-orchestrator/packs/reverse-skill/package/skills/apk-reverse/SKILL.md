---
name: apk-reverse
description: Use for Android APK reverse engineering in a CLI environment. Covers APK unpacking, Java decompilation, smali modification, repackaging, Frida dynamic hooking, and switching to so/native analysis when needed. Prefer the locally installed jadx, apktool, frida, adb, ida-reverse and radare2.
---

## ACTION REQUIRED (execute right after reading)

> Community comparison for endpoint extraction, adaptive Frida and similar: ../references/community-security-skills.md; dynamic analysis requires a device authorized in scope.

1. `NOW`: read `../field-journal/precedent-reverse.md` to confirm that this skill's operations are authorized routine operations
2. `NOW`: confirm whether the current task falls within the scope of this skill
3. `NEXT`: read `../tool-index.md` and verify tool availability and actual paths
4. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
5. `ACT`: enter step one of the "Workflow" and execute it; do not stop at confirmation

# APK Reverse Engineering CLI Work Standard

## Scope

Prefer this skill when the task falls into one of these scenarios:

- Analyze the Java business logic of an APK
- Locate login, signing, risk control, certificate checks, root detection
- View and modify `AndroidManifest.xml`
- View and modify smali
- Repackage the APK
- Use Frida for Java/native dynamic hooks
- Switch to native analysis when the APK contains a `.so`

## CLI tools verified on the current machine

- `jadx` `1.5.5`
- `apktool` `3.0.2`
- `frida-ps` `17.9.6`
- `adb`
- `java`

## When to prefer the scripts

These flows are frequent and their parameters are easy to get wrong, so prefer the scripts bundled with the skill:

- Run `jadx + apktool` to disk and produce a summary in one pass: `scripts/decode.ps1`
- Frida device check, process listing, spawn/attach injection: `scripts/frida-run.ps1`
- Rebuild, align, sign and install the APK: `scripts/rebuild-sign-install.ps1`
- Quickly extract the key Manifest components and permissions: `scripts/manifest-summary.ps1`

These one-line commands stay as direct calls without a wrapper:

- `adb devices`
- `adb logcat`
- `frida-ps -U`
- `jadx --version`
- `apktool --version`

## Bundled scripts

### `scripts/decode.ps1`

Purpose:

- Run `jadx` and `apktool` together
- Create the task output directory next to the original APK by default
- Print a summary with `package`, `java_files`, `smali_dirs`, `so_files` and similar
- Tolerate `jadx` partial decompilation errors when usable output still exists

Example:

```powershell
pwsh -File "<skill-root>\apk-reverse\scripts\decode.ps1" -ApkPath "D:\DOWNLOAD\app.apk" -Clean
pwsh -File "<skill-root>\apk-reverse\scripts\decode.ps1" -ApkPath "D:\DOWNLOAD\app.apk" -Name demo -SkipJadx
```

### `scripts/frida-run.ps1`

Purpose:

- One entry point for Frida devices, processes and spawn/attach
- Avoid mixing up `-f`, `-n` and `-U` when writing parameters by hand

Example:

```powershell
pwsh -File "<skill-root>\apk-reverse\scripts\frida-run.ps1" -ListDevices
pwsh -File "<skill-root>\apk-reverse\scripts\frida-run.ps1" -Usb -ListProcesses
pwsh -File "<skill-root>\apk-reverse\scripts\frida-run.ps1" -Usb -Spawn -Package com.example.app -ScriptPath "D:\hooks\test.js"
```

### `scripts/rebuild-sign-install.ps1`

Purpose:

- `apktool b` rebuilds the APK
- `zipalign` alignment
- `apksigner` signing and verification
- Optional direct `adb install`

Example:

```powershell
pwsh -File "<skill-root>\apk-reverse\scripts\rebuild-sign-install.ps1" -ProjectDir "C:\work\apktool_out" -Clean
pwsh -File "<skill-root>\apk-reverse\scripts\rebuild-sign-install.ps1" -ProjectDir "C:\work\apktool_out" -Install -Reinstall -DeviceSerial "127.0.0.1:7555"
```

Notes:

- Generates and reuses a debug keystore by default
- Writes output next to `ProjectDir` by default, so it sits with the original package and the unpacked directory

### `scripts/manifest-summary.ps1`

Purpose:

- Extract the package name
- List permissions
- List activity/service/receiver/provider
- Mark the main launch activity

Example:

```powershell
pwsh -File "<skill-root>\apk-reverse\scripts\manifest-summary.ps1" -ManifestPath "C:\work\apktool_out\AndroidManifest.xml"
```

To analyze `.so`, `lib/arm64-v8a/*.so` or `lib/armeabi-v7a/*.so`, combine with:

- `ida-reverse`
- `radare2`

## Tool roles

### `jadx`

Used for:

- Reading Java decompilation
- Searching package, class and method names
- Understanding the APK from the high-level logic first

Common commands:

```bash
jadx -d jadx_out app.apk
jadx --single-class com.example.LoginActivity -d jadx_out app.apk
jadx --deobf -d jadx_out app.apk
```

### `JEB Pro` (optional commercial tool)

Used for:

- Cross-validation and deep decompilation of Android DEX / APK / ARM
- Additional static analysis when JADX output is incomplete or heavily obfuscated
- Second-toolchain verification of classes, methods and call relationships of the same target

Boundaries:

- JEB Pro is commercial software; the user must obtain and install a valid license; this package does not download, crack or circumvent the license.
- Call it only when `tool-index` confirms that JEB is available locally; otherwise keep using `jadx`, `apktool`, Ghidra, IDA or radare2.
- Third-party JEB MCP bridges are not a dependency of this package. Before installing one, review its source, permissions, network behavior and version per `../ops/skill-supply-chain.md`, and register it only after explicit user confirmation.

### `apktool`

Used for:

- Unpack the APK
- View and modify `AndroidManifest.xml`
- View and modify smali
- Rebuild the APK

Common commands:

```bash
apktool d app.apk -o apktool_out
apktool b apktool_out -o rebuilt.apk
```

### `frida`

Used for:

- Observe Java method calls dynamically
- Hook native exported functions
- Bypass root detection, certificate checks, debugger detection

Common commands:

```bash
frida-ps -U
frida -U -f com.example.app -l hook.js
frida-trace -U -f com.example.app -j '*!*certificate*'
```

### `adb`

Used for:

- Device connection
- Install the APK
- View logs
- Pull files

Common commands:

```bash
adb devices
adb install -r app.apk
adb shell pm list packages
adb logcat
adb pull /data/local/tmp/file .
```

## Recommended workflow

### 1. Triage

First determine the rough makeup of the APK; do not rush to modify the package or hook.

Suggested actions:

1. Export Java code with `jadx -d jadx_out app.apk`
2. Export smali and resources with `apktool d app.apk -o apktool_out`
3. Look first at:
   - `AndroidManifest.xml`
   - the main `package`
   - `application`, `activity`, `service`, `receiver`
   - whether the `lib/` directory holds any `.so`
4. Issue #65 threat pattern quick reference (authorized samples/devices; details in `../reverse-engineering/references/nonpe-format-cookbook.md` §7–8):
   - Transparent/hidden icon (AU): `aapt dump badging` + manifest theme/label/icon → `E-android-hidden-icon-manifest`
   - Magisk/script device-wipe signatures and remote curl|sh (AR/AS) → record the signatures and URLs as evidence, **do not execute** destructive commands
   - Persistence paths (AT): `service.d` / `priv-app` and similar → `E-android-persistence`

### 2. Java logic observation

Read `jadx_out` first:

- `MainActivity`
- `Application`
- Login, network, crypto and risk-control classes
- Third-party SDK initialization classes

Common keywords:

- `login`
- `sign`
- `encrypt`
- `cipher`
- `token`
- `root`
- `certificate`
- `trust`
- `okhttp`
- `retrofit`
- `webview`

If the Java code is readable, locate the business logic here first.

### 3. Smali and resource-layer confirmation

When the `jadx` result is incomplete, heavily obfuscated, or you need an actual patch, switch to `apktool_out`:

- Look at `smali*/`
- Look at `res/values/strings.xml`
- Look at `AndroidManifest.xml`

Patch these first:

- `android:exported`
- Debug flags
- Root detection return values
- Login verification logic
- Certificate check branches

### 4. Rebuild and install

After modification:

```bash
apktool b apktool_out -o rebuilt.apk
```

Or close the loop with the script:

```powershell
pwsh -File "<skill-root>\apk-reverse\scripts\rebuild-sign-install.ps1" -ProjectDir "apktool_out" -Install -Reinstall -DeviceSerial "127.0.0.1:7555"
```

Notes:

- This skill only guarantees the `apktool` rebuild chain
- To install on a device afterwards, a signing step is usually also needed
- If the task reaches signing/alignment, add `apksigner` / `zipalign`

### 5. Dynamic hooks

When static analysis is not enough, use Frida:

- Hook the login function
- Hook key points in `OkHttp` / `Retrofit` / `WebView`
- Hook `javax.crypto`, `MessageDigest`
- Hook the root detection function
- Hook the SSL pinning logic

Principles:

- Hook the Java layer first, then decide whether a native hook is needed
- Print arguments and return values first, then decide whether to modify return values

Suggestions:

- Use `frida-*` directly for simple one-off commands
- Prefer `scripts/frida-run.ps1` for injection flows that need stable reuse

### 6. Native `.so` branch

If the APK contains a key `.so`:

- Find `lib/**/*.so` with `apktool` or `jadx`
- For exported symbols, strings and quick triage only, `radare2` is enough
- For long-term deep analysis, decompilation, renaming and type recovery, use `ida-reverse`

Switch to native quickly on these signals:

- The Java layer is only a JNI wrapper
- The core signing logic is not in Java
- Key logic disappears after `System.loadLibrary()`
- Certificate checks/risk control live in the `.so`

## Output requirements

At minimum, the final output states:

- Entry components and key classes
- Whether the key logic is in Java, smali or the `.so`
- Confirmed sensitive points: login, signing, root, SSL, WebView, JNI
- If you patched, what you changed
- If you hooked, which class/method/exported function you hooked

## Prohibited

- Do not modify smali blindly at the start
- Do not write hooks before reading the manifest and the main entry
- Do not treat incomplete Java decompilation as "the logic cannot be analyzed"
- Do not keep grinding on the Java layer when the `.so` clearly carries the core logic

## Quick command notes

```bash
# Decompile Java
jadx -d jadx_out app.apk

# Unpack the APK
apktool d app.apk -o apktool_out

# Rebuild the APK
apktool b apktool_out -o rebuilt.apk

# Devices and processes
adb devices
frida-ps -U

# Spawn and inject
frida -U -f com.example.app -l hook.js
```

---

## Routing context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Downstream exits**:
- Core logic in the `.so` → `ida-reverse/` or `radare2/`
- Dynamic hook/verification needed → `reverse-engineering/tools-dynamic.md` (Frida section)
- General reverse engineering methodology → `reverse-engineering/SKILL.md`

**Sibling modules**: `reverse-engineering/` (.so analysis and advanced Frida usage)

---

## On-Demand Bootstrap

This skill's entry scripts are wired into the unified bootstrap system. A missing tool does not raise an error right away; the scripts try to install it automatically.

### Automation boundaries

| Tool | Auto-installable | Install method | Notes |
|------|-----------|---------|------|
| jadx | ✓ | GitHub Release ZIP | Downloads and extracts automatically to `%USERPROFILE%\Tools\jadx\` |
| apktool | ✓ | GitHub Release JAR + wrapper | Downloads the jar automatically and generates a bat in `%USERPROFILE%\Tools\apktool\` |
| JEB Pro | ✗ | User installs manually and supplies a valid license | Optional Android / ARM cross-validation tool; third-party MCP bridges need a separate audit |
| frida / frida-ps | ✓ | pip install frida-tools | Requires Python to be installed |
| adb | ✓ | winget / fallback path | Installs Android Platform-Tools automatically |
| zipalign | ✗ | Install Android Build-Tools manually | `sdkmanager "build-tools;35.0.0"` |
| apksigner | ✗ | Install Android Build-Tools manually | Same as above |

### Bootstrap trigger points

- `scripts/decode.ps1`: calls `bootstrap-reverse.ps1` automatically when jadx or apktool is missing
- `scripts/rebuild-sign-install.ps1`: calls bootstrap automatically when adb or apktool is missing
- `scripts/frida-run.ps1`: still checks manually for now (frida is usually already installed through pip)

### When bootstrap fails

If the automatic install fails, the script raises a clear error with a manual install link. Common causes:
- No network (GitHub API / PyPI unreachable)
- winget unavailable (Windows version too old)
- Java not installed (apktool depends on a JDK)


## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
- [ ] If hidden-icon/device-wipe/persistence clues appeared: did I record E-android-* Evidence per the U–AV cookbook (within the authorized scope)?
