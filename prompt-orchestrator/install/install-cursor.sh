#!/usr/bin/env bash
set -euo pipefail

ORCHESTRATOR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="${HOME}/.cursor"

echo "==> Installing prompt-orchestrator to Cursor (${TARGET_DIR})"

for src in ".cursor/commands" ".cursor/rules" "AGENTS.md"; do
    if [ ! -e "${ORCHESTRATOR_DIR}/${src}" ]; then
        echo "!! Missing generated source '${src}'. Run: python3 tools/generate_integrations.py" >&2
        exit 1
    fi
done

mkdir -p "${TARGET_DIR}/commands" "${TARGET_DIR}/rules"

# "/name" slash commands, one per skill/workflow
cp -r "${ORCHESTRATOR_DIR}/.cursor/commands/"* "${TARGET_DIR}/commands/"

# Always-on rule that loads AGENTS.md as the orchestrator's operating spec
cp "${ORCHESTRATOR_DIR}/.cursor/rules/orchestrator.mdc" "${TARGET_DIR}/rules/prompt-orchestrator.mdc"
cp "${ORCHESTRATOR_DIR}/AGENTS.md" "${TARGET_DIR}/AGENTS.md"

CMD_COUNT=$(ls "${ORCHESTRATOR_DIR}/.cursor/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')
echo "==> Done: ${CMD_COUNT} slash commands + orchestrator rule installed globally."
echo "    Type '/' in Cursor's chat/agent input to browse them."
echo "    Note: Cursor's global commands/rules directories are a recent feature;"
echo "    if they are not picked up, run install/install-project.sh on your"
echo "    specific project instead to install .cursor/ locally."
