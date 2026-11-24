# APK Security Testing Quick Reference

> Compiled from OWASP MASTG (Mobile Application Security Testing Guide).
> Covers six dimensions: static analysis, dynamic analysis, network communication, data storage, authentication and authorization, code protection.

---

## Static analysis checklist

### Manifest audit

```text
□ android:debuggable="true" → debuggable (should not appear in production)
□ android:allowBackup="true" → data can be extracted through backup
□ Components with android:exported="true" → exposed Activity/Service/Receiver/Provider
□ Custom permission protectionLevel → is it normal (should be signature)
□ scheme in intent-filter → can the custom deeplink be hijacked
□ android:usesCleartextTraffic="true" → plaintext HTTP allowed
□ minSdkVersion too low → security features may be missing
```

### Code audit key points

```text
□ Hard-coded keys/tokens (search "key", "secret", "password", "api_key")
□ Insecure random numbers (java.util.Random instead of SecureRandom)
□ Insecure encryption (ECB mode, DES, MD5 for passwords)
□ WebView configuration (setJavaScriptEnabled + addJavascriptInterface = RCE risk)
□ SQL injection (rawQuery concatenating user input)
□ Path traversal (ContentProvider openFile without path validation)
□ Log leaks (Log.d/Log.i print sensitive information)
□ Clipboard leaks (ClipboardManager stores sensitive data)
□ Implicit Intent leaks (sendBroadcast without a package name)
```

### Third-party library audit

```text
□ Outdated OkHttp/Retrofit versions (known vulnerabilities)
□ Outdated WebView engine
□ SDKs with known vulnerabilities (check CVEs)
□ Data collection scope of ad SDKs
□ Push SDK configuration (does it leak tokens)
```

---

## Dynamic analysis checklist

### Priority Frida hook targets

| Target | Hook point | Purpose |
|------|---------|------|
| Login authentication | `LoginActivity.login()` | Observe credential handling |
| Signature generation | `*Sign*`, `*sign*`, `*encrypt*` | Reconstruct the signing algorithm |
| SSL Pinning | `CertificatePinner.check` | Bypass for capture |
| Root detection | `*root*`, `*su*`, `*magisk*` | Bypass detection |
| Crypto operations | `javax.crypto.Cipher` | Extract keys/IVs |
| Token storage | `SharedPreferences.getString` | Observe token reads and writes |
| Network requests | `OkHttpClient.newCall` | Observe request construction |

### Common Frida one-liners

```bash
# Trace every crypto operation
frida-trace -U -f com.target.app -j '*Cipher*!*'

# Trace every HTTP request
frida-trace -U -f com.target.app -j '*OkHttp*!*'

# Trace SharedPreferences reads and writes
frida-trace -U -f com.target.app -j '*SharedPreferences*!*'

# Trace every native function call
frida-trace -U -f com.target.app -i 'Java_*'
```

### Objection quick commands

```bash
# Connect
objection -g com.target.app explore

# Common commands
android hooking list activities
android hooking list services
android sslpinning disable
android root disable
android clipboard monitor
env                              # view app directories
sqlite connect <db_path>         # connect to a database
```

---

## Network communication security

### Capture setup

```text
Method 1: system proxy + Burp/mitmproxy
- Set the WiFi proxy → Burp listening address
- Install the CA certificate on the device
- Android 7+ needs network_security_config or a Frida bypass

Method 2: VPN mode (recommended)
- Use HttpCanary / Packet Capture
- No root, no proxy configuration needed
- But it cannot decrypt traffic protected by SSL pinning

Method 3: Frida + r2frida
- Intercept network calls directly inside the process
- Not limited by proxy/VPN
```

### Check items

```text
□ HTTPS used (for every API call)?
□ SSL pinning (certificate binding)?
□ Certificate validation correct (self-signed rejected)?
□ Certificate Transparency (CT) checks?
□ Are API keys sent in plaintext in requests?
□ Do tokens have an expiry mechanism?
□ Is there request signing against tampering?
□ Is there replay protection (nonce/timestamp)?
□ Is WebSocket encrypted?
□ Is sensitive data in URL parameters (which get logged)?
```

---

## Data storage security

### Check locations

| Location | Risk | Check command |
|------|------|---------|
| SharedPreferences | Plaintext token/password storage | `adb shell cat /data/data/pkg/shared_prefs/*.xml` |
| SQLite database | Unencrypted sensitive data | `adb pull /data/data/pkg/databases/` |
| External storage | Readable by any app | `adb shell ls /sdcard/Android/data/pkg/` |
| App logs | Leak debug information | `adb logcat \| grep pkg` |
| Backup files | allowBackup=true | `adb backup -f backup.ab pkg` |
| Keyboard cache | Input history | Check whether `inputType` is `textPassword` |
| Screenshot protection | Sensitive screens can be captured | Check `FLAG_SECURE` |

### Encrypted storage option comparison

| Option | Security | Notes |
|------|--------|------|
| Plaintext SharedPreferences | No | Read directly after root |
| EncryptedSharedPreferences | ✓ | AndroidX Security library |
| SQLCipher | ✓ | Encrypted SQLite |
| Android Keystore | ✓✓ | Hardware-level key protection |
| Custom AES encryption | | Depends on key management |

---

## Authentication and authorization

### Common vulnerabilities

| Vulnerability | Test method |
|------|---------|
| Weak password policy | Try 123456, password and similar |
| No lockout mechanism | Brute-force the login endpoint |
| Tokens never expire | Replay an old token after logout |
| Broken access control | Modify the user_id in the request |
| SMS verification code brute force | 4/6-digit codes without rate limiting |
| OAuth misconfiguration | redirect_uri can be tampered with |
| Biometric authentication bypass | Hook BiometricPrompt |
| Device binding bypass | Modify device_id |

### Test payloads

```bash
# Access control test
curl -H "Authorization: Bearer USER_A_TOKEN" \
     "https://api.target.com/users/USER_B_ID/profile"

# Token replay
# 1. Log in normally and get a token
# 2. Log out
# 3. Request with the old token → should return 401

# SMS verification code brute force
for code in $(seq 0000 9999); do
    curl -X POST "https://api.target.com/verify" \
         -d "phone=13800138000&code=$code"
done
```

---

## Code protection assessment

| Protection | Detection method | Bypass difficulty |
|---------|---------|---------|
| ProGuard obfuscation | Check in jadx whether class names are a/b/c | Low (only renaming) |
| String encryption | Find the decryption function, hook it to get plaintext | Medium |
| Anti-debugging | Try to attach a debugger | Medium (Frida can bypass) |
| Root detection | Run on a rooted device | Medium (generic script bypass) |
| Emulator detection | Run on an emulator | Low-medium |
| Integrity check | Install after modifying the APK | Medium (patch the check function) |
| Hardening/packer | Look at the entry class and .so | Medium-high (needs unpacking) |
| Native protection | Core logic in the .so | High (needs IDA analysis) |
| VMP virtualization | Code runs virtualized | Very high |

---

## Quick test process (30 minutes)

```text
1. [5min] Unpack + Manifest audit
   apktool d app.apk
   Check debuggable/allowBackup/exported/cleartext

2. [10min] Quick code audit
   jadx -d out app.apk
   Search: password, key, secret, token, http://

3. [5min] Network test
   Configure the proxy → use the app → check for plaintext/weak encryption

4. [5min] Storage check
   adb shell → check shared_prefs and databases

5. [5min] Dynamic verification
   Frida hook key functions → confirm the findings
```
