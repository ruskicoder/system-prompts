#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
    echo "!! Python 3 is required for the Antigravity installer (no extra packages)." >&2
    exit 1
fi
ARGS=()
WITH_HARNESS=0
for arg in "$@"; do
    case "${arg}" in
        --with-harness) WITH_HARNESS=1 ;;
        --core) ;;
        *) ARGS+=("${arg}") ;;
    esac
done
python3 "${SCRIPT_DIR}/antigravity_plugin.py" ${ARGS[@]+"${ARGS[@]}"}
if [ "${WITH_HARNESS}" = 1 ]; then
    bash "${SCRIPT_DIR}/install-harness.sh" antigravity
fi
