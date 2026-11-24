# ---------------------------------------------------------------------------------------------
# Runtime (tools/installer/runtime.sh). Bash 3.2 or later, POSIX tools only, no Python for the
# core and the packs. The data block above this line comes from install/spec.json and packs/.
# ---------------------------------------------------------------------------------------------

PO_NL='
'
PO_TAB="$(printf '\t')"
PO_HARNESS_MARK="prompt-orchestrator-harness"

po_say() { printf '%s\n' "$*"; }
po_warn() { printf 'warning: %s\n' "$*" >&2; }
po_die() { printf 'error: %s\n' "$*" >&2; exit 1; }

# ------------------------------------------------------------------ setup and locations

po_expand() {  # replace {NAME} tokens with the location L_NAME
    local s="$1" out="" name val
    while :; do
        case "$s" in
            *"{"[A-Z]*"}"*)
                out="$out${s%%"{"*}"
                s="${s#*"{"}"
                name="${s%%"}"*}"
                s="${s#*"}"}"
                eval "val=\${L_${name}-}"
                [ -n "$val" ] || po_die "location {$name} is not set"
                out="$out$val"
                ;;
            *) printf '%s' "$out$s"; return 0 ;;
        esac
    done
}

po_setup() {
    po_init_locations
    PO_DATA="$L_DATA_HOME"
    PO_MANIFEST="$PO_DATA/$PO_MANIFEST_NAME"
    PO_PACKS_DIR="$PO_ROOT/$PO_PACKS_REL"
    if command -v sha256sum >/dev/null 2>&1; then
        PO_SHA_TOOL=sha256sum
    elif command -v shasum >/dev/null 2>&1; then
        PO_SHA_TOOL=shasum
    else
        po_die "sha256sum or shasum is required"
    fi
    PO_TMP="$(mktemp -d "${TMPDIR:-/tmp}/po-install.XXXXXX")"
    trap 'rm -rf "$PO_TMP"' EXIT
    PO_STAMP="$(date +%Y%m%d-%H%M%S)"
    PO_CHANGES=0
    PO_OWNER=""
    : > "$PO_TMP/dirs.new"
    : > "$PO_TMP/ext.dirs.before"
}

po_sha() { if [ "$PO_SHA_TOOL" = sha256sum ]; then sha256sum; else shasum -a 256; fi; }
po_hash() { po_sha < "$1" | cut -c1-64; }

po_python_any() {  # first Python 3 on PATH, any minor version
    local c
    for c in python3 python; do
        if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info[0] != 3)' 2>/dev/null; then
            printf '%s' "$c"; return 0
        fi
    done
    return 1
}

po_python_harness() {  # Python that meets the harness minimum
    local c
    for c in python3 python; do
        if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys; sys.exit(sys.version_info < ($PO_HARNESS_PY_MAJOR, $PO_HARNESS_PY_MINOR))" 2>/dev/null; then
            printf '%s' "$c"; return 0
        fi
    done
    return 1
}

po_has_word() { case " $1 " in *" $2 "*) return 0 ;; esac; return 1; }

po_change() { PO_CHANGES=$((PO_CHANGES + 1)); }

# ------------------------------------------------------------------ manifest
# One line per record: owner, kind, path, hash, extra (tab separated). Kinds: f file (exact
# copy), d document (compared without the harness block), x file made by an external step,
# b marker block in a shared file, k backup of a replaced file or folder, u undo step,
# h harness install, m MCP server entry in a client config (extra: helper record),
# n private npm prefix of a pack, D folder the installer created (owner @dirs).

po_man_lines() { if [ -f "$PO_MANIFEST" ]; then cat "$PO_MANIFEST"; fi; }

po_man_owner() { po_man_lines | awk -F'\t' -v o="$1" '$1==o'; }

po_rec() { printf '%s\t%s\t%s\t%s\t%s\n' "$PO_OWNER" "$1" "$2" "${3:--}" "${4:--}" >> "$PO_TMP/new.tsv"; }

po_man_store() {  # $1 owner to replace (may be empty), $2 file with that owner's new lines
    [ "$PO_DRY" = 1 ] && return 0
    local had=0
    [ -f "$PO_MANIFEST" ] && had=1
    if [ "$had" = 0 ] && [ ! -s "$2" ] && [ ! -s "$PO_TMP/dirs.new" ]; then return 0; fi
    po_ensure_dir "$PO_DATA"
    { po_man_lines | awk -F'\t' -v o="$1" 'o=="" || $1!=o'; cat "$2" "$PO_TMP/dirs.new"; } \
        | awk '!seen[$0]++' > "$PO_TMP/manifest.next"
    : > "$PO_TMP/dirs.new"
    cp "$PO_TMP/manifest.next" "$PO_MANIFEST.tmp"
    mv "$PO_MANIFEST.tmp" "$PO_MANIFEST"
}

po_known_hash() {  # is path recorded with this hash by any owner?
    po_man_lines | awk -F'\t' -v p="$1" -v h="$2" '$3==p && $4==h {f=1} END {exit !f}'
}

po_ensure_dir() {  # mkdir -p that records each folder it creates
    local d="$1"
    [ -d "$d" ] && return 0
    [ -e "$d" ] && po_die "$d exists and is not a folder"
    po_ensure_dir "$(dirname "$d")"
    if [ "$PO_DRY" = 1 ]; then return 0; fi
    mkdir "$d"
    printf '@dirs\tD\t%s\t-\t-\n' "$d" >> "$PO_TMP/dirs.new"
}

po_owner_begin() {
    PO_OWNER="$1"
    : > "$PO_TMP/new.tsv"
    po_man_owner "$1" > "$PO_TMP/old.tsv"
}

po_owner_end() {  # store the owner's records and remove what this run no longer installs
    local owner="$PO_OWNER"
    if [ "$PO_DRY" = 1 ]; then PO_OWNER=""; return 0; fi
    # keep backups for paths that are still installed
    awk -F'\t' 'FILENAME==ARGV[1] { if ($2!="k") live[$3]=1; next }
        $2=="k" { if ($3 in live) { print; next } for (l in live) if (index(l, $3 "/")==1) { print; next } }' \
        "$PO_TMP/new.tsv" "$PO_TMP/old.tsv" > "$PO_TMP/keep.tsv"
    cat "$PO_TMP/keep.tsv" >> "$PO_TMP/new.tsv"
    awk -F'\t' 'FILENAME==ARGV[1] { seen[$2 FS $3]=1; next } !(($2 FS $3) in seen)' \
        "$PO_TMP/new.tsv" "$PO_TMP/old.tsv" > "$PO_TMP/stale.tsv"
    po_man_store "$owner" "$PO_TMP/new.tsv"
    if [ -s "$PO_TMP/stale.tsv" ]; then
        po_remove_lines "$PO_TMP/stale.tsv"
        po_sweep_dirs
    fi
    PO_OWNER=""
}

# ------------------------------------------------------------------ text helpers

po_trim_tail() { awk '{ l[NR]=$0 } END { n=NR; while (n>0 && l[n] ~ /^[ \t\r]*$/) n--; for (i=1; i<=n; i++) print l[i] }'; }

po_strip_harness() {  # print a file without the harness block, trailing blank lines dropped
    awk -v s="<!-- $PO_HARNESS_MARK:start -->" -v e="<!-- $PO_HARNESS_MARK:end -->" \
        '$0==s {skip=1} !skip {print} $0==e {skip=0}' "$1" | po_trim_tail
}

po_harness_block() {
    awk -v s="<!-- $PO_HARNESS_MARK:start -->" -v e="<!-- $PO_HARNESS_MARK:end -->" \
        '$0==s {on=1} on {print} $0==e {on=0}' "$1"
}

po_strip_block() {  # remove <!-- marker:start --> .. <!-- marker:end --> and one blank line before it
    awk -v s="<!-- $2:start -->" -v e="<!-- $2:end -->" '
        $0==s { skip=1; held=0; next }
        skip { if ($0==e) skip=0; next }
        { if (held) print pend; if ($0=="") { pend=$0; held=1 } else { print; held=0 } }
        END { if (held) print pend }' "$1"
}

# ------------------------------------------------------------------ file operations

po_backup() {  # move a file or folder we do not own out of the way, record it for restore
    local path="$1" dest
    dest="$PO_DATA/backups/$PO_STAMP${path}"
    po_ensure_dir "$(dirname "$dest")"
    mv "$path" "$dest"
    po_rec k "$path" "$dest"
    po_say "  backed up $path -> $dest"
}

po_put_file() {  # $1 source, $2 destination, $3 source hash, $4 destination hash or -
    local src="$1" dst="$2" sh="$3" dh="$4"
    if [ "$sh" = "$dh" ]; then po_rec f "$dst" "$sh"; return 0; fi
    po_change
    if [ "$PO_DRY" = 1 ]; then po_say "  would write $dst"; return 0; fi
    if [ "$dh" != "-" ] && ! po_known_hash "$dst" "$dh"; then po_backup "$dst"; fi
    po_ensure_dir "$(dirname "$dst")"
    rm -f "$dst"
    cp "$src" "$dst"
    po_rec f "$dst" "$sh"
}

po_list_files() {  # relative file paths under $1, sorted, without caches
    (cd "$1" && find . -type f ! -name '*.pyc' ! -name '.DS_Store' ! -path '*/__pycache__/*' | sed 's#^\./##' | LC_ALL=C sort)
}

po_hash_rel() {  # $1 folder, $2 list of relative paths -> "rel<TAB>hash"
    [ -s "$2" ] || return 0
    (cd "$1" && tr '\n' '\0' < "$2" | if [ "$PO_SHA_TOOL" = sha256sum ]; then xargs -0 sha256sum; else xargs -0 shasum -a 256; fi) \
        | awk '{ h=substr($0,1,64); r=substr($0,67); print r "\t" h }'
}

po_tree() {  # copy every file under folder $1 to folder $2
    local src="$1" dst="$2" rel sh dh
    [ -d "$src" ] || po_die "missing source folder $src (run: python3 tools/generate_integrations.py)"
    po_list_files "$src" > "$PO_TMP/tree.list"
    po_hash_rel "$src" "$PO_TMP/tree.list" > "$PO_TMP/tree.src"
    : > "$PO_TMP/tree.have"
    if [ -d "$dst" ]; then
        while IFS= read -r rel; do
            if [ -f "$dst/$rel" ]; then printf '%s\n' "$rel"; fi
        done < "$PO_TMP/tree.list" > "$PO_TMP/tree.have"
    fi
    po_hash_rel "$dst" "$PO_TMP/tree.have" > "$PO_TMP/tree.dst"
    awk -F'\t' 'FILENAME==ARGV[1] { d[$1]=$2; next } { print $1 "\t" $2 "\t" (($1 in d) ? d[$1] : "-") }' \
        "$PO_TMP/tree.dst" "$PO_TMP/tree.src" > "$PO_TMP/tree.plan"
    while IFS="$PO_TAB" read -r rel sh dh; do
        po_put_file "$src/$rel" "$dst/$rel" "$sh" "$dh"
    done < "$PO_TMP/tree.plan"
}

po_file() {  # exact copy of one file
    local src="$1" dst="$2" dh="-"
    [ -f "$src" ] || po_die "missing source file $src (run: python3 tools/generate_integrations.py)"
    [ -f "$dst" ] && dh="$(po_hash "$dst")"
    po_put_file "$src" "$dst" "$(po_hash "$src")" "$dh"
}

po_doc() {  # copy a document and keep a harness block that the destination holds
    local src="$1" dst="$2" sh dh="-" block=""
    [ -f "$src" ] || po_die "missing source file $src (run: python3 tools/generate_integrations.py)"
    sh="$(po_trim_tail < "$src" | po_sha | cut -c1-64)"
    if [ -f "$dst" ]; then
        dh="$(po_strip_harness "$dst" | po_sha | cut -c1-64)"
        block="$(po_harness_block "$dst")"
    fi
    if [ "$sh" = "$dh" ]; then po_rec d "$dst" "$sh"; return 0; fi
    po_change
    if [ "$PO_DRY" = 1 ]; then po_say "  would write $dst"; return 0; fi
    if [ "$dh" != "-" ] && ! po_known_hash "$dst" "$dh"; then
        cp "$dst" "$PO_TMP/doc.keep"
        po_backup "$dst"
    fi
    po_ensure_dir "$(dirname "$dst")"
    { po_trim_tail < "$src"; if [ -n "$block" ]; then printf '\n%s\n' "$block"; fi; } > "$PO_TMP/doc.next"
    cp "$PO_TMP/doc.next" "$dst"
    po_rec d "$dst" "$sh"
}

po_block() {  # $1 file, $2 marker, $3 text: append a marked block once
    local dst="$1" marker="$2" text="$3" made
    if [ -f "$dst" ] && grep -qF "<!-- $marker:start -->" "$dst"; then
        made="$(awk -F'\t' -v p="$dst" '$2=="b" && $3==p {print $5}' "$PO_TMP/old.tsv")"
        po_rec b "$dst" "$marker" "${made:-old}"
        return 0
    fi
    po_change
    if [ "$PO_DRY" = 1 ]; then po_say "  would add the $marker block to $dst"; return 0; fi
    made=old
    [ -f "$dst" ] || made=new
    po_ensure_dir "$(dirname "$dst")"
    printf '\n<!-- %s:start -->\n%s\n<!-- %s:end -->\n' "$marker" "$text" "$marker" >> "$dst"
    po_rec b "$dst" "$marker" "$made"
}

po_snapshot() {  # "path<TAB>hash" for every file under the tracked paths
    local p
    for p in "$@"; do
        if [ -d "$p" ]; then
            find "$p" -type f | LC_ALL=C sort | while IFS= read -r f; do printf '%s\t%s\n' "$f" "$(po_hash "$f")"; done
        elif [ -f "$p" ]; then
            printf '%s\t%s\n' "$p" "$(po_hash "$p")"
        fi
    done
}

po_missing_dirs() {  # folders from each path up to the first existing ancestor
    local p d
    for p in "$@"; do
        d="$p"
        [ -f "$d" ] && continue
        case "$d" in */*.json|*/.gitconfig) d="$(dirname "$d")" ;; esac
        while [ -n "$d" ] && [ "$d" != "/" ] && [ ! -d "$d" ]; do printf '%s\n' "$d"; d="$(dirname "$d")"; done
    done
}

po_dir_snapshot() {  # every folder under the tracked paths
    local p
    for p in "$@"; do if [ -d "$p" ]; then find "$p" -type d; fi; done | LC_ALL=C sort
}

po_track_begin() {  # snapshot the tracked paths in PO_TRACK before an external step
    po_snapshot "${PO_TRACK[@]}" > "$PO_TMP/ext.before"
    po_missing_dirs "${PO_TRACK[@]}" > "$PO_TMP/ext.dirs"
    po_dir_snapshot "${PO_TRACK[@]}" >> "$PO_TMP/ext.dirs.before"
}

po_track_end() {  # record files and folders the external step created
    local f h
    po_snapshot "${PO_TRACK[@]}" > "$PO_TMP/ext.after"
    while IFS="$PO_TAB" read -r f h; do
        if ! awk -F'\t' -v p="$f" '$1==p {found=1} END {exit !found}' "$PO_TMP/ext.before"; then
            po_rec x "$f" "$h"
        elif awk -F'\t' -v p="$f" '$2=="x" && $3==p {found=1} END {exit !found}' "$PO_TMP/old.tsv"; then
            po_rec x "$f" "$h"
        fi
    done < "$PO_TMP/ext.after"
    {
        while IFS= read -r f; do if [ -d "$f" ]; then printf '%s\n' "$f"; fi; done < "$PO_TMP/ext.dirs"
        po_dir_snapshot "${PO_TRACK[@]}" | awk -v b="$PO_TMP/ext.dirs.before" 'BEGIN { while ((getline l < b) > 0) seen[l]=1 } !($0 in seen)'
    } | while IFS= read -r f; do printf '@dirs\tD\t%s\t-\t-\n' "$f"; done >> "$PO_TMP/dirs.new"
    if ! cmp -s "$PO_TMP/ext.before" "$PO_TMP/ext.after"; then po_change; fi
    : > "$PO_TMP/ext.dirs.before"
}

po_attribution() {  # run ensure_attribution_off.py and record what it created
    local script="$1" hooks="$2" py
    shift 2
    if ! py="$(po_python_any)" || [ ! -f "$script" ]; then
        if [ "$PO_DRY" = 1 ] && [ -n "${py:-}" ]; then po_say "  would run $script"; return 0; fi
        po_warn "python3 or $script missing: AI attribution not forced off"
        return 0
    fi
    if [ "$PO_DRY" = 1 ]; then po_say "  would run $py $script"; return 0; fi
    PO_TRACK=("$@")
    po_track_begin
    "$py" "$script" --quiet || po_warn "ensure_attribution_off.py exited with an error"
    po_track_end
    po_rec u "$hooks" - git-hooks
    po_rec u "$1" - "json-strip:no-ai-trailer"
}

po_plugin() {  # $1 package, $2 mirror folder, $3 destination, $4 backup folder
    local src="$1" mirror="$2" dst="$3" backups="$4"
    if [ ! -f "$src/plugin.json" ] || [ ! -d "$src/skills" ]; then po_die "missing $src (run: python3 tools/generate_integrations.py)"; fi
    if ! diff -r -q -x __pycache__ -x '*.pyc' "$src/skills" "$mirror" >/dev/null 2>&1; then
        po_die "$src/skills differs from $mirror; regenerate with python3 tools/generate_integrations.py"
    fi
    if [ -L "$dst" ] || { [ -e "$dst" ] && [ ! -d "$dst" ]; }; then po_die "refusing to replace a link or file: $dst"; fi
    if [ -d "$dst" ] && ! po_man_lines | awk -F'\t' -v p="$dst/" 'index($3, p)==1 && $2=="f" {f=1} END {exit !f}'; then
        po_change
        if [ "$PO_DRY" = 1 ]; then
            po_say "  would move the existing plugin $dst to $backups"
        else
            po_ensure_dir "$backups"
            mv "$dst" "$backups/prompt-orchestrator-$PO_STAMP"
            po_rec k "$dst" "$backups/prompt-orchestrator-$PO_STAMP"
            po_say "  previous plugin kept at $backups/prompt-orchestrator-$PO_STAMP"
        fi
    fi
    po_tree "$src" "$dst"
}

# ------------------------------------------------------------------ JSON hook edits

po_json_strip() {  # $1 file, $2 text: drop hook entries whose command holds the text
    local f="$1" needle="$2" py
    [ -f "$f" ] || return 0
    grep -qF "$needle" "$f" || return 0
    if py="$(po_python_any)"; then
        "$py" - "$f" "$needle" <<'PO_PY'
import json, sys
path, needle = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as fh:
    data = json.load(fh)
hooks = data.get("hooks")
removed = 0
if isinstance(hooks, dict):
    for event in list(hooks):
        kept_groups = []
        for group in hooks[event] if isinstance(hooks[event], list) else []:
            entries = group.get("hooks", []) if isinstance(group, dict) else []
            kept = [h for h in entries if needle not in str(h.get("command", "")).replace("\\", "/")]
            removed += len(entries) - len(kept)
            if kept:
                kept_groups.append(dict(group, hooks=kept))
        if kept_groups:
            hooks[event] = kept_groups
        else:
            del hooks[event]
if removed:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(data, indent=2) + "\n")
PO_PY
    elif command -v jq >/dev/null 2>&1; then
        jq --arg n "$needle" '(.hooks // {}) as $h | if ($h|type)=="object" then .hooks = ($h | with_entries(.value |= (map(.hooks |= map(select(((.command // "") | gsub("\\\\"; "/") | contains($n)) | not))) | map(select((.hooks | length) > 0)))) | with_entries(select((.value | length) > 0))) else . end' \
            "$f" > "$PO_TMP/json.next" && cp "$PO_TMP/json.next" "$f"
    else
        po_warn "$f still holds hook entries for $needle; remove them by hand (no python3 or jq)"
    fi
}

po_json_add_hooks() {  # $1 file, $2 command, $3 lines "event<TAB>matcher<TAB>timeout<TAB>status", $4 text that marks ours
    local f="$1" cmd="$2" spec="$3" mark="$4" py
    if [ -f "$f" ] && grep -qF "$mark" "$f"; then return 1; fi
    if py="$(po_python_any)"; then
        "$py" - "$f" "$cmd" "$spec" <<'PO_PY'
import json, os, sys
path, command, spec = sys.argv[1], sys.argv[2], sys.argv[3]
data = {}
if os.path.exists(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
hooks = data.setdefault("hooks", {})
for line in spec.splitlines():
    event, matcher, timeout, status = line.split("\t")
    group = {"hooks": [{"type": "command", "command": command, "timeout": int(timeout), "statusMessage": status}]}
    if matcher != "-":
        group = {"matcher": matcher, **group}
    hooks.setdefault(event, []).append(group)
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(data, indent=2) + "\n")
PO_PY
        return 0
    fi
    if [ ! -f "$f" ]; then
        local event matcher timeout status first=1 esc
        esc="$(printf '%s' "$cmd" | sed 's/\\/\\\\/g; s/"/\\"/g')"
        {
            printf '{\n  "hooks": {\n'
            while IFS="$PO_TAB" read -r event matcher timeout status; do
                [ "$first" = 1 ] || printf ',\n'
                first=0
                printf '    "%s": [{' "$event"
                [ "$matcher" = "-" ] || printf '"matcher": "%s", ' "$matcher"
                printf '"hooks": [{"type": "command", "command": "%s", "timeout": %s, "statusMessage": "%s"}]}]' "$esc" "$timeout" "$status"
            done <<PO_SPEC
$spec
PO_SPEC
            printf '\n  }\n}\n'
        } > "$f"
        return 0
    fi
    po_warn "add the hooks for $cmd to $f by hand (no python3 for the JSON merge)"
    return 1
}

# ------------------------------------------------------------------ removal

po_remove_lines() {  # remove the records in file $1; paths other owners still use stay
    local kind path hash extra shared cur
    po_man_lines | awk -F'\t' -v o="$PO_OWNER_REMOVING" '$1!=o && $1!="@dirs"' > "$PO_TMP/ref.tsv"
    if [ -f "$PO_TMP/new.tsv" ] && [ -n "$PO_OWNER" ]; then cat "$PO_TMP/new.tsv" >> "$PO_TMP/ref.tsv"; fi
    awk -F'\t' 'FILENAME==ARGV[1] { if ($2!="k" && $2!="u" && $2!="h" && $2!="m" && $2!="n") ref[$3]=1; next } { print (($3 in ref && $2!="m" && $2!="n") ? 1 : 0) "\t" $2 "\t" $3 "\t" $4 "\t" $5 }' \
        "$PO_TMP/ref.tsv" "$1" > "$PO_TMP/rm.tsv"
    # harness first: its uninstall reads the files the core put there
    while IFS="$PO_TAB" read -r shared kind path hash extra; do
        [ "$kind" = h ] || continue
        po_harness_uninstall "$path"
    done < "$PO_TMP/rm.tsv"
    while IFS="$PO_TAB" read -r shared kind path hash extra; do
        [ "$shared" = 0 ] || continue
        case "$kind" in
            f|x)
                [ -f "$path" ] || continue
                if [ "$(po_hash "$path")" = "$hash" ]; then rm -f "$path"; po_change
                else po_warn "kept $path: changed since install"; fi
                ;;
            d)
                [ -f "$path" ] || continue
                if [ "$(po_strip_harness "$path" | po_sha | cut -c1-64)" = "$hash" ]; then
                    if grep -qF "<!-- $PO_HARNESS_MARK:start -->" "$path"; then
                        po_harness_block "$path" > "$PO_TMP/doc.next"; cp "$PO_TMP/doc.next" "$path"
                    else
                        rm -f "$path"
                    fi
                    po_change
                else
                    po_warn "kept $path: changed since install"
                fi
                ;;
            b)
                [ -f "$path" ] || continue
                po_strip_block "$path" "$hash" > "$PO_TMP/block.next"
                if [ "$extra" = new ] && ! grep -q '[^[:space:]]' "$PO_TMP/block.next"; then rm -f "$path"
                else cp "$PO_TMP/block.next" "$path"; fi
                po_change
                ;;
            m) po_mcp_unregister "$path" "$hash" "$extra" ;;
        esac
    done < "$PO_TMP/rm.tsv"
    while IFS="$PO_TAB" read -r shared kind path hash extra; do
        case "$kind:$extra" in
            u:git-hooks)
                if command -v git >/dev/null 2>&1; then
                    cur="$(git config --global --get core.hooksPath 2>/dev/null || true)"
                    if [ "$cur" = "$path" ]; then git config --global --unset core.hooksPath && po_change; fi
                fi
                ;;
            u:json-strip:*) po_json_strip "$path" "${extra#json-strip:}" ;;
            u:npm-rm:*) po_npm_remove "$path" "${extra#npm-rm:}" ;;
            n:*)
                case "$path" in
                    "$PO_DATA/packages/"?*) if [ -d "$path" ]; then rm -rf "$path"; po_change; fi ;;
                    *) po_warn "kept $path: not inside $PO_DATA/packages" ;;
                esac
                ;;
        esac
    done < "$PO_TMP/rm.tsv"
    while IFS="$PO_TAB" read -r shared kind path hash extra; do
        [ "$kind" = k ] || continue
        if [ -d "$path" ] && [ -e "$hash" ]; then find "$path" -depth -type d -empty -exec rmdir {} \; 2>/dev/null || true; fi
        if [ ! -e "$path" ] && [ -e "$hash" ]; then
            mkdir -p "$(dirname "$path")"
            mv "$hash" "$path"
            po_say "  restored $path"
            po_change
        fi
    done < "$PO_TMP/rm.tsv"
}

po_sweep_dirs() {  # remove folders the installer created once they are empty
    [ -f "$PO_MANIFEST" ] || return 0
    local d
    awk -F'\t' '$1=="@dirs" {print $3}' "$PO_MANIFEST" | LC_ALL=C sort -r > "$PO_TMP/dirs.list"
    : > "$PO_TMP/dirs.gone"
    while IFS= read -r d; do
        if [ ! -d "$d" ]; then printf '%s\n' "$d" >> "$PO_TMP/dirs.gone"; continue; fi
        [ "$d" = "$PO_DATA" ] && continue
        if rmdir "$d" 2>/dev/null; then printf '%s\n' "$d" >> "$PO_TMP/dirs.gone"; fi
    done < "$PO_TMP/dirs.list"
    if [ -s "$PO_TMP/dirs.gone" ]; then
        awk -F'\t' 'FILENAME==ARGV[1] {g[$0]=1; next} !($1=="@dirs" && ($3 in g))' "$PO_TMP/dirs.gone" "$PO_MANIFEST" > "$PO_TMP/manifest.next"
        cp "$PO_TMP/manifest.next" "$PO_MANIFEST"
    fi
    if ! awk -F'\t' '$1!="@dirs" {f=1} END {exit !f}' "$PO_MANIFEST"; then
        awk -F'\t' '$1=="@dirs" {print $3}' "$PO_MANIFEST" | LC_ALL=C sort -r > "$PO_TMP/dirs.list"
        rm -f "$PO_MANIFEST"
        while IFS= read -r d; do rmdir "$d" 2>/dev/null || true; done < "$PO_TMP/dirs.list"
    fi
}

po_remove_owner() {
    local owner="$1"
    po_man_owner "$owner" > "$PO_TMP/owner.rm"
    [ -s "$PO_TMP/owner.rm" ] || return 0
    po_say "--- removing $owner"
    if [ "$PO_DRY" = 1 ]; then
        awk -F'\t' '$2!="D" {print "  would remove " $3}' "$PO_TMP/owner.rm"
        return 0
    fi
    PO_OWNER_REMOVING="$owner"
    PO_OWNER=""
    po_remove_lines "$PO_TMP/owner.rm"
    PO_OWNER_REMOVING=""
    po_man_lines | awk -F'\t' -v o="$owner" '$1!=o' > "$PO_TMP/manifest.next"
    cp "$PO_TMP/manifest.next" "$PO_MANIFEST"
    po_sweep_dirs
}

po_owner_prefix() {  # is an owner recorded that starts with $1 (and is not $2)?
    po_owners | awk -v p="$1" -v x="${2:-}" 'index($0, p)==1 && $0!=x {f=1} END {exit !f}'
}

po_owners() { po_man_lines | awk -F'\t' '$1!="@dirs" && !seen[$1]++ {print $1}'; }

# ------------------------------------------------------------------ tools and projects

po_run_steps() {  # $1 lines "op<TAB>a<TAB>b<TAB>c<TAB>d"
    local op a b c d
    while IFS="$PO_TAB" read -r op a b c d; do
        [ -n "$op" ] || continue
        case "$op" in
            tree) po_tree "$PO_ROOT/$a" "$(po_expand "$b")" ;;
            file) po_file "$PO_ROOT/$a" "$(po_expand "$b")" ;;
            doc) po_doc "$PO_ROOT/$a" "$(po_expand "$b")" ;;
            block) po_block "$(po_expand "$a")" "$b" "$c" ;;
            attribution)
                local tracks=() t
                local IFS_OLD="$IFS"
                IFS='|'
                for t in $c; do tracks+=("$(IFS="$IFS_OLD"; po_expand "$t")"); done
                IFS="$IFS_OLD"
                po_attribution "$(po_expand "$a")" "$(po_expand "$b")" "${tracks[@]}"
                ;;
            plugin) po_plugin "$PO_ROOT/$a" "$PO_ROOT/$b" "$(po_expand "$c")" "$(po_expand "$d")" ;;
            *) po_die "unknown step $op" ;;
        esac
    done <<PO_STEPS
$1
PO_STEPS
}

po_install_core() {
    local tool="$1" steps
    steps="$(po_tool_steps "$tool")"
    [ -n "$steps" ] || return 0
    po_say "=== core: $(po_tool_label "$tool")"
    po_owner_begin "core:$tool"
    po_run_steps "$steps"
    po_owner_end
}

po_install_project() {  # $1 project id, $2 folder
    local kind="$1" dir="$2"
    [ -d "$dir" ] || po_die "project folder does not exist: $dir"
    dir="$(cd "$dir" && pwd)"
    if [ "$dir" = "$PO_ROOT" ]; then po_say "==> $dir is the prompt-orchestrator source; nothing to copy"; return 0; fi
    # shellcheck disable=SC2034  # read through po_expand
    L_PROJECT="$dir"
    po_say "=== $(po_project_label "$kind"): $dir"
    po_owner_begin "$kind:$dir"
    po_run_steps "$(po_project_steps "$kind")"
    po_owner_end
}

# ------------------------------------------------------------------ harness

po_harness_install() {
    local tool="$1" py family profile opt
    po_has_word "$PO_HARNESS_TOOLS" "$tool" || return 0
    if ! py="$(po_python_harness)"; then
        po_say "  harness skipped for $tool: needs Python $PO_HARNESS_PY_MAJOR.$PO_HARNESS_PY_MINOR or later"
        return 0
    fi
    set -- "$PO_ROOT/$PO_HARNESS_SCRIPT" install --tool "$tool"
    family="$(po_harness_family "$tool")"
    profile=""
    [ "$family" = claude ] && profile="$PO_PROFILE_CLAUDE"
    [ "$family" = codex ] && profile="$PO_PROFILE_CODEX"
    [ -n "$profile" ] && set -- "$@" --profile "$profile"
    for opt in $PO_HARNESS_OFF; do set -- "$@" "--no-$opt"; done
    po_say "=== harness: $(po_tool_label "$tool")"
    po_say "  \$ $py $*"
    [ "$PO_DRY" = 1 ] && return 0
    "$py" "$@" || { PO_FAILED="$PO_FAILED harness:$tool"; return 0; }
    po_owner_begin "harness:$tool"
    po_rec h "$tool"
    po_owner_end
}

po_harness_uninstall() {
    local tool="$1" py
    if ! py="$(po_python_harness)"; then
        po_warn "harness for $tool not removed: needs Python $PO_HARNESS_PY_MAJOR.$PO_HARNESS_PY_MINOR or later"
        return 0
    fi
    "$py" "$PO_ROOT/$PO_HARNESS_SCRIPT" uninstall --tool "$tool" || po_warn "harness uninstall failed for $tool"
}

# ------------------------------------------------------------------ packs

po_pack_known() { po_has_word "$PO_PACKS" "$1"; }
po_set_known() { po_has_word "$(po_pack_get "$1" sets)" "$2"; }

po_add_sets() {  # parse "pack[:set],set,pack2" into PO_SEL_SETS
    local spec="$1" tok cur="" p s IFS_OLD="$IFS"
    IFS=','
    for tok in $spec; do
        IFS="$IFS_OLD"
        [ -n "$tok" ] || continue
        case "$tok" in
            *:*)
                p="${tok%%:*}"; s="${tok#*:}"
                po_pack_known "$p" || po_die "unknown pack: $p (see: install.sh packs list)"
                cur="$p"
                if [ -z "$s" ] || [ "$s" = "*" ]; then
                    for s in $(po_base_sets "$p"); do po_sel_add "$p:$s"; done
                else
                    po_set_known "$p" "$s" || po_die "pack $p has no set $s"
                    po_sel_add "$p:$s"
                fi
                ;;
            *)
                if po_pack_known "$tok"; then
                    cur="$tok"
                    for s in $(po_base_sets "$tok"); do po_sel_add "$tok:$s"; done
                elif [ -n "$cur" ] && po_set_known "$cur" "$tok"; then
                    po_sel_add "$cur:$tok"
                else
                    po_die "unknown pack or set: $tok"
                fi
                ;;
        esac
        IFS=','
    done
    IFS="$IFS_OLD"
}

po_sel_add() { po_has_word "$PO_SEL_SETS" "$1" || PO_SEL_SETS="${PO_SEL_SETS:+$PO_SEL_SETS }$1"; }

po_base_sets() {  # sets of pack $1 that require no other set; a bare pack name selects these
    local s
    for s in $(po_pack_get "$1" sets); do [ -z "$(po_set_get "$1" "$s" requires)" ] && printf '%s ' "$s"; done
    return 0
}

po_sel_toggle() {  # toggle "pack:set" and keep required sets with it
    local p="${1%%:*}" s="${1#*:}" o r
    if po_has_word "$PO_SEL_SETS" "$1"; then
        po_sel_del "$1"
        for o in $(po_pack_get "$p" sets); do po_has_word "$(po_set_get "$p" "$o" requires)" "$s" && po_sel_del "$p:$o"; done
    else
        for r in $(po_set_get "$p" "$s" requires); do po_sel_add "$p:$r"; done
        po_sel_add "$1"
    fi
    return 0
}
po_sel_del() {
    local out="" w
    for w in $PO_SEL_SETS; do [ "$w" = "$1" ] || out="${out:+$out }$w"; done
    PO_SEL_SETS="$out"
}

po_pack_tools() {  # tools that receive pack skills
    local t out=""
    if [ -n "$PO_TOOLS_GIVEN" ]; then printf '%s' "$PO_SEL_TOOLS"; return 0; fi
    for t in $(po_owners | awk -F: '$1=="core" {print $2}'); do out="${out:+$out }$t"; done
    if [ "$PO_DO_CORE" = 1 ]; then for t in $PO_SEL_TOOLS; do po_has_word "$out" "$t" || out="${out:+$out }$t"; done; fi
    [ -n "$out" ] || out="$PO_SEL_TOOLS"
    printf '%s' "$out"
}

po_install_set() {  # $1 pack, $2 set, $3 tools
    local pack="$1" set="$2" tools="$3" kind tool dir skill mcp=""
    kind="$(po_pack_get "$pack" kind)"
    po_say "=== pack $pack, set $set ($(po_set_get "$pack" "$set" count) skills)"
    if [ "$kind" = release ]; then po_release_install "$pack" "$set" "$tools"; return 0; fi
    [ -n "$(po_mcp_get "$pack" set)" ] && [ "$(po_mcp_get "$pack" set)" = "$set" ] && mcp=1
    if po_has_word "$(po_npm_get "$pack" "" sets)" "$set"; then
        po_node_ready "$pack" npm
        po_npm_install "$pack" "$set"
    elif [ -n "$mcp" ]; then
        po_node_ready "$pack"
    fi
    for tool in $tools; do
        if [ -z "$mcp" ] || [ -z "$(po_tool_mcp "$tool")" ]; then
            if [ -z "$(po_tool_skills "$tool")" ] || [ -z "$(po_set_get "$pack" "$set" skills)" ]; then continue; fi
        fi
        po_owner_begin "pack:$pack:$set:$tool"
        for skill in $(po_set_get "$pack" "$set" skills); do
            while IFS= read -r dir; do
                [ -n "$dir" ] || continue
                po_tree "$PO_PACKS_DIR/$pack/skills/$skill" "$(po_expand "$dir")/$skill"
            done <<PO_DIRS
$(po_tool_skills "$tool")
PO_DIRS
        done
        if [ -n "$mcp" ]; then po_mcp_register "$pack" "$tool"; fi
        po_owner_end
    done
    if [ "$kind" = package ]; then
        po_owner_begin "pack:$pack:payload"
        po_tree "$PO_PACKS_DIR/$pack/$(po_pack_get "$pack" payload)" "$PO_DATA/packages/$pack"
        po_owner_end
    fi
}

po_remove_pack_spec() {  # "pack" or "pack:set"; a set takes the sets that require it along
    local spec="$1" pack set owner rest sets="" s
    pack="${spec%%:*}"
    set=""
    case "$spec" in *:*) set="${spec#*:}" ;; esac
    po_pack_known "$pack" || po_die "unknown pack: $pack"
    if [ -n "$set" ]; then
        po_set_known "$pack" "$set" || po_die "pack $pack has no set $set"
        for s in $(po_pack_get "$pack" sets); do po_has_word "$(po_set_get "$pack" "$s" requires)" "$set" && sets="$sets $s"; done
        sets="$sets $set"
    fi
    po_owners > "$PO_TMP/owners.list"
    for s in ${sets:-"*"}; do
        while IFS= read -r owner <&3; do
            case "$owner" in "pack:$pack:"*) ;; *) continue ;; esac
            rest="${owner#"pack:$pack:"}"
            case "$rest" in payload|npm) continue ;; esac
            if [ "$s" != "*" ] && [ "${rest%%:*}" != "$s" ]; then continue; fi
            po_remove_owner "$owner"
        done 3< "$PO_TMP/owners.list"
    done
    if ! po_owners | awk -v p="pack:$pack:" 'index($0, p)==1 && $0!=p "payload" && $0!=p "npm" {f=1} END {exit !f}'; then
        po_remove_owner "pack:$pack:payload"
        po_remove_owner "pack:$pack:npm"
    fi
}

# ------------------------------------------------------------------ npm and MCP packs

po_helper() { node "$PO_ROOT/$PO_PACK_HELPER" "$@"; }

po_node_ready() {  # $1 pack, $2 "npm" when the pack installs npm packages
    local pack="$1" range msg
    command -v node >/dev/null 2>&1 || po_die "pack $pack needs Node.js on PATH"
    if [ "${2:-}" = npm ]; then
        command -v npm >/dev/null 2>&1 || po_die "pack $pack needs npm on PATH"
        range="$(po_npm_get "$pack" "" node)"
        msg="$(po_helper node-check "$range")" || po_die "pack $pack: $msg"
    fi
}

po_npm() {  # npm with a throwaway cache and without the update notifier, audit and funding messages
    env NO_UPDATE_NOTIFIER=1 npm_config_update_notifier=false npm_config_audit=false npm_config_fund=false \
        npm_config_cache="$PO_TMP/npm-cache" npm "$@"
}

po_npm_check() {  # $1 prefix, $2 pack, $3 set: prints the helper verdict, fails unless ok
    po_helper npm-check "$1" "$(po_npm_get "$2" "$3" name)" "$(po_npm_get "$2" "$3" version)" "$(po_npm_get "$2" "$3" integrity)"
}

po_npm_install() {  # $1 pack, $2 set: install the set's pinned npm package into <data_home>/packages/<pack>
    local pack="$1" set="$2" prefix name version verdict
    prefix="$PO_DATA/packages/$pack"
    name="$(po_npm_get "$pack" "$set" name)"
    version="$(po_npm_get "$pack" "$set" version)"
    if [ "$set" != "$(po_npm_get "$pack" "" base)" ]; then po_npm_addon "$pack" "$set" "$prefix"; return 0; fi
    po_owner_begin "pack:$pack:npm"
    if verdict="$(po_npm_check "$prefix" "$pack" "$set")"; then
        po_rec n "$prefix" "$name@$version"
        po_npm_absent "$pack" "$prefix"
        po_owner_end
        return 0
    fi
    po_change
    if [ "$PO_DRY" = 1 ]; then
        po_say "  would run npm install --prefix $prefix $name@$version --omit=optional --ignore-scripts and check its integrity"
        po_owner_end
        return 0
    fi
    if [ -e "$prefix" ] && ! awk -F'\t' -v p="$prefix" '$2=="n" && $3==p {f=1} END {exit !f}' "$PO_TMP/old.tsv"; then po_backup "$prefix"; fi
    po_ensure_dir "$prefix"
    po_say "  \$ npm install --prefix $prefix $name@$version --omit=optional --ignore-scripts --save-exact"
    if ! po_npm install --prefix "$prefix" "$name@$version" --omit=optional --ignore-scripts --save-exact --no-audit --no-fund; then
        rm -rf "$prefix"
        po_die "npm install of $name@$version failed"
    fi
    if ! verdict="$(po_npm_check "$prefix" "$pack" "$set")"; then
        rm -rf "$prefix"
        po_die "$name@$version in $prefix fails the pinned check ($verdict); refusing to install"
    fi
    po_say "  $name@$version matches the pinned integrity"
    po_rec n "$prefix" "$name@$version"
    po_npm_absent "$pack" "$prefix"
    po_owner_end
}

po_npm_absent() {  # $1 pack, $2 prefix: packages of sets that are not installed must be absent
    local s
    for s in $(po_npm_get "$1" "" sets); do
        [ "$s" = "$(po_npm_get "$1" "" base)" ] && continue
        po_has_word "$PO_SEL_SETS" "$1:$s" && continue
        po_owner_prefix "pack:$1:$s:" && continue
        if [ -e "$2/node_modules/$(po_npm_get "$1" "$s" name)" ]; then
            po_die "$2 holds $(po_npm_get "$1" "$s" name), but set $1:$s is not installed; remove $2 and install again"
        fi
    done
}

po_npm_addon() {  # $1 pack, $2 set, $3 prefix: an npm package and its pinned native binding
    local pack="$1" set="$2" prefix="$3" name version url member plat want file asset got binding have src
    name="$(po_npm_get "$pack" "$set" name)"
    version="$(po_npm_get "$pack" "$set" version)"
    url="$(po_npm_get "$pack" "$set" url)"
    member="$(po_npm_get "$pack" "$set" member)"
    binding="$prefix/node_modules/$name/$member"
    po_owner_begin "pack:$pack:$set:all"
    have="$(awk -F'\t' -v p="$binding" '$2=="x" && $3==p {print $4}' "$PO_TMP/old.tsv")"
    if po_npm_check "$prefix" "$pack" "$set" >/dev/null && { [ -z "$url" ] || { [ -f "$binding" ] && [ "$(po_hash "$binding")" = "$have" ]; }; }; then
        [ -n "$url" ] && po_rec x "$binding" "$have"
        po_rec u "$prefix" - "npm-rm:$name"
        po_owner_end
        return 0
    fi
    po_change
    if [ -n "$url" ]; then
        plat="$(po_helper platform)"
        want="$(po_npm_get "$pack" "$set" "sha256:$plat")"
        [ -n "$want" ] || po_die "no pinned digest for the $name binding on $plat; refusing to install $pack:$set"
        url="$(printf '%s' "$url" | sed "s/{version}/$version/g; s/{platform}/$plat/g")"
        file="${url##*/}"
    fi
    if [ "$PO_DRY" = 1 ]; then
        [ -n "$url" ] && po_say "  would download $url and check its sha256 against $want"
        po_say "  would run npm install --prefix $prefix $name@$version --ignore-scripts and check its integrity"
        po_owner_end
        return 0
    fi
    if [ -n "$url" ]; then
        src="$(po_bundle_for "$pack")"
        if [ -n "$src" ]; then
            asset="$src/$file"
            [ -f "$asset" ] || po_die "bundle folder has no $file: $src"
        else
            asset="$PO_TMP/$file"
            po_fetch "$url" "$asset"
        fi
        got="$(po_hash "$asset")"
        [ "$got" = "$want" ] || po_die "$file has sha256 $got, but $pack pins $want; refusing to install $pack:$set"
        po_say "  $file matches the pinned sha256"
        rm -rf "$PO_TMP/binding"
        mkdir -p "$PO_TMP/binding"
        tar -xzf "$asset" -C "$PO_TMP/binding" "$member" || po_die "cannot extract $member from $file"
        [ -f "$PO_TMP/binding/$member" ] || po_die "$file holds no $member"
    fi
    po_say "  \$ npm install --prefix $prefix $name@$version --ignore-scripts --save-exact"
    po_npm install --prefix "$prefix" "$name@$version" --omit=optional --ignore-scripts --save-exact --no-audit --no-fund \
        || po_die "npm install of $name@$version failed"
    if ! got="$(po_npm_check "$prefix" "$pack" "$set")"; then
        po_npm uninstall --prefix "$prefix" "$name" --ignore-scripts --no-audit --no-fund >/dev/null 2>&1 || true
        po_die "$name@$version in $prefix fails the pinned check ($got); refusing to install"
    fi
    po_say "  $name@$version matches the pinned integrity"
    if [ -n "$url" ]; then
        mkdir -p "$(dirname "$binding")"
        cp "$PO_TMP/binding/$member" "$binding"
        po_rec x "$binding" "$(po_hash "$binding")"
        po_say "  binding -> $binding"
    fi
    po_rec u "$prefix" - "npm-rm:$name"
    po_owner_end
}

po_npm_remove() {  # $1 prefix, $2 package: undo an add-on npm install
    [ -d "$1/node_modules/$2" ] || return 0
    if command -v npm >/dev/null 2>&1 && po_npm uninstall --prefix "$1" "$2" --ignore-scripts --no-audit --no-fund >/dev/null 2>&1; then
        po_change
    else
        po_warn "could not run npm uninstall $2 in $1; remove $1/node_modules/$2 by hand"
    fi
}

po_mcp_register() {  # $1 pack, $2 tool: add the pack's MCP server to the tool's config
    local pack="$1" tool="$2" line format file name old out status rest resolved rec
    line="$(po_tool_mcp "$tool")"
    [ -n "$line" ] || return 0
    format="${line%%"$PO_TAB"*}"
    file="$(po_expand "${line#*"$PO_TAB"}")"
    name="$(po_mcp_get "$pack" name)"
    old="$(awk -F'\t' '$2=="m" {print $5; exit}' "$PO_TMP/old.tsv")"
    if [ "$PO_DRY" = 1 ]; then
        po_say "  would register the MCP server $name in $file"
        po_change
        return 0
    fi
    po_ensure_dir "$(dirname "$file")"
    out="$(po_helper mcp-add "$format" "$file" "$name" "$(po_mcp_get "$pack" spec_b64)" "$PO_DATA/packages/$pack" "${old:--}")" \
        || po_die "MCP registration failed for $file"
    status="${out%%"$PO_TAB"*}"
    rest="${out#*"$PO_TAB"}"
    resolved="${rest%%"$PO_TAB"*}"
    rec="${rest#*"$PO_TAB"}"
    case "$status" in
        added) po_change; po_say "  MCP server $name -> $resolved"; po_rec m "$resolved" "$name" "$rec" ;;
        present) po_rec m "$resolved" "$name" "$rec" ;;
        foreign) po_say "  $resolved already has the same $name entry; the installer leaves it unmanaged" ;;
        *) po_warn "MCP server $name not registered in $resolved" ;;
    esac
}

po_mcp_unregister() {  # $1 config file, $2 server name, $3 helper record
    local verdict
    if ! command -v node >/dev/null 2>&1; then
        po_warn "Node.js not found: remove the $2 entry from $1 by hand"
        return 0
    fi
    verdict="$(po_helper mcp-remove "$3")" || verdict=error
    case "$verdict" in
        removed) po_change ;;
        absent) ;;
        changed) po_warn "kept the $2 entry in $1: changed since install" ;;
        *) po_warn "could not remove the $2 entry from $1" ;;
    esac
}

po_sets_ordered() {  # selected sets, the sets that others require first
    local w
    for w in $PO_SEL_SETS; do [ -z "$(po_set_get "${w%%:*}" "${w#*:}" requires)" ] && printf '%s\n' "$w"; done
    for w in $PO_SEL_SETS; do [ -n "$(po_set_get "${w%%:*}" "${w#*:}" requires)" ] && printf '%s\n' "$w"; done
    return 0
}

po_check_requires() {  # refuse a set whose required set is neither selected nor installed
    local w p s r
    for w in $PO_SEL_SETS; do
        p="${w%%:*}"
        s="${w#*:}"
        for r in $(po_set_get "$p" "$s" requires); do
            po_has_word "$PO_SEL_SETS" "$p:$r" && continue
            po_owner_prefix "pack:$p:$r:" && continue
            po_die "set $p:$s needs set $p:$r; install both, for example --packs $p:$r,$s"
        done
    done
}

# ------------------------------------------------------------------ release packs (procable)

po_platform() {  # print "os arch"
    local os arch
    case "$(uname -s)" in
        Linux) os=linux ;;
        Darwin) os=darwin ;;
        MINGW*|MSYS*|CYGWIN*) os=windows ;;
        *) po_die "unsupported platform $(uname -s)" ;;
    esac
    case "$(uname -m)" in
        x86_64|amd64) arch=x64 ;;
        arm64|aarch64) arch=arm64 ;;
        *) po_die "unsupported machine $(uname -m)" ;;
    esac
    [ "$os" = windows ] && arch=x64
    printf '%s %s' "$os" "$arch"
}

po_lock_value() {  # value of a flat string key in a JSON file
    tr ',{}' '\n' < "$1" | sed -n "s/^[[:space:]]*\"$2\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p" | head -n 1
}

po_fetch() {
    po_say "  get $1"
    if command -v curl >/dev/null 2>&1; then curl -fsSL -o "$2.part" "$1"
    elif command -v wget >/dev/null 2>&1; then wget -q -O "$2.part" "$1"
    else po_die "curl or wget is required to download $1"; fi
    mv "$2.part" "$2"
}

po_release_install() {  # $1 pack, $2 set, $3 tools
    local pack="$1" set="$2" tools="$3" lock version repo pinned os arch engine bundle src tag base name
    local providers="" t p skill roots root dir bin hooks codex_dir launcher env_name
    lock="$PO_PACKS_DIR/$pack/$(po_release_get "$pack" lock)"
    version="$(po_lock_value "$lock" version)"
    repo="$(po_lock_value "$lock" repo)"
    pinned="$(po_lock_value "$lock" sha256sums)"
    if [ -z "$version" ] || [ -z "$repo" ] || [ -z "$pinned" ]; then po_die "$lock does not pin version, repo and sha256sums"; fi
    os="$(po_platform)"
    arch="${os#* }"
    os="${os% *}"
    engine="$(po_release_get "$pack" engine | sed "s/{os}/$os/; s/{arch}/$arch/")"
    [ "$os" = windows ] && engine="$engine.exe"
    bundle="$(po_release_get "$pack" bundle)"
    skill="$(po_set_get "$pack" "$set" skills)"
    for t in $tools; do
        p="$(po_release_provider "$pack" "$t")"
        [ -n "$p" ] && ! po_has_word "$providers" "$p" && providers="${providers:+$providers }$p"
    done
    if [ -z "$providers" ]; then po_say "  no selected tool is supported by $pack"; return 0; fi
    providers="$(printf '%s' "$providers" | tr ' ' '\n' | LC_ALL=C sort | tr '\n' ',' | sed 's/,$//')"
    tag="$(po_release_get "$pack" tag | sed "s/{version}/$version/")"
    base="https://github.com/$repo/releases/download/$tag"
    if [ -n "$(po_bundle_for "$pack")" ]; then
        src="$(po_bundle_for "$pack")"
        [ -d "$src" ] || po_die "bundle folder does not exist: $src"
        src="$(cd "$src" && pwd)"
    else
        src="$PO_DATA/packages/$pack/$version"
    fi
    po_say "  $pack $version for $providers ($os-$arch) from $src"
    if [ "$PO_DRY" = 1 ]; then
        po_say "  would verify SHA256SUMS against $pinned and run $engine install --global --yes --providers=$providers"
        po_change
        return 0
    fi
    po_owner_begin "pack:$pack:$set:all"
    if [ -z "$(po_bundle_for "$pack")" ]; then
        po_ensure_dir "$src"
        for name in SHA256SUMS "$bundle" "$engine"; do
            if [ ! -f "$src/$name" ]; then po_fetch "$base/$name" "$src/$name"; fi
            po_rec x "$src/$name" "$(po_hash "$src/$name")"
        done
    fi
    [ "$(po_hash "$src/SHA256SUMS")" = "$pinned" ] || po_die "$src/SHA256SUMS does not match the digest pinned in $lock; refusing to install"
    for name in "$bundle" "$engine"; do
        local want
        want="$(awk -v n="$name" '{ f=$2; sub(/^\*/, "", f); if (f==n) print tolower($1) }' "$src/SHA256SUMS" | head -n 1)"
        [ -n "$want" ] || po_die "SHA256SUMS lists no $name"
        [ "$(po_hash "$src/$name")" = "$want" ] || po_die "$src/$name fails its checksum; refusing to install"
    done
    PO_TRACK=()
    roots="$(po_release_get "$pack" roots)"
    while IFS= read -r root; do [ -n "$root" ] && PO_TRACK+=("$(po_expand "$root")/$skill"); done <<PO_ROOTS
$roots
PO_ROOTS
    hooks="$(po_release_get "$pack" hook_files)"
    while IFS= read -r root; do [ -n "$root" ] && PO_TRACK+=("$(po_expand "$root")"); done <<PO_HOOKS
$hooks
PO_HOOKS
    po_track_begin
    chmod +x "$src/$engine" 2>/dev/null || true
    set -- "$src/$engine" install --global --yes "--providers=$providers"
    [ "$PO_RELEASE_NO_HOOKS" = 1 ] && set -- "$@" --no-hooks
    env_name="$(po_release_get "$pack" bundle_env)"
    po_say "  \$ $*"
    env "$env_name=$src/$bundle" "$@" || po_die "the $pack installer exited with an error"
    bin="$skill"
    [ "$os" = windows ] && bin="$skill.exe"
    while IFS= read -r root; do
        [ -n "$root" ] || continue
        dir="$(po_expand "$root")/$skill"
        if [ -f "$dir/SKILL.md" ]; then
            if ! cmp -s "$src/$engine" "$dir/scripts/bin/$os-$arch/$bin" 2>/dev/null; then
                po_ensure_dir "$dir/scripts/bin/$os-$arch"
                cp "$src/$engine" "$dir/scripts/bin/$os-$arch/$bin"
                chmod +x "$dir/scripts/bin/$os-$arch/$bin" 2>/dev/null || true
            fi
            po_say "  engine -> $dir/scripts/bin/$os-$arch/$bin"
        fi
    done <<PO_ROOTS
$roots
PO_ROOTS
    codex_dir="$(po_expand '{HOME}')/.agents/skills/$skill"
    if po_has_word "$(printf '%s' "$providers" | tr ',' ' ')" codex && [ "$PO_RELEASE_NO_HOOKS" != 1 ] && [ -f "$codex_dir/SKILL.md" ]; then
        launcher="$codex_dir/scripts/$skill"
        [ "$os" = windows ] && launcher="$codex_dir/scripts/$skill.cmd"
        if po_json_add_hooks "$(po_expand '{CODEX_HOME}')/hooks.json" "\"$launcher\" hook" "$(po_release_get "$pack" codex_hooks)" "$launcher"; then
            po_say "  codex hooks added to $(po_expand '{CODEX_HOME}')/hooks.json"
        fi
    fi
    po_track_end
    while IFS= read -r root; do
        [ -n "$root" ] && po_rec u "$(po_expand "$root")" - "json-strip:$skill/scripts/$skill"
    done <<PO_HOOKS
$hooks
PO_HOOKS
    po_owner_end
    po_say "==> $pack $version installed; it runs offline."
}

po_bundle_for() {
    local b
    while IFS= read -r b; do case "$b" in "$1="*) printf '%s' "${b#*=}"; return 0 ;; esac; done <<PO_BUNDLE_LIST
$PO_BUNDLES
PO_BUNDLE_LIST
    return 0
}

# ------------------------------------------------------------------ reports

po_core_where() {  # destinations of the core steps of the selected tools
    local t op a b c d
    for t in $1; do
        while IFS="$PO_TAB" read -r op a b c d; do
            case "$op" in
                tree|file|doc) printf '    %s: %s\n' "$t" "$(po_expand "$b")" ;;
                block) printf '    %s: %s (marker block)\n' "$t" "$(po_expand "$a")" ;;
                plugin) printf '    %s: %s\n' "$t" "$(po_expand "$c")" ;;
                attribution) printf '    %s: AI attribution off (settings.json, global git hooks)\n' "$t" ;;
            esac
        done <<PO_STEPS
$(po_tool_steps "$t")
PO_STEPS
    done
}

po_skill_dirs_for() {
    local t d out=""
    for t in $1; do
        while IFS= read -r d; do
            [ -n "$d" ] || continue
            d="$(po_expand "$d")"
            case "$PO_NL$out$PO_NL" in *"$PO_NL$d$PO_NL"*) ;; *) out="$out$d$PO_NL" ;; esac
        done <<PO_DIRS
$(po_tool_skills "$t")
PO_DIRS
    done
    printf '%s' "$out"
}

po_packs_list() {
    local pack set mark n=0
    for pack in $PO_PACKS; do
        po_say "$pack: $(po_pack_get "$pack" label) [$(po_pack_get "$pack" kind), $(po_pack_get "$pack" license)]"
        po_say "  $(po_pack_get "$pack" description)"
        for set in $(po_pack_get "$pack" sets); do
            n=$((n + 1))
            mark=" "
            if po_owner_prefix "pack:$pack:$set:"; then mark=x; fi
            printf '  [%s] %s:%s (%s skills) %s%s\n' "$mark" "$pack" "$set" "$(po_set_get "$pack" "$set" count)" \
                "$(po_set_get "$pack" "$set" description)" "$(po_needs_note "$pack" "$set")"
        done
    done
}

po_needs_note() {  # " Needs set X." for a set that requires another
    local r
    r="$(po_set_get "$1" "$2" requires)"
    [ -n "$r" ] && printf ' Needs set %s.' "$r"
    return 0
}

po_status() {
    local owner
    po_say "source: $PO_ROOT"
    po_say "data home: $PO_DATA"
    if [ ! -f "$PO_MANIFEST" ]; then po_say "nothing installed (no manifest at $PO_MANIFEST)"; return 0; fi
    po_say "manifest: $PO_MANIFEST"
    for owner in $(po_owners); do
        printf '  %-48s %s files\n' "$owner" "$(po_man_owner "$owner" | awk -F'\t' '$2 ~ /^[fdxbmn]$/' | wc -l | tr -d ' ')"
    done
    po_say "created folders: $(po_man_owner @dirs | wc -l | tr -d ' ')"
}

# ------------------------------------------------------------------ text menu

po_read() {  # read one line of menu input; end of input cancels
    if ! IFS= read -r PO_ANSWER; then po_say ""; po_say "cancelled (end of input)"; exit 1; fi
    PO_ANSWER="$(printf '%s' "$PO_ANSWER" | tr -d '\r' | tr '[:upper:]' '[:lower:]')"
}

po_toggle_tool() {
    local t="$1" out="" w
    if po_has_word "$PO_SEL_TOOLS" "$t"; then
        for w in $PO_SEL_TOOLS; do [ "$w" = "$t" ] || out="${out:+$out }$w"; done
        PO_SEL_TOOLS="$out"
    else
        PO_SEL_TOOLS="${PO_SEL_TOOLS:+$PO_SEL_TOOLS }$t"
    fi
}

po_tui() {
    local screen=1 i t pack set n
    while :; do
        po_say ""
        case "$screen" in
            1)
                po_say "prompt-orchestrator installer. Step 1 of 5: tools"
                i=0
                for t in $PO_TOOLS; do
                    i=$((i + 1))
                    printf '  %2d. [%s] %s\n' "$i" "$(po_has_word "$PO_SEL_TOOLS" "$t" && echo x || echo ' ')" "$(po_tool_label "$t")"
                done
                po_say "Next step installs the core for the checked tools into:"
                po_core_where "$PO_SEL_TOOLS"
                po_say "Keys: number toggles a tool, a all, n none, Enter next, q quit"
                po_read
                case "$PO_ANSWER" in
                    "") screen=2 ;;
                    q) po_say "cancelled"; exit 1 ;;
                    a) PO_SEL_TOOLS="$PO_TOOLS" ;;
                    n) PO_SEL_TOOLS="" ;;
                    *[!0-9]*) po_say "unknown choice" ;;
                    *) i=0; for t in $PO_TOOLS; do i=$((i + 1)); [ "$i" = "$PO_ANSWER" ] && po_toggle_tool "$t"; done ;;
                esac
                ;;
            2)
                po_say "Step 2 of 5: core skills and workflows"
                po_say "  [c] core: $([ "$PO_DO_CORE" = 1 ] && echo yes || echo no)"
                po_say "Next step installs the core skills and workflows into:"
                po_core_where "$PO_SEL_TOOLS"
                po_say "Keys: c toggles the core, Enter next, b back, q quit"
                po_read
                case "$PO_ANSWER" in
                    "") screen=3 ;; b) screen=1 ;; q) po_say "cancelled"; exit 1 ;;
                    c) PO_DO_CORE=$((1 - PO_DO_CORE)) ;;
                    *) po_say "unknown choice" ;;
                esac
                ;;
            3)
                po_say "Step 3 of 5: harness (tiered agents, plan profiles, hooks)"
                if po_python_harness >/dev/null; then
                    po_say "  [h] harness: $([ "$PO_DO_HARNESS" = 1 ] && echo yes || echo no)"
                else
                    po_say "  [h] harness: $([ "$PO_DO_HARNESS" = 1 ] && echo yes || echo no) (needs Python $PO_HARNESS_PY_MAJOR.$PO_HARNESS_PY_MINOR; skipped on this machine)"
                fi
                po_say "  [pc] Claude plan profile: ${PO_PROFILE_CLAUDE:-not set}"
                po_say "  [px] Codex plan profile: ${PO_PROFILE_CODEX:-not set}"
                i=0
                for t in $PO_HARNESS_OPTIONS; do
                    i=$((i + 1))
                    printf '  g%s. [%s] %s\n' "$i" "$(po_has_word "$PO_HARNESS_OFF" "$t" && echo ' ' || echo x)" "$(po_harness_option_label "$t")"
                done
                po_say "Next step runs $PO_HARNESS_SCRIPT for each checked tool. It writes agents, overlays and hooks into each tool's folder and keeps its own manifest."
                po_say "Keys: h toggles, pc or px cycles a profile, g<number> toggles an option, Enter next, b back, q quit"
                po_read
                case "$PO_ANSWER" in
                    "") screen=4 ;; b) screen=2 ;; q) po_say "cancelled"; exit 1 ;;
                    h) PO_DO_HARNESS=$((1 - PO_DO_HARNESS)) ;;
                    pc) PO_PROFILE_CLAUDE="$(po_cycle "$PO_PROFILE_CLAUDE" "$(po_harness_profiles claude)")" ;;
                    px) PO_PROFILE_CODEX="$(po_cycle "$PO_PROFILE_CODEX" "$(po_harness_profiles codex)")" ;;
                    g[0-9]*)
                        i=0
                        for t in $PO_HARNESS_OPTIONS; do
                            i=$((i + 1))
                            if [ "g$i" = "$PO_ANSWER" ]; then
                                if po_has_word "$PO_HARNESS_OFF" "$t"; then
                                    PO_HARNESS_OFF="$(printf '%s\n' "$PO_HARNESS_OFF" | awk -v t="$t" '{ for (i=1; i<=NF; i++) if ($i!=t) printf "%s ", $i }')"
                                else
                                    PO_HARNESS_OFF="$PO_HARNESS_OFF $t"
                                fi
                            fi
                        done
                        ;;
                    *) po_say "unknown choice" ;;
                esac
                ;;
            4)
                po_say "Step 4 of 5: packs (opt-in skill sets)"
                n=0
                i=0
                for pack in $PO_PACKS; do
                    i=$((i + 1))
                    po_say "  p$i. $(po_pack_get "$pack" label) ($pack): $(po_pack_get "$pack" description)"
                    for set in $(po_pack_get "$pack" sets); do
                        n=$((n + 1))
                        printf '    %3d. [%s] %s, %s skills: %s%s\n' "$n" "$(po_has_word "$PO_SEL_SETS" "$pack:$set" && echo x || echo ' ')" \
                            "$(po_set_get "$pack" "$set" label)" "$(po_set_get "$pack" "$set" count)" "$(po_set_get "$pack" "$set" description)" \
                            "$(po_needs_note "$pack" "$set")"
                    done
                done
                po_say "Next step installs $(po_sel_count) skills from the checked sets into:"
                po_skill_dirs_for "$(po_pack_tools)" | sed 's/^/    /'
                po_say "A set that needs another set selects both. Keys: number toggles a set, p<number> toggles a whole pack, Enter next, b back, q quit"
                po_read
                case "$PO_ANSWER" in
                    "") screen=5 ;; b) screen=3 ;; q) po_say "cancelled"; exit 1 ;;
                    p[0-9]*)
                        i=0
                        for pack in $PO_PACKS; do
                            i=$((i + 1))
                            [ "p$i" = "$PO_ANSWER" ] || continue
                            if po_has_word "$PO_SEL_SETS" "$pack:$(po_pack_get "$pack" sets | awk '{print $1}')"; then
                                for set in $(po_pack_get "$pack" sets); do po_sel_del "$pack:$set"; done
                            else
                                for set in $(po_base_sets "$pack"); do po_sel_add "$pack:$set"; done
                            fi
                        done
                        ;;
                    *[!0-9]*) po_say "unknown choice" ;;
                    *)
                        n=0
                        for pack in $PO_PACKS; do
                            for set in $(po_pack_get "$pack" sets); do
                                n=$((n + 1))
                                [ "$n" = "$PO_ANSWER" ] || continue
                                po_sel_toggle "$pack:$set"
                            done
                        done
                        ;;
                esac
                ;;
            5)
                po_say "Step 5 of 5: review"
                po_say "  tools: ${PO_SEL_TOOLS:-none}"
                po_say "  core: $([ "$PO_DO_CORE" = 1 ] && echo yes || echo no)"
                po_say "  harness: $([ "$PO_DO_HARNESS" = 1 ] && echo yes || echo no)"
                po_say "  packs: ${PO_SEL_SETS:-none}"
                po_say "Next step installs the items above. The manifest goes to $PO_MANIFEST."
                po_say "Keys: Enter installs, b back, q quit"
                po_read
                case "$PO_ANSWER" in
                    "") return 0 ;; b) screen=4 ;; q) po_say "cancelled"; exit 1 ;;
                    *) po_say "unknown choice" ;;
                esac
                ;;
        esac
    done
}

po_cycle() {  # next value after $1 in the list $2, with "" first
    local cur="$1" first="" prev="" v
    if [ -z "$cur" ]; then printf '%s\n' "$2" | awk '{ printf "%s", $1 }'; return 0; fi
    for v in $2; do
        [ -z "$first" ] && first="$v"
        if [ "$prev" = "$cur" ]; then printf '%s' "$v"; return 0; fi
        prev="$v"
    done
    printf ''
}

po_sel_count() {
    local w total=0
    for w in $PO_SEL_SETS; do total=$((total + $(po_set_get "${w%%:*}" "${w#*:}" count))); done
    printf '%s' "$total"
}

# ------------------------------------------------------------------ commands

po_usage() {
    cat <<PO_USAGE
prompt-orchestrator installer (generated from install/spec.json)

Usage:
  install.sh                                  menu in a terminal, defaults otherwise
  install.sh [install] [options]              install the core, the harness and packs
  install.sh tui                              menu, also with scripted input
  install.sh status                           what the manifest records
  install.sh packs list                       packs and sets with skill counts
  install.sh packs install SPEC...            install packs or sets (no core, no harness)
  install.sh packs remove SPEC...             remove packs or sets
  install.sh uninstall [--tools LIST] [--project DIR]
  install.sh project [DIR]                    every tool inside one project folder
  install.sh windsurf [DIR]                   Windsurf workflows and rules inside one project

Options:
  --tools LIST            comma-separated tool ids: $(printf '%s' "$PO_TOOLS" | tr ' ' ',')
  --core | --no-core      install the core skills and workflows (default: yes)
  --core-only             core without the harness
  --harness | --no-harness  run the harness installer (default: yes, needs Python 3.11)
  --harness-only          harness without the core
  --profile NAME          plan profile for Claude and Codex tools where it applies
  --profile-claude NAME   $(po_harness_profiles claude | tr ' ' ',')
  --profile-codex NAME    $(po_harness_profiles codex | tr ' ' ',')
  --no-OPTION             turn off a harness option: $(printf '%s' "$PO_HARNESS_OPTIONS" | tr ' ' ',')
  --packs SPEC            pack[:set][,set...] and more packs, for example
                          --packs claude-red-offense:web,recon,logo-design
                          A bare pack name skips sets that need another set
                          (rea-frida); name those: --packs rea:rea,rea-frida
  --sets SPEC             same as --packs
  --bundle PACK=DIR       read a release pack or a pinned binding from a local folder
  --procable-bundle DIR   same as --bundle procable=DIR
  --no-release-hooks      install release packs without their hooks
  --dry-run               print the plan and change nothing
  --yes, -y               no menu
PO_USAGE
}

po_main() {
    PO_CMD=""
    PO_SUB=""
    PO_ARGS=""
    PO_POS1=""
    PO_DRY=0
    PO_YES=0
    PO_DO_CORE=1
    PO_DO_HARNESS=$PO_HARNESS_DEFAULT
    PO_TOOLS_GIVEN=""
    PO_SEL_TOOLS="$PO_DEFAULT_TOOLS"
    PO_SEL_SETS=""
    PO_PROFILE_CLAUDE=""
    PO_PROFILE_CODEX=""
    PO_HARNESS_OFF=""
    PO_BUNDLES=""
    PO_RELEASE_NO_HOOKS=0
    PO_PROJECT_DIR=""
    PO_FAILED=""
    PO_OWNER_REMOVING=""
    local packs_spec="" arg opt t
    while [ $# -gt 0 ]; do
        arg="$1"
        case "$arg" in
            --tools) shift; [ $# -gt 0 ] || po_die "--tools needs a value"
                PO_TOOLS_GIVEN=1; PO_SEL_TOOLS="$(printf '%s' "$1" | tr ',' ' ')"
                for t in $PO_SEL_TOOLS; do po_has_word "$PO_TOOLS" "$t" || po_die "unknown tool: $t"; done ;;
            --core) PO_DO_CORE=1 ;;
            --no-core) PO_DO_CORE=0 ;;
            --core-only) PO_DO_CORE=1; PO_DO_HARNESS=0 ;;
            --harness|--with-harness) PO_DO_HARNESS=1 ;;
            --no-harness) PO_DO_HARNESS=0 ;;
            --harness-only) PO_DO_CORE=0; PO_DO_HARNESS=1 ;;
            --profile) shift; [ $# -gt 0 ] || po_die "--profile needs a value"
                po_has_word "$(po_harness_profiles claude)" "$1" && PO_PROFILE_CLAUDE="$1"
                po_has_word "$(po_harness_profiles codex)" "$1" && PO_PROFILE_CODEX="$1"
                [ -n "$PO_PROFILE_CLAUDE$PO_PROFILE_CODEX" ] || po_die "unknown profile: $1" ;;
            --profile-claude) shift; po_has_word "$(po_harness_profiles claude)" "${1:-}" || po_die "unknown Claude profile: ${1:-}"; PO_PROFILE_CLAUDE="$1" ;;
            --profile-codex) shift; po_has_word "$(po_harness_profiles codex)" "${1:-}" || po_die "unknown Codex profile: ${1:-}"; PO_PROFILE_CODEX="$1" ;;
            --packs|--sets) shift; [ $# -gt 0 ] || po_die "$arg needs a value"; packs_spec="$packs_spec${packs_spec:+,}$1" ;;
            --bundle) shift; case "${1:-}" in *=*) PO_BUNDLES="$PO_BUNDLES$PO_NL$1" ;; *) po_die "--bundle needs PACK=DIR" ;; esac ;;
            --procable-bundle) shift; [ $# -gt 0 ] || po_die "--procable-bundle needs a folder"; PO_BUNDLES="$PO_BUNDLES${PO_NL}procable=$1" ;;
            --no-release-hooks|--no-procable-hooks) PO_RELEASE_NO_HOOKS=1 ;;
            --project) shift; PO_PROJECT_DIR="${1:-}" ;;
            --dry-run) PO_DRY=1 ;;
            --yes|-y) PO_YES=1 ;;
            -h|--help|help) po_usage; return 0 ;;
            --no-*)
                opt="${arg#--no-}"
                po_has_word "$PO_HARNESS_OPTIONS" "$opt" || po_die "unknown option: $arg"
                PO_HARNESS_OFF="$PO_HARNESS_OFF $opt" ;;
            -*) po_die "unknown option: $arg (see --help)" ;;
            *)
                if [ -z "$PO_CMD" ]; then PO_CMD="$arg"
                elif [ "$PO_CMD" = packs ] && [ -z "$PO_SUB" ]; then PO_SUB="$arg"
                else PO_ARGS="$PO_ARGS $arg"; [ -n "$PO_POS1" ] || PO_POS1="$arg"; fi ;;
        esac
        shift
    done
    po_setup
    case "${PO_CMD:-install}" in
        install|tui)
            [ -n "$packs_spec" ] && po_add_sets "$packs_spec"
            if [ "${PO_CMD:-}" = tui ] || { [ "$PO_YES" = 0 ] && [ "$PO_DRY" = 0 ] && [ -t 0 ]; }; then po_tui; fi
            po_install_all
            ;;
        status) po_status ;;
        packs)
            case "$PO_SUB" in
                list|"") po_packs_list ;;
                install|add)
                    for arg in $PO_ARGS; do po_add_sets "$arg"; done
                    [ -n "$PO_SEL_SETS" ] || po_die "name a pack or set, see: install.sh packs list"
                    PO_DO_CORE=0; PO_DO_HARNESS=0
                    po_install_all ;;
                remove|rm|uninstall)
                    [ -n "$PO_ARGS" ] || po_die "name a pack or set to remove"
                    for arg in $PO_ARGS; do po_remove_pack_spec "$arg"; done
                    po_report ;;
                *) po_die "unknown packs command: $PO_SUB" ;;
            esac
            ;;
        uninstall|remove) po_uninstall ;;
        project|windsurf)
            po_install_project "$PO_CMD" "${PO_POS1:-$(pwd)}"
            po_report ;;
        *) po_die "unknown command: $PO_CMD (see --help)" ;;
    esac
}

po_install_all() {
    local t w tools
    po_check_requires
    [ "$PO_DRY" = 1 ] && po_say "dry run: nothing is written"
    if [ "$PO_DO_CORE" = 1 ]; then
        for t in $PO_SEL_TOOLS; do po_install_core "$t"; done
    fi
    if [ "$PO_DO_HARNESS" = 1 ]; then
        for t in $PO_SEL_TOOLS; do po_harness_install "$t"; done
    fi
    if [ -n "$PO_SEL_SETS" ]; then
        tools="$(po_pack_tools)"
        for w in $(po_sets_ordered); do po_install_set "${w%%:*}" "${w#*:}" "$tools"; done
    fi
    po_report
    if [ "$PO_DO_HARNESS" = 1 ] && po_has_word "$PO_SEL_TOOLS" claude && [ -z "$PO_PROFILE_CLAUDE" ] && po_python_harness >/dev/null; then
        po_say "    Claude plan profile not set: run /autosetup in a Claude Code session."
    fi
}

po_report() {
    if [ -n "$PO_FAILED" ]; then po_say "==> finished with failures:$PO_FAILED"; exit 1; fi
    if [ "$PO_CHANGES" = 0 ]; then po_say "==> no change: everything is already in place"
    elif [ "$PO_DRY" = 1 ]; then po_say "==> dry run: $PO_CHANGES changes planned"
    else po_say "==> done: $PO_CHANGES changes"; fi
}

po_uninstall() {
    local owner t order
    po_owners > "$PO_TMP/owners.all"
    if [ -n "$PO_PROJECT_DIR" ]; then
        [ -d "$PO_PROJECT_DIR" ] && PO_PROJECT_DIR="$(cd "$PO_PROJECT_DIR" && pwd)"
        while IFS= read -r owner <&3; do
            case "$owner" in "project:$PO_PROJECT_DIR"|"windsurf:$PO_PROJECT_DIR") po_remove_owner "$owner" ;; esac
        done 3< "$PO_TMP/owners.all"
    elif [ -n "$PO_TOOLS_GIVEN" ]; then
        for t in $PO_SEL_TOOLS; do
            while IFS= read -r owner <&3; do
                case "$owner" in "harness:$t"|"core:$t"|pack:*:"$t") po_remove_owner "$owner" ;; esac
            done 3< "$PO_TMP/owners.all"
        done
    else
        for order in harness pack core other; do
            while IFS= read -r owner <&3; do
                case "$order:$owner" in
                    harness:harness:*|pack:pack:*|core:core:*) po_remove_owner "$owner" ;;
                    other:*) po_remove_owner "$owner" ;;
                esac
            done 3< "$PO_TMP/owners.all"
        done
    fi
    po_report
}
