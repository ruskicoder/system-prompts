#!/usr/bin/env bash
set -euo pipefail

ORCHESTRATOR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AGENT="${HOME}/.gemini/antigravity"
IDE="${HOME}/.gemini/antigravity-ide"

for target in "$AGENT" "$IDE"; do
    echo "==> Installing to ${target}"
    mkdir -p "${target}/skills" "${target}/workflows" "${target}/steering"

    cp "${ORCHESTRATOR_DIR}/AGENT.md" "${target}/AGENTS.md"
    cp -r "${ORCHESTRATOR_DIR}/skills/"* "${target}/skills/"
    cp -r "${ORCHESTRATOR_DIR}/workflows/"* "${target}/workflows/"
done

echo "==> Done: installed to antigravity (agent) + antigravity-ide (IDE)"
