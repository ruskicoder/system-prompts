#!/usr/bin/env bash
# tool-discovery.sh: tool discovery library for Kali Linux
# Equivalent of the Windows ToolDiscovery.ps1

set -euo pipefail

# ─── Path derivation ───────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KALI_SCRIPTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KALI_DIR="$(cd "$KALI_SCRIPTS_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$KALI_DIR/.." && pwd)"
SKILL_ROOT="$PROJECT_ROOT/skills"

# ─── Tool catalog definitions ─────────────────────────────────────────────────────────────────

# Definition format of each tool: name|skill|purpose|version_args|fallback_commands
# fallback_commands are separated by commas
declare -a TOOL_CATALOG=(
    "jadx|apk-reverse|Java decompilation|--version|jadx,${HOME}/tools/jadx/bin/jadx,/opt/jadx/bin/jadx"
    "apktool|apk-reverse|APK unpacking and rebuilding|--version|apktool,${HOME}/tools/apktool/apktool,/usr/local/bin/apktool"
    "adb|apk-reverse|Device connection and logcat|version|adb,${HOME}/Android/Sdk/platform-tools/adb"
    "java|apk-reverse|Runs jars and the Java toolchain|-version|java"
    "apksigner|apk-reverse|APK signing|--version|apksigner,${HOME}/Android/Sdk/build-tools/*/apksigner"
    "zipalign|apk-reverse|APK alignment||zipalign,${HOME}/Android/Sdk/build-tools/*/zipalign"
    "frida|apk-reverse|Frida dynamic instrumentation|--version|frida"
    "frida-ps|apk-reverse|Frida process enumeration|--version|frida-ps"
    "r2|radare2|radare2 main analyzer|-v|r2,radare2,${HOME}/tools/radare2/bin/r2,/usr/bin/r2"
    "rabin2|radare2|Binary recon|-v|rabin2,${HOME}/tools/radare2/bin/rabin2,/usr/bin/rabin2"
    "rasm2|radare2|Assembly and disassembly|-v|rasm2,${HOME}/tools/radare2/bin/rasm2"
    "radiff2|radare2|Binary diffing|-v|radiff2,${HOME}/tools/radare2/bin/radiff2"
    "rahash2|radare2|Hashing and checksums|-v|rahash2,${HOME}/tools/radare2/bin/rahash2"
    "rax2|radare2|Base and bitwise conversion|-v|rax2,${HOME}/tools/radare2/bin/rax2"
    "python|reverse-engineering|Helper script execution|--version|python3,python"
    "pip|reverse-engineering|Python package management|--version|pip3,pip"
    "node|js-reverse|Runs Node-side JS reproduction and MCP clients|--version|node"
    "npx|js-reverse|Runs temporary npm packages and MCP entry points|--version|npx"
    "jshookmcp|js-reverse|Starts the @jshookmcp/jshook MCP through npx||npx"
    "reqable-mcp|pentest-tools|Starts the Reqable desktop client MCP through npx||npx"
    "xquik-mcp|threat-intelligence|Remote MCP for public X threat intelligence||"
    "jeb-pro|apk-reverse|Commercial Android/ARM decompiler (manual licensed install)|--version|jeb,${HOME}/tools/JEB/jeb,${HOME}/JEB/jeb,/opt/jeb/jeb"
    "binaryninja|binary-ninja-reverse|Binary Ninja commercial reverse engineering platform (manual licensed install)|--version|binaryninja,binaryninja-headless,${HOME}/BinaryNinja/binaryninja,${HOME}/tools/BinaryNinja/binaryninja,/opt/binaryninja/binaryninja"
    "agent-browser|browser-automation|Browser automation (Playwright)|--version|agent-browser"
    "analyzeHeadless|reverse-engineering|Ghidra headless analysis||analyzeHeadless,${HOME}/tools/ghidra/support/analyzeHeadless,/opt/ghidra/support/analyzeHeadless,/usr/share/ghidra/support/analyzeHeadless"
    "playwright|browser-automation|Playwright browser engine|--version|playwright,npx playwright"
    "proxycat|pentest-tools|Proxy pool management and rotation|--version|proxycat"
    "nmap|pentest-tools|Port scanning and service detection|--version|nmap"
    "sqlmap|pentest-tools|SQL injection automation|--version|sqlmap"
    "hashcat|pentest-tools|Password cracking|--version|hashcat"
    "hydra|pentest-tools|Online password brute force|-h|hydra"
    "gobuster|pentest-tools|Directory brute force|version|gobuster"
    "ffuf|pentest-tools|Fuzzing|-V|ffuf"
    "msfconsole|pentest-tools|Metasploit framework|--version|msfconsole"
    "nikto|pentest-tools|Web vulnerability scanning|-Version|nikto"
    "binwalk|reverse-engineering|Firmware analysis and extraction|--help|binwalk"
    "pwntools|reverse-engineering|CTF pwn exploit development framework|version|pwn"
    "bkcrack|reverse-engineering|CTF ZIP/PKZIP ZipCrypto known-plaintext attack|--version|bkcrack"
    "yara|malware-analysis|Malware rule matching engine|--version|yara"
    "gdb|reverse-engineering|Debugger|--version|gdb"
    "objdump|reverse-engineering|Disassembly|--version|objdump"
    "strings|reverse-engineering|String extraction|--version|strings"
    "file|reverse-engineering|File type identification|--version|file"
    "nuclei|pentest-tools|Vulnerability scanning|-version|nuclei"
    # ─── Tools new in Kali 2026.1 ───
    "metasploitmcp|pentest-tools|Metasploit MCP Server|-h|metasploitmcp"
    "mcp-kali-server|pentest-tools|Official Kali MCP server (terminal bridge)|-h|kali-server-mcp,mcp-server"
    "hexstrike-ai|pentest-tools|AI MCP security automation platform (150+ tools)||hexstrike-ai"
    "adaptixc2|pentest-tools|Post-exploitation and adversary emulation framework||AdaptixServer"
    "atomic-operator|pentest-tools|Atomic Red Team test execution|--help|atomic-operator"
    "sstimap|pentest-tools|Automatic SSTI detection and exploitation|-h|sstimap"
    "xsstrike|pentest-tools|Advanced XSS scanner|-h|xsstrike"
    "wpprobe|pentest-tools|WordPress plugin enumeration|--help|wpprobe"
    "fluxion|pentest-tools|WiFi security audit and social engineering||fluxion"
    "gef|reverse-engineering|GDB Enhanced Features (modern debugging)||gdb"
    "evil-winrm-py|pentest-tools|Python WinRM remote execution|-h|evil-winrm-py"
    "coercer|pentest-tools|Windows authentication coercion (AD attacks)|-h|coercer"
    "pentestswarm|pentest-tools|Swarm-intelligence autonomous pentest framework (Swarm AI)|--version|pentestswarm"
    # ─── Classic preinstalled Kali tools that were not listed before ───
    "netexec|pentest-tools|Network service enumeration and exploitation (CrackMapExec successor)|--help|nxc,netexec"
    "responder|pentest-tools|LLMNR/NBT-NS/MDNS poisoning|-h|responder"
    "crackmapexec|pentest-tools|Swiss army knife for network pentesting|--help|crackmapexec,cme"
    "bloodhound|pentest-tools|AD attack path visualization||bloodhound"
    "certipy|pentest-tools|AD certificate services attacks|--version|certipy"
    "wfuzz|pentest-tools|Web fuzzing|--help|wfuzz"
    "john|pentest-tools|Password cracking||john"
    "aircrack-ng|pentest-tools|WiFi cracking suite|--help|aircrack-ng"
    "wireshark|pentest-tools|Network protocol analysis|--version|wireshark,tshark"
    "burpsuite|pentest-tools|Web proxy and vulnerability scanning||burpsuite"
)

# Script reference mapping
declare -A SCRIPT_REFS=(
    ["jadx"]="apk-reverse/scripts/decode.sh"
    ["apktool"]="apk-reverse/scripts/decode.sh,apk-reverse/scripts/rebuild-sign-install.sh"
    ["adb"]="apk-reverse/scripts/rebuild-sign-install.sh"
    ["java"]="apk-reverse/scripts/decode.sh"
    ["apksigner"]="apk-reverse/scripts/rebuild-sign-install.sh"
    ["zipalign"]="apk-reverse/scripts/rebuild-sign-install.sh"
    ["frida"]="apk-reverse/scripts/frida-run.sh"
    ["frida-ps"]="apk-reverse/scripts/frida-run.sh"
    ["r2"]="radare2/scripts/recon.sh"
    ["rabin2"]="radare2/scripts/recon.sh"
    ["rasm2"]="radare2/SKILL.md"
    ["radiff2"]="radare2/SKILL.md"
    ["rahash2"]="radare2/SKILL.md"
    ["rax2"]="radare2/SKILL.md"
    ["python"]="apk-reverse/scripts/frida-run.sh"
    ["node"]="js-reverse/SKILL.md"
    ["npx"]="js-reverse/SKILL.md"
    ["jshookmcp"]="js-reverse/SKILL.md"
    ["reqable-mcp"]="pentest-tools/SKILL.md"
    ["xquik-mcp"]="threat-intelligence/SKILL.md"
    ["jeb-pro"]="apk-reverse/SKILL.md"
    ["binaryninja"]="binary-ninja-reverse/SKILL.md"
    ["agent-browser"]="browser-automation/SKILL.md"
    ["playwright"]="browser-automation/SKILL.md"
    ["nmap"]="pentest-tools/SKILL.md"
    ["proxycat"]="pentest-tools/SKILL.md"
    ["metasploitmcp"]="pentest-tools/SKILL.md"
    ["mcp-kali-server"]="pentest-tools/SKILL.md"
    ["hexstrike-ai"]="pentest-tools/SKILL.md"
    ["adaptixc2"]="pentest-tools/SKILL.md"
    ["sstimap"]="pentest-tools/SKILL.md"
    ["xsstrike"]="pentest-tools/SKILL.md"
    ["wpprobe"]="pentest-tools/SKILL.md"
    ["coercer"]="pentest-tools/SKILL.md"
    ["pentestswarm"]="pentest-tools/SKILL.md"
    ["evil-winrm-py"]="pentest-tools/SKILL.md"
    ["gef"]="reverse-engineering/SKILL.md"
    ["bkcrack"]="reverse-engineering/crypto-decode-tools.md,../CTF-Sandbox-Orchestrator/competition-zip-archive/SKILL.md"
    ["netexec"]="pentest-tools/SKILL.md"
    ["responder"]="pentest-tools/SKILL.md"
)

# ─── Tool discovery functions ─────────────────────────────────────────────────────────────────

# Find the full path of a command
find_command() {
    local name="$1"
    command -v "$name" 2>/dev/null || true
}

# Check whether a port is listening
test_tcp_port() {
    local port="$1"
    local host="${2:-127.0.0.1}"
    (echo >/dev/tcp/"$host"/"$port") 2>/dev/null && return 0
    # fallback to nc
    nc -z "$host" "$port" 2>/dev/null && return 0
    return 1
}

# Get the tool version
get_tool_version() {
    local cmd="$1"
    local version_args="$2"

    if [[ -z "$version_args" ]]; then
        echo ""
        return
    fi

    local output
    if [[ "${cmd##*/}" == "pwn" && "$version_args" == "version" ]]; then
        output=$(PWNLIB_NOTERM=1 "$cmd" version 2>&1 | head -n1) || true
    else
        output=$("$cmd" $version_args 2>&1 | head -n1) || true
    fi
    echo "$output"
}

# Parse a tool definition and check availability
# Returns: name|skill|purpose|available|resolved_path|version|source
resolve_tool() {
    local entry="$1"
    IFS='|' read -r name skill purpose version_args fallbacks <<< "$entry"

    IFS=',' read -ra candidates <<< "$fallbacks"

    for candidate in "${candidates[@]}"; do
        # Expand globs (such as build-tools/*/apksigner)
        local expanded
        expanded=$(compgen -G "$candidate" 2>/dev/null | head -n1) || expanded=""

        if [[ -n "$expanded" && -x "$expanded" ]]; then
            local ver
            ver=$(get_tool_version "$expanded" "$version_args")
            echo "${name}|${skill}|${purpose}|yes|${expanded}|${ver}|path"
            return
        fi

        # Try to resolve it as a command name
        local cmd_path
        cmd_path=$(find_command "$candidate")
        if [[ -n "$cmd_path" ]]; then
            local ver
            ver=$(get_tool_version "$cmd_path" "$version_args")
            echo "${name}|${skill}|${purpose}|yes|${cmd_path}|${ver}|command"
            return
        fi
    done

    # Not found
    echo "${name}|${skill}|${purpose}|no|||missing"
}

# Get the MCP configuration path (Claude Code)
get_claude_mcp_config_path() {
    echo "${HOME}/.claude/mcp.json"
}

# Check whether the MCP server is registered
check_mcp_registered() {
    local server_name="$1"
    local config_path
    config_path=$(get_claude_mcp_config_path)

    if [[ ! -f "$config_path" ]]; then
        echo "false"
        return
    fi

    if command -v jq &>/dev/null; then
        local result
        result=$(jq -r ".mcpServers.\"${server_name}\" // empty" "$config_path" 2>/dev/null)
        if [[ -n "$result" ]]; then
            echo "true"
        else
            echo "false"
        fi
    else
        # fallback: grep
        if grep -q "\"${server_name}\"" "$config_path" 2>/dev/null; then
            echo "true"
        else
            echo "false"
        fi
    fi
}

# Get the bootstrap manifest path
get_bootstrap_manifest_path() {
    echo "${KALI_SCRIPTS_DIR}/bootstrap-manifest.json"
}

# Get the capability definition from the manifest (needs jq)
get_capability_definition() {
    local name="$1"
    local manifest
    manifest=$(get_bootstrap_manifest_path)

    if [[ ! -f "$manifest" ]]; then
        echo ""
        return
    fi

    if command -v jq &>/dev/null; then
        jq -r ".capabilities[] | select(.name == \"${name}\")" "$manifest" 2>/dev/null
    else
        echo ""
    fi
}
