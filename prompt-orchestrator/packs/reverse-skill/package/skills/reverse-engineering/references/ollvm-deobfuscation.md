# OLLVM Deobfuscation / Obfuscator-LLVM Deobfuscation

> OLLVM deobfuscation workflow for APK .so, ELF binaries and control flow flattening scenarios.
> Tool and variant information is based on a 2026 survey of active community projects, not training memory.
> Applies to: Android NDK hardening, CTF reverse engineering, packed .so analysis, countering commercial obfuscators.

---

## 0. Quick decision: which tool should I use?

Match your environment and your judgment of the target's obfuscation type directly:

| Your situation | First choice | Alternative | Notes |
|---------|---------|------|------|
| IDA Pro 7.5-7.7 + Hex-Rays, want one-click deflattening | **obpo-plugin** | d810-ng | obpo uses microcode + data flow + concolic execution with the strongest results, but it is a cloud plugin (needs network access, core is closed source) |
| IDA Pro (any fairly recent version), want local all-in-one deobfuscation | **d810-ng** | Original D-810 | Local, open source, integrates Z3, supports OLLVM/Tigress/Hodur/Approov and other variants |
| Binary Ninja | **ollvm-breaker** |: | Aimed at hands-on Android .so work (hardened samples such as libvdog) |
| No IDA/BN, pure script, target x86/x64 | **ollvm-unflattener** (Miasm) | angr deflat | Miasm symbolic execution, multi-layer BFS processing |
| No IDA/BN, pure script, target x86/x64 | **ollvm-unflattener** (Miasm) | angr deflat | Miasm symbolic execution, multi-layer BFS processing |
| Pure Python symbolic execution, CTF scenarios | **angr** Deobfuscator | Triton | No GUI dependency, scriptable |
| Target is an ARM64 .so, no IDA | **deollvm** (Unicorn) | angr | Unicorn-based ARM64 deflat |
| BR obfuscation (indirect branches) | **DeObfBR** | Make the data section read-only | Goron/Arkari-style BR obfuscation can be countered simply by making the data section read-only |
| Tigress obfuscation | d810-ng `UnflattenerSwitchCase`/`UnflattenerTigressIndirect` |: | d810-ng has built-in Tigress-specific unflatteners |

> **Core advice:** prefer **d810-ng** (local, actively maintained, broad variant coverage). When the cloud service is available, **obpo-plugin** gives the best results. If both fail, use **angr/Miasm** symbolic execution for custom handling.

---

## 1. The modern OLLVM variant ecosystem (2026 community survey)

OLLVM is no longer just the original 2017 repository. These are the currently active obfuscator forks; **before deobfuscating you must determine which variant the target uses**, because countermeasures differ a lot between variants:

### 1.1 Obfuscator fork lineage

| Variant | Base LLVM | New features compared with the original OLLVM | Countermeasure key points |
|------|----------|----------------------|---------|
| **Obfuscator** (original) | 3.3~4.0 | sub + bcf + fla (the three basic passes) | Every standard tool handles it |
| **Hikari** | 6~8 | Anti Class Dump, Function Call Obfuscate, Function Wrapper, Indirect Branching, Split BB, String Encryption | Decrypt strings + repair indirect jumps first |
| **Hikari-LLVM15** | 15~19 | + Anti Debugging, Anti Hook, Constant Encryption | Now closed source; Constant Encryption makes static analysis harder |
| **goron** | 7~10 | Indirect Branch/Call/GlobalVariable | Goron-style indirect obfuscation can be countered simply by "making the data section read-only" |
| **Arkari** (komimoe/Hikari) | 14~latest | Based on goron, continuously maintained | Same as goron; a read-only data section partially counters it |
| **Pluto** | 14 | MBA Obfuscation, Random CF, Split BB, **Trap Angr** (aimed specifically at angr) | The Trap Angr pass breaks angr symbolic execution; switch tools or work around the trap |
| **Polaris** (formerly Pluto) | 16 | Alias Access, Indirect Branch/Call, String Encryption, Merge Function, Linear MBA, Dirty Bytes Insertion, Function Splitting, Junk Insertion | Combines Hikari+Pluto, the trickiest; handle it layer by layer |
| **O-MVLL** | open-obfuscator | Python-driven pass manager; Anti Hooking, Arithmetic(MBA), BB Duplicate, CF Breaking, Function Outline, Indirect Branch/Call, Opaque Constants | Common in modern Android hardening; the Python configuration is easy to customize |
| **amice** (Rust) | Rust implementation | The full set + VM Flatten, Instruction Virtualization, Delayed Offset Loading, Parameter Aggregation | Includes virtualization; needs VM handler reconstruction rather than plain deflat |
| **VMP family** (SmallVmp/VMPilot/xVMP/VMPacker) |: | Instruction virtualization | **Not in the OLLVM category**; needs VM reverse engineering with VM-specific tools |

### 1.2 Key identification clues

- **Trap Angr** (Pluto/Polaris): if angr blows up or hits path explosion midway, suspect the Trap Angr pass → switch to d810-ng or a Unicorn dynamic method
- **Goron/Arkari indirect jumps**: if the dispatcher uses indirect jumps (BR x8 instead of a switch), first try making the related data section read-only; the indirect jump targets often become statically solvable
- **Constant Encryption** (Hikari-LLVM15/Polaris/O-MVLL): constants are decrypted at runtime, so pure static analysis cannot see the real values → run the decryption stub dynamically with Unicorn
- **VM Flatten** (amice): control flow becomes a VM dispatch loop; **do not treat it as ordinary fla**; identify the VM handler table first

---

## 2. OLLVM obfuscation type detection

Identification traits of the three core OLLVM passes:

### 2.1 Control Flow Flattening (`fla`)

**IDA view traits:**
- The function entry first jumps to a single dispatcher block
- The main logic is split into many basic blocks, each ending with a jump back to the dispatcher
- The dispatcher decides the next block through a **state variable**
- A huge `switch` structure with no logical relation between cases

```
Original:             OLLVM flattened:
  block_A               entry -> dispatcher
  block_B                 ↓
  block_C              state_machine:
                         switch(state):
                           0 → block_A
                           1 → block_B
                           2 → block_C
```

**Variant forms (the various dispatchers d810-ng identifies):**
- O-LLVM: switch / if-chain + state variable
- Tigress: `m_jtbl` (switch-case) or `m_ijmp` (indirect jump, needs a `goto_table_info` configuration)
- Hodur (PlugX): nested `while(1)` state machine, `jnz state, #CONST`, **no switch dispatcher**
- Approov: `while(v8 != C)`, state constants concentrated in `0xF6000–0xF6FFF`

### 2.2 Bogus Control Flow (`bcf`)

- **Unreachable fake branches** inserted between real branches
- Fake branches guarded by **opaque predicates** (always-true/always-false conditions that static analysis cannot prove directly)
- Lots of dead code inflates the function size

```c
// Classic opaque predicate: x(x+1) is always even, which the compiler cannot prove
if (x * (x + 1) % 2 == 0) {
    // Real logic
} else {
    // Unreachable junk code
}
```

### 2.3 Instruction Substitution (`sub`) → MBA

- Simple arithmetic/bitwise operations replaced with equivalent complex expressions (MBA, Mixed Boolean-Arithmetic)

```
a + b  →  (a ^ b) + 2*(a & b)
a ^ b  →  (a | b) - (a & b)
a - b  →  a + (~b) + 1
```

### 2.4 Quick classification table

| Obfuscation type | IDA trait | Main countermeasure |
|---------|---------|------------|
| fla (flattening) | Huge switch + dispatcher | obpo / d810-ng / deflat |
| bcf (bogus control flow) | Unreachable branches + dead code | d810-ng opaque predicate removal / symbolic execution |
| sub/MBA | Complex arithmetic expressions | d810-ng MBA simplifier / SiMBA (Z3) |
| fla + bcf + sub | Everything at once, extreme bloat | **Layered deobfuscation (bcf first, then fla, then sub)** |

---

## 3. Mainstream tools in detail (active community projects)

### 3.1 obpo-plugin: the strongest results, a cloud plugin

> [obpo-project/obpo-plugin](https://github.com/obpo-project/obpo-plugin) · 629 stars · active as of 2026-06

A pseudocode optimizer based on Hex-Rays **microcode** that rebuilds flattened control flow with **data flow tracking + program slicing + concolic execution**. Widely regarded in the community as one of the strongest.

**Key features:**
- Operates at the microcode layer and optimizes the decompiler output directly (does not change the ASM)
- Supports IDA 7.5.0 / 7.6.0 / 7.7.0 + Hex-Rays
- Architectures: ARM, ARM64, x86, x86_64, PowerPC, PowerPC64, MIPS (7.6/7.5)
- **Cloud plugin**: the target function binary is uploaded to obpo-server for processing (core closed source, plugin free and open source)
- The server is maintained at the author's own expense, timeout 600s, **multithreaded/abusive calls are forbidden**

**Installation and usage:**
```text
1. Download obpo_plugin.py and the obpoplugin directory
2. Copy them into the IDA plugins path
3. Restart IDA and open the target binary
4. Locate the dispatcher block in the CFG; it usually looks like this:
   [screenshot: see assets/dispatchblock.png in the repository]
5. Right-click → OBPO → Mark and process function
6. Refresh the decompiler when processing finishes
7. Depending on the decompiler changes, keep marking newly appearing dispatcher blocks (iterate for nested fla)
```

**Use cases and limits:**
- Standard and nested fla, good results
- Needs network access; use with caution on sensitive samples (internal undisclosed vulnerabilities, trade secrets) because the binary is uploaded
- The server may go down; depends on the author's maintenance
- Cannot solve every obfuscation (the author says so explicitly)

### 3.2 d810-ng: the local all-in-one first choice

> [w00tzenheimer/d810-ng](https://github.com/w00tzenheimer/d810-ng) · 223 stars · updated 2026-06-26

The modern maintained/refactored version of D-810 (Next Generation). Runs locally, open source, integrates the **Z3 SMT** solver, the broadest variant coverage.

**Core capabilities (from the d810-ng README):**

*Instruction-level optimization:*
| Category | Description |
|------|------|
| MBA simplification | `(a+b)-2*(a&b) => a^b`, DSL rules verified with Z3 |
| Hacker's Delight | Bitwise equivalences (from the book Hacker's Delight) |
| O-LLVM patterns | MBA patterns specific to Obfuscator-LLVM |
| Constant folding | 22 constant simplification rules |
| Predicate simplification | Opaque predicate removal (setz/setnz/lnot/smod) |
| Z3 rules | SMT solving when template matching fails |
| Hodur-specific | MBA patterns of the PlugX (Hodur) malware |

*Control flow unflatteners (by target obfuscation):*
| Unflattener | Target | Description |
|------------|------|------|
| `Unflattener` | O-LLVM | Standard switch/if-chain + state variable |
| `UnflattenerSwitchCase` | Tigress | Tigress switch-case dispatch (`m_jtbl`) |
| `UnflattenerTigressIndirect` | Tigress | Tigress indirect jumps (`m_ijmp`), needs a `goto_table_info` configuration |
| `HodurUnflattener` | Hodur (PlugX) | Nested `while(1)` + `jnz state, #CONST`, no switch |
| `BadWhileLoop` | Approov | `while(v8 != C)`, state constants in 0xF6000–0xF6FFF |
| `UnflattenerFakeJump` | General | Removes always-true/always-false conditional jumps |
| `SingleIterationLoopUnflattener` | Leftovers | Cleans up single-iteration loops where `INIT == CHECK` and `UPDATE != CHECK` |
| `UnflattenControlFlowRule` (experimental) | General | CFG unflattener based on path emulation |

**Installation and usage:**
```text
1. clone d810-ng
2. Install dependencies (including Z3)
3. Copy into the IDA plugins directory
4. Load the plugin in IDA with Ctrl-Shift-D
5. Tick the rule sets to apply in the GUI
6. Apply to the target function
```

**Why d810-ng rather than the original D-810:**
- The original D-810 is now less maintained
- d810-ng has CI tests, refactored code, and new Tigress/Hodur/Approov-specific unflatteners
- It integrates Z3 and falls back to SMT solving when template matching fails, with a higher success rate

### 3.3 ollvm-unflattener: Miasm symbolic execution, pure script

> [cdong1012/ollvm-unflattener](https://github.com/cdong1012/ollvm-unflattener) · 265 stars · active as of 2026-06

Based on the **Miasm** symbolic execution engine, independent of IDA/BN, a pure Python command line.

**Features:**
- Recovers the original control flow with Miasm symbolic execution (unlike the purely static approach of MODeflattener)
- **Multi-layer BFS processing**: follows the target function's calls automatically and deobfuscates recursively
- Supports Windows/Linux x86/x64
- Outputs a new deobfuscated binary

**Installation and usage:**
```bash
git clone https://github.com/cdong1012/ollvm-unflattener.git
cd ollvm-unflattener
pip install -r requirements.txt   # miasm, graphviz, keystone-engine

# Basic usage
python unflattener -i <input.bin> -o <output.bin> -t <function_addr> -a
# -a: follow calls automatically for multi-layer processing
```

**Applies to:** no IDA, x86/x64 targets, batch scripted processing.

### 3.4 ollvm-breaker: hands-on with Binary Ninja

> [amimo/ollvm-breaker](https://github.com/amimo/ollvm-breaker) · 441 stars

Deflattens with **Binary Ninja**; the repository ships the Android hardened sample `libvdog.so` as a test case and has already repaired functions such as JNI_OnLoad, crazy::GetPackageName and prevent_attach_one.

**Applies to:** Binary Ninja users, hands-on Android .so work.

### 3.5 deollvm: ARM64 Unicorn

> [GeT1t/deollvm](https://github.com/GeT1t/deollvm) · 34 stars · 2026-04

ARM64 OLLVM deflat based on **Unicorn**. An alternative for ARM64 .so without IDA.

### 3.6 DeObfBR: BR obfuscation specialist

> [Mrack/DeObfBR](https://github.com/Mrack/DeObfBR) · 96 stars · 2026-06-25

Removes **BR obfuscation** specifically (indirect branch obfuscation, Goron/Arkari style).

**Simple countermeasure (from awesome-ollvm):** Goron/Arkari-style indirect obfuscation can be countered simply by **making the data section read-only**: indirect jump targets often depend on a data section that is writable at runtime, and once it is read-only they become statically solvable.

### 3.7 angr: general symbolic execution framework

```python
import angr

proj = angr.Project("target.so", auto_load_libs=False)
cfg = proj.analyses.CFGFast()
func = proj.kb.functions[0x12345]

# Built-in Deobfuscator
deob = proj.analyses.Deobfuscator(func=func)
deob.normalize()
```

**The Trap Angr pass of Pluto/Polaris:** these two variants include traps written specifically against angr symbolic execution. If angr hits path explosion or errors, suspect Trap Angr → switch to d810-ng or a Unicorn dynamic method.

---

## 4. Complete deobfuscation workflow (by scenario)

### 4.1 General decision tree

```
Target binary
  ↓
1. Identify the OLLVM variant (see the clues in section 1.2)
  ├── Original OLLVM / Hikari / O-MVLL  → standard fla/bcf/sub
  ├── Pluto / Polaris                → watch for Trap Angr, avoid angr
  ├── Goron / Arkari                 → try a read-only data section first, then handle BR
  ├── Tigress                        → d810-ng Tigress unflattener
  ├── Hodur (PlugX)                  → d810-ng HodurUnflattener
  └── amice (with VM)                  → not plain fla; needs VM handler reconstruction
  ↓
2. Choose the tool (see the decision table in section 0)
  ├── IDA + network access + non-sensitive sample → obpo-plugin
  ├── IDA + local              → d810-ng
  ├── Binary Ninja            → ollvm-breaker
  ├── No GUI + x86/x64           → ollvm-unflattener (Miasm)
  ├── No GUI + ARM64             → deollvm (Unicorn) / angr
  └── Pure symbolic execution / CTF           → angr
  ↓
3. Layered deobfuscation (order matters)
  a) Remove opaque predicates first (bcf)   → d810-ng opaque predicate removal
  b) Then remove control flow flattening (fla) → unflattener
  c) Finally simplify MBA (sub)       → d810-ng MBA simplifier / SiMBA
  ↓
4. Verification
  ├── Is the function size significantly smaller?
  ├── Did the CFG change from a star/radial shape to a chain/tree?
  └── Do Frida hooks on key functions verify the logic is correct?
```

### 4.2 Android NDK .so deobfuscation specifics

OLLVM-hardened .so files built with the Android NDK are the most common APK reverse engineering scenario.

**Step 1: extract the .so:**
```bash
adb pull /data/app/~~/lib/arm64/libnative.so
# Or unpack the APK directly: unzip target.apk -d out/ ; find out -name "*.so"
```

**Step 2: identify OLLVM and the variant:**
```bash
readelf -a libnative.so | grep -E "Size|text"   # unusually large .text but few functions → most likely OLLVM
# Open in IDA and look at function traits:
#   huge switch → fla
#   unreachable branches → bcf
#   complex arithmetic → sub/MBA
#   indirect jumps BR x8 → Goron/Arkari, try a read-only data section
#   while(1) + jnz state → Hodur, use the d810-ng HodurUnflattener
```

**Step 3: deobfuscate (layered):**
```
a) bcf: d810-ng opaque predicate removal  (or automatic handling by obpo)
b) fla: d810-ng Unflattener / obpo-plugin / deollvm(ARM64)
c) sub: d810-ng MBA simplifier
```

**Step 4: dynamic verification with Frida:**
```javascript
// Trace the OLLVM state variable to help deflat determine its address
const target = Module.findBaseAddress("libnative.so");
console.log("[+] libnative.so @", target);

// Hook at the dispatcher entry and observe the sequence of state changes
Interceptor.attach(target.add(0x1234), {  // dispatcher offset
    onEnter(args) {
        // Read the state variable (determine the register/stack location from the decompilation)
        console.log("[state]", this.context.x8);  // assuming state is in x8
    }
});
```

### 4.3 Quick deobfuscation in CTF scenarios

CTFs are usually short on time; take the fastest path first:

```python
#!/usr/bin/env python3
"""CTF OLLVM quick deflat with angr"""
import angr

proj = angr.Project("challenge", auto_load_libs=False)
cfg = proj.analyses.CFGFast()

# Find the largest functions (the most likely to be obfuscated)
funcs = sorted(cfg.functions.values(), key=lambda f: f.size, reverse=True)[:5]
for func in funcs:
    print(f"[*] {func.name} @ {hex(func.addr)} size={hex(func.size)}")
    try:
        deob = proj.analyses.Deobfuscator(func=func)
        deob.normalize()
        print(f"    [+] deobfuscated")
    except Exception as e:
        print(f"    [-] failed: {e}")
        # angr fails → suspect Trap Angr → switch to d810-ng / Unicorn
```

---

## 5. MBA expression simplification

### 5.1 Common OLLVM MBA patterns

```python
# These identities are the simplification targets of expressions generated by the OLLVM sub pass
"(a | b) + (a & b)"        # → a + b
"(a | b) - (a & b)"        # → a ^ b
"(a ^ b) + 2*(a & b)"      # → a + b
"(a | b) & ~(a & b)"       # → a ^ b
"~(~a & ~b)"               # → a | b (De Morgan)
```

### 5.2 Tool choice

| Tool | Method | Applies to |
|------|------|------|
| **d810-ng MBA simplifier** | Batch inside IDA, Z3 verified | First choice, integrated into the decompilation flow |
| **SiMBA** (`pip install simba-simplifier`) | Command line/library | Pure expression simplification, batch processing |
| **Arybo** | Symbolic bit vectors | Large numbers of MBA expressions |
| **Z3 direct solving** | SMT | Most general, when template matching fails |

```python
# SiMBA example
from simba import simplify_mba
exprs = ["(a | b) + (a & b)", "(a ^ b) + 2*(a & b)"]
for e in exprs:
    print(f"{e}  →  {simplify_mba(e)}")
```

---

## 6. Complete deobfuscation case script

```bash
#!/bin/bash
# OLLVM deobfuscation pipeline (2026 community tools)
# For ELF/.so hardened with standard OLLVM / Hikari / O-MVLL

BINARY=$1

echo "[*] Stage 0: basic analysis and variant identification"
file $BINARY
readelf -h $BINARY 2>/dev/null | head -5
echo "    → confirm the variant in IDA (see section 1)"

echo "[*] Stage 1: d810-ng local deobfuscation (first choice)"
echo "    IDA → Ctrl-Shift-D to load d810-ng"
echo "    Tick: MBA + Opaque predicate + Unflattener"
echo "    Apply to target functions"
echo "    Save the IDB"

echo "[*] Stage 2: obpo-plugin (if d810-ng is not enough and network access is available)"
echo "    IDA → right-click the dispatcher → OBPO → Mark and process"
echo "    ⚠️ Do not use on sensitive samples (the binary is uploaded to the cloud service)"

echo "[*] Stage 3: alternative without IDA (x86/x64)"
echo "    python unflattener -i $BINARY -o deobf.bin -t <func_addr> -a"

echo "[*] Stage 4: alternative for ARM64 .so without IDA"
echo "    deollvm (Unicorn) or the angr Deobfuscator"

echo "[+] Done. Reanalyze in IDA to verify."
```

---

## 7. Common pitfalls (lessons from the community)

| Problem | Cause | Fix |
|------|------|---------|
| angr path explosion/abnormal exit | The **Trap Angr** pass of Pluto/Polaris | Switch to d810-ng or a Unicorn dynamic method |
| obpo-plugin cannot connect | The server is maintained at the author's expense and may be down | Switch to local d810-ng; you can open an issue in the obpo repository |
| Goron/Arkari indirect jump deflat fails | The dispatcher uses BR x8 rather than a switch | Make the data section read-only first, then use DeObfBR |
| Functions still messy after d810-ng | OLLVM with custom pass parameters/seed | Remove opaque predicates with symbolic execution first, then unflatten |
| Nested fla (multi-layer flattening) not fully cleaned in one pass | obpo/d810-ng clean only one layer per pass | **Iterate**: mark the newly appearing dispatcher each time |
| deflat errors on an ARM64 .so | Old deflat scripts support only x86 | Use d810-ng / obpo (ARM64 support) / deollvm |
| Hikari strings not visible | String Encryption pass | Emulate the decryption stub with Unicorn and dump the decrypted strings |
| deflat has no effect at all on amice targets | Includes VM Flatten / Instruction Virtualization | **Not OLLVM fla**; needs VM handler reconstruction (see VM reverse engineering) |
| Hodur(PugX) sample has no switch dispatcher | Nested while(1) + jnz state | Use the d810-ng **HodurUnflattener**, not the ordinary Unflattener |
| No visible pattern in Approov state constants | Constants concentrated in 0xF6000–0xF6FFF | Use the d810-ng **BadWhileLoop** unflattener |
| obpo misused on sensitive samples | The binary is uploaded to the cloud service | Use **only local tools** (d810-ng/angr) for classified/undisclosed vulnerability samples |
| Frida hook on an OLLVM function hangs | The modified state variable causes an infinite loop | Add a conditional breakpoint at the dispatcher entry to limit the execution count |

---

## 8. Tool quick reference (2026 community activity)

| Tool | Platform | Method | Stars/price | Last update | Open source | Notes |
|------|------|------|---------|---------|------|------|
| **obpo-plugin** | IDA | microcode+concolic (cloud) | 629 | 2026-06 | Plugin open source/core closed | Strongest results, needs network access |
| **ollvm-breaker** | Binary Ninja | BN API | 441 | 2026-06 | Yes | Hands-on Android .so work |
| **ollvm-unflattener** | CLI | Miasm symbolic execution | 265 | 2026-06 | Yes | x86/x64, multi-layer BFS |
| **d810-ng** | IDA | microcode+Z3 | 223 | 2026-06 | Yes | **Local first choice**, broad variant coverage |
| **DeObfBR** |: | BR obfuscation specialist | 96 | 2026-06 | Yes | Goron/Arkari indirect branches |
| **IDA_Ollvm-unflattener** | IDA | Miasm plugin edition | 90 | 2026-04 | Yes | IDA plugin wrapper of ollvm-unflattener |
| **deollvm** | CLI | Unicorn | 34 | 2026-04 | Yes | ARM64 specialist |
| **angr** | CLI | Symbolic execution |: | Active | Yes | General, countered by Trap Angr |
| **SiMBA** | CLI/library | MBA simplification |: |: | Yes | Expression simplification |
| **Triton** | CLI | Symbolic execution + taint |: | Active | Yes | Dynamic symbolic execution |

---

## 9. Reference links

**Obfuscators (for understanding the target of countermeasures):**
- [obfuscator-llvm/obfuscator](https://github.com/obfuscator-llvm/obfuscator): the original OLLVM
- [HikariObfuscator/Hikari](https://github.com/HikariObfuscator/Hikari); Hikari
- [komimoe/Hikari](https://github.com/komimoe/Hikari): Arkari (based on goron, LLVM 14+)
- [amimo/goron](https://github.com/amimo/goron): goron
- [bluesadi/Pluto](https://github.com/bluesadi/Pluto): Pluto
- [za233/Polaris-Obfuscator](https://github.com/za233/Polaris-Obfuscator): Polaris (formerly Pluto)
- [open-obfuscator/o-mvll](https://github.com/open-obfuscator/o-mvll); O-MVLL
- [fuqiuluo/amice](https://github.com/fuqiuluo/amice): OLLVM passes implemented in Rust
- [lich4/awesome-ollvm](https://github.com/lich4/awesome-ollvm): **overview of the variant ecosystem (strongly recommended to read first)**

**Deobfuscation tools:**
- [obpo-project/obpo-plugin](https://github.com/obpo-project/obpo-plugin): the strongest cloud plugin
- [w00tzenheimer/d810-ng](https://github.com/w00tzenheimer/d810-ng): local first choice
- [cdong1012/ollvm-unflattener](https://github.com/cdong1012/ollvm-unflattener): pure Miasm script
- [amimo/ollvm-breaker](https://github.com/amimo/ollvm-breaker); Binary Ninja
- [GeT1t/deollvm](https://github.com/GeT1t/deollvm): ARM64 Unicorn
- [Mrack/DeObfBR](https://github.com/Mrack/DeObfBR): BR obfuscation specialist
- [maskelihileci/IDA_Ollvm-unflattener](https://github.com/maskelihileci/IDA_Ollvm-unflattener): IDA plugin edition
- [angr](https://angr.io/): symbolic execution framework
- [SiMBA](https://github.com/tech-srl/simba): MBA simplification

**Academic/blogs:**
- [Quarkslab: Deobfuscation: Recovering an OLLVM-protected program](https://blog.quarkslab.com/deobfuscation-recovering-an-ollvm-protected-program.html): the classic deflat principles
- [MODeflattener](https://github.com/mrT4ntr4/MODeflattener): static deflat (a counterpart to ollvm-unflattener)

> Related documents: [[anti-analysis.md]] (anti-debugging/anti-analysis overview), [[tools-advanced.md]] (advanced tool set), [[elf-analysis.md]] (ELF file analysis), [[ai-assisted-re.md]] (AI-assisted reverse engineering)
