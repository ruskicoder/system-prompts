---
name: ida-reverse
description: |
  IDA Pro reverse engineering assistant skill. Always use this skill when the user mentions reverse engineering, decompilation, analyzing binaries/PE/ELF/APK/DLL/SO, cracking, finding passwords, vulnerability analysis, virus analysis, firmware analysis, or needs to analyze exe/dll/so/elf/macho/sys and similar files.

  Ensure to use this skill when the user wants to analyze any binary file, regardless of whether they explicitly mention "IDA" or "reverse engineering". This includes requests like "take a look at this exe", "analyze this dll", "help me crack it", "find the password", "how do I register this software", etc.

  Use the bundled scripts (scripts/start.ps1, scripts/open.ps1) for deterministic server management and file opening; do NOT write ad-hoc PowerShell commands for these operations.
---

# IDA Pro Reverse Engineering Skill

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md` to confirm that this skill's operations are authorized routine operations
2. `NOW`: confirm whether the current task falls within the scope of this skill
3. `NEXT`: read `../tool-index.md` and verify tool availability and actual paths
4. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
5. `NEXT`: if the task involves a **debugger** or **automatic ASM patching from hints** → read `references/debugger-and-auto-patch.md`
6. `ACT`: enter the first step of the "Workflow" and execute it; do not stop at a confirmation state

## Known issues and lessons (required reading)

### Pitfalls hit

1. **Do not rely on `idb_open` (old name `idalib_open`) through MCP calls from some AI clients**
   - The MCP client of some code AI clients has a BUG in output schema validation for open-type tools
   - Error: `Structured content does not match the tool's output schema`
   - **Fix**: call the HTTP API directly with the `scripts/open.ps1` script to bypass the MCP validation layer
   - The current ida-pro-mcp 2.x tool names are `idb_open` / `idb_list` / `idb_save` (no longer `idalib_*`)
   - After the file opens it returns a `session_id` (database); later tool calls must carry that session

2. **Files under `C:\Windows\System32\` cannot be opened for lack of permission**
   - idalib cannot read files under the System32 directory directly
   - **Fix**: `open.ps1` detects this automatically, copies the file to the `temporary directory` and opens it there

3. **The server start command blocks the conversation**
   - After `idalib-mcp` starts it keeps printing INFO logs to the console
   - **Fix**: use `scripts/start.ps1` (silent background start with `-WindowStyle Hidden`)
   - The script waits until the service is ready, then exits without blocking the conversation

4. **MCP server names must not contain hyphens**
   - Using `ida-pro-mcp` as the server name before may have caused tool registration problems
   - **Current configuration**: server name `idapro`, tool prefix `idapro_*`

5. **Remote HTTP vs Local Stdio**
   - `type:"local"` (stdio) mode: `idalib_open` has the same schema validation problem
   - `type:"remote"` (HTTP) mode: open the file directly with the script first, then use the MCP tools
   - **Current approach**: Remote HTTP mode

6. **PR #389 fixed part of the schema problems**
   - The author mrexodia merged a fix through PR #389 after issue #388
   - It fixed the structuredContent schema in HTTP mode, but validation on the side of some code AI clients still has problems
   - The latest `main` branch version is installed

7. **An idalib timeout leaves an orphaned worker process holding lock files**
   - After the first `open.ps1` timeout, the idalib python worker subprocess can become orphaned and keep holding `.id0`/`.id1`/`.nam`
   - Any later tool, or dragging the file into the IDA GUI by hand, reports "insufficient permissions"
   - `taskkill /F /T` on the process tree is **forbidden**: `/T` also kills the GUI `ida.exe` child process
   - **Fix**: `start.ps1` replaces the managed supervisor only when no one listens on the port, or when `tools/list` returns quickly but lacks `py_eval` (old supervisor); an RPC timeout while 13337 still listens counts as busy and is not killed. While a database opens, `open.ps1` writes `opening.lock`, and the watchdog must not `-Force`
   - **Deadlock exception**: only when `tools/list` **has failed continuously for more than 3 minutes** (by the last-healthy timestamp, not the process creation time), with no in-flight `opening.lock` and no GUI holding the port, does it `-Force` replace the supervisor, and it still does not kill `ida.exe`
   - **Fallback**: when `open.ps1` detects that the old database is locked, it copies it to Temp automatically with a GUID prefix

8. **Opening with automatic analysis looks like a hang**
   - `idalib_open(run_auto_analysis=true)` may not respond for a long time while the backend is still opening and analyzing
   - Users previously saw "PowerShell prints nothing for a long time" and easily mistook it for a hung script
   - **Current fix**: `open.ps1` adds `-TimeoutSeconds` and switches to a background request + foreground polling + periodic progress output
   - When polling finds the session ready it returns `OK:filename:session_id` early; on timeout it returns `ERR:open_timeout_xxs`

9. **HTTP MCP exits silently after login**
   - Cursor/Claude `type: http` does not start the process on your behalf; the old scheduled task ran only once at login
   - `pythonw` has no console, and the Application log is empty when it crashes
   - **Fix**: `start.ps1` reuses the server by default when healthy; `watchdog.ps1` checks every minute; logs are in `%LOCALAPPDATA%\reverse-skill\ida-mcp\`
   - Install: `scripts/install-autostart.ps1`. If the port is not up yet when the HTTP client starts, refresh once manually in the MCP panel

10. **Streamable HTTP GET `/mcp` stalls the single-threaded supervisor**
   - Some HTTP MCP clients send a long-lived GET (SSE) to `/mcp`. The stock `idalib_supervisor` uses an `HTTPServer` with `background=False` and handles one request at a time
   - Result: `tools/list` times out and the client marks `idapro` as error
   - **Fix**: `run-supervisor.py` swaps HTTP to `ThreadingHTTPServer` and accepts GET `/mcp`; if the patch fails it is skipped and the supervisor still starts. When stuck, use `scripts/recover.ps1` (immediate `-Force`)

### Workflow principles

| Step | What to do | With what |
|------|--------|--------|
| 1 | Make sure the HTTP server is running | `scripts/start.ps1` (no arguments) |
| 2 | Open the target binary | `scripts/open.ps1 -Path "xxx.exe"` |
| 3 | Use the MCP analysis tools | Call `idapro_*` / HTTP tools directly (about 65, depending on version) |
| 4 | Analysis complete | Tools stay available automatically |

## Script resources

### start.ps1: start the MCP HTTP server

Path: `scripts/start.ps1`

- Resolves `IDADIR` automatically (environment variable / portable desktop path / common install paths)
- Prefers IDA's bundled `Python314\python.exe -m ida_pro_mcp.idalib_supervisor`
- By default probes `http://127.0.0.1:13337/mcp` first; when healthy it prints `OK:<n>:reuse` and exits
- 13337 listening but `tools/list` times out → `WARN:busy` / `OK:busy:reuse`, **no kill** (it cannot respond while a database opens or the GUI holds it)
- `tools/list` **failing continuously for more than 3 minutes** (last-healthy timestamp) with no `opening.lock` → treated as a deadlock, prints `INFO:deadlock` and `-Force` replaces the supervisor. An in-progress `idb_open` and the GUI never take this path
- Replaces the managed supervisor only when no one listens on the port, `py_eval` is missing, or the deadlock above occurs; **never kills `ida.exe`, never uses `taskkill /T`**
- When the GUI holds 13337 it prints `WARN:gui_busy` and exits without starting another supervisor
- Prints `OK:<tool count>` on success (currently about 66) and `ERR:timeout` on failure
- supervisor log: `%LOCALAPPDATA%\reverse-skill\ida-mcp\supervisor.log`
- The server runs in the background and does not block the conversation

**How to call**:
```
powershell -File "<skill-root>\ida-reverse\scripts\start.ps1"
```

### watchdog.ps1 / recover.ps1 / install-autostart.ps1: keep alive

- `watchdog.ps1`: probes 13337; healthy → reuse (and refresh last-healthy); GUI / `open.ps1` database lock / busy for less than 3 minutes since last-healthy → reuse; only `tools/list` failing continuously for more than 3 minutes leads to `start.ps1 -Force`
- `recover.ps1`: immediate `start.ps1 -Force` (does not kill `ida.exe`). Use it when the HTTP client marks `idapro` as error
- `install-autostart.ps1`: registers the scheduled task `reverse-skill-ida-mcp` (at login + every minute)
- Log: `%LOCALAPPDATA%\reverse-skill\ida-mcp\watchdog.log`

### open.ps1: open a binary file

Path: `scripts/open.ps1`

- Calls `idb_open` directly through the HTTP API, bypassing MCP schema validation
- Detects System32 paths automatically and copies to a temporary directory
- Removes old database files with the same name automatically (`.id0`/`.id1`/`.nam`/`.til`/`.i64`)
- Degrades automatically when the old database is locked: copies to Temp with a GUID prefix and opens it without an error
- Runs the open request in the background to avoid a long synchronous wait that makes the script unresponsive
- Supports `-TimeoutSeconds`; on timeout returns `ERR:open_timeout_xxs` instead of hanging forever
- Prints `INFO:opening:elapsed/timeout seconds` every 10 seconds, so you can tell analysis is still running
- Prints `OK:filename:session_id` on success, with a `(temp copy)` mark when degraded
- Retries automatically through a Temp copy on failure

**How to call**:
```
powershell -File "<skill-root>\ida-reverse\scripts\open.ps1" -Path "C:\path\to\file.exe"
```

**Optional parameters**:
```
# Specify the SessionId
powershell -File "scripts\open.ps1" -Path "file.exe" -SessionId "my_session"

# Skip automatic analysis (recommended for large files)
powershell -File "scripts\open.ps1" -Path "large.exe" -NoAutoAnalysis

# Set a timeout so opening with automatic analysis does not stay silent for long
powershell -File "scripts\open.ps1" -Path "file.exe" -TimeoutSeconds 600
```

**Output conventions**:
```
# Analysis in progress (printed every 10 seconds)
INFO:opening:11/600s

# Opened successfully
OK:sample.exe:abcd1234

# Opened successfully, but degraded to a Temp copy because of a lock file
OK:1234abcd-sample.exe:abcd1234 (temp copy)

# Timeout limit reached
ERR:open_timeout_600s
```

**Measured notes**:
- `Snipaste.exe` with automatic analysis took about `324s` to return success in a measurement; this is "long analysis", not "script deadlock"
- So for GUI programs or more complex samples, set `-TimeoutSeconds 600` explicitly

## Core tool list

### Overview analysis (first step)
- `idapro_survey_binary(detail_level="minimal")`: quick overview: function count, strings, segments, entry points, import categories (crypto/network/file IO)
- `idapro_list_funcs(queries)`: list functions (paged, filter by name)
- `idapro_list_globals(queries)`: list global variables
- `idapro_entity_query(kind, filter)`: unified query: functions/globals/imports/strings/names

### Decompilation and disassembly
- `idapro_decompile(addr)`: decompile to pseudocode
- `idapro_disasm(addr, max_instructions=N)`: disassemble
- `idapro_analyze_function(addr, include_asm=false)`: combined analysis (pseudocode + strings + constants + callers + callees + blocks)
- `idapro_func_profile(queries)`: function summary metrics

### Cross-references and data flow
- `idapro_xrefs_to(addrs)`: find who references the target address
- `idapro_xref_query(addr, direction)`: advanced xref query (direction/type filters)
- `idapro_callees(addrs)`: list of child functions
- `idapro_callgraph(roots, max_depth)`: call graph
- `idapro_trace_data_flow(addr, direction, max_depth)`: data flow tracing (forward/backward)

### Search
- `idapro_find_regex(pattern, limit)`: regex search over strings
- `idapro_search_text(pattern)`: search text in the disassembly listing
- `idapro_find_bytes(patterns, limit)`: byte pattern search (supports ?? wildcards)
- `idapro_find(type, targets)`: advanced search (immediates/strings/references)

### Memory and data
- `idapro_get_bytes(addrs)`: read raw bytes
- `idapro_get_string(addrs)`: read strings
- `idapro_get_int(queries)`: read integer values
- `idapro_get_global_value(queries)`: read global variable values
- `idapro_read_struct(queries)`: read struct field values
- `idapro_search_structs(filter)`: search structs

### Modification operations
- `idapro_set_comments(items)`: add comments (two-way sync between disassembly and decompilation)
- `idapro_append_comments(items)`: append comments
- `idapro_rename(batch)`: bulk rename (functions/globals/locals/stack variables)
- `idapro_patch_asm(items)`: patch assembly instructions
- `idapro_patch(patches)`: patch bytes
- `idapro_define_func(items)`: define functions
- `idapro_undefine(items)`: undefine
- `idapro_define_code(items)`: convert bytes to code

### Type system
- `idapro_declare_type(decls)`: declare C structs/enums/unions
- `idapro_set_type(edits)`: apply types to functions/globals/locals
- `idapro_infer_types(addrs)`: infer types
- `idapro_type_query(queries)`: query declared types
- `idapro_type_inspect(queries)`: inspect type details

### Stack frame
- `idapro_stack_frame(addrs)`: view stack frame variables
- `idapro_declare_stack(items)`: declare stack variables
- `idapro_delete_stack(items)`: delete stack variables

### Signatures
- `idapro_make_signature(addrs)`: generate a unique byte signature for an address
- `idapro_make_signature_for_function(addrs)`: generate a signature for a function
- `idapro_find_xref_signatures(addrs)`: generate signatures for code that references an address

### Debugger + hint-driven ASM patch (#136)
- `idapro_open_file(file_path)`: open a file in a GUI IDA instance
- Debugger tools are hidden by default; append `?ext=dbg` to the MCP URL to enable them (**GUI IDA only**; run `start-gui.ps1` first)
- Static patch: `idapro_patch_asm(items)` / `idapro_patch(patches)` (see "Modification operations")
- **Contract for automatic patching from a prompt**: analyze and locate the address → generate a patch plan JSON → validate with `scripts/apply-asm-patch.py --dry-run` → apply through MCP or `--apply` → re-disassemble to verify → write Evidence
- Complete steps / hard rules / anti-patterns: `references/debugger-and-auto-patch.md`
- The authorization gate is unchanged: ACT against the target is forbidden until `scope.md` has `auth.status=granted`; `case-guard --Force` must not bypass it

### Session management (ida-pro-mcp 2.x)
- `idapro_idb_open` / HTTP `idb_open`: prefer opening with `open.ps1`
- `idapro_idb_list` / HTTP `idb_list`: list every session
- `idapro_idb_save` / HTTP `idb_save`: save the database
- Most analysis tools need a `database=<session_id>` parameter (the session printed by open.ps1)

### Other
- `idapro_int_convert(inputs)`: number base conversion (**you must use this; do not convert bases yourself!**)
- `idapro_export_funcs(addrs, format)`: export functions (json/c_header/prototypes)
- `idapro_py_eval(code)`: run Python in the IDA context
- `idapro_server_health()`: server health check
- `idapro_server_warmup()`: warm up subsystems (string cache, Hex-Rays and others)

## Complete reverse engineering workflow

### Step 1: Start the server

**Path A: Headless idalib (needs a valid license)**
```
powershell -File "scripts/start.ps1"
```
Output `OK:<tool count>` (currently about 65) means ready.

**Path B: GUI + plugin (when the idalib license fails or interactive analysis is needed)**
```
powershell -File "scripts/start-gui.ps1" -Path "C:\target.exe"
```
Or double-click the portable `Launch-IDA-Pro.cmd` and open the sample in IDA.

Once the Output window shows `[MCP] ... port=13337`, the MCP tools are available.

See `LOCAL-SETUP.md` for the general connection steps.

### Step 2: Open the file

Headless:
```
powershell -File "scripts/open.ps1" -Path "C:\target.exe" -TimeoutSeconds 600
```
Output `OK:filename:session_id` means success (a trailing `(temp copy)` means it degraded to a temporary copy automatically).

If `ERR:idalib_license:...` appears, switch to Path B (GUI mode); do not retry open.ps1 repeatedly.

GUI mode: Open the sample directly in IDA; open.ps1 is not needed.

### Step 3: Global overview (with the import table hard gate)
```
idapro_survey_binary(detail_level="minimal")
```
Focus on:
- Architecture (x86/x64/ARM)
- Entry point (main/WinMain/DllMain)
- Interesting strings (URLs, paths, error messages)
- **Import categories (MUST)**: crypto functions / network APIs / file operations / process injection / registry; must be recorded as Evidence (suggested id: `E-imports`); use `idapro_entity_query(kind="imports")` or the imports section of the survey output
- **DLL/SYS**: export table alongside the import table (Evidence `E-exports`)
- **.NET**: without a traditional IAT, write a summary of modules/metadata/managed references into the E-imports semantic slot as the equivalent anchor
- **Clean import table**: note the suspicion of dynamic loading and push for dynamic API breakpoint verification
- Hot functions (functions with high xref counts are usually key logic)

**Hard gate**: until the imports view/category summary (or a valid equivalent anchor) is written to Evidence, you MUST NOT enter Step 4 deep conclusions and MUST NOT claim the survey is complete. When the import table is empty or the query fails, you still MUST record the failure. When IAT repair of a packed binary fails, you MUST record `E-iat-repair-fail` and switch to dynamic debugging to capture APIs; grinding on static is forbidden. When the user asks to redo the import table/IAT check, you MUST redo the named step (when blocked, apply the feasibility gate: explain + confirm; if forced, mark quality=unreadable); swapping in an unrelated step is forbidden.

### Step 4: Dig into key functions
```
idapro_analyze_function(addr="key function name")
```
Or:
```
idapro_decompile(addr="function name")
idapro_disasm(addr="function name", max_instructions=50)
```

### Step 5: Data flow and cross-references
```
idapro_xrefs_to(addrs="key address/string")
idapro_callgraph(roots=["key function"], max_depth=3)
idapro_trace_data_flow(addr="key address", direction="backward", max_depth=5)
```

### Step 6: Record and refine
```
idapro_set_comments(items=[{"addr": "0x140001000", "comment": "your understanding"}])
idapro_rename(batch={"func": [{"addr": "function address", "name": "meaningful name"}]})
```

### Step 7: Write the report
After the analysis, produce `report.md` recording the findings and steps.

## Prompt engineering guidelines

1. **Do not convert bases by hand**: whenever a number needs converting, use `idapro_int_convert`
2. **Survey first, then dig in**: look at the overview before targeted analysis
3. **Keep adding comments and renames**: update function and variable names throughout the analysis to improve the accuracy of later analysis
4. **Follow cross-references**: when you find interesting data/strings, use `xrefs_to` to see who references them
5. **For obfuscated code**: preprocess first with string decryption, import hash removal, control flow flattening removal and similar
6. **C++ STL code**: identify library functions with FLIRT/Lumina first, then analyze the business logic
7. **Do not brute force**: derive the solution from the disassembly and use simple Python for calculations
8. **On "No database bound"**: no binary is open yet; run `open.ps1` first
9. **On "Failed to open database"**: an old database file may be locked; `open.ps1` degrades to a Temp copy automatically (the output carries a `(temp copy)` mark)
10. **When opening GUI/complex samples with automatic analysis**: add `-TimeoutSeconds 600` by default, and do not mistake a long `INFO:opening:...` for a hung script

---

## Routing context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Upstream alternative**: `radare2/` (if you do not want to open IDA, run quick r2 reconnaissance first)
**Downstream exits**:
- Frida dynamic verification needed → `reverse-engineering/tools-dynamic.md`
- Symbolic execution/angr needed → `reverse-engineering/tools-dynamic.md`
- General reverse engineering methodology needed → `reverse-engineering/SKILL.md`

**Sibling modules**: `radare2/` (alternative when IDA is unavailable)

---

## On-Demand Bootstrap

This skill's entry scripts are wired into the unified bootstrap system.

### Automation boundaries

| Tool | Auto-installable | Install method | Notes |
|------|-----------|---------|------|
| idalib-mcp | ✓ | pip install (from GitHub) | Installed automatically when `start.ps1` finds it missing |
| IDA Pro itself | ✗ | Commercial software, install manually | Set the `IDADIR` environment variable to the install directory |

### Install steps (verified)

```cmd
# 1. Set the IDA path (replace with your actual IDA install directory)
setx IDADIR "<your IDA install directory>"

# 2. Install ida-pro-mcp from GitHub (ida-mcp on PyPI is a different project; do not install the wrong one!)
pip install git+https://github.com/mrexodia/ida-pro-mcp.git

# 3. Install the IDA plugin (choose Streamable HTTP + Global + select all clients)
ida-pro-mcp --install

# 4. Restart IDA Pro and open the target file
# The plugin listens on 127.0.0.1:13337 automatically

# 5. Verify
ida-pro-mcp --config
```

> **Note**: the `ida-mcp` package on PyPI (author jtsylve) is a different project, not the one we need.
> You must install `mrexodia/ida-pro-mcp` from GitHub.

### Bootstrap trigger points

- `scripts/start.ps1`: calls `bootstrap-reverse.ps1` automatically when `idalib-mcp` is missing
- MCP registration: bootstrap writes `idapro` into the Claude MCP configuration automatically

### Prerequisites

- IDA Pro is installed and the `IDADIR` environment variable is set (or the default path in the script is correct)
- Prefer the `ida-pro-mcp` in IDA's bundled Python314 (the portable edition already includes it)
- Common local configuration:
  - User env `IDADIR` → IDA install directory (containing `ida.exe`)
  - Optional `~\Tools\bin\idalib-mcp.cmd` / `ida-pro-mcp.cmd` wrappers
  - Keep only `idapro` as the client MCP server name → `http://127.0.0.1:13337/mcp`


## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Are survey/imports written to Evidence (E-imports or equivalent)? Does a DLL/SYS include E-exports? Did an IAT failure record E-iat-repair-fail?
- [ ] If the user asked to redo the import table/IAT, did I redo the same step?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
