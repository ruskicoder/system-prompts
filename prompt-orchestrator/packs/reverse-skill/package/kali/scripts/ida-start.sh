#!/usr/bin/env bash
# ida-start.sh: starts the IDA Pro MCP HTTP service (Linux version)
# Equivalent of the Windows ida-reverse/scripts/start.ps1

set -euo pipefail

# ─── Configuration (edit to match your installation) ─────────────────────────────────────────────────────

IDADIR="${IDADIR:-/opt/idapro}"
MCP_PORT="${IDA_MCP_PORT:-13337}"

# Path of the idalib-mcp executable (usually on PATH after pip install)
MCP_SERVER_CMD="${IDA_MCP_SERVER:-ida-pro-mcp}"

# ─── Checks ─────────────────────────────────────────────────────────────────────────

if [[ ! -d "$IDADIR" ]]; then
    echo "ERR: IDADIR does not exist: $IDADIR"
    echo "Set the IDADIR environment variable to the IDA Pro install directory"
    exit 1
fi

if ! command -v "$MCP_SERVER_CMD" &>/dev/null; then
    echo "ERR: $MCP_SERVER_CMD not found"
    echo "Run first: pip3 install git+https://github.com/mrexodia/ida-pro-mcp.git"
    exit 1
fi

# ─── Kill old processes ───────────────────────────────────────────────────────────────────

pkill -f "ida-pro-mcp" 2>/dev/null || true
sleep 1

# ─── Start the service ──────────────────────────────────────────────────────────────────────

echo "INFO: Starting the IDA MCP HTTP service (port $MCP_PORT) ..."
export IDADIR

nohup "$MCP_SERVER_CMD" --port "$MCP_PORT" > /tmp/ida-mcp.log 2>&1 &
MCP_PID=$!

# ─── Wait until ready ──────────────────────────────────────────────────────────────────────

TIMEOUT=45
ELAPSED=0

while [[ $ELAPSED -lt $TIMEOUT ]]; do
    if nc -z 127.0.0.1 "$MCP_PORT" 2>/dev/null; then
        echo "OK: IDA MCP service ready (PID=$MCP_PID, port=$MCP_PORT)"
        exit 0
    fi
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

echo "ERR: timed out after ${TIMEOUT}s; the service is not ready"
echo "See the log: /tmp/ida-mcp.log"
exit 1
