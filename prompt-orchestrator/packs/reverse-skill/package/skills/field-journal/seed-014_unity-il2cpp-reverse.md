# [seed] Unity IL2CPP Game Reverse Engineering → Recover Metadata + Modify Logic

## Scenario classification
Game security / mobile reverse engineering

## Target overview
A Unity-built Android game (IL2CPP mode) whose in-app purchases or core algorithms are written in C# but compiled to native. The goal is to recover method names, locate the key logic, and implement modifications by patching / hooking.

## Complete execution chain

1. Unpack the APK and confirm it is IL2CPP
   ```bash
   unzip target.apk -d apk
   ls apk/lib/arm64-v8a/        # libil2cpp.so present means IL2CPP
   ls apk/assets/bin/Data/Managed/Metadata/
   # key file: global-metadata.dat
   ```
2. Recover the metadata with **Il2CppDumper**
   ```bash
   Il2CppDumper libil2cpp.so global-metadata.dat output/
   # outputs: DummyDll/ + script.json + il2cpp.h + dump.cs
   ```
3. Run the IDA IL2CPP script (`ida_with_struct.py`)
   - Load libil2cpp.so → File → Script File → choose ida_with_struct.py → choose script.json
   - IDA now shows C# method names, signatures and strings
4. Search dump.cs for business keywords (`AddCoin` / `OnPurchase` / `Verify` / `IsVip` / `CheckSign`)
5. Take the offsets of the key methods → jump there in IDA and read the disassembly / decompilation
6. Choose the modification method:
   - **Static patch**: change the check directly in IDA to `mov w0, #1; ret`
   - **Dynamic hook**: Frida on the il2cpp methods (with Frida-Il2CppBridge)
7. Repackage and verify / inject and verify

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| Il2CppDumper reports an unsupported metadata version | Newer Unity changed the metadata format | Upgrade Il2CppDumper to the latest / use Il2CppInspectorRedux instead | 30min |
| global-metadata.dat is encrypted | AntiCheatToolkit / custom encryption is used | Find the decryption function during game initialization (usually around il2cpp_init) → dump with Frida after mmap | 2h |
| dump.cs shows method names but IDA does not match | script.json and the so are inconsistent | Always use the outputs of the same dump; clear the cache when switching IDA | 20min |
| Frida hooking an IL2CPP method errors | IL2CPP methods are not standard Java/ObjC; the method offset must be computed | Use the frida-il2cpp-bridge library instead of writing Interceptor.attach by hand | 1h |
| The game crashes after patching | File hash checks or anti-tamper | Find the hash check logic and patch it too, or use hooks without changing files | 2h |
| Crash on launch after repackaging | An apksigner v2 signature cannot survive byte changes before re-signing | Delete META-INF + apktool b + apksigner sign in one go | 30min |

## Toolchain findings

- **Il2CppDumper** is old but still the default choice
- **Il2CppInspectorRedux** is more modern, supports newer Unity, and outputs plugin scripts for IDA / Ghidra / Binary Ninja
- **frida-il2cpp-bridge** is the de facto standard for hooking on IL2CPP, many times stronger than bare Frida
- **DnSpy** / **dnSpyEx** to read DummyDll (the dumped pseudo .NET assemblies)
- **UnityCheat**-family helper tools (the GameGuardian family is not covered)

## Key code/commands

frida-il2cpp-bridge hook example:

```typescript
// hook.ts
import "frida-il2cpp-bridge";

Il2Cpp.perform(() => {
    const Assembly = Il2Cpp.domain.assembly("Assembly-CSharp").image;

    // hook static method
    const PlayerData = Assembly.class("PlayerData");
    PlayerData.method("AddCoin").implementation = function (n: number) {
        console.log("[+] AddCoin called with:", n);
        return this.method("AddCoin").invoke(99999); // change to 99999
    };

    // hook instance method
    const Purchase = Assembly.class("Purchase");
    Purchase.method("VerifyReceipt").implementation = function () {
        console.log("[+] VerifyReceipt → always true");
        return true;
    };
});
```

```bash
# build + inject
npm install frida-il2cpp-bridge
frida-compile hook.ts -o hook.js
frida -U -f com.target.game -l hook.js --no-pause
```

IDA static patch:

```text
1. Open libil2cpp.so and run il2cpp_load_metadata.py
2. Jump to the offset of IsPurchaseValid from dump.cs
3. Change the function start to MOV W0, #1; RET (ARM64)
4. Apply Patches → Save → put it back into the APK → re-sign
```

## Improvement suggestions for this package

- `reverse-engineering/SKILL.md` already covers Unity but lacks a case of the **complete IL2CPP workflow**
- Write `reverse-engineering/references/il2cpp-cheatsheet.md` as a separate document: dump tool comparison, frida-bridge templates, handling encrypted metadata
- Add frida-il2cpp-bridge to the bootstrap manifest

## Reusable patterns/script snippets

**Standard IL2CPP flow**:

```text
1. Confirm IL2CPP (check for libil2cpp.so under lib/abi)
2. Find the metadata (assets/bin/Data/Managed/Metadata/global-metadata.dat, or encrypted)
3. Recover with Il2CppDumper / Inspector
4. IDA + scripts bring back the metadata
5. Search dump.cs for business keywords
6. Choose patch or hook
7. Verify (launch + the actual scenario)
```

**Handling encrypted metadata**:

```text
1. Hook the fopen/open family of calls with Frida to see who reads global-metadata.dat
2. Dump the decrypted metadata from memory after mmap/read
3. Feed the dumped memory to Il2CppDumper as metadata
```

## Evolution actions
- [ ] Add a complete il2cpp chapter to reverse-engineering/references
- [ ] Add frida-il2cpp-bridge / Il2CppInspectorRedux to the bootstrap-manifest
- [x] The routing matrix already includes Unity / IL2CPP

## Environment information
- Windows / macOS (to run Il2CppDumper), target device Android arm64
- IDA Pro 7.7+ or Ghidra 11+
- frida-tools 16.x, frida-il2cpp-bridge 0.9+
- Unity versions: 2019.x - 2022.x (the metadata format differs slightly between versions)

## Redaction requirements
This entry is seed data, written from public technical patterns, with no real game involved. The package name `com.target.game` is a placeholder.
