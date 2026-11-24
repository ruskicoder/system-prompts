# IDA Pro MCP Tool Quick Reference

> ida-pro-mcp 2.x tools grouped by function, with common parameters and typical usage.
> Server name: `idapro`, tool prefix: `idapro_*`, runs in HTTP mode. The tool count varies by version (about 66, including `py_eval`).

---

## Start and session management

### Server start

```powershell
# Start the MCP HTTP server (silent in the background; healthy → OK:<n>:reuse)
powershell -File "scripts/start.ps1"
# Output OK:<tool count> means ready (about 66, including py_eval)

# Open the target file (bypasses schema validation)
powershell -File "scripts/open.ps1" -Path "C:\target.exe"
# Output OK:filename:session_id

# Add a timeout for large files/GUI programs
powershell -File "scripts/open.ps1" -Path "C:\big.exe" -TimeoutSeconds 600

# Skip automatic analysis (fast open)
powershell -File "scripts/open.ps1" -Path "C:\huge.sys" -NoAutoAnalysis
```

### Session tools

| Tool | Purpose | Example |
|------|------|------|
| `idapro_idb_list()` / HTTP `idb_list` | List every session |: |
| `idapro_idb_open()` / HTTP `idb_open` | Open a database (prefer `open.ps1`) | Large files go through the script |
| `idapro_idb_save(path)` / HTTP `idb_save` | Save the database | Save analysis progress |
| `idapro_idb_current()` | Currently bound session (if the version provides it) |: |
| `idapro_idb_switch(session_id)` | Switch sessions | When comparing several files |
| `idapro_idb_close(session_id)` | Close a session | Release resources |
| `idapro_server_health()` | Server health check |: |
| `idapro_server_warmup()` | Warm up subsystems | Before first use |

---

## Step one: global overview

### survey_binary: quick overview

```
idapro_survey_binary(detail_level="minimal")
```

Returns:
- Architecture (x86/x64/ARM/MIPS)
- Entry point
- Total function count
- String statistics
- Segment information
- Import categories (crypto/network/file IO/registry)
- Hot functions with high xref counts

**detail_level options**:
- `"minimal"`: quick overview (recommended first choice)
- `"standard"`: more detail
- `"full"`: complete information

### Function list

```
# List every function (paged)
idapro_list_funcs(queries=[{"offset": 0, "limit": 50}])

# Filter by name
idapro_list_funcs(queries=[{"filter": "crypt", "offset": 0, "limit": 20}])
idapro_list_funcs(queries=[{"filter": "main", "offset": 0, "limit": 10}])
```

### Unified query

```
# Query imported functions
idapro_entity_query(kind="imports", filter="Create")

# Query strings
idapro_entity_query(kind="strings", filter="http")

# Query every named symbol
idapro_entity_query(kind="names", filter="")
```

---

## Decompilation and disassembly

### Decompile (pseudocode)

```
# By function name
idapro_decompile(addr="main")
idapro_decompile(addr="sub_140001000")

# By address
idapro_decompile(addr="0x140001000")
```

### Disassemble

```
# Default instruction count
idapro_disasm(addr="main")

# Specify the instruction count
idapro_disasm(addr="0x401000", max_instructions=100)
```

### Combined analysis (recommended)

```
# Get in one call: pseudocode + strings + constants + callers + callees + basic blocks
idapro_analyze_function(addr="main", include_asm=false)

# Include assembly
idapro_analyze_function(addr="sub_401000", include_asm=true)
```

### Function summary

```
# Get function metrics in bulk (size, block count, xref count)
idapro_func_profile(queries=["main", "sub_401000", "sub_402000"])
```

---

## Cross-references and call graphs

### Who references the target

```
# See who calls a function
idapro_xrefs_to(addrs=["sub_401000"])

# See who references a string/data
idapro_xrefs_to(addrs=["0x404000"])

# Batch query
idapro_xrefs_to(addrs=["CreateFileW", "ReadFile", "WriteFile"])
```

### Advanced xref query

```
# Specify direction and type
idapro_xref_query(addr="0x401000", direction="to")    # who references me
idapro_xref_query(addr="0x401000", direction="from")  # whom I reference
```

### Callee list

```
idapro_callees(addrs=["main"])
```

### Call graph

```
# Start from main, depth 3
idapro_callgraph(roots=["main"], max_depth=3)

# Several starting points
idapro_callgraph(roots=["sub_401000", "sub_402000"], max_depth=2)
```

### Data flow tracing

```
# Trace backward: where does this value come from
idapro_trace_data_flow(addr="0x401050", direction="backward", max_depth=5)

# Trace forward: where does this value flow
idapro_trace_data_flow(addr="0x401050", direction="forward", max_depth=5)
```

---

## Search

### String search (regex)

```
# Search for URLs
idapro_find_regex(pattern="https?://", limit=20)

# Search for file paths
idapro_find_regex(pattern="C:\\\\", limit=20)

# Search for error messages
idapro_find_regex(pattern="error|fail|invalid", limit=30)

# Search for keys/passwords
idapro_find_regex(pattern="key|password|secret|token", limit=20)
```

### Disassembly text search

```
# Search in the disassembly listing
idapro_search_text(pattern="call    sub_")
idapro_search_text(pattern="xor     eax, eax")
```

### Byte pattern search

```
# Exact bytes
idapro_find_bytes(patterns=["48 8B 05"], limit=10)

# With wildcards
idapro_find_bytes(patterns=["48 89 ?? 24 ??"], limit=10)

# Several patterns
idapro_find_bytes(patterns=["CC CC CC CC", "90 90 90 90"], limit=5)
```

### Advanced search

```
# Search immediates
idapro_find(type="immediate", targets=["0xDEADBEEF"])

# Search string references
idapro_find(type="string", targets=["password"])
```

---

## Memory and data reads

### Read raw bytes

```
idapro_get_bytes(addrs=[{"addr": "0x401000", "size": 64}])
```

### Read strings

```
idapro_get_string(addrs=["0x404000", "0x404100"])
```

### Read integers

```
idapro_get_int(queries=[{"addr": "0x405000", "size": 4}])
```

### Read global variables

```
idapro_get_global_value(queries=["g_flag", "g_key_size"])
```

### Read structs

```
idapro_read_struct(queries=[{"addr": "0x405000", "type": "HEADER"}])
```

### Search structs

```
idapro_search_structs(filter="FILE")
```

---

## Modification operations

### Add comments

```
# Single comment
idapro_set_comments(items=[{"addr": "0x401000", "comment": "decryption function entry"}])

# Batch comments
idapro_set_comments(items=[
    {"addr": "0x401000", "comment": "XOR decryption loop"},
    {"addr": "0x401050", "comment": "key initialization"},
    {"addr": "0x4010A0", "comment": "result check"}
])

# Append a comment (does not overwrite existing ones)
idapro_append_comments(items=[{"addr": "0x401000", "comment": "addendum: key length 16"}])
```

### Rename

```
# Rename a function
idapro_rename(batch={"func": [
    {"addr": "sub_401000", "name": "decrypt_payload"},
    {"addr": "sub_402000", "name": "verify_license"}
]})

# Rename a global variable
idapro_rename(batch={"global": [
    {"addr": "0x405000", "name": "g_encryption_key"}
]})

# Rename a local variable
idapro_rename(batch={"local": [
    {"func": "decrypt_payload", "old": "v1", "name": "plaintext_buf"}
]})
```

### Patch assembly

Prompt-driven auto-patch contract (dry-run → apply → Evidence): see [debugger-and-auto-patch.md](debugger-and-auto-patch.md).
Helper: `python3 skills/ida-reverse/scripts/apply-asm-patch.py --plan patch_plan.json --dry-run`.

```
# NOP out detection code
idapro_patch_asm(items=[{"addr": "0x401050", "asm": "nop"}])

# Change a jump
idapro_patch_asm(items=[{"addr": "0x401060", "asm": "jmp 0x401080"}])

# Force return true
idapro_patch_asm(items=[
    {"addr": "0x401000", "asm": "mov eax, 1"},
    {"addr": "0x401005", "asm": "ret"}
])
```

### Patch bytes

```
# Write bytes directly
idapro_patch(patches=[{"addr": "0x401050", "bytes": "9090909090"}])
```

---

## Type system

### Declare structs

```
idapro_declare_type(decls=[{
    "name": "PacketHeader",
    "decl": "struct PacketHeader { uint32_t magic; uint16_t type; uint16_t length; uint8_t data[0]; };"
}])
```

### Apply types

```
# Set a function prototype
idapro_set_type(edits=[{
    "addr": "sub_401000",
    "type": "int __fastcall decrypt(void *buf, int size, const char *key)"
}])

# Set the type of a global variable
idapro_set_type(edits=[{
    "addr": "0x405000",
    "type": "PacketHeader"
}])
```

### Infer types

```
idapro_infer_types(addrs=["sub_401000", "sub_402000"])
```

### Query/inspect types

```
idapro_type_query(queries=["Packet"])
idapro_type_inspect(queries=["PacketHeader"])
```

---

## Stack frame analysis

```
# View a function's stack frame
idapro_stack_frame(addrs=["main", "sub_401000"])

# Declare stack variables
idapro_declare_stack(items=[{
    "func": "sub_401000",
    "offset": -0x20,
    "name": "local_buf",
    "type": "char [32]"
}])
```

---

## Signature generation

```
# Generate a unique byte signature for an address
idapro_make_signature(addrs=["0x401000"])

# Generate a signature for a whole function
idapro_make_signature_for_function(addrs=["decrypt_payload"])

# Generate signatures for code that references an address
idapro_find_xref_signatures(addrs=["0x405000"])
```

---

## Number base conversion

```
# Hexadecimal → decimal
idapro_int_convert(inputs=["0x401000"])

# Decimal → hexadecimal
idapro_int_convert(inputs=["4198400"])

# Batch conversion
idapro_int_convert(inputs=["0xDEAD", "0xBEEF", "12345"])
```

> **Always use this tool for base conversion; never compute it yourself!**

---

## Export and scripting

### Export functions

```
# JSON format
idapro_export_funcs(addrs=["main", "sub_401000"], format="json")

# C header
idapro_export_funcs(addrs=["main", "sub_401000"], format="c_header")

# Function prototypes
idapro_export_funcs(addrs=["main", "sub_401000"], format="prototypes")
```

### Run Python scripts

```
# Run Python in the IDA context
idapro_py_eval(code="import idautils; print(list(idautils.Functions())[:10])")

# Get segment information
idapro_py_eval(code="import idc; print(idc.get_segm_name(0x401000))")

# Batch operations
idapro_py_eval(code="import ida_funcs; f=ida_funcs.get_func(0x401000); print(f.size())")
```

---

## Typical analysis flows

### Malware analysis

```text
1. survey_binary → look at imports (network APIs? crypto? registry?)
2. find_regex("http|socket|connect") → find network-related strings
3. xrefs_to(network string address) → find the referencing function
4. decompile(referencing function) → read the communication logic
5. trace_data_flow(crypto argument, "backward") → trace the key source
6. set_comments + rename → annotate the findings
```

### Registration check cracking

```text
1. find_regex("serial|license|register|valid") → find validation-related strings
2. xrefs_to(validation string) → locate the validation function
3. analyze_function(validation function) → understand the logic
4. callgraph(validation function, 2) → look at the call chain
5. patch_asm(conditional jump address, "jmp always_pass") → patch
```

### CTF reverse engineering

```text
1. survey_binary → confirm the architecture and entry
2. decompile("main") → read the main logic
3. find_regex("flag|correct|wrong") → find the decision point
4. trace_data_flow(decision point, "backward") → trace the input transformation
5. Compute/decrypt with Python → get the flag
```

### Vulnerability analysis

```text
1. entity_query(kind="imports", filter="strcpy|sprintf|gets") → find dangerous functions
2. xrefs_to(dangerous function) → find call sites
3. analyze_function(function containing the call site) → read the context
4. stack_frame(function) → confirm the buffer size
5. trace_data_flow(dangerous argument, "backward") → confirm user control
```

---

## Common errors and fixes

| Error | Cause | Fix |
|------|------|------|
| "No database bound" | No file is open | Run `open.ps1` |
| "Failed to open database" | Old database is locked | `open.ps1` degrades to Temp automatically |
| Schema validation failure | MCP client BUG | Use `open.ps1` instead of `idb_open` |
| Tool timeout | Large file still being analyzed | Add `-TimeoutSeconds 600` |
| "ERR:timeout" (start.ps1) | Server failed to start | Check the Python/idalib-mcp install |
| Base conversion error | Manual calculation mistake | Use `idapro_int_convert` |
| Function name not found | Imprecise name | Search with `list_funcs` + filter first |
