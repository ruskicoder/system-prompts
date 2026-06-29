#!/usr/bin/env bash
set -euo pipefail

ORCHESTRATOR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="${HOME}/.gemini"

echo "==> Installing prompt-orchestrator to Gemini CLI (${TARGET_DIR})"
mkdir -p "${TARGET_DIR}/skills" "${TARGET_DIR}/workflows"

cp "${ORCHESTRATOR_DIR}/AGENT.md" "${TARGET_DIR}/GEMINI.md"
cp -r "${ORCHESTRATOR_DIR}/skills/"* "${TARGET_DIR}/skills/"
cp -r "${ORCHESTRATOR_DIR}/workflows/"* "${TARGET_DIR}/workflows/"

echo "==> Done: GEMINI.md (556 lines), $(ls "${ORCHESTRATOR_DIR}/skills/"*.md | wc -l) skills, $(ls "${ORCHESTRATOR_DIR}/workflows/"*.md | wc -l) workflows"
