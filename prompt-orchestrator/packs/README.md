# Packs (pack format v1)

A pack is an opt-in skill set in `packs/<pack-id>/`. The default install skips `packs/`. The user picks
packs per set with `--packs`, `packs install` or the pack screen of the installer menu.
`python3 tools/validate_packs.py` checks every pack against this format, and CI runs the check.
`python3 tools/generate_installers.py` reads each `pack.json` and writes the pack data into the installers.

## pack.json

`packs/<pack-id>/pack.json` is UTF-8 JSON with these keys.

| Key | Value |
|---|---|
| `schema` | `1` |
| `id` | `<pack-id>`, lowercase `[a-z0-9-]`, equal to the folder name |
| `label` | short name |
| `description` | one sentence |
| `kind` | `"skills"`, `"package"` or `"release"` (optional third kind, see below) |
| `license` | SPDX id |
| `upstream` | `"https://github.com/<owner>/<repo>"`, or `null` for in-house content |
| `upstream_commit` | 40-hex sha, or `null` |
| `vetting` | `{"status": "passed", "vetted": "YYYY-MM-DD"}`, or `null` for in-house content |
| `sets` | list of `{"id": "<set-id>", "label": "...", "description": "one sentence", "skills": ["<skill-folder>", ...]}`, optionally with `"requires"` |
| `package` | kind `package` only: `{"payload": "package"}` |
| `release` | kind `release` only: the release object below |
| `npm` | optional, kinds `skills` and `package`: pinned npm packages in a private prefix (below) |
| `mcp` | optional, kinds `skills` and `package`: one MCP server that the installer registers (below) |

The validator rejects other keys.

## Set requirements

A set may carry `"requires": ["<set-id>", ...]`, the other sets of the same pack that it needs. A
required set may not require another set. Such a set is an add-on:

- A bare pack name (`--packs rea`, `packs install rea`) and `p<number>` in the menu select only the
  sets without `requires`. Name an add-on set to get it: `--packs rea:rea,rea-frida`.
- The installer refuses an add-on set when its required set is neither selected nor installed.
- In the menu, checking an add-on set also checks the sets it requires. Unchecking a set also unchecks
  the add-on sets that require it.
- `packs remove <pack>:<set>` also removes the add-on sets that require that set.

A set lists at least one skill, unless the set installs an npm package. `packs/rea` has the add-on
set `rea-frida` with no skill.

## Skills

`packs/<pack-id>/skills/<skill-name>/` holds one skill in Agent Skills layout (`SKILL.md` plus the
skill's own `scripts/`, `references/`, `assets/` and `LICENSE`). The installer copies the folder as is into
the skills folder of each selected tool.

- The folder name equals the front-matter `name`. The name matches `^[a-z0-9][a-z0-9-]*$`.
- The description holds at most 1024 characters.
- Each skill folder belongs to exactly one set. A set may hold one skill.
- A skill name may not repeat a core skill, a core workflow or a skill of another pack.
- In a third-party pack, `SKILL.md` carries `origin: third-party`, `vetting: passed`, `vetted`, `license`,
  `upstream` (GitHub blob URL of the upstream `SKILL.md` at the commit) and `upstream-commit`.

## Kind package

`packs/<pack-id>/package/` holds the full ported tree. The installer copies the tree to
`<data_home>/packages/<pack-id>/`. On Linux and macOS, `<data_home>` is `$XDG_DATA_HOME/prompt-orchestrator`
or `~/.local/share/prompt-orchestrator`. On Windows, `<data_home>` is `%LOCALAPPDATA%\prompt-orchestrator`.
The entry skill under `skills/` names both payload paths in plain text. The installer does no
placeholder substitution.

## Kind release (optional third kind)

A release pack installs a skill from a release that the upstream project publishes, pinned by digest.
`packs/procable` is the only release pack. The pack ships no `skills/` folder, because the release
bundle holds the skill. The pack holds one set with one skill.

| `release` key | Value |
|---|---|
| `lock` | file name of the lock in the pack folder, with `version`, `repo` and `sha256sums` (64-hex digest of `SHA256SUMS`) |
| `tag` | release tag, with `{version}` |
| `bundle` | file name of the skill bundle in the release |
| `engine` | file name of the engine, with `{os}` and `{arch}`; Windows adds `.exe` |
| `providers` | map from installer tool id to the engine's provider id |
| `codex_hooks` | hooks the installer adds to `$CODEX_HOME/hooks.json` (`event`, `matcher` or `null`, `timeout`, `status`) |
| `skill_roots` | skills folders where the engine installs the skill, with `{HOME}`, `{OPENCODE}` or `{CODEX_HOME}` |
| `hook_files` | settings files where the engine or the installer writes hooks |

The installer downloads `SHA256SUMS`, the bundle and the engine for the platform into
`<data_home>/packages/<pack-id>/<version>/`, or reads them from `--bundle <pack-id>=DIR`. Before the
engine runs, the installer checks the digest of `SHA256SUMS` against the lock and each file against
`SHA256SUMS`. A mismatch stops the install.

## npm packages (`npm`)

The `npm` object installs pinned npm packages into one private prefix per pack,
`<data_home>/packages/<pack-id>/`. Every MCP client then starts the server from that prefix, so no
client runs `npx` and no install follows `@latest`.

| Key | Value |
|---|---|
| `node` | Node.js versions the packages support: `X.Y.Z`, `^X.Y.Z` or `>=X.Y.Z`, joined by ` \|\| ` |
| `packages` | list of `{"set", "name", "version", "integrity"}`, each optionally with `"binding"` |

- `set` names the set that installs the package. A set installs at most one package. The first package
  creates the prefix, so its set requires nothing. Every other package belongs to an add-on set that
  requires the first package's set.
- `version` is an exact `X.Y.Z` pin. `integrity` is the npm `dist.integrity` string (`sha512-...`).
- The installer runs `npm install --prefix <prefix> <name>@<version> --omit=optional --ignore-scripts
  --save-exact` with a throwaway npm cache and `NO_UPDATE_NOTIFIER=1`. Then it compares the version and
  the integrity that `package-lock.json` records with the pins. On a mismatch the installer removes what
  it installed and stops.
- `--omit=optional` keeps optional dependencies out. A package that an optional dependency would bring
  arrives only through its own add-on set, and the installer stops if it finds that package without
  its set.
- `binding` replaces an install script that downloads a native file without a checksum. Its `url` is an
  `https://github.com/` `.tar.gz` URL with `{version}` and `{platform}`. Its `member` names the file
  inside the archive. Its `sha256` maps each `<process.platform>-<process.arch>` key, for example
  `linux-x64`, to a 64-hex digest. The installer downloads the archive, or reads it from `--bundle <pack-id>=DIR`,
  checks the digest, installs the npm package with `--ignore-scripts` and extracts `member` into the
  package folder. A platform without a pinned digest and a digest mismatch both stop the install before
  npm runs.
- The packs need `node` and `npm` on PATH. The rest of the installer still needs neither.

## MCP server (`mcp`)

| Key | Value |
|---|---|
| `set` | the set that registers the server |
| `name` | server name in each client config, `[a-z0-9-]` |
| `command` | the program, for example `node` |
| `args` | list of strings; `{PACKAGE}` stands for the pack's npm prefix |
| `env` | map of environment variables for the server |

The validator rejects other keys, so a pack cannot set an auto-approval or trust field. It also rejects
`npx` and `@latest`. The `"mcp"` key of a tool in `install/spec.json` names the config file and format
of each client that the engine can edit safely. Each entry looks like this:

| Tool | File | Entry |
|---|---|---|
| Claude Code (user scope) | `~/.claude.json` | `mcpServers.<name>`: `type` `stdio`, `command`, `args`, `env` |
| Codex | `$CODEX_HOME/config.toml` | `[mcp_servers.<name>]`: `command`, `args`, `env` |
| Cursor | `~/.cursor/mcp.json` | `mcpServers.<name>`: `command`, `args`, `env` |
| Gemini CLI | `~/.gemini/settings.json` | `mcpServers.<name>`: `command`, `args`, `env` (no `trust`) |
| OpenCode | `~/.config/opencode/opencode.json`, or `opencode.jsonc` when only that file exists | `mcp.<name>`: `type` `local`, `command` list, `environment`, `enabled` |

`install/pack_helper.mjs` makes every config edit, for `install.sh` and `install.ps1` alike. It
inserts the one entry as a text fragment and keeps comments, key order, indentation and line endings.
The manifest records the fragment. Removal deletes only that fragment, so the rest of the file stays
byte-identical. An entry that the user changed after install stays in place with a warning. An existing
entry with the same name and other content also stays: the installer reports it and adds nothing.

## Manifest kinds for npm and MCP

| Kind | Path | Removal |
|---|---|---|
| `n` | the npm prefix, owner `pack:<pack-id>:npm` | the folder goes once no set of the pack is left |
| `m` | a client config file, owner `pack:<pack-id>:<set>:<tool>` | the helper removes the recorded entry |
| `x` | an extracted binding | removed when its digest still matches |
| `u` with `npm-rm:<name>` | the npm prefix | `npm uninstall <name>` in the prefix |

## Other files

`packs/<pack-id>/LICENSE` holds the upstream license. Add `NOTICE` when upstream ships one.

## Commands

```bash
bash install/install.sh packs list
bash install/install.sh packs install claude-red-offense:web,recon
bash install/install.sh packs remove claude-red-offense
bash install/install.sh packs install rea --tools claude,codex,cursor,gemini,opencode
bash install/install.sh packs install rea:rea,rea-frida
python3 tools/validate_packs.py
```
