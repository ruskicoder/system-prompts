# [seed] iOS Jailbreak Detection Bypass + Traffic Capture

## Scenario classification
iOS reverse engineering / mobile security testing

## Target overview
An iOS app crashes immediately on a jailbroken device or shows "abnormal environment"; jailbreak detection must be bypassed before its HTTP requests can be analyzed further.

## Complete execution chain

1. Prepare the jailbroken device (Dopamine / palera1n / unc0ver) → install frida-server (Cydia source `build.frida.re`)
2. Copy the IPA to the device, install the signature with AppSync Unified → confirm `frida-ps -U` works after launch
3. Launch the app → crash or the "abnormal environment" pop-up
4. Use `frida-trace -U -i 'open' -i 'stat' -i 'access' -i 'fork' com.target.app` to see the detection calls
5. Common hits: probing `/Applications/Cydia.app`, `/private/var/lib/apt`, `/usr/sbin/sshd`, whether `fork()` succeeds, `/etc/apt`
6. One-click bypass with objection: `objection --gadget com.target.app explore -s "ios jailbreak disable"`
7. After a successful launch, capture with a frida hook on NSURLSession, or set up mitmproxy with a system certificate

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| Still crashes after the objection bypass | The app uses SSL pinning + jailbreak detection together | Enable both `ios sslpinning disable` and `ios jailbreak disable` | 15min |
| The app detects before launch, too early for the hook | Jailbreak detection runs in `+load` or `__attribute__((constructor))` | Use `-f` spawn mode + `frida-trace --aux 'spawn=1'` | 20min |
| The app hangs after hooking stat | Hooking stat also affects some system calls | Hook only stat calls triggered by code inside the app bundle (filter by caller) | 30min |
| The app still detects frida-server after it starts | The app checks port 27042 and frida strings | Rename `frida-server` + change the default port (`-l 0.0.0.0:1234`), client uses `-H ip:1234` | 25min |
| Still SSL errors after installing the mitmproxy certificate | On iOS 14+, system certificates need one more switch in "General → About → Certificate Trust Settings" | After installing the certificate, enable it in the trust settings | 10min |

## Toolchain findings

- **objection** is the Swiss army knife of iOS security testing, with built-in jailbreak / sslpin / clipboard / keychain dump modules
- **r2frida** connects radare2 to frida, allowing runtime disassembly + register changes; far stronger than plain frida
- **Hopper / IDA** decompile iOS binaries (for iOS Mach-O, IDA 7+ or Ghidra both work)
- **dumpdecrypted** is outdated; use **frida-ios-dump** to decrypt apps now

## Key code/commands

General jailbreak detection hook template:

```javascript
// intercept NSFileManager fileExistsAtPath checks for jailbreak directories
var NSFileManager = ObjC.classes.NSFileManager;
Interceptor.attach(NSFileManager['- fileExistsAtPath:'].implementation, {
    onEnter: function (args) {
        var path = ObjC.Object(args[2]).toString();
        var jbPaths = [
            '/Applications/Cydia.app',
            '/Library/MobileSubstrate/MobileSubstrate.dylib',
            '/bin/bash', '/usr/sbin/sshd',
            '/etc/apt', '/private/var/lib/apt/'
        ];
        if (jbPaths.indexOf(path) !== -1) {
            this.shouldFake = true;
            console.log('[+] Hide JB path: ' + path);
        }
    },
    onLeave: function (retval) {
        if (this.shouldFake) retval.replace(0);
    }
});

// intercept fork(): a jailbroken device can fork, a non-jailbroken one returns -1
var fork = Module.findExportByName(null, 'fork');
Interceptor.replace(fork, new NativeCallback(function () {
    return -1;
}, 'int', []));
```

One-click decryption (for decompiling with jadx and the like):

```bash
frida-ios-dump -l com.target.app
# outputs Payload/TargetApp.app + the decrypted Mach-O
```

## Improvement suggestions for this package

- Add a sub-skill `ios-reverse/` (parallel to `apk-reverse/`) covering decryption, jailbreak detection bypass, SSL pinning, Keychain dump, frida-ios-dump and `+load` timing
- The existing `apk-reverse/` should not carry iOS content, to avoid confusion

## Reusable patterns/script snippets

**iOS security testing quick reference**:

```text
1. Jailbreak environment preparation (Dopamine 16.x / older palera1n)
2. Decrypt with frida-ios-dump
3. View the class hierarchy with otool / class-dump
4. Start an objection console
5. ios jailbreak disable
6. ios sslpinning disable
7. Capture with mitmproxy (system certificate + trust settings both enabled)
8. After finding the key logic, dig deeper statically with IDA / Hopper
```

## Evolution actions
- [ ] **Suggest adding an ios-reverse skill** (the current routing matrix sends iOS to reverse-engineering/platforms.md, which is not detailed enough)
- [ ] Add frida-ios-dump to the bootstrap manifest
- [ ] Add an "iOS security testing checklist" to references/

## Environment information
- Jailbroken device: iPhone X (iOS 16.5) + Dopamine 1.1.7
- Host: macOS 13+ / Kali (mitmproxy + frida-tools)
- frida-server-ios: 16.x

## Redaction requirements
This entry is seed data, written from public technical patterns, with no real target involved. The Bundle ID `com.target.app` is a placeholder.
