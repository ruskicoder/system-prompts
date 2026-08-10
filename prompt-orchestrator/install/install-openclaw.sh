#!/usr/bin/env bash
set -euo pipefail

# Install prompt-orchestrator master specs into OpenClaw workspace
TARGET_DIR="${HOME}/.openclaw"
mkdir -p "${TARGET_DIR}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ORCHESTRATOR_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "==> Installing prompt-orchestrator to OpenClaw at ${TARGET_DIR}..."
cp "${ORCHESTRATOR_DIR}/AGENT.md" "${TARGET_DIR}/AGENT.md"
cp -r "${ORCHESTRATOR_DIR}/skills" "${TARGET_DIR}/"
cp -r "${ORCHESTRATOR_DIR}/workflows" "${TARGET_DIR}/"

echo "==> OpenClaw installation complete."
