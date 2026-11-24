# IDA ↔ reverse-skill Integration (portable)

This page has general steps without any machine-specific absolute paths. The local readiness report stays in `LOCAL-READINESS.md` at the repository root (gitignored).

## Target shape

| Item | Convention |
|----|------|
| IDA install directory | Environment variable `IDADIR` (the directory contains `ida.exe` or `ida.dll`) |
| HTTP MCP | `http://127.0.0.1:13337/mcp` |
| Client server name | Keep only **`idapro`** (do not also register `ida-pro-mcp`) |
| Start | `scripts/start.ps1` (`--unsafe`, no `?ext=dbg`) |
| Open database | Prefer `scripts/open.ps1` for large files; do not call `idb_open` directly through some clients |

Two MCP names pointing at the same 13337 register the tools twice and compete with the idalib worker for the port.

## Installation

```powershell
setx IDADIR "<your IDA install directory>"

# You must use mrexodia/ida-pro-mcp; do not install ida-mcp from PyPI
python -m pip install "git+https://github.com/mrexodia/ida-pro-mcp.git"

# Activate idalib (adjust the path to the local IDA)
python "<IDADIR>\idalib\python\py-activate-idalib.py" -d "<IDADIR>"

# Install the plugin + client configuration
python -m ida_pro_mcp --install --transport streamable-http --scope global
```

## Start and keep alive

A `type: http` MCP entry does not start the process on your behalf. When 13337 is not listening, every client reports an error.

| Script | Role |
|------|------|
| `scripts/start.ps1` | Healthy → `OK:<n>:reuse` and refresh last-healthy; port listening but RPC timeout counts as busy, no kill; replaces the managed supervisor only when no one listens, `py_eval` is missing, or tools/list fails continuously for more than 3 minutes (with no `opening.lock`); never kills `ida.exe` |
| `scripts/watchdog.ps1` | Checks every minute; healthy → reuse; GUI / `open.ps1` database lock / less than 3 minutes since last-healthy → reuse; **`-Force` only after tools/list fails continuously for more than 3 minutes** |
| `scripts/recover.ps1` | Immediate `-Force` restart of the supervisor (does not kill `ida.exe`). Use it when the HTTP client marks `idapro` as error |
| `scripts/install-autostart.ps1` | Registers the scheduled task `reverse-skill-ida-mcp` (at login + every minute) |
| `scripts/start-gui.ps1` | Opens the GUI plugin when the idalib license fails |
| `scripts/open.ps1` | Calls `idb_open` directly over HTTP, bypassing the schema validation of some clients |

Logs: `%LOCALAPPDATA%\reverse-skill\ida-mcp\supervisor.log` and `watchdog.log`.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "skills\ida-reverse\scripts\start.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "skills\ida-reverse\scripts\open.ps1" -Path "C:\path\to\target.exe" -TimeoutSeconds 600
powershell -NoProfile -ExecutionPolicy Bypass -File "skills\ida-reverse\scripts\install-autostart.ps1"
```

When the GUI holds 13337 but does not respond for a moment, `start.ps1` prints `WARN:gui_busy` and exits, to avoid killing an IDA that is busy analyzing.

## Clients

All point to Streamable HTTP: `http://127.0.0.1:13337/mcp`, server name `idapro`.

Start a new session after changing the configuration. If the port was not listening when Cursor started, bringing the service up afterwards **does not reconnect automatically**; refresh manually in the MCP panel.

## Known caveats

1. System32 files: `open.ps1` copies them to a temporary path (the output carries `(temp copy)`)
2. Do not call `idb_open` directly through some clients' MCP
3. `start.ps1` prefers `python -m ida_pro_mcp.idalib_supervisor`, which is more stable than the `.cmd` wrapper
4. When a formal install and a portable desktop package coexist, `IDADIR` wins
5. Do not add `?ext=dbg` (debugger tools are not exposed by default)
