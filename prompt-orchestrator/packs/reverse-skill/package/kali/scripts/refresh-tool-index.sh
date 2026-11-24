#!/usr/bin/env bash
# refresh-tool-index.sh: tool index refresh for Kali Linux
# Equivalent of the Windows refresh-tool-index.ps1
# Output: skills/tool-index.md + skills/tool-index.json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/tool-discovery.sh"

OUTPUT_MD="${1:-${SKILL_ROOT}/tool-index.md}"
OUTPUT_JSON="${2:-${SKILL_ROOT}/tool-index.json}"

GENERATED_AT=$(date '+%Y-%m-%d %H:%M:%S %z')

# ─── Generate Markdown ────────────────────────────────────────────────────────────────

{
    echo "# Reverse Engineering Tool Index"
    echo ""
    echo "- Scan time: $GENERATED_AT"
    echo "- Scan platform: Kali Linux ($(uname -r))"
    echo "- Routing entry: \`SKILL.md\` → \`routing.md\` → the matching sub-skill"
    echo "- Note: \`kali/scripts/refresh-tool-index.sh\` generates this table automatically."
    echo "- Note: for MCP servers such as jshookmcp, \`yes\` only means this machine can launch it through node/npx; it does not mean the server is registered and enabled in the MCP configuration."
    echo ""
    echo "| Tool | Skill | Purpose | Available | Path | Version | Source | Script references |"
    echo "|---|---|---|---|---|---|---|---|"

    for entry in "${TOOL_CATALOG[@]}"; do
        result=$(resolve_tool "$entry")
        IFS='|' read -r name skill purpose available resolved_path version source <<< "$result"

        # Get script references
        refs="${SCRIPT_REFS[$name]:-—}"
        refs_display="${refs//,/<br>}"

        path_display="${resolved_path:-—}"
        version_display="${version:-—}"

        echo "| $name | $skill | $purpose | $available | $path_display | $version_display | $source | $refs_display |"
    done
} > "$OUTPUT_MD"

# ─── Capability status view ──────────────────────────────────────────────────────────────────

{
    echo ""
    echo "---"
    echo ""
    echo "## Capability Status"
    echo ""
    echo "| Capability | Tool available | MCP registered | Service online | Auto-installable | Install method |"
    echo "|------|---------|-----------|---------|-----------|---------|"

    CAPABILITY_NAMES=("jadx" "apktool" "jeb-pro" "binaryninja" "frida" "idalib-mcp" "jshookmcp" "reqable-mcp" "xquik-mcp" "anything-analyzer" "idapro" "r2" "adb" "agent-browser" "ghidra-mcp" "seclists" "proxycat" "burpsuite-mcp" "nmap" "sqlmap" "hashcat" "hydra" "gobuster" "ffuf" "msfconsole" "nuclei" "pwntools" "bkcrack")

    for cap_name in "${CAPABILITY_NAMES[@]}"; do
        # Check whether the tool is available
        tool_available="✗"
        case "$cap_name" in
            jeb-pro)
                if command -v jeb &>/dev/null || [[ -x "$HOME/tools/JEB/jeb" ]] || [[ -x "$HOME/JEB/jeb" ]] || [[ -x "/opt/jeb/jeb" ]]; then
                    tool_available="✓"
                fi
                ;;
            binaryninja)
                if command -v binaryninja &>/dev/null || command -v binaryninja-headless &>/dev/null || [[ -x "$HOME/BinaryNinja/binaryninja" ]] || [[ -x "/opt/binaryninja/binaryninja" ]]; then
                    tool_available="✓"
                fi
                ;;
            pwntools)
                if command -v pwn &>/dev/null; then tool_available="✓"; fi
                ;;
            reqable-mcp|jshookmcp)
                if command -v npx &>/dev/null; then tool_available="✓"; fi
                ;;
            *)
                if command -v "$cap_name" &>/dev/null; then tool_available="✓"; fi
                ;;
        esac

        # Check the MCP registration state
        mcp_registered="—"
        mcp_name="$cap_name"
        case "$cap_name" in
            jshookmcp) mcp_name="jshook" ;;
            xquik-mcp) mcp_name="xquik" ;;
        esac
        mcp_check=$(check_mcp_registered "$mcp_name")
        if [[ "$mcp_check" == "true" ]]; then
            mcp_registered="✓"
        fi

        # Check whether the service is online
        service_online="—"
        case "$cap_name" in
            idapro)
                if test_tcp_port 13337 2>/dev/null; then service_online="✓"; fi
                ;;
            anything-analyzer)
                if test_tcp_port 23816 2>/dev/null; then service_online="✓"; fi
                ;;
            ghidra-mcp)
                if test_tcp_port 8765 2>/dev/null; then service_online="✓"; fi
                ;;
            burpsuite-mcp)
                if test_tcp_port 9876 2>/dev/null; then service_online="✓"; fi
                ;;
        esac

        # Get the install method
        can_auto="✓"
        bootstrap_kind="apt-package"
        case "$cap_name" in
            jadx|ghidra-mcp|seclists)
                bootstrap_kind="github-release"
                ;;
            frida|idalib-mcp|proxycat|pwntools)
                bootstrap_kind="pip-package"
                ;;
            jshookmcp|reqable-mcp|agent-browser)
                bootstrap_kind="npm-mcp"
                ;;
            xquik-mcp)
                bootstrap_kind="remote-http-mcp"
                ;;
            jeb-pro|binaryninja)
                bootstrap_kind="manual"
                can_auto="✗"
                ;;
            anything-analyzer|idapro)
                bootstrap_kind="local-http-mcp"
                ;;
            burpsuite-mcp)
                bootstrap_kind="manual"
                can_auto="✗"
                ;;
        esac

        echo "| $cap_name | $tool_available | $mcp_registered | $service_online | $can_auto | $bootstrap_kind |"
    done

    echo ""
    echo "> ✓ = yes | ✗ = no | — = not applicable or not checked"
    echo ""
} >> "$OUTPUT_MD"

# ─── Generate JSON ─────────────────────────────────────────────────────────────────────

if command -v jq &>/dev/null; then
    # Generate structured JSON with jq
    json_tools="[]"
    for entry in "${TOOL_CATALOG[@]}"; do
        result=$(resolve_tool "$entry")
        IFS='|' read -r name skill purpose available resolved_path version source <<< "$result"
        refs="${SCRIPT_REFS[$name]:-}"

        avail_bool="false"
        [[ "$available" == "yes" ]] && avail_bool="true"

        json_tools=$(echo "$json_tools" | jq \
            --arg name "$name" \
            --arg skill "$skill" \
            --arg purpose "$purpose" \
            --argjson available "$avail_bool" \
            --arg resolved_path "$resolved_path" \
            --arg version "$version" \
            --arg source "$source" \
            --arg script_refs "$refs" \
            '. + [{
                name: $name,
                skill: $skill,
                purpose: $purpose,
                available: $available,
                resolved_path: $resolved_path,
                version: $version,
                source: $source,
                script_refs: ($script_refs | split(","))
            }]')
    done

    jq -n \
        --arg generated_at "$GENERATED_AT" \
        --arg platform "kali-linux" \
        --argjson tools "$json_tools" \
        '{
            generated_at: $generated_at,
            platform: $platform,
            routing_entry: ["SKILL.md", "routing.md"],
            tools: $tools
        }' > "$OUTPUT_JSON"
else
    # Without jq, generate simple JSON
    echo "{\"generated_at\": \"$GENERATED_AT\", \"platform\": \"kali-linux\", \"note\": \"install jq for full JSON output\"}" > "$OUTPUT_JSON"
fi

echo "✅ Tool index refreshed"
echo "  markdown=$OUTPUT_MD"
echo "  json=$OUTPUT_JSON"
echo "  tools=${#TOOL_CATALOG[@]}"
