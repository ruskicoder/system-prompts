#!/usr/bin/env bash
set -euo pipefail

# Install prompt-orchestrator master specs into an OpenClaw workspace
TARGET_DIR="${HOME}/.openclaw"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ORCHESTRATOR_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "==> Installing prompt-orchestrator to OpenClaw at ${TARGET_DIR}..."
mkdir -p "${TARGET_DIR}/skills" "${TARGET_DIR}/workflows"

cp "${ORCHESTRATOR_DIR}/AGENT.md" "${TARGET_DIR}/AGENT.md"
cp "${ORCHESTRATOR_DIR}/AGENTS.md" "${TARGET_DIR}/AGENTS.md"
cp -r "${ORCHESTRATOR_DIR}/skills/"* "${TARGET_DIR}/skills/"
cp -r "${ORCHESTRATOR_DIR}/workflows/"* "${TARGET_DIR}/workflows/"

# OpenClaw doesn't (yet) publish a documented Agent-Skills discovery path,
# so also drop the folder-based standard in for forward compatibility.
mkdir -p "${TARGET_DIR}/agents-skills"
cp -r "${ORCHESTRATOR_DIR}/.agents/skills/"* "${TARGET_DIR}/agents-skills/"

echo "==> OpenClaw installation complete."
