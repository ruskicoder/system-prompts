#!/usr/bin/env bash
set -euo pipefail

# Universal installer: copies every generated integration into a target
# project so it is immediately usable by Claude Code, Codex, Cursor,
# OpenCode, Gemini CLI, Antigravity, Windsurf, and any other tool that
# reads AGENTS.md or the open Agent Skills standard (.agents/skills/) —
# with no per-tool global setup required.

ORCHESTRATOR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="${1:-$(pwd)}"

if [ ! -d "${TARGET_DIR}" ]; then
    echo "!! Target project directory does not exist: ${TARGET_DIR}" >&2
    echo "   Usage: bash install/install-project.sh /path/to/your/project" >&2
    exit 1
fi
TARGET_DIR="$(cd "${TARGET_DIR}" && pwd)"

if [ "${TARGET_DIR}" = "${ORCHESTRATOR_DIR}" ]; then
    echo "==> Target is the prompt-orchestrator repo itself; nothing to copy (files already generated here)."
    exit 0
fi

echo "==> Installing prompt-orchestrator into project: ${TARGET_DIR}"

DOT_DIRS=(".agents" ".claude" ".claude-plugin" ".codex" ".cursor" ".gemini" ".opencode" ".windsurf")
ROOT_FILES=("AGENTS.md" "AGENT.md" "CLAUDE.md" "INTEGRATIONS.md")
CONTENT_DIRS=("skills" "workflows")

for d in "${DOT_DIRS[@]}"; do
    if [ -d "${ORCHESTRATOR_DIR}/${d}" ]; then
        mkdir -p "${TARGET_DIR}/${d}"
        cp -r "${ORCHESTRATOR_DIR}/${d}/." "${TARGET_DIR}/${d}/"
        echo "   [OK] ${d}/"
    fi
done

for f in "${ROOT_FILES[@]}"; do
    if [ -f "${ORCHESTRATOR_DIR}/${f}" ]; then
        cp "${ORCHESTRATOR_DIR}/${f}" "${TARGET_DIR}/${f}"
        echo "   [OK] ${f}"
    fi
done

for d in "${CONTENT_DIRS[@]}"; do
    if [ -d "${ORCHESTRATOR_DIR}/${d}" ]; then
        mkdir -p "${TARGET_DIR}/${d}"
        cp -r "${ORCHESTRATOR_DIR}/${d}/." "${TARGET_DIR}/${d}/"
        echo "   [OK] ${d}/ (canonical source, in case you want to edit + regenerate)"
    fi
done

echo ""
echo "==> Done. ${TARGET_DIR} now works out of the box with:"
echo "    Claude / Claude Code (.claude/skills, CLAUDE.md)"
echo "    Codex CLI / IDE       (.agents/skills, .codex/prompts, AGENTS.md)"
echo "    Cursor                (.cursor/commands, .cursor/rules)"
echo "    OpenCode              (.opencode/skills, .opencode/commands)"
echo "    Gemini CLI            (.gemini/commands, AGENTS.md, .agents/skills)"
echo "    Antigravity           (.gemini/commands, .agents/skills)"
echo "    Windsurf               (.windsurf/workflows, .windsurf/rules)"
echo "    Any other agent       (AGENTS.md fallback, .agents/skills)"
