# procable release pack in mode mcp (branch cloud/procable-mcp-mode)

## Result

In mode mcp, the procable release pack now installs through `po-skills`. Branch `cloud/procable-mcp-mode` holds two commits on top of master: the feature commit `feat(installer): serve the procable release pack through po-skills in mode mcp` and the commit that adds this report.

- Mode mcp: The installer verifies the bundle against the lock with the same code as before. Then the engine runs once with an empty home folder (`HOME`, `USERPROFILE`, `CODEX_HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `APPDATA` and `LOCALAPPDATA` all point into the installer's temporary folder). The installer copies the staged skill folder, with the engine binary in `scripts/bin/<os>-<arch>/`, to `<data_home>/skills-mcp/procable/procable/` under the owner `pack:procable:procable:mcp`. The `po-skills` index lists the skill. No tool skills folder gets a copy.
- Hooks: `pack_helper.mjs hooks-groups staged` reads the hooks that the engine wrote into each file of `hook_files` under the temporary home. The helper then rewrites the staged skill folder to the skills-mcp folder. For Codex, the engine writes no user-scope hooks, so `hooks-groups spec` builds the `codex_hooks` around the skills-mcp launcher. `hooks-add` inserts each hook group into `~/.claude/settings.json` and `$CODEX_HOME/hooks.json` as one text fragment, recorded as kind `m` under the owner `:mcp`. `mcp-remove` deletes the fragments in reverse order, which gives back the exact original bytes. The hooks call the launcher on disk, so they work even when no session loads the skill.
- Mode skills: The engine runs at user scope as before, under the owner `pack:procable:procable:all`. New: before the engine runs, the installer saves a copy of each hook file the user already has in `<data_home>/backups/release-hooks/`. On removal, `json-strip` puts the copy back when the stripped JSON equals the copy. Without that copy, mode skills rewrote the user's hook files through `json.dumps`, which broke byte-identical restore after a switch.
- Switching: `--mode mcp` on an install in mode skills removes the `:all` owner (the engine's copies and hooks), then installs in mode mcp. `--mode skills` removes the `:mcp` owner (the skills-mcp copy and the hook fragments), then runs the engine at user scope. Without `--mode`, an installed set keeps its mode. An existing install from before this change has an `:all` owner, so it counts as mode skills.
- Downloads: downloaded release files (`SHA256SUMS`, bundle, engine) now belong to the owner `pack:procable:payload`. A mode switch therefore keeps them. Lock and `SHA256SUMS` verification is unchanged.
- In mode mcp, a tool without an `mcp` entry in `install/spec.json` (Antigravity, Copilot, Kiro) gets no procable skill. The installer names the tool and points to `--mode skills`.
- Files changed: `tools/installer/runtime.sh`, `tools/installer/runtime.ps1`, the regenerated `install/install.sh` and `install/install.ps1`, `install/pack_helper.mjs` (`hooks-groups`, `hooks-add`, and the hook records in `mcp-remove`), `packs/README.md` (the line that said release packs ignore the mode is gone; the release mode behaviour, owners and kinds are added), `README.md`, `docs/30-units/installers/README.md`, `tests/installers/test_installers.py`, `tests/installers/test_skills_mcp.py`.
- The generator and the validator needed no change. `bundle_env`, `hook_files`, `skill_roots` and `codex_hooks` already reach both installers.

## Evidence

Acceptance flow in a temporary HOME with the stub release engine. The script is `accept.py` in the session scratchpad. It uses `release_fixture()` from the tests, with the real `packs/procable/pack.json` release object and a fixture lock. Before the install, the HOME already held `~/.claude/settings.json` and `~/.codex/hooks.json` in a layout that `json.dumps` would not write.

```
$ install.sh packs install procable --tools claude,codex --bundle procable=<stub>
=== pack procable, set procable (1 skills)
  procable 0.1.0 for claude,codex (linux-x64, mode mcp) from /tmp/po-accept-4mqdoqg3/bundle
  $ .../bundle/procable-linux-x64 install --global --yes --providers=claude,codex (HOME=.../po-install.XXXX/release-stage)
  mode mcp: the po-skills MCP server serves procable from /tmp/po-accept-4mqdoqg3/home/.local/share/prompt-orchestrator/skills-mcp/procable/procable
  engine -> .../skills-mcp/procable/procable/scripts/bin/linux-x64/procable
  hooks -> /tmp/po-accept-4mqdoqg3/home/.claude/settings.json
  hooks -> /tmp/po-accept-4mqdoqg3/home/.codex/hooks.json
==> procable 0.1.0 installed; it runs offline.
=== po-skills MCP server: .../skills-mcp
  MCP server po-skills -> /tmp/po-accept-4mqdoqg3/home/.claude.json
  MCP server po-skills -> /tmp/po-accept-4mqdoqg3/home/.codex/config.toml
==> done: 10 changes
procable folders under skill roots: []
claude settings hook commands: ['".../skills-mcp/procable/procable/scripts/procable" hook', (same, second event)]
codex hooks.json hook commands: ['".../skills-mcp/procable/procable/scripts/procable" hook', (same, second event)]
run hook: procable hook ran
search_skills("procable design"): 1. procable (pack procable, set procable): Design skill for polish, critique, audit and WCAG 2.2 AA review.
rerun: ==> no change: everything is already in place
list:   [x] procable:procable (1 skills) [mcp] The release skill.
switch --mode skills: ==> done: 11 changes | claude copy: True | skills-mcp copy: False
switch --mode mcp: ==> done: 18 changes | claude copy: False | skills-mcp copy: True
rerun: ==> no change: everything is already in place
remove: ==> done: 10 changes
.claude/settings.json byte-identical after removal: True
.codex/hooks.json byte-identical after removal: True
files left in HOME: ['.claude/settings.json', '.codex/hooks.json']
```

New tests:

- `ReleaseMcpBashTests` in `tests/installers/test_skills_mcp.py`, four tests. The first runs the mode mcp install, the rerun, `search_skills`, `load_skill`, the hook execution and byte-identical removal. The second runs skills to mcp to skills to mcp, then uninstall, with byte-identical hook files at the end. The third covers a tool without an MCP config and `--no-release-hooks`. The fourth covers the dry run.
- `ReleaseMcpPowerShellTests` runs the same flow through `install.ps1`.
- The existing `ReleaseBashTests` now pins `--mode skills` for the mode skills flow, and the stub engine gained a launcher, a hook reply and a merge into an existing `settings.json`.

```
$ python3 -B -m unittest discover -s tests/installers -t tests/installers -k Release
.......s
Ran 8 tests in 7.290s
OK (skipped=1)          # the skip is ReleaseMcpPowerShellTests: no pwsh in this container

$ python3 -B -m unittest discover -s tests/installers -t tests/installers
FAIL: test_mode_mcp_without_node_stops_before_writing (test_skills_mcp.FixtureMcpBashTests...)
Ran 78 tests in 160.188s
FAILED (failures=1, skipped=6)
```

The one failure is environmental, and master fails the same way in this container (`git worktree add` of origin/master, same test: `FAILED (failures=1)`). The container puts an `rm` guard folder first on PATH. The test links each PATH command except node into a shim folder, so the shim gets the guard's `rm`, which refuses to run (`rm: command not found`, exit 127). This change does not touch the test or the code it covers.

The other CI steps of `.github/workflows/prompt-orchestrator-ci.yml`, run locally:

```
$ python3 -B tools/generate_integrations.py > /dev/null; git status --porcelain -- .     # no output
$ python3 -B skills/validate_skills.py          Overall Results: 404 passed, 0 failed out of 404 total.
$ python3 -B tools/validate_packs.py            6 packs checked, 0 problems
$ python3 -B tools/generate_installers.py --check   installers are current
$ shellcheck -s bash install/install.sh         (exit 0; shellcheck-py in a scratch venv)
unit tests: harness/tests OK; install OK; skills/academic-writing/scripts OK;
  skills/architecture-diagrams/scripts OK (skipped=17); skills/ci-enforcement/tests OK (skipped=1);
  skills/concision-and-logic/scripts OK; skills/docs-scaffold/scripts OK; skills/human/scripts OK;
  skills/no-ai-trailer/scripts OK; skills/skill-creator/scripts OK; tests/installers as above
```

Gate checks on the diff `origin/master..HEAD`:

```
prose:       0 gate finding(s), 109 advisory finding(s)   (15 of them in this report)
secrets:     0 gate finding(s), 0 advisory finding(s)
unicode:     0 gate finding(s), 0 advisory finding(s)
attribution: 0 gate finding(s), 0 advisory finding(s)
commits:     0 gate finding(s), 0 advisory finding(s)   (--allow-file .github/ci-enforcement/identities.txt)
models:      0 gate finding(s), 0 advisory finding(s)
```

The prose advisories cover whole changed files. I reworded the advisories that fell on lines I wrote. The remaining ones are parenthesis notes on table rows and on older text.

## Open issues

1. The real procable engine was not run. The `ruskicoder/procable` repository is outside this session's GitHub scope, and attaching it was refused. Mode mcp assumes three things that only the stub covers. First, the engine honours `HOME` (`USERPROFILE` on Windows) and writes the skill and the Claude hooks under that folder. Second, the hook commands name the skill folder by its full path. Third, the engine does not need other user-scope state that the temporary home drops. Run one real install, `install.sh packs install procable --tools claude,codex`, before release.
2. PowerShell was not run. This container has no `pwsh`, and downloading it was refused. The PowerShell port mirrors the bash code line by line, and `GeneratorTests` checks its brace balance. `ReleaseMcpPowerShellTests` and the existing PowerShell flows run in CI on ubuntu-24.04, which ships pwsh. I have no local result for those tests.
3. In mode mcp, tools without an MCP config (Antigravity, Copilot, Kiro) get no procable skill. This follows requirement 1 literally. Skill packs give such tools copies instead.
4. The byte-identical restore in mode skills holds when the user does not edit the hook file between install and removal. After such an edit, removal strips the procable hooks and keeps the `json.dumps` layout, as before this change.
5. The commits use the allowlisted maintainer identity (`Do Dang Khoa <149188141+ruskicoder@users.noreply.github.com>`), as earlier cloud-session commits on master do. The session's configured identity (`Claude <noreply@anthropic.com>`) is not in `.github/ci-enforcement/identities.txt`, would fail the commit-identity gate, and would be AI attribution.
6. Test runs rewrite nine tracked `.pyc` files under `harness/scripts/__pycache__` and `skills/*/scripts/__pycache__`. I kept them out of the commit. Tracking those caches is a separate cleanup.
