#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "==> Installing prompt-orchestrator to all platforms..."
echo ""

for script in "${SCRIPT_DIR}"/install-*.sh; do
    [ "$(basename "$script")" = "install-all.sh" ] && continue
    echo "--- Running $(basename "$script") ---"
    bash "$script"
    echo ""
done

echo "==> All installations complete"
