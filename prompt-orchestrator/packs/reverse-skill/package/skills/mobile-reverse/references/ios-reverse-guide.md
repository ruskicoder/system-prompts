# iOS Reverse Engineering Specifics

## IPA acquisition and decryption

```bash
# Download from the App Store
ipatool search "Target App"
ipatool purchase -b com.target.app
ipatool download -b com.target.app -o app.ipa

# Extract installed apps from the device
# Jailbroken device
scp root@device:/private/var/containers/Bundle/Application/*/Target.app .

# Decryption (App Store binaries are encrypted FAT format)
# frida-ios-dump (recommended)
python3 dump.py com.target.app -o decrypted.ipa

# Clutch
Clutch -i  # list installed apps
Clutch -d 1  # decrypt the first one

# dumpdecrypted
DYLD_INSERT_LIBRARIES=dumpdecrypted.dylib /path/to/App
```

### Offline decryption: fairplay-decrypt (16-byte account credential)

Source <https://github.com/EthanArbuckle/fairplay-decrypt>, installed at `~/Developer/fairplay-decrypt` (built and self-checked on both Tom-MacM5 and M4-32G-001).

Difference from frida-ios-dump / Clutch: those two **must run on a jailbroken device with the target app loaded on the device**; fairplay-decrypt **unpacks offline**: with the 16-byte FairPlay credential of the App Store account, it decrypts an encrypted IPA directly on macOS/Linux, with no device present and without loading the target app.

```bash
cd ~/Developer/fairplay-decrypt

# One-time preparation (done; only needed on a new machine)
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
make transform                     # build only the C transformer; make all fails on machines with only CommandLineTools (see below)

# Decrypt
.venv/bin/python decrypt.py /path/to/encrypted.ipa /path/to/decrypted.ipa \
  --credential /path/to/credential.bin
```

Key points:

- `credential.bin` is exactly 16 bytes and belongs to **the account that owns the app**, one per account, reusable across apps.
- The output path must not exist; the tool refuses to overwrite; input and output cannot be the same file.
- Supports SUPF v3/v5, SINF `priv` of 448 and 440 bytes (440 requires the last 8 bytes to be all zero), encrypted arm64 slices.
- `decrypt.py` relies on `transform` (the C transformer) + `transform_const_data.bin` in the same directory for page key derivation; **both must be at the project root**, otherwise it reports `build transform executable and keep constant-data file`.
- It decrypts arm64 pages of encrypted segments (`cryptid` non-zero); binaries already at cryptid=0 are skipped, and when everything is skipped it reports `no encrypted arm64 binaries`.

Credential retrieval (`credential-retrieval/`) needs **a paired jailbroken device with root SSH**, plus `idevice_id` and `iproxy`:

```bash
python3 credential-retrieval/retrieve.py --output-dir /path/to/new-dir   # produces credential.bin
```

This submodule builds the iOS target with `xcrun --sdk iphoneos` and **requires a full Xcode + `ldid`** (with only CommandLineTools it fails with `CommonCrypto/CommonCryptor.h not found`; Tom-MacM5 and M4-32G-001 are both in that state now, so `make all` fails on both while `make transform` works). So: **decryption is always available; retrieving credentials needs a full Xcode + a jailbroken device**. If the credential was obtained elsewhere, feed it to `--credential` directly.

## Mach-O analysis

```bash
# Basic information
otool -l TargetBinary | grep crypt    # encryption status
otool -L TargetBinary                 # dynamic library dependencies
otool -hv TargetBinary                # header information
jtool2 --pages TargetBinary           # memory page information

# Thin a fat binary
lipo -info TargetBinary
lipo TargetBinary -thin arm64 -output TargetBinary_arm64

# Symbol analysis
nm -g TargetBinary                    # exported symbols
nm -a TargetBinary                    # every symbol
swift-demangle <mangled_name>         # restore Swift symbols

# class-dump
class-dump -H TargetBinary -o headers/
# Export ObjC classes and method declarations to the headers/ directory
```

## Objective-C runtime analysis

```text
Message passing mechanism:
objc_msgSend(id self, SEL op, ...)  →  dynamic method dispatch
  ↓
Runtime lookup:
1. Class method list cache
2. Class method list
3. Superclass lookup level by level
4. +resolveInstanceMethod / +resolveClassMethod
5. forwardingTargetForSelector
6. methodSignatureForSelector + forwardInvocation
```

### Frida ObjC Hook

```javascript
// Hook an instance method
var hook = ObjC.classes.ClassName["- instanceMethod:"];
Interceptor.attach(hook.implementation, {
    onEnter: function(args) {
        // args[0] = self, args[1] = selector, args[2+] = method args
        console.log("self: " + new ObjC.Object(args[0]));
        console.log("arg: " + args[2].toInt32());
    }
});

// Hook a class method
var hook = ObjC.classes.ClassName["+ classMethod:"];
Interceptor.attach(hook.implementation, { ... });

// Call an ObjC method
var NSString = ObjC.classes.NSString;
var str = NSString.stringWithString_("test");
console.log(str.UTF8String());
```

## Swift reverse engineering

```text
Swift name mangling:
$s10ModuleName5ClassC6method3argSi_tF
  │ │         │     │ │      │  │   └─ parameter type
  │ │         │     │ │      │  └───── return type  
  │ │         │     │ │      └──────── parameter name
  │ │         │     │ └─────────────── method name
  │ │         │     └──────────────── class name (length + name)
  │ │         └────────────────────── module name
  │ └──────────────────────────────── identifier marker
  └────────────────────────────────── global marker

Tools: swift-demangle, Hopper (automatic restoration)
```

## Jailbreak detection bypass

```text
Detection method categories:

1. Filesystem checks:
   □ /Applications/Cydia.app
   □ /var/lib/apt/
   □ /bin/bash
   □ /usr/sbin/sshd
   → Hook NSFileManager.fileExistsAtPath:

2. Sandbox escape detection:
   □ Whether fork() succeeds (forbidden inside the sandbox)
   □ system() calls
   → Hook fork → return -1

3. Dyld injection detection:
   □ _dyld_get_image_count > limit
   → Keep the return value within a reasonable range

4. Scheme detection:
   □ cydia:// URL Scheme
   → Hook UIApplication.canOpenURL:

5. sysctl detection:
   □ CTL_KERN/KERN_PROC/KERN_PROC_PID → kinfo_proc
   → Hook sysctl → clear the P_TRACED bit in p_flag
```

### Unified Frida bypass script

```javascript
// File detection bypass
var NSFileManager = ObjC.classes.NSFileManager;
var defaultManager = NSFileManager.defaultManager();
Interceptor.attach(defaultManager["- fileExistsAtPath:"].implementation, {
    onLeave: function(retval) {
        var path = ObjC.Object(args[2]).toString();
        if (path.includes("Cydia") || path.includes("apt") || 
            path.includes("sshd") || path.includes("bash")) {
            retval.replace(0); // false
        }
    }
});

// fork bypass
Interceptor.replace(Module.findExportByName(null, "fork"), 
    new NativeCallback(function() { return -1; }, 'int', []));

// dyld bypass
var _dyld_get_image_count = Module.findExportByName(null, "_dyld_get_image_count");
Interceptor.attach(_dyld_get_image_count, {
    onLeave: function(retval) {
        if (retval.toInt32() > 200) retval.replace(200);
    }
});
```

## Key protection bypass checklist

| Protection | iOS bypass method |
|------|-------------|
| App Store encryption | frida-ios-dump / Clutch (device online) / fairplay-decrypt (offline, needs account credential) |
| SSL Pinning | Objection `ios sslpinning disable` / SSL Kill Switch 2 |
| Jailbreak detection | Objection `ios jailbreak disable` / custom Frida hook |
| Anti-debugging (PT_DENY_ATTACH) | Inject after Frida starts / debugserver |
| Integrity check | Hook the MAC check / code signature verification |
| Anti-injection | Modify the Mach-O to remove the __RESTRICT segment |
| Swift obfuscation | swift-demangle + LLM-assisted semantic recovery |
| Screenshot protection | Hook UIScreen.mainScreen.snapshotViewAfterScreenUpdates |

Source: OWASP MSTG, frida-ios-dump, The iPhone Wiki
