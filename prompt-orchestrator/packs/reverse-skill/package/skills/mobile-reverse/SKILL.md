---
name: mobile-reverse
description: Use for authorized Android or iOS application reverse engineering and security testing, including APK or IPA analysis, runtime instrumentation, SSL pinning, and platform protection checks.
---
# Mobile Reverse Engineering

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md` to confirm that this skill's operations are authorized routine operations
2. `NOW`: confirm whether the current task falls within the scope of this skill
3. `NEXT`: read `../tool-index.md` and verify tool availability and actual paths
4. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
5. `ACT`: enter step one of the "Workflow" and execute it; do not stop at confirmation

> Unified reverse engineering methodology for Android + iOS
> Frida / Objection / OWASP MSTG / SSL Pinning Bypass

## When to use

- Android APK reverse engineering and security testing
- iOS IPA reverse engineering and security testing
- Dynamic runtime instrumentation of mobile apps
- SSL pinning / root detection / jailbreak detection bypass
- Mobile crypto algorithm extraction (AES/RSA/HMAC keys)
- Mobile application penetration testing (OWASP MASTG)
- App testing on non-rooted/non-jailbroken environments

## Four-phase workflow

### Phase 1: Information gathering

```text
Android:
□ Get the APK (Google Play / APKMirror / adb pull)
□ Manifest analysis: permissions, exported components, Intent Filters, backup flag
□ androguard: androguard analyze APK → components/permissions/signature
□ APKLeaks: scan for hard-coded API keys / tokens / secrets
□ Hardening detection: packed or not (360/Tencent/Bangcle/Ijiami)

iOS:
□ Get the IPA (App Store / ipatool / Apple Configurator)
□ Decrypt App Store binaries: frida-ios-dump / Clutch (device online); fairplay-decrypt (offline, needs account credentials)
□ Info.plist analysis: ATS configuration, URL Scheme, Queries Schemes
□ class-dump: export the ObjC class structure
□ Hardening detection: whether Swift/ObjC obfuscation is used
```

### Phase 2: Static analysis

```text
Cross-platform:
□ JADX-GUI: APK → Java source (Android)
□ Ghidra / Hopper: .so / Mach-O decompilation
□ radare2 / Cutter: quick CLI reconnaissance

Android specifics:
□ apktool d app.apk → smali code + resources
□ dex2jar: DEX → JAR → JD-GUI
□ smali/baksmali: Dalvik bytecode modification

iOS specifics:
□ class-dump: export ObjC headers
□ Swift symbol recovery: swift-demangle
□ dsymutil: debug symbol extraction
□ otool -L: view dynamic library dependencies
□ jtool2: Mach-O analysis
```

### Phase 3: Dynamic analysis

```text
Frida: general dynamic instrumentation:
□ frida-ps -U: list device processes
□ frida-trace -U -i "open*" com.app: trace function calls
□ Custom hook scripts: modify arguments/return values, call private methods

Objection: Frida enhancement layer (no scripts needed):
□ objection -g "com.app" explore
□ android root disable / ios jailbreak disable
□ android sslpinning disable / ios sslpinning disable
□ android keystore list / ios keychain dump
□ env / ls / sqlite connect

Frida Gadget (no root/jailbreak needed):
□ Inject frida-gadget.so / FridaGadget.dylib into the APK/IPA
□ Re-sign → install → hook without device privileges
□ objection patchapk --source app.apk (fully automatic)
```

### Phase 4: Network analysis

```text
□ Burp Suite: intercept HTTP/HTTPS, modify requests/responses
□ mitmproxy: scripted proxy (Python API)
□ Wireshark: PCAP capture analysis
□ Certificate install: Android user certificate → system certificate (Magisk + MoveCert)
□ SSL pinning bypass: Frida/Objection/Xposed/SSL Kill Switch 2
□ WebSocket / gRPC traffic analysis
```

## Common bypass quick reference

### SSL Pinning

```bash
# Objection (simplest)
objection -g "com.app" explore
android sslpinning disable

# Frida generic script
frida -U -l ssl_pinning_bypass.js -f com.app

# Xposed (Android)
TrustMeAlready module → disables certificate checks globally
```

### Root / jailbreak detection

```bash
# Objection
android root disable
ios jailbreak disable

# Frida custom (multi-layer detection)
Java.perform(function() {
    var RootBeer = Java.use("com.scottyab.rootbeer.RootBeer");
    RootBeer.isRooted.implementation = function() { return false; };
    // Extra bypasses: Magisk su detection, frida-server detection, /proc/self/maps detection
});
```

### Anti-debugging

```bash
# Android
frida -U -l anti_debug_bypass.js -f com.app
# Bypass: ptrace(TracerPid), /proc/self/status, isDebuggerConnected()

# iOS
# Bypass: PT_DENY_ATTACH, sysctl CTL_KERN/KERN_PROC/KERN_PROC_PID
frida -U -l ios_anti_debug.js -f com.app
```

## Mobile crypto extraction

```javascript
// Android: hook Cipher.getInstance to get the key + algorithm
Java.perform(function() {
    var Cipher = Java.use("javax.crypto.Cipher");
    Cipher.getInstance.overload('java.lang.String').implementation = function(algo) {
        console.log("[Cipher] Algorithm: " + algo);
        return this.getInstance(algo);
    };
    Cipher.init.overload('int', 'java.security.Key').implementation = function(mode, key) {
        console.log("[Cipher] Key: " + bytesToHex(key.getEncoded()));
        return this.init(mode, key);
    };
});

// iOS — Hook CCCrypt
Interceptor.attach(Module.findExportByName("libcommonCrypto.dylib", "CCCrypt"), {
    onEnter: function(args) {
        console.log("CCCrypt op: " + args[0] + " alg: " + args[1]);
        console.log("Key: " + hexdump(args[3], { length: args[4].toInt32() }));
    }
});
```

## Toolchain

| Tool | Platform | Purpose |
|------|:--:|------|
| JADX-GUI | A | Java decompilation |
| apktool | A | APK unpack/rebuild |
| Ghidra | A+I | Multi-architecture decompilation |
| Hopper | I | iOS-specific disassembly |
| Frida | A+I | Dynamic instrumentation |
| Objection | A+I | Frida REPL enhancement |
| MobSF | A+I | Automated SAST+DAST |
| class-dump | I | ObjC class export |
| frida-ios-dump | I | IPA decryption (device online) |
| fairplay-decrypt | I | Offline IPA decryption (16B account credentials, see references/ios-reverse-guide.md) |
| jtool2 | I | Mach-O analysis |
| Burp Suite | A+I | HTTP interception |
| mitmproxy | A+I | Scripted proxy |

> A=Android, I=iOS

## References

- `references/frida-objection-deep.md`: in-depth Frida + Objection usage
- `references/ios-reverse-guide.md`: iOS reverse engineering specifics
- `references/anti-detection-bypass.md`: root/jailbreak/anti-debugging/SSL pinning bypass


## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
