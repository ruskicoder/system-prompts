#!/usr/bin/env bash
set -euo pipefail

ORCHESTRATOR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-${HOME}/.codex}"
AGENTS_SKILLS_HOME="${HOME}/.agents/skills"

echo "==> Installing prompt-orchestrator to Codex (${CODEX_HOME})"

for src in ".agents/skills" ".codex/prompts" "AGENTS.md"; do
    if [ ! -e "${ORCHESTRATOR_DIR}/${src}" ]; then
        echo "!! Missing generated source '${src}'. Run: python3 tools/generate_integrations.py" >&2
        exit 1
    fi
done

# Agent Skills standard (auto-discovered, works with implicit invocation
# per the skill's description as well as an explicit mention in-prompt)
mkdir -p "${AGENTS_SKILLS_HOME}"
cp -r "${ORCHESTRATOR_DIR}/.agents/skills/"* "${AGENTS_SKILLS_HOME}/"

# Legacy custom prompts -> guaranteed "/prompts:<name>" slash invocation
mkdir -p "${CODEX_HOME}/prompts"
cp -r "${ORCHESTRATOR_DIR}/.codex/prompts/"* "${CODEX_HOME}/prompts/"

# Universal instructions fallback, read natively by Codex (walked from
# $HOME/AGENTS.md up through the repo tree)
cp "${ORCHESTRATOR_DIR}/AGENTS.md" "${CODEX_HOME}/AGENTS.md"

SKILL_COUNT=$(ls -d "${ORCHESTRATOR_DIR}/.agents/skills/"*/ 2>/dev/null | wc -l | tr -d ' ')
CMD_COUNT=$(ls "${ORCHESTRATOR_DIR}/.codex/prompts/"*.md 2>/dev/null | wc -l | tr -d ' ')
echo "==> Done: ${SKILL_COUNT} skills installed to ${AGENTS_SKILLS_HOME} (Agent Skills standard)."
echo "    ${CMD_COUNT} legacy prompts installed to ${CODEX_HOME}/prompts (use '/prompts:<name>')."
echo "    AGENTS.md deployed to ${CODEX_HOME}/AGENTS.md."
