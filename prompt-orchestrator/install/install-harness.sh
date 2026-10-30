#!/usr/bin/env bash
# install-harness.sh [tool...] - add the harness to an existing core install.
# With no tools, installs for Claude Code and Codex. Example: bash install/install-harness.sh claude
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TOOLS="${*:-claude codex}"
if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then
    exec python3 "${SCRIPT_DIR}/install.py" --harness-only --yes --tools "$(echo ${TOOLS} | tr ' ' ',')"
fi
exec bash "${SCRIPT_DIR}/install-tui.sh" --harness-only --yes --tools "$(echo ${TOOLS} | tr ' ' ',')"
