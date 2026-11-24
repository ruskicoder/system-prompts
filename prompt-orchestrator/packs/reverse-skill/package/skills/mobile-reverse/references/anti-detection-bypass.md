# Root / Jailbreak / Anti-Debugging / SSL Pinning Bypass

## Detection layer model

```
Layer 1: static detection (at install/startup)
  ├─ Package manager detection (Cydia, apt, Magisk)
  ├─ File detection (su, busybox, frida-server)
  └─ Property detection (ro.debuggable, ro.secure)

Layer 2: runtime detection (continuous)
  ├─ Process detection (frida-server, magiskd)
  ├─ Port detection (27042 frida default)
  ├─ Memory detection (/proc/self/maps injection traces)
  └─ Stack detection (Frida call frames)

Layer 3: environment detection (triggered on demand)
  ├─ ptrace detection (TracerPid)
  ├─ /proc/self/status detection
  ├─ build.prop detection (test-keys)
  └─ Direct syscall detection (bypasses libc)
```

## Android root detection bypass

### Common detection libraries and bypasses

| Detection library | Detection method | Bypass |
|--------|---------|---------|
| RootBeer | Combination of 8 checks | Hook each check method to return false |
| SafetyNet | Google Play Services remote attestation | Use Magisk Hide / Shamiko / Play Integrity Fix |
| Google Play Integrity | Replaces SafetyNet | Trickystore + PIF |
| Custom native detection | syscall reads /proc/self/status | Hook the syscall or change the /proc mount |

### Comprehensive Frida bypass

```javascript
Java.perform(function() {
    // RootBeer
    var RootBeer = Java.use("com.scottyab.rootbeer.RootBeer");
    var methods = ["isRooted", "isRootedWithBusyBox", "checkSuExists",
        "detectRootManagementApps", "detectPotentiallyDangerousApps",
        "detectTestKeys", "checkForDangerousProps", "checkForRWPaths"];
    methods.forEach(function(m) {
        RootBeer[m].implementation = function() { return false; };
    });

    // Generic Build.TAGS detection
    var Build = Java.use("android.os.Build");
    var original = Build.TAGS.value;
    Build.TAGS.value = "release-keys";

    // PackageManager → hide package names
    var PackageManager = Java.use("android.content.pm.PackageManager");
    PackageManager.getPackageInfo.overload('java.lang.String', 'int').implementation = function(pkg, flags) {
        if (pkg == "de.robv.android.xposed.installer" || 
            pkg.includes("magisk") || pkg.includes("frida")) {
            throw Java.use("android.content.pm.PackageManager$NameNotFoundException").$new();
        }
        return this.getPackageInfo(pkg, flags);
    };
});
```

## iOS jailbreak detection bypass

### Multi-layer Frida hooks

```javascript
// 1. Filesystem detection
var NSFileManager = ObjC.classes.NSFileManager;
var paths = [
    "/Applications/Cydia.app", "/var/lib/apt", "/bin/bash",
    "/usr/sbin/sshd", "/etc/apt", "/Library/MobileSubstrate"
];
// Hook fileExistsAtPath to return NO

// 2. fork detection (forbidden inside the sandbox)
var fork_ptr = Module.findExportByName("libSystem.B.dylib", "fork");
Interceptor.replace(fork_ptr, new NativeCallback(function() {
    return -1;
}, 'int', []));

// 3. Scheme detection
// Through a MobileSubstrate hook
var LSApplicationWorkspace = ObjC.classes.LSApplicationWorkspace;
// Hook defaultWorkspace → canOpenURL → return NO for cydia://

// 4. Signature detection
var MISValidateSignature = Module.findExportByName(null, "MISValidateSignature");
Interceptor.attach(MISValidateSignature, {
    onLeave: function(retval) { retval.replace(0); }
});
```

## Anti-debugging bypass

### Android

```javascript
// 1. ptrace self → prevents attaching
// Native: ptrace(PTRACE_TRACEME, 0, NULL, 0)
// Bypass: hook ptrace → return 0

// 2. TracerPid detection
// /proc/self/status → TracerPid: 0
var fopen = Module.findExportByName(null, "fopen");
Interceptor.attach(fopen, {
    onEnter: function(args) {
        this.path = Memory.readUtf8String(args[0]);
    },
    onLeave: function(retval) {
        if (this.path && this.path.includes("status")) {
            // Modify the returned FILE* to return forged content
        }
    }
});

// 3. isDebuggerConnected (Java)
var Debug = Java.use("android.os.Debug");
Debug.isDebuggerConnected.implementation = function() { return false; };
```

### iOS

```javascript
// 1. PT_DENY_ATTACH
// ptrace(PT_DENY_ATTACH, 0, NULL, 0) → prevents a debugger from attaching
var ptrace = Module.findExportByName(null, "ptrace");
Interceptor.replace(ptrace, new NativeCallback(function(request, pid, addr, data) {
    if (request == 31) return 0; // PT_DENY_ATTACH → ignore
    return ptrace(request, pid, addr, data);
}, 'int', ['int', 'int', 'pointer', 'int']));

// 2. sysctl detection
var sysctl = Module.findExportByName(null, "sysctl");
Interceptor.attach(sysctl, {
    onLeave: function(retval) {
        // Modify the p_flag field of kinfo_proc → clear P_TRACED
    }
});

// 3. getppid detection (checks whether the parent process is launchd)
// getppid() != 1 while debugging
```

## SSL pinning bypass

### Android five-layer bypass

```text
Layer 1: TrustManager: accept every certificate
Layer 2: OkHttp CertificatePinner: hook it to empty the pins list
Layer 3: WebView SSL Error Handler: ignore certificate errors
Layer 4: Network Security Config: modify the xml → trust user certificates
Layer 5: Native SSL (OpenSSL/BoringSSL): hook SSL_get_verify_result → X509_V_OK
```

### iOS four-layer bypass

```text
Layer 1: NSURLSession: hook SecTrustEvaluate → kSecTrustResultProceed
Layer 2: Alamofire: hook ServerTrustManager
Layer 3: AFNetworking: hook AFSecurityPolicy
Layer 4: libcurl: LD_PRELOAD replaces the SSL verification callback
```

### Generic Objection commands

```bash
# Android
objection -g "com.app" explore
android sslpinning disable
# Equivalent to: automatically hooking the 5 layers above

# iOS
objection -g "com.app" explore
ios sslpinning disable
# Equivalent to: automatically hooking the 4 layers above
```

Source: OWASP MSTG, Frida CodeShare, objection wiki
