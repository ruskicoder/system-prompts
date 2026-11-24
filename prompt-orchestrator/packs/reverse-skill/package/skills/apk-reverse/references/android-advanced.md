# Android Advanced Reverse Engineering Reference

> Covers native SO analysis, advanced Frida usage, SSL pinning bypass, root detection countermeasures, unpacking hardened apps, Flutter/React Native reverse engineering.

---

## Native SO reverse engineering

### Analysis flow

```text
1. Extract the .so files from the APK
   unzip app.apk lib/arm64-v8a/*.so -d extracted/

2. Confirm the architecture and basic information
   file libxxx.so
   rabin2 -I libxxx.so

3. Find the JNI entry
   - Search for JNI_OnLoad (dynamic registration)
   - Search for Java_com_xxx_yyy (static registration)
   - nm -D libxxx.so | grep -i java

4. Load and analyze in IDA/Ghidra
   - Import the JNI header (jni.h types)
   - Annotate the JNIEnv* parameter
   - Find the RegisterNatives call (function table of dynamic registration)

5. Locate the key logic
   - Trace from the Java-layer native method names
   - Cross-reference from strings (keys, URLs, error messages)
   - Trace from calls into crypto library functions (AES/MD5/SHA)
```

### JNI function registration

```c
// Static registration: function name = Java_package_class_method
JNIEXPORT jstring JNICALL Java_com_example_app_Security_getSign(
    JNIEnv *env, jobject thiz, jstring input) { ... }

// Dynamic registration: RegisterNatives is called in JNI_OnLoad
static JNINativeMethod methods[] = {
    {"getSign", "(Ljava/lang/String;)Ljava/lang/String;", (void*)native_getSign},
};

JNIEXPORT jint JNI_OnLoad(JavaVM *vm, void *reserved) {
    JNIEnv *env;
    vm->GetEnv((void**)&env, JNI_VERSION_1_6);
    jclass clazz = env->FindClass("com/example/app/Security");
    env->RegisterNatives(clazz, methods, sizeof(methods)/sizeof(methods[0]));
    return JNI_VERSION_1_6;
}
```

### Tips for analyzing JNI in IDA

```text
1. Import the JNI type library
   File → Load File → Parse C Header → jni.h

2. Annotate the first parameter as JNIEnv*
   Right-click the parameter → Set type → JNIEnv*
   so calls such as env->FindClass / env->GetMethodID are recognized automatically

3. Find RegisterNatives
   Search for calls through JNIEnv vtable offset 0x35C (ARM64)
   → the third argument is the JNINativeMethod array
   → extract every native function address from the array
```

---

## Advanced Frida usage

### Hook native functions

```javascript
// Hook libc functions
Interceptor.attach(Module.findExportByName("libc.so", "open"), {
    onEnter: function(args) {
        this.path = args[0].readUtf8String();
        console.log("[open] " + this.path);
    },
    onLeave: function(retval) {
        if (this.path.includes("su") || this.path.includes("magisk")) {
            console.log("[open] Blocked root check: " + this.path);
            retval.replace(-1);  // return failure
        }
    }
});

// Hook functions in a custom SO
var base = Module.findBaseAddress("libsecurity.so");
var targetFunc = base.add(0x1234);  // offset address
Interceptor.attach(targetFunc, {
    onEnter: function(args) {
        console.log("arg0: " + args[0].readUtf8String());
    },
    onLeave: function(retval) {
        console.log("return: " + retval.readUtf8String());
    }
});
```

### Hook Java methods

```javascript
Java.perform(function() {
    // Hook an instance method
    var Security = Java.use("com.example.app.Security");
    Security.getSign.implementation = function(input) {
        console.log("[getSign] input: " + input);
        var result = this.getSign(input);  // call the original method
        console.log("[getSign] output: " + result);
        return result;
    };

    // Hook a constructor
    Security.$init.overload('java.lang.String').implementation = function(key) {
        console.log("[Security.<init>] key: " + key);
        this.$init(key);
    };

    // Hook an overloaded method
    Security.encrypt.overload('java.lang.String', 'int').implementation = function(data, mode) {
        console.log("[encrypt] data=" + data + " mode=" + mode);
        return this.encrypt(data, mode);
    };
});
```

### Memory search and modification

```javascript
// Search memory for a string
Process.enumerateModules().forEach(function(module) {
    if (module.name === "libtarget.so") {
        Memory.scan(module.base, module.size, "48 65 6C 6C 6F", {  // "Hello"
            onMatch: function(address, size) {
                console.log("Found at: " + address);
            }
        });
    }
});

// Modify memory (patch instructions)
var addr = Module.findBaseAddress("libsecurity.so").add(0x5678);
Memory.patchCode(addr, 4, function(code) {
    var writer = new Arm64Writer(code, {pc: addr});
    writer.putNop();  // replace with NOP
    writer.flush();
});
```

---

## SSL pinning bypass

### Generic option (recommended)

```javascript
// Frida generic SSL pinning bypass
// Source: https://github.com/0xCD4/SSL-bypass
Java.perform(function() {
    // 1. TrustManager bypass
    var TrustManager = Java.registerClass({
        name: 'com.custom.TrustManager',
        implements: [Java.use('javax.net.ssl.X509TrustManager')],
        methods: {
            checkClientTrusted: function(chain, authType) {},
            checkServerTrusted: function(chain, authType) {},
            getAcceptedIssuers: function() { return []; }
        }
    });

    // 2. SSLContext replacement
    var SSLContext = Java.use('javax.net.ssl.SSLContext');
    var sslContext = SSLContext.getInstance("TLS");
    sslContext.init(null, [TrustManager.$new()], null);

    // 3. OkHttp CertificatePinner bypass
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function() {};
    } catch(e) {}
});
```

### Per-framework bypass

| Framework | Bypass method |
|------|---------|
| OkHttp3 | Hook `CertificatePinner.check` to return empty |
| Retrofit | Same as OkHttp (uses OkHttp underneath) |
| Volley | Hook the SSL factory of `HurlStack` |
| Flutter | Hook `SecurityContext` in `dart:io` (needs a special script) |
| React Native | Hook `OkHttpClientProvider` |
| WebView | Hook `WebViewClient.onReceivedSslError` |

### Flutter specifics

```javascript
// Flutter SSL pinning bypass (requires finding the ssl_verify_peer_cert function)
var flutter_lib = Module.findBaseAddress("libflutter.so");
// Search for the byte signature of ssl_verify_peer_cert
var pattern = "FF 03 05 D1 FD 7B 0F A9";  // ARM64 signature
Memory.scan(flutter_lib, Module.findModuleByName("libflutter.so").size, pattern, {
    onMatch: function(address) {
        Interceptor.replace(address, new NativeCallback(function() {
            return 0;  // return success
        }, 'int', []));
    }
});
```

---

## Root detection bypass

### Common detection methods

| Detection method | Bypass method |
|---------|---------|
| Check `/system/app/Superuser.apk` | Hook `File.exists()` to return false |
| Check the `su` command | Hook `Runtime.exec()` to intercept su calls |
| Check `/proc/self/mounts` | Hook file reads and filter magisk-related entries |
| SafetyNet/Play Integrity | Magisk Hide / Zygisk + Shamiko |
| Check the Magisk package name | Randomize the Magisk package name |
| Check `/data/adb/` | Hook `opendir`/`access` |

### Frida generic root bypass

```javascript
Java.perform(function() {
    // Hook File.exists
    var File = Java.use("java.io.File");
    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        var blacklist = ["su", "Superuser", "magisk", "busybox", "xposed"];
        for (var i = 0; i < blacklist.length; i++) {
            if (path.toLowerCase().includes(blacklist[i])) {
                return false;
            }
        }
        return this.exists();
    };

    // Hook System.getProperty
    var System = Java.use("java.lang.System");
    System.getProperty.overload('java.lang.String').implementation = function(key) {
        if (key === "ro.debuggable" || key === "ro.secure") {
            return "1";
        }
        return this.getProperty(key);
    };
});
```

---

## Hardening/packer identification and unpacking

### Common hardening vendors

| Hardening | Identification traits | Unpacking method |
|------|---------|---------|
| 360 Jiagu | `libjiagu.so`, `com.stub.StubApp` | FART / Frida dump dex |
| Tencent Legu | `libshell*.so`, `com.tencent.StubShell` | FART / BlackDex |
| Bangcle | `libDexHelper.so`, `com.secneo.apkwrapper` | FART |
| Ijiami | `libexec.so`, `s.h.e.l.l` | Frida dump |
| NetEase Yidun | `libnesec.so` | Frida dump |
| Naga | `libnaga.so` | Frida dump |

### General unpacking methods

```text
Method 1: FART (unpacking in the ART environment)
- Flash the FART ROM or use the Frida edition of FART
- Automatically dumps every dex loaded by any ClassLoader

Method 2: Frida DEX Dump
- frida -U -f com.target.app -l dex_dump.js
- Hook at DexFile::OpenMemory and dump the dex in memory

Method 3: BlackDex
- Unpacking tool that needs no root
- Install the BlackDex APK directly and choose the target app to unpack

Method 4: manual dump
- Enumerate every ClassLoader with Frida
- Find the app's ClassLoader → get the DexFile object
- Read and save the dex memory region
```

### Frida DEX dump script

```javascript
Java.perform(function() {
    Java.enumerateClassLoaders({
        onMatch: function(loader) {
            try {
                var dexFiles = loader.getDexFileList();
                console.log("ClassLoader: " + loader);
                console.log("  DEX files: " + dexFiles);
            } catch(e) {}
        },
        onComplete: function() {}
    });
});
```

---

## React Native / Flutter reverse engineering

### React Native

```text
1. Unpack the APK → assets/index.android.bundle (JS code)
2. Format the JS → search for API addresses, keys, signing logic
3. If there is Hermes bytecode (.hbc file) → decompile with hermes-dec
4. Hook: use Frida to hook the Java-layer ReactBridge
```

### Flutter

```text
1. Flutter code compiles to libapp.so (Dart AOT)
2. It cannot be decompiled directly to Dart source
3. Analysis methods:
   - reFlutter tool: patch libflutter.so to get the snapshot
   - Doldrums: parse the Dart snapshot to recover class/function information
   - Frida hooks on key functions in libflutter.so
4. Network analysis: Flutter ignores the system proxy, so SSL needs special handling
```

---

## Tool quick reference

| Tool | Purpose | Install |
|------|------|------|
| jadx | Java decompilation | Already in bootstrap |
| apktool | Unpack/repack | Already in bootstrap |
| Frida | Dynamic hooking | `pip install frida-tools` |
| Objection | Frida wrapper (easier to use) | `pip install objection` |
| MobSF | Automated mobile security analysis | Docker deployment |
| BlackDex | Unpacking without root | APK install |
| FART | ART unpacking | Flash the ROM or use the Frida edition |
| hermes-dec | Hermes bytecode decompilation | npm install |
| reFlutter | Flutter reverse engineering helper | pip install |
| Magisk + Shamiko | Root hiding | Flash |

---

## Reference resources

| Resource | Description | Link |
|------|------|------|
| OWASP MASTG | Mobile security testing guide | https://mas.owasp.org/ |
| FridaBypassKit | Generic bypass framework | https://github.com/okankurtuluss/FridaBypassKit |
| SSL-bypass | Generic SSL pinning bypass | https://github.com/0xCD4/SSL-bypass |
| awesome-frida | Frida resource collection | https://github.com/dweinstein/awesome-frida |
| Android Security Awesome | Android security resources | https://github.com/ashishb/android-security-awesome |
