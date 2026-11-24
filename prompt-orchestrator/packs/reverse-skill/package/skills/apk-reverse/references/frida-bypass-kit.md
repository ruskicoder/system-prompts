# Frida Bypass Kit: Generic Android Security Bypass Framework

> Source: [FridaBypassKit](https://github.com/okankurtuluss/FridaBypassKit) (2025)
> When to use: APK dynamic analysis needs to bypass root detection, SSL pinning, emulator detection, anti-debugging

## Overview

FridaBypassKit is a Frida script that integrates four bypass capabilities and works out of the box without app-specific customization.

## Four bypass capabilities

### 1. Root detection bypass

- Hook `File.exists()` to hide su binaries
- Intercept root check calls through `Runtime.exec()`
- Hide root-related packages (Magisk, SuperSU and others) from PackageManager
- Modify system properties so the device looks unrooted

### 2. SSL pinning bypass

- Hook `TrustManagerImpl.verifyChain()`
- Hook `TrustManagerImpl.checkTrustedRecursive()`
- Bypass certificate chain validation
- Return an empty certificate chain to avoid the check
- Compatible with OkHttp, Retrofit and custom implementations

### 3. Emulator detection bypass

- Fake TelephonyManager return values
- Return a fake phone number and carrier name
- Modify Build properties

### 4. Anti-debugging bypass

- Hook `Debug.isDebuggerConnected()`
- Block debugger detection
- Bypass anti-debugging checks

## Usage

```bash
# Prerequisites
pip install frida-tools
adb push frida-server /data/local/tmp/
adb shell chmod 755 /data/local/tmp/frida-server
adb shell su -c /data/local/tmp/frida-server &

# Inject into the target app
frida -U -f com.example.app -l FridaBypassKit.js
```

## Other recommended Frida bypass scripts

| Project | Characteristics | Link |
|------|------|------|
| httptoolkit/frida-interception-and-unpinning | MitM all HTTPS traffic directly | [GitHub](https://github.com/httptoolkit/frida-interception-and-unpinning) |
| 0xCD4/SSL-bypass | Generic non-customized SSL bypass | [GitHub](https://github.com/0xCD4/SSL-bypass) |
| incogbyte/ssl-bypass gist | Bypasses common SSL pinning methods | [Gist](https://gist.github.com/incogbyte/1e0e2f38b5602e72b1380f21ba04b15e) |
| Zero3141/Frida-OkHttp-Bypass | Targets OkHttp CertificatePinner specifically | [GitHub](https://github.com/Zero3141/Frida-OkHttp-Bypass) |

## Integration with this package

In the `apk-reverse` workflow, use it in these situations:

1. The app detects root and refuses to run → enable the Root Detection Bypass
2. HTTPS requests show no plaintext during capture → enable the SSL Pinning Bypass
3. The app detects the emulator and refuses to run → enable the Emulator Detection Bypass
4. The app crashes after Frida attaches → enable the Debug Detection Bypass

Recommended combination: run the full FridaBypassKit first, then adjust for the specific case.
