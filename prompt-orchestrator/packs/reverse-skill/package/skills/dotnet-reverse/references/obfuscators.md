# .NET Obfuscator Deobfuscation in Detail

Identification, unpacking and anti-tamper bypass for mainstream .NET obfuscators. Core tools: **de4dot** (detects most packers automatically) + **dnSpyEx** (manual patching) + **dnlib** (scripting).

## Overall decision table

| Obfuscator | de4dot type | Typical traits | Automatic unpacking | Manual key points |
|--------|-------------|---------|---------|---------|
| ConfuserEx 1.x/2.x | `cfze` | anti-tamper, control flow distortion, string encryption, anti-debugging | Yes: mostly automatic | New versions need anti-tamper patched first |
| ConfuserEx 3.x / private forks | `cfze` | Same as above + custom protector | partial | Runtime dump / dnlib |
| SmartAssembly | `sa` | String encoding, resource compression, hidden method calls | Yes: automatic | Resource decompression |
| Babel.NET | `babel` | Method body encryption, control flow, strings | Yes: automatic |: |
| Eazfuscator.NET | `eaz` | String/resource encryption, expression obfuscation | partial | String decryptor |
| .NET Reactor | `reactor` | necrobit (code section encryption) + anti-tamper | hard for new versions | dump + rebuild metadata |
| Themida .NET |: | Outer shell + virtualization | No: de4dot cannot | Dump memory, use the native approach |
| Agile.NET / CliSecure | `agile` | Method body encryption | Yes: automatic |: |

## Standard de4dot usage

```powershell
# Automatic detection (enough in most cases)
de4dot target.exe -o target-clean.exe

# Specify the type explicitly (when automatic detection fails)
de4dot --type cfze target.exe -o target-clean.exe

# Probe the packer type first
de4dot --detect target.exe

# Batch
de4dot *.exe

# Decrypt strings only, leave control flow alone (minimal intervention)
de4dot --strtyp delegate --strtok METHOD_TOKEN target.exe
```

de4dot's `--strtyp` / `strtok` mode only decrypts string decryptors (with the decryption method token given) and keeps the original control flow. It suits the "I only want the plaintext strings and do not want to touch anti-tamper" case.

---

## ConfuserEx (most common)

### Trait identification

- The entry module `<module>` class carries an anti-tamper check with `[MethodImpl(NoInlining)]`
- Many string decryptor calls with `Dictionary<string, T>`
- Control flow flattening (switch dispatch + state variable)
- `.cmp` compressed resources embedded in resources
- dnSpyEx C# view: garbled class/method names (`\uXXXX` or meaningless characters), method bodies full of `int num = ...; switch(num)`

### Unpacking flow

```powershell
# 1. Standard unpacking
de4dot target.exe -o target-clean.exe

# 2. If de4dot reports "unknown" or the result does not open → a new/private ConfuserEx version
#    Confirm anti-tamper first:
Open in dnSpyEx → find the integrity check in Module .cctor or Main
```

### anti-tamper bypass (common in new ConfuserEx versions)

ConfuserEx `anti tamper` checks method body hashes at runtime and crashes when they change. de4dot usually handles old versions; new versions need manual work:

```text
Method A: patch the check function directly in dnSpyEx:
  1. Find the anti-tamper check method (usually called from the static constructor of <module>)
  2. IL edit: change the check method body to ret (return directly)
  3. Save → feed it to de4dot again

Method B: runtime dump:
  1. Run it and dump the in-memory assembly with MegaDumper / ExtremeDumper
  2. The dump is already decrypted; clean up the leftovers with de4dot
```

### After control flow restoration

de4dot restores flattened switch dispatch to normal if/while. If it is not fully restored (leftover state machine), run de4dot again or follow the IL by hand.

---

## SmartAssembly

```powershell
de4dot --type sa target.exe -o target-clean.exe
```

Traits:
- Strings encoded with the `SmartAssembly.Runtime.Strong` family
- Resource compression (`{assembly}.Resources`)
- Hidden method calls (`ProcessCaller` / indirect calls)

de4dot has the best compatibility with SmartAssembly and usually handles it in one command.

---

## .NET Reactor (necrobit)

The **necrobit** feature of `.NET Reactor` stores the real method bodies encrypted in resources and decrypts and injects them at runtime; the original method bodies are empty shells. de4dot works for old versions and often fails on new ones (4.x+).

```text
When de4dot fails:
1. Let the program run (dotnet target.exe or double-click)
2. Dump the process memory with MegaDumper / ExtremeDumper → export the decrypted assembly
3. Clean the leftover obfuscation of the dump with de4dot
4. If the metadata is damaged, rebuild it with dnlib (see common-workflow.md)
```

---

## Manual string decryptor extraction

Obfuscators encrypt strings and call a decryption method at runtime to restore them. de4dot detects most decryptors automatically; when it fails, do it manually:

```text
1. Find the decryption method in dnSpyEx (usually a fixed signature: static string Decrypt(int) or Decrypt(string, int))
   - Traits: called many times, numeric constant arguments, returns string
2. Note the method token (such as 0x06000012)
3. Point de4dot at the decryptor:
   de4dot --strtyp delegate --strtok 0x06000012 target.exe -o target-clean.exe
```

If the decryption method itself is obfuscated (control flow flattening), remove the control flow obfuscation first, then locate the decryptor.

## Common anti-debugging techniques

| Technique | Location | Bypass |
|------|------|------|
| `Debugger.IsAttached` check | Any method | IL change to `ldc.i4.0; ret` or patch the getter |
| `Debugger.IsLogging` |: | Same as above |
| Timing detection (`DateTime.Now` difference) | Method entry | Patch out the difference comparison |
| `CheckRemoteDebuggerPresent` P/Invoke |: | nop the call |
| Exception-driven control flow (try/catch path selection) | Main logic | Cannot simply nop; analyze the real path through the catch block |

> .NET anti-debugging is simpler than native: most of it is managed API calls, and one IL line change in dnSpyEx is enough.

## Fallbacks when de4dot fails

1. **de4dot --detect** to see the detection result, compared with the table above
2. **Runtime dump** (MegaDumper / ExtremeDumper / Process Hacker module export)
3. **dnlib script** to decrypt manually (see the dnlib section of common-workflow.md)
4. **Dynamic first**: run it, break at the decryption point and read the plaintext directly; intelligence is available without unpacking

Community references: Washi's blog "misconceptions-about-dotnet" (common misconceptions in IL analysis), the Kanxue .NET reverse engineering board, Guided Hacking "Top 5 .NET RE Tools".
