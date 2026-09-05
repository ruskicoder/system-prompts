#!/usr/bin/env bash
set -euo pipefail

ORCHESTRATOR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="${HOME}/.claude"

echo "==> Installing prompt-orchestrator to Claude / Claude Code (${TARGET_DIR})"

for src in ".claude/skills" "AGENTS.md"; do
    if [ ! -e "${ORCHESTRATOR_DIR}/${src}" ]; then
        echo "!! Missing generated source '${src}'. Run: python3 tools/generate_integrations.py" >&2
        exit 1
    fi
done

mkdir -p "${TARGET_DIR}/skills"
cp -r "${ORCHESTRATOR_DIR}/.claude/skills/"* "${TARGET_DIR}/skills/"
cp "${ORCHESTRATOR_DIR}/AGENTS.md" "${TARGET_DIR}/AGENTS.md"

# Merge into (rather than overwrite) the personal CLAUDE.md, so the
# orchestrator loads in every project without clobbering existing memory.
CLAUDE_MD="${TARGET_DIR}/CLAUDE.md"
MARKER="<!-- prompt-orchestrator:start -->"
mkdir -p "${TARGET_DIR}"
touch "${CLAUDE_MD}"
if grep -qF "${MARKER}" "${CLAUDE_MD}" 2>/dev/null; then
    echo "==> ${CLAUDE_MD} already references prompt-orchestrator, skipping merge"
else
    {
        echo ""
        echo "${MARKER}"
        echo "@AGENTS.md"
        echo "<!-- prompt-orchestrator:end -->"
    } >> "${CLAUDE_MD}"
fi

SKILL_COUNT=$(ls -d "${ORCHESTRATOR_DIR}/.claude/skills/"*/ 2>/dev/null | wc -l | tr -d ' ')
echo "==> Done: ${SKILL_COUNT} skills installed as native Claude Code Skills."
echo "    Each is usable automatically (description match) or explicitly via '/<name>'."
echo "    For a project-scoped install instead of this global one, run:"
echo "        bash install/install-project.sh /path/to/your/project"
