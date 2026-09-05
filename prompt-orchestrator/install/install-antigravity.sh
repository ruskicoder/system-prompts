#!/usr/bin/env bash
set -euo pipefail

ORCHESTRATOR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS_SKILLS_HOME="${HOME}/.agents/skills"
TARGETS=(
    "${HOME}/.gemini/antigravity"
    "${HOME}/.gemini/antigravity-ide"
)

for src in ".gemini/commands" ".agents/skills" "AGENT.md"; do
    if [ ! -e "${ORCHESTRATOR_DIR}/${src}" ]; then
        echo "!! Missing generated source '${src}'. Run: python3 tools/generate_integrations.py" >&2
        exit 1
    fi
done

# Antigravity shares the same open Agent Skills standard as Gemini CLI, so
# the skill library lives in one shared home directory.
mkdir -p "${AGENTS_SKILLS_HOME}"
cp -r "${ORCHESTRATOR_DIR}/.agents/skills/"* "${AGENTS_SKILLS_HOME}/"

for target in "${TARGETS[@]}"; do
    echo "==> Installing to ${target}"
    mkdir -p "${target}/commands"
    cp -r "${ORCHESTRATOR_DIR}/.gemini/commands/"* "${target}/commands/"
    cp "${ORCHESTRATOR_DIR}/AGENT.md" "${target}/AGENTS.md"
done

echo "==> Done: installed to antigravity (agent) + antigravity-ide (IDE), plus"
echo "    shared skills at ${AGENTS_SKILLS_HOME}. Type '/' to browse commands."
