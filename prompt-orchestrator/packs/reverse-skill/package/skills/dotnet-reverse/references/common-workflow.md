# .NET Reverse Engineering General Workflow

Complete workflow details, IL patch reliability, string decryptor extraction, state machine recognition, dnlib scripting.

## Complete workflow (end to end)

```text
1. Identify  → confirm a .NET managed program (not native)
2. Detect    → identify the obfuscator with DIE / de4dot --detect
3. Deobf     → deobfuscate with de4dot (keep the original sample)
4. Static    → locate with the dnSpyEx C# view, read key logic in the IL view
5. Dynamic   → break on key methods in the dnSpyEx debugger and read runtime plaintext
6. Patch     → modify in the IL editor, Save Module
```

Write the output of each step to disk: original sample `target.exe` → unpacked `target-clean.exe` → patched `target-patched.exe`.

## IL patch vs C# patch reliability

**Core conclusion: make key modifications in the IL editor, not the C# editor.**

| Dimension | C# editor (Edit Method C#) | IL editor (Edit IL) |
|------|---------------------------|---------------------|
| Compile failure risk | High (missing references, syntax, lambda rewrite failures) | Almost zero |
| Fidelity | The compiler regenerates IL, which may differ from the original | Replaced as is, instruction by instruction |
| Suited to | Changing a string, a constant, simple logic | Changing branches, removing checks, changing control flow |
| async/await/state machines | Often fails to compile or distorts | Change state machine fields directly, reliable |

The dnSpyEx C# decompiler is read-only decompilation + attempted recompilation, and recompiling compiler-generated code (state machines, closures, `yield`) fails easily. The IL editor edits instruction by instruction, what you see is what you get.

### Typical IL patch patterns

```text
Change a branch (if (check) → always true):
  Original: call bool Foo::Check()
      brfalse.s SKIP
  Changed: ldc.i4.1            ; push true
      brfalse.s SKIP      ; now never jumps, SKIP does not run
  Or more directly:
      ldc.i4.1
      ret                 ; the method returns true directly

Change a branch (if (check) → always false):
  ldc.i4.0
  ret

Remove a whole check block:
  nop everything, or change it to ret + the correct return value

Change a string constant:
  Changing a string in the C# editor usually works (ldstr swaps the token directly), but if the string lives in resources/encrypted, change the decryption logic

Change a numeric constant:
  Change the operand of the ldarg / ldc instruction directly
```

## State machine recognition (async/await / yield)

C# `async/await` and `IEnumerator` yield compile into **state machines**: the compiler generates a nested class whose `MoveNext()` dispatches with a switch on the `state` field. The dnSpyEx C# view restores it as async, but the decompilation can be distorted; reading `MoveNext` in the IL view is the most accurate.

```text
MoveNext structure of async/await:
  switch(this.<>1__state) {
    case 0: ... logic before await; this.<>1__state = 1; await MoveNext;
    case 1: ... logic after await;
  }

To patch async logic: change the state transition in MoveNext or the branch in the specific case.
Changing async in the C# editor almost always fails → you must use IL.
```

## String decryptor extraction

See `obfuscators.md`. This adds batch string decryption scripted with dnlib:

```csharp
// dnlib script: scan every string decryptor call, restore at runtime, write back
// Usage: dotnet script decrypt.csproj target.exe 0x06000012
using System;
using System.Reflection;
using dnlib.DotNet;
using dnlib.DotNet.Writer;
using dnlib.DotNet.Emit;

var module = ModuleDefMD.Load(args[0]);
var decryptorToken = uint.Parse(args[1], System.Globalization.NumberStyles.HexNumber);

// Find the decryption method and call it through reflection (the assembly must be loaded into the AppDomain)
// Walk every method and replace call Decryptor(token) with ldstr "decrypted result"
foreach (var type in module.GetTypes())
    foreach (var method in type.Methods)
    {
        if (!method.HasBody) continue;
        var instrs = method.Body.Instructions;
        for (int i = 0; i < instrs.Count; i++)
        {
            // Recognize the call-decryptor pattern, call the decryptor for plaintext, replace with ldstr
            // (The boilerplate for calling the decryptor through reflection is omitted; idea: load the original assembly →
            //   MethodInfo.Invoke for plaintext → instrs[i] = OpCodes.Ldstr + operand=plaintext)
        }
    }

var opts = new ModuleWriterOptions(module);
module.Write("target-decrypted.exe", opts);
```

dnlib is the de facto standard for .NET metadata programming, and de4dot uses it internally. It is the first choice for custom deobfuscation scripts.

## Dynamic debugging key points

The dnSpyEx debugger is far friendlier for .NET programs than for native:

- **Breakpoint at the method entry**: right-click the method → Add Breakpoint
- **View object values**: once paused, read object fields and string contents directly in the Locals / Watch windows
- **Memory writes**: runtime variable values can be changed directly (Edit Value)
- **Exception breakpoints**: Debug → Exceptions, tick the exception types to break on; obfuscators often use exception-driven control flow, and breaking on exceptions shows the real path

### Exception-driven control flow

Some obfuscators put normal logic inside `try` and use `throw` + `catch` for jumps. Statically the IL looks like exception handling, but it is actually control flow:

```text
try { throw new CustomException(0x42); }
catch (CustomException e) {
    switch(e.Code) {
        case 0x42: real logic A; break;
        case 0x43: real logic B; break;
    }
}
```

Set an exception breakpoint (break on `CustomException`) and follow how the `Code` value flows; faster than grinding through the IL.

## Module initializer (Module .cctor)

The static constructor of a `.NET` module (the `.cctor` of `<module>`) runs first when the assembly loads, and obfuscators often put anti-tamper / decryption initialization there. Analysis order:

```text
1. Look at <module>.cctor (Module .cctor) first: decryption/anti-debugging initialization
2. Then Program.Main / Startup
3. anti-tamper in the .cctor → patch the .cctor first, then unpack
```

## General pattern for extracting configuration / C2 / keys

Red team tools and loaders often embed encrypted configuration in resources or fields and decrypt it at runtime:

```text
Locating flow:
1. Check strings for plaintext URLs/IPs (usually none after obfuscation)
2. Find byte[] fields + the decryption method (AES/XOR)
3. Break dynamically at the return point of the decryption method and dump the decrypted plaintext
4. Common: AES-256-CBC with Key==IV (the Codegate 2013 pattern, see the .NET section of reverse-engineering/tools.md)
```

See `references/sharp-tools.md` for the specific configuration structures of red team tools.

## Boundary with reverse-engineering

- **IL2CPP / NativeAOT** → compiled to native, no CLR metadata → use `reverse-engineering/` (IDA/r2); this skill only identifies it
- **Managed .NET** (standard C# exe/dll, Mono/Unity managed layer, Xamarin) → this skill
- **Mixed (native loader + .NET payload)** → the loader part goes to `reverse-engineering/`; after the .NET payload is dumped, switch to this skill

## Output file list

Each .NET reverse engineering task should produce:
- `target-original.exe` (original sample, untouched)
- `target-clean.exe` (after de4dot unpacking)
- `notes.md` (identified obfuscator, decryptor tokens, key method addresses, configuration/C2/keys)
- `target-patched.exe` (after patching, if needed)
- `il-diff.txt` (IL before and after the patch, if a patch was made)
