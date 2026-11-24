---
id: units.installers.tests
type: test
status: draft
owner: unassigned
summary: "Installer test coverage."
---

# Tests

## Unit
`python3 -B -m unittest discover -s install -p 'test_*.py' -v` covers `validate_package()` for the Antigravity plugin (valid package, bad manifest, missing, changed and extra skills, changed companion files, generator output).

`python3 -B -m unittest discover -s tests/installers -t tests/installers -v` covers the generator (`--check`, headers, PowerShell and cmd text, shellcheck and `bash -n`), the pack validator (repository packs, fixture packs, broken copies), and the pack fixtures in `tests/installers/fixtures/packs/`.

## Integration
The same suite runs the generated bash installer in a temporary HOME: core install and re-run, pack sets and payloads, status, packs list, set and pack removal, uninstall to an empty HOME, dry run, scripted menu input, end of input, backup and restore of a foreign file, a changed file kept on removal, a harness block kept across re-runs, project and Windsurf installs, the Antigravity plugin backup, and a release pack with a stub engine (install, re-run, tampered checksums). The PowerShell flow runs when `pwsh` exists.

## System
`RepositoryInstallerTests` runs the committed `install/install.sh` with the real packs: core for Claude Code, Codex and OpenCode, `claude-red-offense:recon` and `logo-design`, status, pack removal and uninstall.
