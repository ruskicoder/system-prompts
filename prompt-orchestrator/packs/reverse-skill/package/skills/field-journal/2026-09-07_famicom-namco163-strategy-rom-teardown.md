# 2026-09-07 Static Teardown of a Famicom / Namco-163 Strategy RPG ROM

## Scenario classification
Binary analysis (game reverse engineering / retro console / 6502 / iNES mapper)

## Target overview
The user provided a `.nes` file inside a zip (Sangokushi 2 - Hanou no Tairiku (J), Namcot 1992),
and asked for a static analysis of the game: the mapper, memory map, 6502 kernel (boot/frame/raster), expansion audio, and the hardware check at startup.

## Scope summary (redacted)
- auth_basis: own_system (offline-sample preset, a ROM file owned by the local user)
- network_profile: offline
- asset_types: [local NES ROM file]

## Roles
- lead_role: lead
- specialists: []

## Complete execution chain

1. `master-route.ps1` → initial verdict ida-reverse (medium); `case-init.ps1 -Preset offline-sample` → PRIMARY landed on R0 `reverse-engineering/` (a better fit; 6502 needs no IDA).
2. Unzipped: contains the `.nes` + an ad readme from the download site (no technical value).
3. iNES header parsing: mapper 19 (Namco 163), PRG 256KB, CHR 256KB, battery SRAM, H-mirror bit.
4. **Found a dump anomaly**: the file is 1,048,608 bytes = exactly 2× the size the header declares. The trailing 524,304 bytes are 6395 lines of pure spaces + CRLF (the packaging tool concatenated an empty text buffer into the .nes). Took the first 524,304 bytes as the clean image.
5. `pip install capstone` → confirmed that `CS_ARCH_MOS65XX / CS_MODE_MOS65XX_6502` is available (capstone 6 ships 6502).
6. Linear disassembly desynchronized at data tables → wrote a ~80-line recursive descent tracer (follows JSR/JMP/branches, basic-block deduplication) that covers ~720 instructions of the fixed bank starting from the 3 vectors.
7. Manual annotation section by section: RESET / NMI($F800) / IRQ($FB2D) / bankswitch trampoline($F237) / raster dispatch($FB3F) / scroll update($EAF7) / CHR loading($F206).
8. `$F3BD` (the only subroutine RESET calls) identified as a hardware check: reads the bit stream of its own machine code vs `$4017` samples; mismatch → RTS and normal startup; full match → LCG(5x+1) wipes the 8KB save RAM + fills the palette with a solid color + `JMP $F41E` infinite loop.
9. CHR: rendered a 32-bank contact sheet → classified the font (0-2, including kanji officer/city names) / map / title logo ("©1992 NAMCOT") + portraits / battle sprites.
10. Produced 6 evidence entries + an HTML report (Artifact) + a mermaid raster flowchart.

## Evidence chain summary (redacted)
| E-id | severity | status | source_type | Reusable command pattern | Related Finding |
|------|----------|--------|-------------|----------------|--------------|
| E-001 | info | observed | command | `python analyze.py` (header parsing + proof of the 2x whitespace padding) | F-dump |
| E-002 | info | observed | command | `python trace.py` (recursive 6502 tracer + N163 register write points) | F-arch |
| E-005 | info | observed | command | `python check.py` (disassembly of the `$F3BD` hardware check) | F-hwcheck |

> Offline case: evidence `repro_command` holds the local script path, and notes mark it offline, exempt from the remote reproducibility requirement.

## Finding / Path summary
- top_finding: the `$F3BD` hardware authenticity check at startup compares the `$4016/$4017` bit stream; a mismatch means RTS and normal startup (real hardware/faithful emulators take this path), a full match means an LCG save wipe + hang. Mechanism high / intent (anti-piracy vs peripheral detection) medium.
- path_type: callflow
- path_one_liner: RESET→JSR $F3BD→(70 bit comparisons of 4016/4017)→BNE $F421 RTS startup ‖ full match→SRAM 5x+1 wipe→solid palette→JMP self infinite loop

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| The .nes file is twice the size the header declares, and the hash does not match the database | The packaging tool appended 6395 lines of blank text to the ROM tail | Cut out the real image with `head -c 524304` | Small |
| Linear disassembly desynchronized right near $E000 and the register write scan was empty | Code and data tables are interleaved in the fixed bank, and the linear sweep was misaligned by $F800 | Wrote a recursive descent tracer starting from the vectors | Medium |
| capstone not installed, suspected no 6502 support | n/a | capstone>=5 ships `CS_ARCH_MOS65XX`, and `CS_MODE_MOS65XX_6502` works directly | Small |

## Toolchain findings
- The MOS65XX architecture of `capstone` is enough for 6502 disassembly (common to NES/Famicom, C64, Apple II). `pip install capstone` is all it takes; python is already yes in tool-index.
- Retro console ROM reverse engineering needs no IDA/Ghidra; a recursive tracer + capstone + a home-made CHR/PNG renderer (pure stdlib zlib+struct, ~30 lines) covers triage→static→synthesis.
- master-route initially judged "NES/Famicom/6502/game" as ida-reverse; case-init corrected it to R0. R0 is the right landing point.

## Key code/commands

```bash
# de-pad a polluted .nes
head -c 524304 game.nes > game_clean.nes

# disassemble the Namco163 fixed kernel bank (last 8KB → $E000)
python -c "from capstone import *; d=open('game_clean.nes','rb').read();
md=Cs(CS_ARCH_MOS65XX,CS_MODE_MOS65XX_6502);
[print(hex(i.address),i.mnemonic,i.op_str) for i in md.disasm(d[16+0x3E000:16+0x40000],0xE000)]"
```

```
Namco 163 (mapper 19) CPU map:
  $8000 <- reg $E000 (ZP shadow $E1)
  $A000 <- reg $E800 (ZP shadow $E2, ORA #$C0 on write keeps the expansion audio on)
  $C000 <- reg $F000 (ZP shadow $E3)
  $E000 fixed = last 8KB
  CHR 8×1KB <- reg $8000..$B800 (ZP shadows $AE-$B5)
  N163 cycle IRQ: counter $5000(lo) / $5800(hi+arm), NMI reloads every frame from ZP $68/$69
  Expansion audio ports: address $F800 / data $4800, driver = PRG module $2E entry $A003
  raster engine: ZP $60=remaining split bands, $62=busy flag, $63=split table row; $FB3F dispatches by $60 to ~10 band handlers
```

## Reusable patterns/script snippets
- **Recursive descent 6502 tracer** (`trace()` in `work/sangokushi2-nes/trace.py`): ~40 lines, basic-block set deduplication, follows bcc/bcs/.../jsr/jmp, stops at rts/rti/indirect jmp. Far more reliable than a linear sweep for "banks with interleaved code and data".
- **Pure stdlib CHR→PNG** (`chrmap.py`): 2bpp planar tile decoding + a hand-written PNG (zlib.compress + struct + crc32), no PIL needed. Reusable directly for any NES/GB/GBA tile dump.
- **"The file is an integer multiple of the header-declared size" → suspect dump pollution/duplication first**: cut it and recompute the hash against the database.

## Improvement suggestions for this package
- Consider adding a `retro-console-reverse/` sub-skill (NES/SNES/GB/GBA/MD), or a section "6502 / iNES / retro consoles" in `reverse-engineering/languages*.md`: capstone MOS65XX, a recursive tracer template, a mapper quick reference (1/4/19/...), CHR/tile rendering snippets. R0 covers it today but has no targeted material.
- routing.json could add weak keywords for "famicom|nes|snes|game boy|6502|iNES|mapper" to avoid an initial verdict of ida-reverse.

## Evolution actions
- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation
- [x] Added a pitfalls record (this file)
- [x] Suggested adding retro-console material (see above; waiting for the user to confirm a PR)

## Environment information
- OS: Windows 11
- Tool versions: Python 3.13, capstone (pip latest, MOS65XX)
- Target platform/version: Nintendo Famicom, iNES mapper 19 (Namco 163), 1992 Namcot

## Redaction requirements
The target of this case is a commercial 1992 Famicom cartridge, not a private asset, with no domains/IPs/credentials. The ROM data does not leave with the journal; only format and architecture conclusions are recorded.

## Index sync
- Added a row to the "Binary / firmware / CTF" subsection of `_index.md`, statistics +1.

---
<!-- [Evolution statistics] Projects completed by this package: 22 | New patterns this time: recursive 6502 tracer + stdlib CHR→PNG | Toolchain problems fixed this time: 0 -->
<!-- [Community contribution] Ask the user whether to PR the retro-console material to the main repository -->
