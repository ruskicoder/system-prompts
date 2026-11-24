# 2026-08-20 Removing Server-Driven Ads from a Flutter APK (Third-Party Counterfeit Package)

## Scenario classification
APK reverse engineering / Flutter AOT patching

## Target overview
Removed server-driven banner/pop-up ads from a locally owned APK (`{target_app}` 1.0.8, a third-party counterfeit package) and produced a re-signed output.

## Scope summary (redacted)
- auth_basis: the user's own local file, modified for personal use
- network_profile: pure static analysis + local build, no ACT against external systems
- asset_types: [android_apk, flutter_aot_libapp.so]

## Roles
- lead_role: lead
- specialists: []

## Complete execution chain

1. Target identification: `{target}.apk`: Flutter 3.4.4 (libapp.so 13MB) + the 360 packer (`com.frezrik.jiagu.StubApp`; the real dex is encrypted in a 2.58MB payload at the tail of classes.dex)
2. Static reconnaissance: apktool d / jadx → no third-party ad SDK in the manifest; scanning libapp.so strings → found a server-side ad system (`ad_slot_key`/`ad_show:`/`wcstream_*` slots, the `system/banner/bannerListByMAcct` API)
3. Toolchain setup: the prebuilt blutter on gitee is ARM64-Linux (unusable) → downloaded the blutter-unmgr source → Windows MSVC build (VS2026 BuildTools + cmake + ninja) → compiled the dartvm3.4.4_android_arm64 static library (~15min) → blutter.exe analyzed libapp.so → output pp.txt/objs.txt/asm/ + frida scripts
4. Ad system recovery: class `qya` (ad model, 11 fields), `pya` (banner list), `GBg` (Map<String,dynamic>→Map<String,List<qya>> parser), every slot key and API endpoint
5. Patch design (v2 revision): **equal-length string replacement** (31 ad strings × 2 ABIs): JSON keys → junk strings (parse to null), slot keys → junk strings (lookup fails), reporting tags → junk strings. **API path strings are kept and not replaced** (after replacing them in the first version, the real device hit 404 and hung at startup; see the last pitfall entry). The client stays self-consistent while the server contract breaks.
6. String table format adaptation: arm64 packed table `[0x80|(len<<1)][chars]`; armv7 object table `[len*2 u32le][chars]`. Prefix validation + longest strings first avoid substring overlap (welfare_ad_top/welfare_ad, ad_click:/ad_click).
7. Repackaging: Python zipfile copied 1010 entries (replaced libapp.so×2, removed the old signature) → zipalign -p 4 → apksigner v1+v2+v3 (debug keystore)
8. Verification: Blutter reanalysis of the patched libapp.so passed (snapshot intact); apksigner verify passed; aapt badging consistent; the zip differs only in libapp.so + signature; 0 ad strings left in the APK
9. **Runtime verification on a real device (supplement)**: installed on a real arm64 device → enters the main screen normally, ads gone; logcat confirms zero Flutter exceptions (see the pitfall records)

## Evidence chain summary
| E-id | source_type | Reusable command pattern | Related Finding |
|------|-------------|----------------|--------------|
| E-001 | blutter_out/pp.txt | `[pp+0x210a8] String: "wcstream_banner_top"` | F-001 |
| E-002 | Patch script | `work/patch_libapp.py` | F-001 |
| E-003 | Blutter reanalysis | `python blutter.py <patched_dir> <out>` exit 0 | F-002 |

## Finding / Path summary
- top_finding: for a Flutter app with server-driven ads, removing ads needs no code logic change; equal-length replacement of the JSON keys/slot keys in the string table is enough, keeping the client internally consistent while the server contract fails; **but API path strings must not be replaced** (startup flow request 404 → jsonDecode exception → hangs at startup)
- path_type: solve
- path_one_liner: locate the string table → equal-length replacement of ad JSON keys/slot keys (keep the API paths) → repackage and sign → verify with logcat on a real device

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| 360 packer: real Java dex encrypted | jadx sees only the shell classes (com.frezrik.jiagu + a.*) | The ad logic is in the Flutter Dart layer (libapp.so), so no unpacking is needed | 0.5h |
| The prebuilt blutter from gitee does not run | The binary is ARM64-Linux (for Termux) | Downloaded the blutter-unmgr source and built x64 myself | 1h |
| Windows build: cmake cannot find cl | In cmd, %PATH% expands at parse time and overrides the vcvars environment | `cmd /V:ON` + `set PATH=...;!PATH!` delayed expansion | 0.2h |
| `string(REPLACE "/EHsc" ...)` CMake error | With an empty CMAKE_CXX_FLAGS, REPLACE lacks arguments (newer CMake) | Patched in an `if(CMAKE_CXX_FLAGS)` guard (template + generated files) | 0.2h |
| Missing asm for the obfuscated app's ad functions (size=-1) | Blutter failed to analyze obfuscated/complex functions | Dropped the code-level patch and switched to string table replacement | 0.5h |
| Finding pool entry references by hand failed | Snapshot pool entries are compressed-pointer encoded, with offsets relative to the pool base | Dropped manual encoding reversal and located the string objects directly with Blutter pp.txt | 1h |
| Substring mismatch | "welfare_ad" matched inside "welfare_ad_top" | Replace longest strings first + validate the prefix byte (arm64: 0x80\|len<<1; armv7: len*2) | 0.3h |
| **After replacing the API path, the real device hung at the startup logo** | The first version also replaced `system/banner/bannerListByMAcct` → the startup ad fetch hit a nonexistent endpoint → server 404 (error body not valid JSON) → the startup flow's `jsonDecode` threw `FormatException` (logcat `E flutter`) → the Future that enters the home page was interrupted and the UI stayed on the splash screen forever | **Do not replace API path/URL strings**; replace only JSON keys/slot keys/reporting tags. Locate with variable isolation (a control package that is only re-signed) + `adb logcat -d \| grep "E flutter"`; the MIUI install block needs `settings put global verifier_verify_adb_installs 0` | 1h |

## Toolchain findings
- blutter-unmgr (gitee.com/fest_1/blutter-unmgr): the prebuilt package is ARM64-Linux; the source includes `blutter.py` (automatic Dart version detection + build + run in one)
- Blutter Windows build dependencies: VS BuildTools (with cl) + cmake (≥3.20) + ninja + ICU/capstone (downloaded automatically by init_env_win.py)
- The CMakeLists REPLACE bug needs a patch (see above)

## Reusable patterns
**General flow for removing server-driven ads** (Flutter or native):
1. Decompile and find the ad API endpoint/model key/slot key strings
2. Confirm the string table format (arm64 packed / armv7 object / generic length-prefixed)
3. Equal-length ASCII replacement of **JSON keys/slot keys/reporting tags** (offsets preserved) → the server contract breaks; **keep the API paths**
4. Repackage + zipalign + apksigner (remember to remove the old signature first)
5. Install on a real device + verify with `adb logcat` (watch for uncaught `E flutter` exceptions and make sure the startup flow has no 404)
