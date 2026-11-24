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
| `sets` | list of `{"id": "<set-id>", "label": "...", "description": "one sentence", "skills": ["<skill-folder>", ...]}` |
| `package` | kind `package` only: `{"payload": "package"}` |
| `release` | kind `release` only: the release object below |

The validator rejects other keys.

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

## Other files

`packs/<pack-id>/LICENSE` holds the upstream license. Add `NOTICE` when upstream ships one.

## Commands

```bash
bash install/install.sh packs list
bash install/install.sh packs install claude-red-offense:web,recon
bash install/install.sh packs remove claude-red-offense
python3 tools/validate_packs.py
```
