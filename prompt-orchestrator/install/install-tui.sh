#!/usr/bin/env bash
# install-tui.sh - native installer menu for Linux and macOS when Python 3 is not available.
#
# Installs the core per-tool scripts and the harness's pre-rendered agents and overlay from
# harness/dist. Hooks, the status line, power modes, the frontier gate and the verify gate run
# Python 3.11+, so this path installs agents and instructions only.
#   bash install/install-tui.sh                     menu
#   bash install/install-tui.sh --yes [--core] [--harness-only] [--tools claude,codex]
#   bash install/install-tui.sh --uninstall-harness
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DIST="${ROOT}/harness/dist"
MARKER="prompt-orchestrator-harness"
ALL_TOOLS=(claude codex opencode cursor gemini antigravity openclaw copilot kiro)
CORE_TOOLS=" claude codex opencode cursor gemini antigravity openclaw "
SELECTED=(claude codex opencode cursor gemini antigravity openclaw)
DO_CORE=1 DO_HARNESS=1 YES=0 UNINSTALL=0 CLAUDE_PROFILE=claude-pro

while [ $# -gt 0 ]; do
    case "$1" in
        --core) DO_HARNESS=0 ;;
        --with-harness) DO_HARNESS=1 ;;
        --harness-only) DO_CORE=0 ;;
        --yes|-y) YES=1 ;;
        --uninstall-harness) UNINSTALL=1 ;;
        --tools) shift; IFS=',' read -r -a SELECTED <<< "$1" ;;
        --profile-claude) shift; CLAUDE_PROFILE="$1" ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
    shift
done

agent_dir() {
    case "$1" in
        claude) echo "${HOME}/.claude/agents" ;;
        codex) echo "${CODEX_HOME:-${HOME}/.codex}/agents" ;;
        opencode) echo "${HOME}/.config/opencode/agents" ;;
        cursor) echo "${HOME}/.cursor/agents" ;;
        copilot) echo "${HOME}/.copilot/agents" ;;
        gemini) echo "${HOME}/.gemini/agents" ;;
        antigravity) echo "${HOME}/.gemini/config/agents" ;;
        kiro) echo "${HOME}/.kiro/agents" ;;
        *) echo "" ;;
    esac
}

overlay_file() {
    case "$1" in
        claude) echo "${HOME}/.claude/CLAUDE.md" ;;
        codex) echo "${CODEX_HOME:-${HOME}/.codex}/AGENTS.md" ;;
        opencode) echo "${HOME}/.config/opencode/AGENTS.md" ;;
        gemini) echo "${HOME}/.gemini/GEMINI.md" ;;
        *) echo "" ;;
    esac
}

profile_for() {
    case "$1" in
        claude|opencode) echo "${CLAUDE_PROFILE}" ;;
        codex) echo "codex-plus" ;;
        *) echo "generic" ;;
    esac
}

strip_block() {  # remove the harness block from a shared file
    [ -f "$1" ] || return 0
    sed -i.bak "/<!-- ${MARKER}:start -->/,/<!-- ${MARKER}:end -->/d" "$1" && rm -f "$1.bak"
}

add_block() {
    strip_block "$1"
    mkdir -p "$(dirname "$1")"
    { echo "<!-- ${MARKER}:start -->"; cat "$2"; echo "<!-- ${MARKER}:end -->"; } >> "$1"
}

copy_marked() {  # copy src to dest unless dest exists without the marker
    if [ -f "$2" ] && ! grep -q "${MARKER}" "$2"; then
        echo "  skipped $2: exists without the harness marker"
        return 0
    fi
    mkdir -p "$(dirname "$2")"
    cp "$1" "$2"
}

install_harness_native() {
    local tool="$1" src dest profile
    profile="$(profile_for "${tool}")"
    src="${DIST}/${tool}/${profile}/agents"
    dest="$(agent_dir "${tool}")"
    if [ -n "${dest}" ] && [ -d "${src}" ]; then
        for f in "${src}"/*; do copy_marked "${f}" "${dest}/$(basename "${f}")"; done
        echo "  agents (${profile}) -> ${dest}"
    fi
    case "${tool}" in
        claude)
            copy_marked "${ROOT}/harness/HARNESS.md" "${HOME}/.claude/HARNESS.md"
            grep -q "${MARKER}" "${HOME}/.claude/HARNESS.md" || echo "<!-- ${MARKER} -->" >> "${HOME}/.claude/HARNESS.md"
            printf '@HARNESS.md\n' > "${TMPDIR:-/tmp}/po-harness-import.md"
            add_block "${HOME}/.claude/CLAUDE.md" "${TMPDIR:-/tmp}/po-harness-import.md"
            mkdir -p "${HOME}/.claude/skills/autosetup" "${HOME}/.claude/workflows"
            copy_marked "${DIST}/skills/autosetup/SKILL.md" "${HOME}/.claude/skills/autosetup/SKILL.md"
            for w in "${ROOT}"/harness/workflows/*.js; do
                { echo "// ${MARKER}"; cat "${w}"; } > "${HOME}/.claude/workflows/$(basename "${w}")"
            done
            ;;
        cursor) mkdir -p "${HOME}/.cursor/rules"; { printf -- '---\ndescription: prompt-orchestrator harness overlay\nalwaysApply: true\n---\n<!-- %s -->\n' "${MARKER}"; cat "${ROOT}/harness/HARNESS.md"; } > "${HOME}/.cursor/rules/prompt-orchestrator-harness.mdc" ;;
        kiro) mkdir -p "${HOME}/.kiro/steering"; { echo "<!-- ${MARKER} -->"; cat "${ROOT}/harness/HARNESS.md"; } > "${HOME}/.kiro/steering/prompt-orchestrator-harness.md" ;;
        *) local overlay; overlay="$(overlay_file "${tool}")"; [ -n "${overlay}" ] && add_block "${overlay}" "${ROOT}/harness/HARNESS.md" ;;
    esac
}

uninstall_native() {
    for tool in "${SELECTED[@]}"; do
        local dest overlay
        dest="$(agent_dir "${tool}")"
        if [ -n "${dest}" ] && [ -d "${dest}" ]; then
            grep -l "${MARKER}" "${dest}"/* 2>/dev/null | while read -r f; do rm -f "${f}"; done
        fi
        overlay="$(overlay_file "${tool}")"
        [ -n "${overlay}" ] && strip_block "${overlay}"
        echo "  ${tool}: harness files removed"
    done
    rm -f "${HOME}/.claude/HARNESS.md" "${HOME}/.cursor/rules/prompt-orchestrator-harness.mdc" \
          "${HOME}/.kiro/steering/prompt-orchestrator-harness.md"
    rm -rf "${HOME}/.claude/skills/autosetup"
    grep -l "${MARKER}" "${HOME}"/.claude/workflows/*.js 2>/dev/null | while read -r f; do rm -f "${f}"; done
}

is_selected() { [[ " ${SELECTED[*]} " == *" $1 "* ]]; }

menu() {
    while true; do
        echo ""
        echo "prompt-orchestrator installer (native)"
        echo "  [c] core skills and workflows: $([ ${DO_CORE} = 1 ] && echo yes || echo no)"
        echo "  [h] harness agents and overlay: $([ ${DO_HARNESS} = 1 ] && echo yes || echo no)"
        echo "      (hooks, status line, plan modes and gates need Python 3.11+)"
        echo "  [p] Claude plan profile: ${CLAUDE_PROFILE}"
        local i=1
        for tool in "${ALL_TOOLS[@]}"; do
            echo "   ${i}. [$(is_selected "${tool}" && echo x || echo ' ')] ${tool}"
            i=$((i + 1))
        done
        echo "  Number toggles a tool, a = all, n = none, Enter = install, q = quit"
        read -r -p "> " choice || choice=""
        case "${choice}" in
            "") return 0 ;;
            q) echo "cancelled"; exit 1 ;;
            a) SELECTED=("${ALL_TOOLS[@]}") ;;
            n) SELECTED=() ;;
            c) DO_CORE=$((1 - DO_CORE)) ;;
            h) DO_HARNESS=$((1 - DO_HARNESS)) ;;
            p) case "${CLAUDE_PROFILE}" in claude-pro) CLAUDE_PROFILE=claude-max ;; claude-max) CLAUDE_PROFILE=api ;; api) CLAUDE_PROFILE=free ;; *) CLAUDE_PROFILE=claude-pro ;; esac ;;
            *[!0-9]*) echo "unknown choice" ;;
            *)
                if [ "${choice}" -ge 1 ] && [ "${choice}" -le ${#ALL_TOOLS[@]} ]; then
                    local tool="${ALL_TOOLS[$((choice - 1))]}" kept=()
                    if is_selected "${tool}"; then
                        for t in "${SELECTED[@]}"; do [ "${t}" != "${tool}" ] && kept+=("${t}"); done
                        SELECTED=(${kept[@]+"${kept[@]}"})
                    else
                        SELECTED+=("${tool}")
                    fi
                fi
                ;;
        esac
    done
}

if [ "${UNINSTALL}" = 1 ]; then
    uninstall_native
    exit 0
fi
if [ "${YES}" = 0 ] && [ -t 0 ]; then
    menu
fi

FAILED=()
for tool in "${SELECTED[@]}"; do
    echo ""
    echo "=== ${tool}"
    if [ "${DO_CORE}" = 1 ] && [[ "${CORE_TOOLS}" == *" ${tool} "* ]]; then
        bash "${SCRIPT_DIR}/install-${tool}.sh" || { FAILED+=("${tool}"); continue; }
    fi
    if [ "${DO_HARNESS}" = 1 ]; then
        install_harness_native "${tool}"
    fi
done
echo ""
if [ ${#FAILED[@]} -gt 0 ]; then
    echo "==> finished with failures: ${FAILED[*]}"
    exit 1
fi
echo "==> done. Install Python 3.11+ and run install-harness.sh to add hooks, the status line and plan modes."
