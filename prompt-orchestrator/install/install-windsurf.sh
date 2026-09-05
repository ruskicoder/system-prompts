#!/usr/bin/env bash
set -euo pipefail

# Windsurf's workflows/rules are project-scoped (there is no documented
# global equivalent), so this installs into a target project directory
# instead of $HOME. Defaults to the current directory.

ORCHESTRATOR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="${1:-$(pwd)}"

if [ ! -d "${TARGET_DIR}" ]; then
    echo "!! Target project directory does not exist: ${TARGET_DIR}" >&2
    echo "   Usage: bash install/install-windsurf.sh /path/to/your/project" >&2
    exit 1
fi
TARGET_DIR="$(cd "${TARGET_DIR}" && pwd)"

for src in ".windsurf/workflows" ".windsurf/rules" "AGENTS.md"; do
    if [ ! -e "${ORCHESTRATOR_DIR}/${src}" ]; then
        echo "!! Missing generated source '${src}'. Run: python3 tools/generate_integrations.py" >&2
        exit 1
    fi
done

echo "==> Installing prompt-orchestrator Windsurf workflows into ${TARGET_DIR}"
mkdir -p "${TARGET_DIR}/.windsurf/workflows" "${TARGET_DIR}/.windsurf/rules"
cp -r "${ORCHESTRATOR_DIR}/.windsurf/workflows/"* "${TARGET_DIR}/.windsurf/workflows/"
cp -r "${ORCHESTRATOR_DIR}/.windsurf/rules/"* "${TARGET_DIR}/.windsurf/rules/"
cp "${ORCHESTRATOR_DIR}/AGENTS.md" "${TARGET_DIR}/AGENTS.md"

CMD_COUNT=$(ls "${ORCHESTRATOR_DIR}/.windsurf/workflows/"*.md 2>/dev/null | wc -l | tr -d ' ')
echo "==> Done: ${CMD_COUNT} workflows installed. Type '/' in Cascade to browse them."
