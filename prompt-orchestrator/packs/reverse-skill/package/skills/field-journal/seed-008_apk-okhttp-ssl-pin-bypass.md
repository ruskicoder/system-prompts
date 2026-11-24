# [seed] Bypassing OkHttp SSL Pinning in an APK with Frida

## Scenario classification
APK reverse engineering / mobile security testing

## Target overview
For an Android app that uses OkHttp + a custom CertificatePinner, bypass certificate validation dynamically with Frida so Burp can see plaintext traffic.

## Complete execution chain

1. Install Frida + frida-server, launch the target app, confirm the process name
   ```bash
   adb shell "ps -A | grep com.target.app"
   frida-ps -U | grep target
   ```
2. Try capturing with Burp → a certificate error, which shows pinning is enabled
3. Decompile the APK with jadx → search for `CertificatePinner` or `checkServerTrusted`
4. Confirm whether it is OkHttp's built-in `CertificatePinner` or a custom `X509TrustManager`
5. Write a Frida script that hooks the key validation points
6. Start Frida injection: `frida -U -f com.target.app -l bypass.js --no-pause`
7. Capture again → Burp shows plaintext HTTPS

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| Frida startup error `unable to connect to remote frida-server` | The server is not started or the port is taken | `adb forward tcp:27042 tcp:27042` + start the server | 10min |
| Hook has no effect | The app starts too fast and Frida injects too late | Use spawn mode with the `-f` parameter plus `--no-pause` | 15min |
| Some requests still fail SSL after hooking | The app uses both OkHttp and the native HttpsURLConnection | Also hook `X509TrustManager.checkServerTrusted` and `HostnameVerifier.verify` | 20min |
| Anti-detection: the app exits after detecting Frida | The app checks the frida-server port / `/data/local/tmp/re.frida.server` | Use frida-gadget (inject the .so into the APK) or magisk + zygisk-frida instead | 30min+ |
| Class names not found after ProGuard obfuscation | Class names became short names like `a.b.c` | Use `Find Usages` in jadx to find who instantiates OkHttpClient.Builder | 25min |

## Toolchain findings

- **objection** has the built-in `android sslpinning disable`, one command that handles 80% of scenarios without writing a Frida script
- **frida-multiple-unpinning** (GitHub: WithSecureLabs) covers OkHttp 3/4, Retrofit, HttpsURLConnection, Conscrypt and Cordova; a universal script
- The **MEDUSA** framework ships various Android bypass modules and is quicker to pick up than bare Frida

## Key code/commands

Minimal working OkHttp pin bypass script:

```javascript
Java.perform(function () {
    // 1. OkHttp 3/4 built-in CertificatePinner
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function (host, peers) {
            console.log('[+] OkHttp CertificatePinner.check bypassed: ' + host);
            return;
        };
    } catch (e) {}

    // 2. custom X509TrustManager.checkServerTrusted
    try {
        var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
        TrustManagerImpl.verifyChain.implementation = function (untrusted, holdHost, host, clientAuth, ocspData, tlsSctData) {
            console.log('[+] TrustManagerImpl.verifyChain bypassed: ' + host);
            return untrusted;
        };
    } catch (e) {}

    // 3. HostnameVerifier passes everything
    var HostnameVerifier = Java.use('javax.net.ssl.HostnameVerifier');
    // complete it with the objection templates...
});
```

One-click command (recommended):

```bash
objection --gadget com.target.app explore -s "android sslpinning disable"
```

## Improvement suggestions for this package

- `apk-reverse/references/` should have a dedicated `ssl-pinning-bypass.md` that merges the four mainstream cases OkHttp 3/4, Conscrypt, custom TrustManager and Flutter (boringssl) into a quick reference
- Add `objection` (pip package) to the bootstrap manifest

## Reusable patterns/script snippets

**General bypass flow**:

```text
1. Capture traffic → see which kind of error (CertPin / Hostname / TrustManager)
2. Search jadx for the key classes (CertificatePinner / X509TrustManager / HostnameVerifier)
3. Try objection one-click first → if not, frida-multiple-unpinning → if still not, write it by hand
4. With anti-Frida detection → switch to frida-gadget or zygisk
5. Handle Flutter apps separately (hook ssl_verify_peer_cert in libflutter.so)
```

## Evolution actions
- [x] Covered by the routing matrix (apk-reverse + Frida)
- [x] frida status in tool-index checked
- [ ] Suggest adding the ssl-pinning-bypass.md quick reference

## Environment information
- Kali / Windows + adb + frida-tools 16.x
- Target Android: 8-14 (the TrustManagerImpl path differs by version)
- Injection method: USB debugging + frida-server / or hidden with zygisk-frida

## Redaction requirements
This entry is seed data, written from public technical patterns, with no real target involved. The package name `com.target.app` is a placeholder.
