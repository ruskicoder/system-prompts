# In-Depth Frida + Objection Usage

## Frida core API

### Java runtime (Android)

```javascript
Java.perform(function() {
    // Get class instances
    var String = Java.use("java.lang.String");

    // Hook a static method
    var System = Java.use("java.lang.System");
    System.getProperty.overload('java.lang.String').implementation = function(key) {
        console.log("System.getProperty: " + key);
        return this.getProperty(key);
    };

    // Hook a constructor
    var File = Java.use("java.io.File");
    File.$init.overload('java.lang.String').implementation = function(path) {
        console.log("File opened: " + path);
        return this.$init(path);
    };

    // Enumerate loaded classes
    Java.enumerateLoadedClasses({
        onMatch: function(className) { console.log(className); },
        onComplete: function() {}
    });

    // Modify the return value
    var RootDetector = Java.use("com.app.security.RootDetector");
    RootDetector.isDeviceRooted.implementation = function() {
        return false;
    };
});
```

### Native layer (Android + iOS)

```javascript
// Hook an exported function
Interceptor.attach(Module.findExportByName(null, "open"), {
    onEnter: function(args) {
        this.path = Memory.readUtf8String(args[0]);
    },
    onLeave: function(retval) {
        console.log("open(" + this.path + ") = " + retval);
    }
});

// Hook any address (through an offset)
var base = Module.findBaseAddress("libnative.so");
var target = base.add(0x12345);
Interceptor.attach(target, {
    onEnter: function(args) {
        console.log("Function called from: " + Thread.backtrace(this.context, Backtracer.ACCURATE)
            .map(DebugSymbol.fromAddress).join('\n'));
    }
});

// Modify the return value
Interceptor.attach(Module.findExportByName(null, "strcmp"), {
    onLeave: function(retval) {
        if (retval.toInt32() === 0) return; // strings equal, skip
        // Force match
        retval.replace(0);
    }
});
```

### ObjC runtime (iOS)

```javascript
// Hook an ObjC method
var hook = ObjC.classes.ViewController["- viewDidLoad"];
Interceptor.attach(hook.implementation, {
    onEnter: function(args) {
        console.log("viewDidLoad called");
    }
});

// Enumerate every class
ObjC.enumerateLoadedClasses({
    onMatch: function(className) { console.log(className); },
    onComplete: function() {}
});

// Call an ObjC method
var NSString = ObjC.classes.NSString;
var str = NSString.stringWithString_("Hello from Frida");
```

## Objection command quick reference

### General

```bash
objection -g "com.app" explore           # start
objection -g "com.app" explore -q        # quiet start (inject only, do not wait)
objection patchapk --source app.apk      # inject the Frida Gadget automatically
objection signapk --source app.apk       # sign only

# Filesystem
env              # app data directories
ls               # list files
file download /path/to/file  # download a file
file upload local.txt /remote/path  # upload a file

# SQLite
sqlite connect /path/to/db.sqlite
.tables          # list tables
select * from users;  # query
```

### Android only

```bash
android root disable              # bypass root detection
android sslpinning disable        # bypass SSL pinning
android hooking list classes      # enumerate classes
android hooking list class_methods com.app.Main  # enumerate methods
android hooking watch class com.app.Main  # hook every method
android intent launch_activity com.app.MainActivity  # start an Activity
android heap search instances com.app.User  # heap search
android keystore list             # Keystore entries
```

### iOS only

```bash
ios jailbreak disable             # bypass jailbreak detection
ios sslpinning disable            # bypass SSL pinning
ios keychain dump                 # dump the Keychain
ios nsuserdefaults get            # NSUserDefaults
ios nsurlcache dump               # HTTP cache
ios cookies get                   # read cookies
ios pasteboard monitor            # monitor the pasteboard
ios ui dump                       # UI hierarchy
ios plist cat Info.plist          # read a plist
```

## Deployment without root/jailbreak

### Android: Frida Gadget injection

```bash
# 1. Unpack the APK
apktool d app.apk -o app_unpacked

# 2. Download frida-gadget and put it in the lib directory
cp frida-gadget-17.x.x-android-arm64.so \
   app_unpacked/lib/arm64-v8a/libfrida-gadget.so

# 3. Inject System.loadLibrary("frida-gadget") in smali
# Modify onCreate or attachBaseContext of the main Activity

# 4. Rebuild and sign
apktool b app_unpacked -o app_patched.apk
uber-apk-signer -a app_patched.apk

# 5. Objection automation
objection patchapk --source app.apk --skip-resources
```

### iOS: Frida Gadget injection

```bash
# 1. Decrypt the App Store IPA
python3 frida-ios-dump.py -u -p com.app.target

# 2. Inject FridaGadget.dylib
# Modify the Mach-O Load Commands and add @executable_path/FridaGadget.dylib

# 3. Re-sign
codesign -f -s "Apple Development" Payload/App.app

# 4. Install through Xcode sideload or AltStore
```

## Advanced SSL pinning bypass

### Multi-layer bypass (Android)

```javascript
// 1. OkHttp CertificatePinner
var CertificatePinner = Java.use("okhttp3.CertificatePinner");
CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function() {};

// 2. Custom TrustManager
var TrustManagerImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl");
TrustManagerImpl.verifyChain.implementation = function() { return []; };

// 3. WebView SSL Error
var SslErrorHandler = Java.use("android.webkit.SslErrorHandler");
SslErrorHandler.proceed.implementation = function() { return this.proceed(); };

// 4. Network Security Config
// Requires modifying AndroidManifest.xml → android:networkSecurityConfig="@xml/network_security_config"
// Add trust for user certificates in the xml
```

### Multi-layer bypass (iOS)

```javascript
// 1. NSURLSession
var SecTrustEvaluate = Module.findExportByName("Security", "SecTrustEvaluate");
Interceptor.replace(SecTrustEvaluate, new NativeCallback(function(trust, result) {
    Memory.writeU32(result, 1); // kSecTrustResultProceed = 1
    return 0; // errSecSuccess
}, 'int', ['pointer', 'pointer']));

// 2. Alamofire
// Hook ServerTrustManager.evaluate → always return success
```

Source: Frida docs, Objection wiki, OWASP MSTG
