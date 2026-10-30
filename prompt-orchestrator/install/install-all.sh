#!/usr/bin/env bash
# install-all.sh - install prompt-orchestrator (core and, by default, the harness) for every
# globally-scoped tool. Uses the Python menu (install.py) when Python 3 exists, otherwise the
# native bash menu (install-tui.sh). Flags pass through, for example:
#   bash install/install-all.sh --core --yes        core only, no menu
#   bash install/install-all.sh --yes               core and harness, no menu
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
    exec python3 "${SCRIPT_DIR}/install.py" "$@"
fi
echo "--- Python 3 not found; using the native installer (harness hooks need Python 3.11+)"
exec bash "${SCRIPT_DIR}/install-tui.sh" "$@"
