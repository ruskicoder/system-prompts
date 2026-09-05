#!/usr/bin/env bash
set -euo pipefail

ORCHESTRATOR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="${HOME}/.gemini"
AGENTS_SKILLS_HOME="${HOME}/.agents/skills"

echo "==> Installing prompt-orchestrator to Gemini CLI (${TARGET_DIR})"

for src in ".gemini/commands" ".agents/skills" "AGENT.md"; do
    if [ ! -e "${ORCHESTRATOR_DIR}/${src}" ]; then
        echo "!! Missing generated source '${src}'. Run: python3 tools/generate_integrations.py" >&2
        exit 1
    fi
done

mkdir -p "${TARGET_DIR}/commands" "${AGENTS_SKILLS_HOME}"

# TOML slash commands ("/name")
cp -r "${ORCHESTRATOR_DIR}/.gemini/commands/"* "${TARGET_DIR}/commands/"

# Agent Skills standard (shared with Antigravity, Codex, OpenCode, etc.)
cp -r "${ORCHESTRATOR_DIR}/.agents/skills/"* "${AGENTS_SKILLS_HOME}/"

# Gemini CLI project memory file
cp "${ORCHESTRATOR_DIR}/AGENT.md" "${TARGET_DIR}/GEMINI.md"

CMD_COUNT=$(ls "${ORCHESTRATOR_DIR}/.gemini/commands/"*.toml 2>/dev/null | wc -l | tr -d ' ')
echo "==> Done: ${CMD_COUNT} slash commands + shared skills + GEMINI.md deployed."
echo "    Run '/commands reload' inside Gemini CLI, then type '/' to browse them."
