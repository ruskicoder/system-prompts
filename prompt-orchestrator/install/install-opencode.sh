#!/usr/bin/env bash
set -euo pipefail

ORCHESTRATOR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="${HOME}/.config/opencode"

echo "==> Installing prompt-orchestrator to OpenCode (${TARGET_DIR})"

for src in ".opencode/skills" ".opencode/commands" "AGENTS.md"; do
    if [ ! -e "${ORCHESTRATOR_DIR}/${src}" ]; then
        echo "!! Missing generated source '${src}'. Run: python3 tools/generate_integrations.py" >&2
        exit 1
    fi
done

mkdir -p "${TARGET_DIR}/skills" "${TARGET_DIR}/commands"

# Native skill discovery (OpenCode's built-in `skill` tool + auto-invocation)
cp -r "${ORCHESTRATOR_DIR}/.opencode/skills/"* "${TARGET_DIR}/skills/"

# Explicit "/name" slash commands (guaranteed to work even where
# auto-invocation via the skill tool is ambiguous)
cp -r "${ORCHESTRATOR_DIR}/.opencode/commands/"* "${TARGET_DIR}/commands/"

# Universal instructions fallback, read natively by OpenCode
cp "${ORCHESTRATOR_DIR}/AGENTS.md" "${TARGET_DIR}/AGENTS.md"

SKILL_COUNT=$(ls -d "${ORCHESTRATOR_DIR}/.opencode/skills/"*/ 2>/dev/null | wc -l | tr -d ' ')
CMD_COUNT=$(ls "${ORCHESTRATOR_DIR}/.opencode/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')
echo "==> Done: ${SKILL_COUNT} skills + ${CMD_COUNT} slash commands + AGENTS.md deployed."
echo "    Type '/' in the OpenCode TUI to browse them."
