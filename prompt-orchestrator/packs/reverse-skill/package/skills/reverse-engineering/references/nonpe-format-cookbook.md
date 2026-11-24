# Non-PE / Multi-Format Agent Response Recipes U–AV + AW–DN

> Parallel to the PE anti-debugging recipes A–T (../anti-analysis.md): by **file type**, "trigger → one-line action → Evidence".  
> **Not** a second main flow. After triage identifies the type, jump to the matching skill + this table.  
> Default **authorized isolated lab / authorized samples and devices**. Device wiping, BYOVD, reflective injection and similar are written up for **detection and forensics**, not as unauthorized destruction/exploitation tutorials.  
> A failed bypass or reconstruction MUST also be recorded as Evidence; silently treating it as "harmless" is forbidden.
>
> §1–§8 / U–AV = original rules (Issue #65). §9–§23 / AW–DN = extended rules (Issue #87, deduplicated + semantically enhanced + edge-case patches).

## 0. Routing quick reference

| Type clue | Main skill | Section of this table |
|----------|----------|----------|
| .bat / .cmd / batch | malware-analysis | §1, §19 |
| .ps1 / PowerShell | malware-analysis | §2, §20 |
| Office macros / VBA / XLM / .docm/.xlsm | malware-analysis | §3 (including DD OLE extraction, DJ XLM macros) |
| .docx/.xlsx/.pptx OOXML external links / DDE / .rtf OLE | malware-analysis | §10 (including DK RTF) |
| Web/front-end JS obfuscation, JSVMP | js-reverse | §4, §21 (including DE/DF) |
| .sys / kernel drivers | reverse-engineering/kernel-driver-reverse.md + cre | §5 |
| .dll focus points | malware-analysis / re-agent-workflow | §6 (deduplicated against A–T) |
| APK / Magisk / hidden icon | apk-reverse | §7–§8, §23 |
| .pdf / PDF documents | malware-analysis | §9 |
| .wasm / WebAssembly | reverse-engineering | §11 |
| .jar/.class / Java bytecode | reverse-engineering | §12 |
| .exe(AutoIt) / .au3 | malware-analysis | §13 |
| .hta / HTML Application | malware-analysis | §14 |
| .wsf/.jse/.vbe | malware-analysis | §15 |
| .msi / Windows Installer | malware-analysis | §16 |
| .reg / registry scripts | malware-analysis | §17 |
| .vbs / VBScript | malware-analysis | §18 |
| Xposed/LSPosed modules | apk-reverse | §22 |
| ELF / Linux binaries | reverse-engineering | → elf-analysis.md, anti-analysis.md |
| Mach-O / macOS/iOS | reverse-engineering | → platforms.md |
| Python bytecode | reverse-engineering | → languages.md |

## 1. BAT/CMD (U V W)

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **U** | Many single-character SET variables + %a%%b% concatenation, or ^ line continuations splitting commands | Expand SET line by line; list the reconstructed commands; batch deobfuscation tools are optional; treating it as "no action" before reconstruction is **forbidden** | E-batch-deobf | P0 |
| **V** | Garbled text when opened, HEX header FF FE (UTF-16 LE BOM) | Confirm the BOM → convert to UTF-8, then parse; or chcp 65001 + type | E-batch-encoding | P2 |
| **W** | Many REM/:: lines, redundant GOTOs/labels drowning the real logic | Strip comments; untangle the real GOTO path; run isolated and capture the actual cmd command log | E-batch-deadcode | P1 |

## 2. PowerShell (X Z)

> The numbering keeps the proposer's convention: **there is no patch Y**.

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **X** | Multi-layer FromBase64String / Gzip / Compress / nested -replace | Decode **layer by layer**; record each layer's result separately; tools optional (PowerDecode and others), otherwise manual/scripted | E-ps-decode-layer-N | P0 |
| **Z** | Reversed strings, fragments + concatenation followed by Invoke-Expression/IEX | Reconstruct the full string; break on IEX or use script block logging; record the plaintext command as Evidence | E-ps-string-restore | P1 |

## 3. VBA macros / XLM (AA AB AC DD DJ)

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **AA** | olevba/OLEDump see only P-Code, the source stream is empty (VBA Stomping) | P-Code decompilation tools; if incomplete, observe in the Word/Excel macro debugger; state the limitations | E-vba-pcode | P0 |
| **AB** | Many Chr() concatenations or Base64 strings, suspected shellcode/nested script | Reconstruct the strings in the immediate window/a script; determine the type after decoding; watch CreateObject/Shell dynamically | E-vba-str-decode | P1 |
| **AC** | Meaningless If 1=2, or InsertLines/DeleteLines self-modification | Follow the real branch statically; bp the self-modifying APIs dynamically and dump the modified macro | E-vba-selfmod | P2 |
| **DD** | olevba/oledump detects a VBA macro project (vbaProject.bin); extensions .docm/.xlsm/.pptm | Check the OLE stream structure with oledump.py; extract the VBA source with olevba to detect suspicious APIs; check auto-executing macros such as AutoOpen/Workbook_Open | E-office-vba | P0 |
| **DJ** | .xls/.xlsm contain Excel 4.0/XLM macros (hidden in cell formulas, not a VBA stream); olevba detects XLM macro markers | Extract the XLM macro formulas with olevba --xlm; check EXEC/CALL/REGISTER functions in hidden sheets; reconstruct with XLMMacroDeobfuscator dynamic emulation | E-office-xlm | P0 |

## 4. JavaScript (AD AE AF) → main path js-reverse

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **AD** | Custom bytecode array + while/switch interpreter (JSVMP) | Find the VM entry and opcode dispatch; dynamic trace logs; AST + dynamic dual track; see js-reverse DeepDive | E-js-vmp | P0 |
| **AE** | while(1){switch} + indexes into a large string array | AST/Babel reconstruction; restore strings from array indexes; wakaru and similar optional; **do not** paste the whole PE ollvm-deobfuscation long text | E-js-deobf | P0 |
| **AF** | debugger, hijacked console, performance.now differences, DevTools detection | Disable breakpoints/fix the time source/headless browser; patch the detection point; authorized pages | E-js-anti-debug | P1 |

## 5. SYS kernel drivers (AG AH AI)

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **AG** | DriverEntry is very short, the logic is not in the entry | Scan the non-empty MajorFunction[] slots; prioritize IRP_MJ_DEVICE_CONTROL/CREATE; record the address list as evidence | E-driver-irp-handlers | P0 |
| **AH** | DeviceIoControl / IOCTL dispatch exists | Build the control code → handler table; mark METHOD_* and buffer direction; the user-mode communication surface | E-driver-ioctl | P0 |
| **AI** | The sample loads/drops a well-known vulnerable driver or an oddly signed driver (BYOVD pattern) | Compare against **public** lists such as LOLDrivers; record the driver name/hash/signature; analyze the **call intent**; do **not** expand exploit steps | E-driver-byovd | P1 |

See the kernel-driver-reverse.md flow for details; this table only adds agent action anchors.

## 6. DLL (AJ–AQ), deduplicated against A–T / #72

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **AJ** | DLL analysis looked only at exports/EP and ignored TLS or DllMain | **Both the TLS callback and DllMain must be examined**; the dynamic breakpoint order still follows the four-stage rocket (TLS→EP/DllMain→API→ExitProcess) | E-dll-tls-dllmain | P0 |
| **AK** | Export names benign in front but malicious behind, misnamed, or exports inconsistent with behavior | Cross-check the export table against actual calls; list anomalous exports | E-exports-anomaly | P0 |
| **AL** | No exports or very few, yet still loaded | Locate from the entry, strings, xrefs and callers; do not give up because "there are no exports" | E-dll-noexport | P0 |
| **AM** | A DLL missing from the static IAT is used only at runtime | **See A–T patch R** (Delay-Load / E-delay-import); no duplicate long text here | E-delay-import | P0 pointer |
| **AN** | Parameters and calling convention of exported functions must be reconstructed | Cross-references + watch registers/stack dynamically; mark stdcall/fastcall and others | E-dll-export-abi | P1 |
| **AO** | Suspected DLL hijacking/sideloading | Check same-named DLLs in the application directory, the search path, KnownDLLs; a legitimate program + anomalous DLL combination | E-dll-sideload | P1 |
| **AP** | Clues of fileless mapping/reflective loading | Memory traits, loader behavior, modules without paths; forensics in an authorized environment | E-dll-reflective | P1 |
| **AQ** | Risk lowered only because export names "do not look malicious" | Judging safety only by export names is **forbidden**; combine section permissions, entry, strings and dynamic behavior | E-dll-export-priority | P1 |

The DLL/SYS hard gates still apply: E-imports + E-exports (see re-agent-workflow).

## 7. Android device wiping / persistence (AR AS AT) → apk-reverse

> **Only authorized samples, images or test devices.** The actions are detection and extraction of IOCs and persistence paths, not carrying out destruction.

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **AR** | A Magisk module/script contains **device-wiping signature commands** such as database deletion, flashing, bulk rm of system partitions | Signature command table + module path; mark the high-risk destructive capability; do not run wiping commands | E-android-wiper-cmd | P0 |
| **AS** | Looping curl|sh / remote script pulls, unusual C2 URLs | Extract the URLs; analyze whether the downloaded content contains wiping commands; record temporary paths | E-android-wiper-backdoor | P0 |
| **AT** | /data/adb/service.d, post-fs-data.d, suspicious /system/priv-app and similar | List persistence scripts/APKs; record content summaries as evidence | E-android-persistence | P1 |

## 8. Android transparent/hidden icon (AU AV) → apk-reverse

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **AU** | Fully transparent LAUNCHER icon/empty label, Theme.NoDisplay, no LAUNCHER category, disabled component | aapt dump badging + manifest; check icon pixels after decompilation; record anomalies as evidence | E-android-hidden-icon-manifest | P0 |
| **AV** | Installed but no icon on the home screen, background traffic/autostart/high-risk permissions/dynamically restored icon | pm list vs home screen; dumpsys package; broadcasts and device_admin; record behavior as evidence | E-android-hidden-icon-behavior | P1 |

---

> **§9–§23 below are the Issue #87 extended rules (AW–DC).**
> Sections duplicating existing files were removed: ELF (→ elf-analysis.md), Mach-O (→ platforms.md), Python (→ languages.md).

## 9. Malicious PDF documents (AW AX AY AZ)

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **AW** | pdfid detects /JS, /JavaScript, /OpenAction, /AA, /Launch counts >0 (including obfuscated counts of hex-encoded names such as /4A#61#76#61...) | pdfid -e statistics (compare plain vs obfuscated counts); extract suspicious objects with pdf-parser; peepdf interactive analysis + JS emulation | E-pdf-autoaction | P0 |
| **AX** | pdfid detects /EmbeddedFile >0; object streams contain cascaded FlateDecode/ASCIIHexDecode filter chains; or encoded payloads hidden in /Annot objects | Extract stream data with pdf-parser; decode multi-level cascaded filters with peepdf (including AES-encrypted streams, security handler r5/r6); check Annotation objects; identify the decoded type with file | E-pdf-embedded | P0 |
| **AY** | Extracted PDF JS contains many eval, unescape, String.fromCharCode, atob | Trace execution in the peepdf JS emulation environment; decode Base64/Hex/ROT13 layer by layer; CyberChef as support | E-pdf-js-deobf | P1 |
| **AZ** | Anomalous PDF structure: /JBIG2Decode, manipulated XREF table, jumping object numbers | Rename suspicious keywords with pdfid -d; check known CVE exploitation patterns; extract the exploit trigger conditions | E-pdf-exploit | P1 |

## 10. Office OOXML / DDE / RTF (BA BB DK) → complements §3 VBA

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **BA** | After unzipping docx/xlsx/pptx, word/_rels/ or xl/_rels/ contain suspicious external relationships (including remote template injection) | Check *.rels external links; check vbaData.xml; extract embedded OLE objects; check protocol handler abuse (ms-msdt: / search-ms: / ms-officecmd:) | E-office-ooxml | P0 |
| **BB** | The document contains DDEAUTO or DDEEXEC field codes that run external commands through fields | Scan with olevba --dde; extract the DDE command arguments; check whether they point to PowerShell/an external exe | E-office-dde | P0 |
| **DK** | .rtf file with embedded OLE objects (not OOXML, not a classic OLE compound document) | Extract embedded OLE objects with rtfobj; analyze object types with oleobj; check Equation Editor exploitation (CVE-2017-11882 and others); identify extracted content with file | E-rtf-ole | P0 |

## 11. WebAssembly (BC BD BE)

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **BC** | The file starts with the \x00asm magic bytes; or JS code contains WebAssembly instantiation logic | Convert to text with wasm2wat; check the import section to identify host environment imports; generate pseudocode with wasm-decompile; check the Emscripten glue signature (__wasm_call_ctors) to decide whether it was compiled from JS | E-wasm-struct | P0 |
| **BD** | Many WASM functions with simple logic, function bodies split into tiny functions; or meaningless block/loop nesting | Assess the function minimization level with diswasm; deep analysis with JEB Pro / IDA WASM plugin; dynamic execution trace logs | E-wasm-obfuscation | P1 |
| **BE** | The WASM module interacts with the browser through JS imports/exports, with WebSocket, fetch, WebGL calls | Analyze the JS glue code and the WASM module together; trace data exchange in browser DevTools; extract network communication URLs/domains | E-wasm-c2 | P1 |

## 12. Java JAR/Class (BF BG BH BI)

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **BF** | Opening the JAR in JD-GUI/jadx shows meaningless short class/method names (a.a.a / _0x prefix / numeric class names); or heavy while/switch control flow obfuscation | Identify the obfuscator type (ProGuard / Allatori / ZKM); static deobfuscation with Java Deobfuscator; for heavy obfuscation trace key logic with dynamic debugging | E-java-obfuscation | P0 |
| **BG** | Many Class.forName(), Method.invoke(), Constructor.newInstance(); or a custom ClassLoader + defineClass() loading classes from byte arrays in memory; harmless imports but malicious classes loaded dynamically at runtime | View reflection call details with javap -c -v; trace Class.forName argument strings; check the source of defineClass() byte arrays; break on Method.invoke dynamically | E-java-reflection | P0 |
| **BH** | The JAR contains .so (Linux/Android) or .dll (Windows); or System.loadLibrary() calls | Extract the native library files; identify the format with file; move to the standalone ELF/PE analysis flow | E-java-native | P1 |
| **BI** | After unpacking, the JAR/ZIP contains nested JAR/WAR/EAR; high-entropy .dat/.bin/.img files in /resources, /assets | Unpack every nested archive recursively; entropy analysis to judge encryption/compression; check META-INF/MANIFEST.MF and pom.xml | E-java-nested | P1 |

## 13. AutoIt (BJ BK BL DM)

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **BJ** | PE strings contain the AutoIt / AU3 / EA05 / EA06 signatures; or the resource section contains an AutoIt script resource (distinguish from AutoHotKey; MITRE T1059.010 covers both) | Extract the compiled script with autoit-ripper; identify the encoding family (EA05 = AutoIt3.00 / EA06 = AutoIt3.26); after the EA06 header extract the 8-byte decryption key to decrypt the payload; restore the source | E-autoit-extract | P0 |
| **BK** | The extracted script contains many StringEncrypt/_StringEncrypt; or Execute dynamic execution + meaningless variable names | Static decompilation with myAutToExe; identify anti-debugging techniques; analyze the obfuscated control flow | E-autoit-deobf | P1 |
| **BL** | The script contains RegWrite (registry persistence), FileInstall (file drop), InetGet (network download), Run/RunWait | Mark the sensitive API call sequence; analyze InetGet URLs; trace FileInstall drop paths | E-autoit-malicious | P0 |
| **DM** | AutoIt as a loader performing process hollowing: CallWindowProc/EnumWindows callback + shellcode + injection into a legitimate process (regsvcs.exe and others), dropping a .NET payload (DarkGate / Snake Keylogger / ArechClient2 pattern) | Check the call chain of DllCall/DllCallbackRegister into kernel32 injection APIs; extract the shellcode data; identify the injected target process; extract the .NET payload for standalone analysis | E-autoit-hollowing | P0 |

## 14. HTA / HTML Application (BM BN BO)

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **BM** | HTML contains an HTA:APPLICATION tag, window.execScript or CreateObject calls | Check the HTA:APPLICATION attributes (Application, WindowState); extract the VBS/JS in script tags | E-hta-bypass | P0 |
| **BN** | After the HTA starts through mshta.exe, XMLHttpRequest / ActiveXObject pulls and runs a remote payload | Extract the network request URLs; trace ActiveXObject creation (ADODB.Stream and others); reconstruct the complete download-and-execute chain | E-hta-download-chain | P0 |
| **BO** | The HTA contains only a single very long obfuscated string executed through eval / execScript | Extract and decode the Base64/Hex-encoded payload; detect the encoding type recursively with CyberChef; reconstruct the payload | E-hta-oneline | P1 |

## 15. WSF / JSE / VBE (BP BQ BR BS)

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **BP** | .wsf contains \<job\> + \<script language="..."\> tags mixing JScript/VBScript/Python | Split code blocks by \<script language\>; analyze each by the rules of its language | E-wsf-multi | P0 |
| **BQ** | .jse/.vbe starts with the #@~^ signature, Microsoft Script Encoder encoding | Decode with screnc-decoder; without the tool, execute dynamically + dump the decoded script | E-jse-decode | P0 |
| **BR** | WSF with several \<script\> blocks + \<package\> referencing external resources + \<component\> referencing COM components | Build a cross-block call graph; trace function calls between \<script\> blocks; reconstruct the complete execution flow | E-wsf-call-chain | P1 |
| **BS** | WSF contains WshShell.SendKeys to bypass UAC, WshShell.Run with window style 0 to hide, WScript.Sleep delays to evade | Check whether simulated user actions are used to bypass security prompts; record the stealth execution parameters | E-wsf-anti-detect | P1 |

## 16. MSI installers (BT BU BV)

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **BT** | The MSI file contains a CustomAction table (Binary / Script / DLL custom actions) | Extract the content with msiexec /a or lessmsi; check the CustomAction table; extract the custom action binaries | E-msi-custom-action | P0 |
| **BU** | The MSI Binary table contains VBScript/JScript custom action scripts | Extract the script binaries from the Binary table and decode them into readable scripts; analyze by the VBS/JS rules | E-msi-script | P1 |
| **BV** | The MSI installs silently with /quiet /passive /qn; elevation with ALLUSERS=1 | Record the install command-line arguments; analyze the permission settings in the Property table; mark the silent + elevation combination | E-msi-privilege | P1 |

## 17. REG registry scripts (BW BX BY)

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **BW** | The .reg writes to autostart paths such as HKCU\...\Run or HKLM\...\Run | Extract every path; mark Run path entries as persistence; record the full path and value | E-reg-persistence | P0 |
| **BX** | The .reg modifies HKCR\...\shell\open\command (file association) or HKCR\CLSID\{...}\InprocServer32 (DLL injection) | Check whether shell\open\command is an unusual exe; check the InprocServer32 DLL path | E-reg-hijack | P0 |
| **BY** | The .reg modifies HKLM\...\Policies\System (UAC level), EnableLUA, ConsentPromptBehaviorAdmin | Check the default security configuration before the change; analyze the impact on UAC; mark the downgrade | E-reg-uac-bypass | P1 |

## 18. VBScript (BZ CA CB CC DN)

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **BZ** | .vbs/.js parsed by both VBScript and JScript; conditional compilation (@_win32) or cross-executed language features | Separate the VBScript/JScript code blocks; parse each; identify the mixed execution logic | E-vbs-mixed | P1 |
| **CA** | The script contains CreateObject("WScript.Shell") / CreateObject("Shell.Application") / Scripting.FileSystemObject | Mark high-risk COM object calls; trace Run/Exec arguments; trace file paths created through FSO | E-vbs-com-abuse | P0 |
| **CB** | The script starts with the #@~^ signature, Microsoft Script Encoder encoding (VBS specific) | Decode with screnc-decoder; without the tool, execute dynamically + dump the decoded script | E-vbs-encoded | P0 |
| **CC** | VBA/VBScript contains WScript.Shell.Run + cmd /c + PowerShell, followed by process injection | Trace the CreateObject COM object chain; analyze injection traits in the Run arguments; record the complete process creation chain | E-vbs-inject-chain | P0 |
| **DN** | VBScript/JScript achieves fileless persistence through a WMI ActiveScriptEventConsumer (no startup folder/registry Run key) | Check WMI event subscriptions (__EventFilter + __FilterToConsumerBinding + ActiveScriptEventConsumer); extract the bound script content; mark fileless persistence | E-vbs-wmi-persist | P0 |

## 19. Advanced BAT/CMD obfuscation (CD–CI) → complements §1 U–W

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **CD** | setlocal enabledelayedexpansion + !var! + dynamic variable names (!var_%i%!) | Expand line by line with delayed expansion enabled; Batch-Dump --expand expands automatically | E-bat-delayed-expand | P0 |
| **CE** | Reads its own or another file's :stream ADS (alternate data stream) through type/more/findstr and executes it | Check : suffix references (file.bat:payload); list ADS with dir /r; extract with type file:stream | E-bat-ads-hidden | P0 |
| **CF** | Many echo lines write a .tmp/.cmd temporary file line by line, then call executes it | Extract every echo redirection to reconstruct the temporary file content; monitor scripts generated in the temporary directory | E-bat-temp-gen | P1 |
| **CG** | for %%i in (...) do set var=%%i accumulating variables; for /f parsing command output line by line | Expand each for loop and record each iteration's assignment; serialize and reconstruct the for /f result | E-bat-for-expand | P1 |
| **CH** | The main batch receives arguments through %1 %*, with obfuscated instructions passed in by the parent process/downloader | Check the calling context and record the passed arguments; decode Base64 arguments; reconstruct the complete call chain | E-bat-param-call | P1 |
| **CI** | certutil -decode / powershell -Command / echo \| findstr combinations decode and execute | Extract and decode the Base64/Hex strings; check whether the decoded result is an executable script/PE | E-bat-encoded-exec | P0 |

## 20. Advanced PowerShell bypasses (CJ–CO, DL) → complements §2 X–Z

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **CJ** | AMSI bypasses such as [Ref].Assembly.GetType('...AmsiUtils') / amsiInitFailed / GetTypes() (including the hardware breakpoint bypass: CPU debug registers, no memory writes/VirtualProtect) | Identify the bypass pattern (patch / registry / environment variable / hardware breakpoint); confirm it took effect dynamically; mark the bypass technique type | E-ps-amsi | P0 |
| **CK** | [PSConstraintLanguage] type manipulation or modifying session state through DefaultRunspace to bypass CLM | Identify the CLM bypass pattern; mark bypass-clm; analyze the execution context after the bypass | E-ps-clm-bypass | P0 |
| **CL** | [ScriptBlock]::Create / $ExecutionContext.InvokeCommand constructors; or overriding the ScriptBlock logging settings | Check whether the script disables logging; verify dynamically whether logging was bypassed | E-ps-sb-log-bypass | P1 |
| **CM** | IEX (New-Object Net.WebClient).DownloadString(...) or [Reflection.Assembly]::Load(FromBase64...) fileless execution | Extract the download URL and check the domain/IP reputation; capture in-memory loaded code through PS logs; extract the payload in a simulated isolated network | E-ps-reflect-load | P0 |
| **CN** | Three or more nested encoding layers: outer Base64 → Gzip → XOR → plaintext (beyond the two-layer range of §2 X) | Decode recursively to plaintext or until it cannot continue; record the intermediate state of each layer; automate with PowerDecode; record each layer's result as evidence | E-ps-multi-decode | P0 |
| **CO** | Set-Alias maps IEX to single-character aliases; Get-ChildItem variable: fetches variable values dynamically | Expand every alias mapping back to the original command names; reconstruct variables through AST analysis | E-ps-alias-decode | P1 |
| **DL** | The script patches ntdll.dll EtwEventWrite (stomping) to silence telemetry; often combined with an AMSI bypass | Check for obtaining the EtwEventWrite address + a memory patch (ret 0xC3); check together with the CJ AMSI bypass; mark the double bypass combination | E-ps-etw-bypass | P0 |

## 21. Advanced JavaScript obfuscation (CP CQ DE DF) → complements §4 AD–AF

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **CP** | JS uses Proxy objects to intercept property access + the Reflect API to call methods dynamically, evading static analysis | Identify Proxy get/set/apply trap functions; trace the actual target of Reflect.get; mark the dynamic interception behavior | E-js-proxy | P1 |
| **CQ** | JS contains a _0x... hexadecimal string array + a while(!![]) infinite loop + for+switch control flow (obfuscator.io traits) | Identify obfuscator.io traits (string array + infinite loop); automatic deobfuscation with de4js / jsnice; record the reconstructed code as evidence | E-js-obfuscator | P0 |
| **DE** | The JS body is a large bytecode array + a VM interpreter loop (several while/switch), the entry points to eval/the Function constructor; the business logic is completely unreadable (a deeper case of §4 AD) | Identify the VM entry function and trace the opcode→handler mapping; hook eval output during dynamic browser execution; AST reconstruction with JSimplifier; record the opcode mapping table | E-jsvmp-deep | P0 |
| **DF** | JS uses eval to generate new code and run it immediately, document.write to rewrite the page, or the Function constructor to build function bodies dynamically | Hook eval and the Function constructor to record the generated code; capture the self-modified content through dynamic browser execution | E-js-selfmod | P1 |

## 22. Xposed/LSPosed module analysis (CR–CX) → apk-reverse

> Analyze the Xposed/LSPosed **module itself** as the reverse engineering target (not a tool-use scenario).

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **CR** | AndroidManifest.xml has no android:name entry Activity; meta-data sets xposedmodule=true | Check assets/xposed_init to determine the entry class; search for implementations of the IXposedHookLoadPackage/ZygoteInit/CmdInit interfaces | E-xp-entry | P0 |
| **CS** | The code contains XposedHelpers.findAndHookMethod / XposedBridge.hookMethod / findClass | Extract the first argument (target class) + second argument (target method) of findAndHookMethod; build the target app list | E-xp-hook-targets | P0 |
| **CT** | The module contains DexClassLoader/PathClassLoader dynamic loading; or Runtime.exec / ProcessBuilder command execution | Trace the DexClassLoader constructor arguments; extract the dynamically loaded DEX for standalone analysis; check the exec command arguments | E-xp-dynamic-load | P0 |
| **CU** | Hook targets involve sensitive APIs such as payment/biometrics/SMS/contacts/location/crypto keys | Classify hooked classes/methods by sensitivity; mark payment/biometric/SMS-contacts categories; summarize the threat level | E-xp-sensitive-hooks | P0 |
| **CV** | The code contains XposedBridge detection evasion / Zygote injection trace removal / custom network communication | Check stacktrace modification / removal of XposedBridge class references; check independent network requests (OkHttp/Socket); identify C2 targets | E-xp-anti-detection | P1 |
| **CW** | The code contains dynamic Resources replacement / View drawing interception / an AccessibilityService declaration | Check AssetManager replacement / Resources.updateConfiguration; check the AccessibilityService configuration; identify UI hijacking | E-xp-ui-hijack | P1 |
| **CX** | AndroidManifest.xml declares lsposed xposedscope meta-data; or the code contains package name allowlist checks | Parse the xposedscope target app scope; check dynamic allowlist bypass (reflection modifying scope); identify global hooks exceeding their privileges | E-xp-scope-bypass | P1 |

## 23. In-depth Magisk module analysis (CY–DC, DG–DI) → complements §7 AR–AT

> §7 focuses on device wiping/destructive behavior. This section covers non-destructive but suspicious module behavior: install script analysis, file drops, Zygisk injection, anti-detection, persistence, privilege escalation, lateral infection.

| ID | Trigger | Action (summary) | Evidence | Priority |
|----|------|--------------|----------|------|
| **DG** | The Magisk module ZIP root contains config.sh / install.sh; META-INF/com/google/android/update-binary is a non-standard installer | Extract the on_install/print_modname/set_permissions functions from config.sh/install.sh; check whether update-binary contains extra payloads; mark pm install / dd block device / mount -o remount,rw operations | E-mg-install-script | P0 |
| **DH** | The ZIP contains a system/ / vendor/ / data/ directory structure; or boot-time scripts such as post-fs-data.sh / service.sh | Extract the drop paths and identify whether APKs are dropped into /system/priv-app/; check service.sh + post-fs-data.sh content to identify boot autostart/background keep-alive/C2 communication; mark every write to system partitions | E-mg-file-drop | P0 |
| **CY** | The module contains a zygisk/ directory (native libraries such as arm64-v8a.so); or config.sh declares IS_ZYGISK=true | Extract the zygisk/ native libraries and analyze the ZygiskModule callbacks (onLoad / preAppSpecialize / postAppSpecialize); check JNI hooks | E-mg-zygisk | P0 |
| **DI** | Module scripts write into /data/adb/service.d/ or /data/adb/post-fs-data.d/; or modify crontab/init.rc (a deeper case of §7 AT) | Extract the scripts written to service.d + post-fs-data.d; check logic that infects other modules automatically on uninstall (post-uninstall.sh / module directory monitoring); check protection mechanisms triggered by magisk --remove-modules | E-mg-persistence | P0 |
| **CZ** | Module scripts use resetprop to modify system properties / magiskhide / DenyList; or integrate Shamiko (hides Zygisk itself) / TrickyStore (tampers with the certificate chain) / PlayIntegrityFork (forges the Play Integrity API) | Extract every resetprop call and identify the modified properties (ro.debuggable / ro.build.tags and others); check whether DenyList hides the module itself; identify module-level anti-detection through Shamiko/TrickyStore/PlayIntegrityFork | E-mg-anti-detect | P0 |
| **DA** | Module scripts contain setenforce 0 / mount -o rw,remount /system / chmod 777 on sensitive directories | Check SELinux operations (setenforce/chcon/restorecon); check system partition mounting + dm-verity disabling; mark high-risk privilege escalation | E-mg-privilege | P0 |
| **DB** | Dropped APKs/scripts contain curl/wget/HTTP clients; or dropped APKs request INTERNET + sensitive permissions such as READ_CONTACTS/SMS | Extract the target URLs/IPs of network requests; analyze the permission declarations of dropped APKs; identify data exfiltration logic | E-mg-c2 | P0 |
| **DC** | Scripts walk the /data/adb/modules/ directory, modify other modules' files, or write copies of themselves into other modules | Check module.prop for injected malicious instructions; check other modules' service.sh for appended malicious code; identify "parasitic" logic | E-mg-cross-infect | P0 |

---

## 24. Constraints (global)

1. **No parallel main flow**: phase gates still follow re-agent-workflow / each skill.  
2. **Evidence must be recorded**: including failures, partial reconstruction and quality= markers.  
3. **Deduplicated against A–T**: PE anti-debugging is not repeated; AM→R; AJ adds the DLL view without overturning the TLS rocket.  
4. **Missing tools**: record n/a + the manual equivalent; do not pretend a commercial suite was used.  
5. **Authorization**: destruction/injection/driver vulnerability topics are written only as defensive analysis and forensics.
6. **Extended rule deduplication**: ELF → elf-analysis.md; Mach-O → platforms.md; Python → languages.md. This table does not repeat the rules for those formats.

## 25. P0 minimal checkboxes (when a type matches)

```text
□ bat/cmd → U (+ V/W when needed; advanced CD–CI)
□ ps1 → X (+ Z; advanced CJ–CO + DL ETW)
□ vba/xlm → AA + DD + DJ (+ AB/AC)
□ office ooxml/rtf → BA + DK (+ BB if DDE is suspected)
□ heavily obfuscated js → AD or AE (+ AF; advanced CP/CQ/DE/DF)
□ sys → AG + AH (+ AI if BYOVD is suspected)
□ dll → AJ + AK/AL; Delay-Load goes to R
□ apk destruction/hiding → AR/AS or AU (+ AT/AV)
□ pdf → AW + AX (+ AY/AZ)
□ wasm → BC (+ BD/BE)
□ jar/class → BF + BG (+ BH/BI)
□ autoit → BJ + BL + DM (+ BK)
□ hta → BM + BN (+ BO)
□ wsf/jse/vbe → BP + BQ (+ BR/BS)
□ msi → BT (+ BU/BV)
□ reg → BW + BX (+ BY)
□ vbs → CA + CB + CC + DN (+ BZ)
□ xposed module → CR + CS + CT + CU (+ CV–CX)
□ magisk in depth → DG + DH + CY + DI + CZ + DA (+ DB/DC)
```
