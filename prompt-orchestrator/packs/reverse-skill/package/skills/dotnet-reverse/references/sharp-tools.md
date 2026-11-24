# Red Team Sharp* Tool Analysis & Tool Install Matrix & dnSpy MCP

## Red team Sharp* tool analysis

Many red team tools are written in C# (the Sharp* family); reversing them is a common scenario: understand detection logic, change signatures, extract embedded configuration.

### Common Sharp* tool quick reference

| Tool | Function | Reverse engineering focus |
|------|------|-----------|
| **Rubeus** | Kerberos attacks (AS-REP roast / Kerberoast / S4U / pass-the-ticket) | Rubeus has a fixed project structure; look at the `Interop.*` P/Invoke section for native calls |
| **SharpHound** | BloodHound data collector | LDAP query logic, the attribute set it collects |
| **SharpShell / SharpWS** | Remote execution, lateral movement | WMI / WinRM calls, command obfuscation |
| **Seatbelt** | Information gathering | Collection item list, decision logic |
| **SharpRoast** | Kerberoasting | Ticket request/parsing |
| **Inveigh / SharpSploit** | Man-in-the-middle / general exploitation framework | Reflective loading, API call chains |

### General analysis routine

```text
1. Open in dnSpyEx (usually not obfuscated; a few teams add ConfuserEx)
2. Look at Program.Main or the entry command dispatch (Rubeus uses a switch(command) structure)
3. Find the implementing class/method of the target command
4. Look at the P/Invoke section (Interop.* namespace): native API calls live there
5. Extract embedded resources (some tools embed configuration/templates)
6. To change signatures (EDR evasion): change command strings, API calls, string constants
```

### Rubeus structure example

Rubeus dispatches by command, one class per subcommand. To find the Kerberoasting logic:

```text
Entry: Rubeus.CommandLineParser → parse args
Dispatch: switch(command) → "kerberoast" → run Ask.TGS(...)
P/Invoke: Rubeus.Interop.Lsa* / Native.cs → native Kerberos API
Key: LsaCallAuthenticationPackage (KERB_RETRIEVE_TKT_REQUEST)
```

Change signatures (evasion): rename the command string `"kerberoast"` to a custom name, change the `Rubeus` banner string, change the P/Invoke call order.

### Embedded configuration extraction

Many loaders/tools embed encrypted C2, keys and certificates in resources or fields:

```powershell
# Look at Resources (resource tree) in dnSpyEx
# Or on the command line
powershell -c "[System.Reflection.Assembly]::LoadFile('target.exe').GetManifestResourceNames()"
# Once the resource is found, right-click in dnSpyEx → Extract / Save
```

Configuration decrypted at runtime → break dynamically at the return point of the decryption method and dump the plaintext (see `common-workflow.md`).

---

## Tool install matrix

### Windows (first choice, dnSpyEx is a GUI)

```powershell
# Option A: Chocolatey
choco install dnspy ilspy de4dot detect-it-easy

# Option B: manual release download (recommended, version controlled)
# dnSpyEx:    https://github.com/dnSpyEx/dnSpy/releases
# de4dot:     https://github.com/de4dot/de4dot/releases
# ILSpy:      https://github.com/icsharpcode/ILSpy/releases
# DIE:        https://github.com/horsicq/Detect-It-Easy/releases
# dnlib:      dotnet add package dnlib  (NuGet)
```

### Linux / macOS (no dnSpyEx GUI, use the CLI)

```bash
# ILSpy CLI decompilation
dotnet tool install -g ilspycmd
ilspycmd target.exe -p -o outdir/         # decompile to a directory

# de4dot cross-platform (needs mono or dotnet)
# Download the de4dot .dll build from the release and run it with dotnet
dotnet de4dot.dll target.exe -o target-clean.exe

# dnlib (scripting, needs the dotnet SDK)
dotnet new console -o dnclean && cd dnclean
dotnet add package dnlib

# DIE CLI (diec)
# Linux: install from https://github.com/horsicq/Detect-It-Easy
diec target.exe
```

### .NET runtime prerequisite

```bash
# Linux
sudo apt install dotnet-runtime-8.0        # or 6.0/7.0 depending on the target
# macOS
brew install --cask dotnet-sdk
```

> dnSpyEx (with the IL editor + debugger) exists only as a Windows GUI. .NET reverse engineering on Linux/macOS can only use `ilspycmd` decompilation + `dnlib` script patching, without an equivalent interactive debugging GUI. Prefer Windows when patching is needed.

---

## dnSpy MCP integration

The community already has several dnSpy MCP projects that expose dnSpy decompilation/IL inspection as MCP tools the AI can call directly, fully in line with reverse-skill's MCP philosophy.

### Mainstream dnSpy MCP projects

| Project | Characteristics | Fit |
|------|------|------|
| **soufianetahiri/dnspy-mcp** | Core MCP server exposing decompile, IL inspection and other tools | Claude Code / Cursor |
| **AgentSmithers/DnSpy-MCPserver-Extension** | Runs as a dnSpyEx extension, deep GUI integration | Loaded inside dnSpyEx |
| **malwarecakefactory/dnspy-mcp-extension** | 33 tools covering the full triage → deobfuscation flow | Full-flow automation |

### Register in the Claude MCP configuration

After installing the dnSpyEx extension per the project README, register it in `~/.claude/mcp.json` (the exact command/args follow the project README):

```json
{
  "mcpServers": {
    "dnspy": {
      "command": "dotnet",
      "args": ["path/to/dnspy-mcp.dll"]
    }
  }
}
```

After registration, this skill's AI link path: the user says "analyze this .NET" → route to `dotnet-reverse/` → call the `dnspy_decompile` / `dnspy_inspect_il` tool surface first → switch to the GUI if that fails.

> The dnSpy MCP is not a built-in reverse-skill bootstrap capability; the user installs the extension and registers it manually per the project README. Adding it to `bootstrap-manifest.json` can be considered later.

---

## Community resource index

### Strongly recommended

- **Washi's blog**, a .NET reverse engineering expert: https://blog.washi.dev/posts/misconceptions-about-dotnet/
  - Core point: **do not over-rely on dnSpy's C# decompiler; get familiar with the IL editor** (consistent with this project's IL-first principle)
- **dnSpyEx**: the actively maintained fork of dnSpy: https://github.com/dnSpyEx/dnSpy
- **de4dot**: .NET deobfuscation: https://github.com/de4dot/de4dot
- **dnlib**: metadata programming: https://github.com/dnlib/dnlib

### Practical tutorials

- Medium "De-obfuscating and reversing a .NET/C# spyware": dnSpy + de4dot hands-on info-stealer deobfuscation
- YouTube "dnSpy Patch .NET EXEs & DLLs": step-by-step patching + keygen
- The Kanxue forum .NET reverse engineering board: search ".net reverse engineering" / "dnSpy" / "ConfuserEx" for many hands-on posts, Nuitka reverse engineering and AV evasion discussions
- Guided Hacking "Top 5 .NET Reverse Engineering Tools": dnSpy still ranks first
- StackExchange / Reverse Engineering: advanced questions such as `DynamicMethod` debugging

### Existing .NET resources in this repository (linked)

- The `.NET Analysis` section of `reverse-engineering/tools.md`: dnSpy/ILSpy tool quick reference + the Codegate 2013 two-stage XOR+AES-CBC pattern
- The `.NET` section of `reverse-engineering/field-notes.md`: tool notes
- `reverse-engineering/awesome-re-resources.md`: includes de4dot
- `field-journal/seed-014_unity-il2cpp-reverse.md`: Unity IL2CPP (native side, complements the .NET managed layer)

In-depth .NET reverse engineering content converges in this module; `reverse-engineering/` keeps only the quick reference index.
