#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ORCHESTRATOR_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "==> Installing prompt-orchestrator to all globally-scoped platforms..."
echo ""

# Regenerate the derived integration files from the canonical skills/ and
# workflows/ sources before installing, so installs always ship the latest
# content. Safe to skip if PyYAML isn't available; the repo already ships
# pre-generated output.
if command -v python3 >/dev/null 2>&1 && python3 -c "import yaml" >/dev/null 2>&1; then
    echo "--- Regenerating integrations (tools/generate_integrations.py) ---"
    python3 "${ORCHESTRATOR_DIR}/tools/generate_integrations.py"
    echo ""
else
    echo "--- Skipping regeneration (PyYAML not available); using files already in the repo ---"
    echo ""
fi

# Scripts that install into a user's home/global config directories.
# install-project.sh and install-windsurf.sh are excluded here because
# they target a specific *project* directory (passed as an argument)
# rather than a global one — run them separately, e.g.:
#   bash install/install-project.sh /path/to/your/project
GLOBAL_SCRIPTS=(
    install-claude.sh
    install-antigravity.sh
    install-gemini.sh
    install-codex.sh
    install-cursor.sh
    install-openclaw.sh
    install-opencode.sh
)

for script in "${GLOBAL_SCRIPTS[@]}"; do
    echo "--- Running ${script} ---"
    bash "${SCRIPT_DIR}/${script}"
    echo ""
done

echo "==> All global installations complete."
echo ""
echo "To also make this project itself usable everywhere (or to set up a"
echo "*different* project), run:"
echo "    bash install/install-project.sh /path/to/your/project"
echo "    bash install/install-windsurf.sh /path/to/your/project"
