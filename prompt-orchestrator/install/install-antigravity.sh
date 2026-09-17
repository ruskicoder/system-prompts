#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
    echo "!! Python 3 is required for the Antigravity installer (no extra packages)." >&2
    exit 1
fi
exec python3 "${SCRIPT_DIR}/antigravity_plugin.py" "$@"
