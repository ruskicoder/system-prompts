#!/usr/bin/env bash
set -euo pipefail

ORCHESTRATOR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="${HOME}/.cursor/rules"

echo "==> Installing prompt-orchestrator to Cursor (${TARGET_DIR})"
mkdir -p "${TARGET_DIR}"

cp "${ORCHESTRATOR_DIR}/AGENT.md" "${TARGET_DIR}/AGENT.md"
cp -r "${ORCHESTRATOR_DIR}/skills/" "${TARGET_DIR}/skills/"
cp -r "${ORCHESTRATOR_DIR}/workflows/" "${TARGET_DIR}/workflows/"

echo "==> Done: installed to Cursor rules"
