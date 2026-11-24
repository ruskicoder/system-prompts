# 2026-09-17 Two-Stage "Wrapper + Encrypted Payload" Structure of a Mir2-Family Thick Client

## Scenario classification

Binary analysis / Windows thick client / Mir2 (Legend of Mir) family game client / packed payload / proxy tunnel / anti-cheat integrity checks

## Target overview

Completed an offline static reverse engineering of a Windows x86 C/S game client (`{game_root}`, with non-ASCII characters in the path): confirmed the division of labor between the "user-facing launcher" and the "real main program", the nesting of the encrypted payload, the game engine lineage, the resource container formats, and the launcher's network/privilege/self-update capability surface. `network_profile=offline` throughout; no remote was contacted.

## Complete execution chain

1. Followed the reverse-skill ladder: `RULES.md` → `MASTER-ROUTING.md` → `master-route.ps1` → PRIMARY=`thick-client` (R32) → `case-init.ps1 -Preset offline-sample` → only then started work.
2. **Solved the tool path pitfall first**: `rabin2` cannot open paths with non-ASCII characters (this project path contains a bracketed CJK character), reporting `Cannot open file` with a garbled path. Copied the sample to a pure ASCII temporary directory before analysis, keeping the original file read-only.
3. Ran a "triangle" on both PEs: sections + entropy + imports + resources + overlay. This step directly decides the later route.
4. The main program was judged a **packed stub**: `.text` entropy 8.000, overlay 24 MB with entropy 7.998, **only 4 imports in the whole program** (`LoadLibraryA`/`GetProcAddress`/`VirtualAlloc`/`VirtualFree`), entry at the start of `.text`, and that section is writable and executable.
5. The launcher was judged a **normal MSVC/MFC wrapper**: 685 imports (including `WS2_32` 21 / `CRYPT32` 8), a 22.8 MB `.rsrc`, no overlay, and the PDB leaks the internal project name and developer path.
6. Parsed the resource tree and found that the size of `MYDATA#136` (34,273,734 B) is **identical, byte for byte in count, to the main program's file size** → confirmed "the wrapper embeds the encrypted main program". Also pulled out three small payloads, `MYDATA#131/132/138`.
7. **Keystream recovery (crib drag)**: using "a PE always starts with `4D5A9000 03000000 04000000 FFFF0000`", XORed the ciphertext to recover the keystream directly. Recovered 16 bytes and verified them: **only the first 16 bytes hold**; after decrypting the whole file with this key, the entropy was still 7.9999 and `e_lfanew` did not point to `PE\0\0` → judged **position-dependent (polyalphabetic/rolling) XOR**; static decryption was blocked, so recorded the blocking point and switched surfaces.
8. Switched to **behavioral surface forensics**: GBK-aware string mining + string VA cross-reference mapping recovered the capability surface from `.rdata/.data`: an AES configuration layer (`secretkey`/`ipconfigSecretKey`/`ipconfigSecretVI`), `configServerIP`, `clientFileMD5`/`cDataTopMD5`, proxy tunnel logs, `SeDebugPrivilege`, `\pro.nlp`/`\update.temp`/`\dunupdate.`.
9. Extracted VERSIONINFO and the manifest: the internal name, version, and **`requireAdministrator`**; the company/product fields of VERSIONINFO are still `TODO:` template values, and the file is **not digitally signed**.
10. A resource container triangle settled the engine: map file header `90 01 90 01` + plaintext `"Legend of mir"` → **Mir2**; `.Pak` carries the `GAMEOFMIR` signature → the GOM engine family; `WZL`/`puk` fully encrypted.
11. **Found real runtime leftovers** (not produced by this run): `%APPDATA%\awsip\cloudx<id>.ip`, `%APPDATA%\clinkm2.data`, `pro.nlp`. Recovered the structure of each: `pro.nlp` = BOM + the full GBK path of the install directory (**anti-relocation check**); `clinkm2.data` = `u32 len` + a 32-character hex string (16-byte machine ID) + zero padding to 4096 B; `cloudx*.ip` = `u32 len` (= full file length) + ciphertext.
12. Found the only decodable layer: a file disguised as `.zip` whose header is `78 9C` (zlib, not `PK`); `zlib.decompress()` succeeded on the first try (1.30 MB → 3.09 MB).
13. Semantic recovery of the decompressed body: Delphi object/RTTI tables, including configuration dialog classes, auto-play, auto-supply, monster filters, item/skill lists, and three kinds of list files `Config\%s.%s.{Friends,Target,HeiMingDan}.txt` → judged to be **the configuration tables of a third-party game helper module distributed with the package** (static recovery only, not run).
14. Produced the report + trust boundary diagram + evidence ledger (a reproduction command for every piece of evidence) + timeline, listing the 4 failed methods separately and keeping them out of the conclusions.

## Pitfall record

| Problem | Cause | Solution | Time |
|---|---|---|---|
| `rabin2` reports `Cannot open file` with a garbled path | The tool cannot handle paths with non-ASCII characters | Copy to a pure ASCII temporary directory before analysis | Low |
| `IP`/`Nt`/`MZ` appear in "strings" in high-entropy regions | Random bytes with entropy ≈8 inevitably produce many short false hits | Take strings only from `.rdata/.data`; hits in high-entropy regions never count as evidence | Low |
| A GBK byte-pair scan produced **820,000** "Chinese" strings | GBK-decoding binary byte pairs inevitably produces mass false hits | **Abandoned the method**; used ASCII strings + semantic keywords instead | Medium |
| A UTF-16LE scan produced **56,000** fake Chinese strings | Same as above, from incidental `0x4E-0x9F` high bytes in binaries | **Abandoned the method**; discarded the results entirely | Medium |
| Brute forcing a 2-byte periodic XOR on PAK produced 8557 "feasible" keys | The constraint was too weak (printable only) and had no discriminating power | Judged a degenerate result and **discarded** it; switched to reading the stack dynamically or getting the server password table | Medium |
| The key recovered by crib drag held only for the first 16 bytes | Mistook "polyalphabetic XOR" for "fixed-period XOR" | Used the entropy after full decryption + the signature at `e_lfanew` as **counter-evidence**, confirmed the block and changed route | Medium |
| zipfile cannot open the `.zip` | The extension lies; the content is a zlib stream | Check the magic number first, then pick the decoder | Low |
| The embedded payload and the main program have **the same size but different hashes** | Mistook "size match" for "same content" | A size match is only a lead; confirm with a hash/byte-by-byte comparison | Low |

## Toolchain findings

- The trio **entropy + import count + section layout** identifies a "packed stub" in seconds and is the most time-efficient triage: `.text` entropy 8.000 with ≤ 5 imports is almost certainly a runtime decrypting loader.
- **An abnormal resource section size** is the first lead to an embedded payload; comparing the size of every `MYDATA`/custom-type resource with the sizes of known files in the directory pins the nesting relationship directly.
- **Crib drag requires counter-evidence**: after recovering a key, always verify with "the entropy after full decryption" and "structural fields (such as `e_lfanew`, `PE\0\0`)", otherwise a coincidence of fixed-period XOR passes as success.
- **Runtime leftovers are often easier to read than the binary**: configuration/cache files under `%APPDATA%` usually have a simple "length prefix + encrypted body" structure and are far more efficient to analyze than the packed main program.
- **Extensions are not trustworthy**: `.zip` is actually zlib, `.puk` is actually encrypted data, `.dat` is actually GBK text; always check the magic number first.
- For Windows projects with non-ASCII paths, **copying the sample to an ASCII path first** should be a standard prerequisite step.

## Key code/commands

```powershell
# 0) Routing and authorization gate
powershell -NoProfile -ExecutionPolicy Bypass -File "<ROOT>\skills\scripts\master-route.ps1" `
  -Hint "Windows thick client C/S game client reverse engineering" -ProjectRoot "<PROJECT_ROOT>"
powershell -NoProfile -ExecutionPolicy Bypass -File "<ROOT>\skills\scripts\case-init.ps1" `
  -Hint "<task>" -CaseName "<case>" -Preset offline-sample -Sample "<sample.exe>" -ProjectRoot "<PROJECT_ROOT>"

# 1) Avoid the non-ASCII path pitfall with an ASCII path
Copy-Item -LiteralPath "<PROJECT_ROOT>\{game}.exe" -Destination "C:\Temp\<ascii>\game.exe" -Force

# 2) Packed stub verdict (entropy / sections / imports / overlay)
& "<r2>\rabin2.exe" -I "C:\Temp\<ascii>\game.exe"
& "<r2>\rabin2.exe" -S "C:\Temp\<ascii>\game.exe"
& "<r2>\rabin2.exe" -i "C:\Temp\<ascii>\game.exe"
# If available, use r2.bat for symbolic cross-references (on Windows the main program is r2.bat, not r2.exe)
& "<r2>\r2.bat" -2 -q -e scr.color=0 -c "izz" "<sample>"
```

```python
# 3) crib drag + counter-evidence (the PE header is known plaintext)
MZ = bytes([0x4D,0x5A,0x90,0x00,0x03,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0xFF,0xFF,0x00,0x00])
ks = bytes(a ^ b for a, b in zip(cipher[:16], MZ))
# Period detection: if there is no smaller period within 16 bytes -> the fixed-period XOR hypothesis is suspect
per = next((p for p in range(1, 17) if all(ks[i] == ks[i % p] for i in range(16))), None)
# Counter-evidence: entropy still ≈8 after full decryption, or no 'PE\0\0' at e_lfanew -> polyalphabetic XOR, static path blocked
```

```python
# 4) Lying extensions: check the magic number before picking a decoder
import zlib
d = open(path, 'rb').read()
if d[:2] in (b'\x78\x9c', b'\x78\xda', b'\x78\x01'):
    out = zlib.decompress(d)          # the case where .zip is actually a zlib stream
```

## Improvement suggestions for this package

1. Add a fixed quick check **"entropy 8 + imports ≤5 ⇒ packed stub"** to the triage checklists of `thick-client` and `reverse-engineering`, with the step "compare resource sizes ↔ directory file sizes" to find nested payloads.
2. Add a mandatory **crib-drag counter-evidence** item: after recovering a key, the "full decryption entropy" and "structural fields" must be checked; asserting successful decryption from the first N bytes alone is forbidden. This run nearly misjudged at this point.
3. Add an explicit warning for "strings in high-entropy regions": keyword hits in regions with entropy ≈8 are noise and must not go into the report as capability evidence.
4. Add **"path contains non-ASCII → copy to an ASCII path first"** to the prerequisites of the Windows reverse engineering route, so the tools (rabin2/IDA plugins and so on) do not hit the pitfall repeatedly.
5. Add a **"runtime leftovers first"** hint: when the main program is packed, look in `%APPDATA%`/`%LOCALAPPDATA%`/the registry for configuration and caches first; that pays off better than grinding through the decryption algorithm.

## Reusable patterns/script snippets

1. **Two-stage wrapper identification pattern**: wrapper (normal MSVC/MFC + large resource section + network and checking capabilities) → main program embedded in the resources (size matches the same-named file in the directory) → the main program is a packed stub. Once this pattern is identified, analyze the **wrapper** first (unpacked, all strings readable) rather than the main program.
2. **Length-prefixed configuration record pattern**: `u32 length + payload`, where `length` often equals the full file length; use it to cut out the ciphertext body and to tell whether a file is truncated.
3. **Install path anchor pattern**: write the install directory into a private marker file (BOM + GBK/local encoding) and compare it with the actual path at startup ⇒ "moving it invalidates/kills it". During forensics, pin this file together with the actual directory path.
4. **Naming of integrity check fields**: camelCase key names such as `clientFileMD5` / `cDataTopMD5` are high-value signposts for locating anti-cheat logic and often appear next to `configServerIP` and the update logic.
5. **Method retirement discipline**: degenerate/non-discriminating brute force (such as weakly constrained short-period XOR) and noise-exploding heuristics (broad CJK scans of binaries) should be **explicitly retired and written into the ledger**, so their conclusions do not pollute the report.

## Evolution actions

- [x] Added pitfall records
- [x] Updated the experience index
- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation

## Environment information

- OS: Windows 11 x64
- Tool versions: radare2 6.1.4 (rabin2/rahash2/r2.bat), Python 3 (msys64 ucrt64), zlib
- Target platform/version: Windows x86 PE32 / 32-bit Mir2-family game client

## Redaction requirements

This document keeps only general structures, byte-level format features, capability categories and analysis techniques. Sample names, game names, install directories, machine IDs, internal project names, developer paths, PDB paths, real domains, file hashes and specific offsets are replaced with placeholders or omitted; no sample file or decompressed artifact is attached.
