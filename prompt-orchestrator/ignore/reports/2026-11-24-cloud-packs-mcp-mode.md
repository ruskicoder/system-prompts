# Report: opt-in packs through the po-skills MCP server (branch cloud/packs-mcp-mode)

## Result

Branch `cloud/packs-mcp-mode` starts from master `90b8ad6`. Commit `203b7df` holds the feature. This
report is the second commit.

- Server: `install/po_skills_server.mjs`, a dependency-free Node.js stdio server. The rea pack and
  `pack_helper.mjs` already need Node.js, so Node.js avoids a second runtime. The installer copies the
  server to `<data_home>/skills-mcp/server.mjs`. The server answers MCP 2026-07-28 (`server/discover`,
  protocol version in each request's `_meta`, `resultType`, `ttlMs`, error -32022 for an unsupported
  version). For older clients, `initialize` negotiates 2025-11-25, 2025-06-18, 2025-03-26 or 2024-11-05.
  The server offers `search_skills`, `load_skill` and `list_packs`. The instructions hold 259
  characters. Each tool description stays under 200 characters and starts with its search words.
- Index: `pack_helper.mjs skills-index` builds `<data_home>/skills-mcp/index.json` from the manifest
  and the `SKILL.md` front matter. The server rereads the index only when the file changes and scans no
  folder per call.
- Installer: packs install in mode mcp by default. `--mode skills` keeps the copy into each tool's
  skills folder. Without `--mode`, an installed set keeps its mode. `--mode mcp` on a set in mode
  skills removes the copies that the manifest records. `--mode skills` does the reverse. The installer
  registers `po-skills` once per selected tool with an `mcp` entry in the spec. Removal of the last
  mode mcp set removes the server, the index and each entry. The menu shows the mode, and `m` toggles
  the mode. `packs list` marks installed sets `[mcp]` or `[skills]`.
- Coverage: the kind skills packs, the `reverse-skill` entry skill (payload stays in `packages/`) and
  the `rea` skill (the rea server stays registered). Core skills install as before.
- Shared config fix: with rea and `po-skills` in one config, the second entry inherits the first
  entry's claim on the `mcpServers` container and on the file. Both removal orders restore the config
  byte-identical. Before the fix, three rea tests left `"mcpServers": {}` or a `{}` file behind.
- Spec, generator, validator: `install/spec.json` gains `skills_mcp`. The generator checks the block
  and embeds the settings in both installers. The validator rejects a pack server named `po-skills`
  and description forms that the index reader cannot read.
- Docs: `README.md`, `packs/README.md` and `docs/30-units/installers/README.md`.
- Tests: new `tests/installers/test_skills_mcp.py` (19 tests). Existing tests that assumed copies by
  default now pass `--mode skills` or check the mcp layout.

Measured with the full cyber-skills index (818 skills, 750035 bytes), Node.js v22.23.5, 10 runs:

| Measure | Median | Max | Target |
|---|---|---|---|
| Spawn to `initialize` reply | 0.027 s | 0.035 s | under 1 s |
| Spawn to first `search_skills` reply (index loaded) | 0.049 s | 0.069 s | under 1 s |
| Peak RSS (VmHWM) | 55.5 MB | 55.8 MB | under 100 MB |

## Evidence

Acceptance flow with the committed `install/install.sh` in a temporary HOME, with existing configs
for Claude Code, Codex and OpenCode:

```text
$ install.sh packs install claude-red-offense cyber-skills:cyber-malware --tools claude,codex,opencode
==> done: 362 changes
pack skill folders under tool skills dirs: 0
po-skills entries: claude=1 codex=1 opencode=1
index skills: 118 (claude-red-offense 79 + cyber-malware 39 = 118)
$ (re-run)
==> no change: everything is already in place
$ install.sh packs install logo-design --mode skills
==> done: 102 changes
copies: 3
$ install.sh packs install logo-design --mode mcp
==> done: 137 changes
copies left: 0
$ install.sh packs remove claude-red-offense cyber-skills logo-design
==> done: 396 changes
configs byte-identical after removal (sha256 before = after)
data home exists: no
```

`AcceptanceBashTests` and `AcceptancePowerShellTests` assert the same flow, with parsed and raw counts
of `po-skills` per config and the index names against `pack.json`.

JSON-RPC session against the 818-skill index (`ServerTests`): `initialize`, `tools/list`,
`search_skills("ntlm relay")` and `load_skill`. The first result of the search:

```text
1. detecting-ntlm-relay-with-event-correlation (pack cyber-skills, set cyber-hunting-intel): Detect NTLM relay attacks (T1557.001) by correlating Windows Event 4624 LogonType 3 ...
```

`load_skill` returns the SKILL.md text after a `Folder:` line. The test checks that the folder is an
absolute path that exists and holds that SKILL.md.

Index reader against PyYAML over 900 pack skills:

```text
900 skills 0 mismatches
```

CI steps of `.github/workflows/prompt-orchestrator-ci.yml`, run locally (pwsh 7.4.6 and shellcheck
0.10.0 installed in the session scratchpad):

```text
$ python3 -B tools/generate_integrations.py > /dev/null; git status --porcelain -- .
(no output)
$ python3 -B skills/validate_skills.py
Overall Results: 404 passed, 0 failed out of 404 total.
$ python3 -B tools/validate_packs.py
6 packs checked, 0 problems
$ (pwsh parse of packs/**/*.ps1)
Parsed 42 .ps1 files under packs/, 0 blocking parse errors
$ python3 -B tools/generate_installers.py --check
installers are current
$ shellcheck -s bash install/install.sh
(no output, exit 0)
$ python3 -B -m unittest discover -s tests/installers -t tests/installers
Ran 73 tests in 179.252s
OK (skipped=1)
harness/tests: OK
install: OK
skills/academic-writing/scripts: OK
skills/architecture-diagrams/scripts: OK
skills/ci-enforcement/tests: OK (skipped=1)
skills/concision-and-logic/scripts: OK
skills/docs-scaffold/scripts: OK
skills/human/scripts: OK
skills/no-ai-trailer/scripts: OK
skills/skill-creator/scripts: OK
```

The skipped installer test is `ReaNetworkTests`, which needs `PO_TEST_NETWORK=1`. Before the change,
the same installer suite ran 54 tests with the same skip.

Gate checks on `origin/master..HEAD`:

```text
$ check.py prose --repo . --base origin/master --head HEAD
summary: 0 gate finding(s), 95 advisory finding(s)
$ check.py secrets ...
summary: 0 gate finding(s), 0 advisory finding(s)
$ check.py unicode ...
summary: 0 gate finding(s), 0 advisory finding(s)
$ check.py attribution ...
summary: 0 gate finding(s), 0 advisory finding(s)
$ check.py commits ... --allow-file .github/ci-enforcement/identities.txt
summary: 0 gate finding(s), 0 advisory finding(s)
$ check.py models --root prompt-orchestrator ...
summary: 0 gate finding(s), 0 advisory finding(s)
```

## Open issues

1. Commit identity: the session's default identity is `Claude <noreply@anthropic.com>`. The commit
   identity gate allows only `Do Dang Khoa <149188141+ruskicoder@users.noreply.github.com>`, so both
   commits carry that identity, as the earlier branch commits do.
2. No live client test: this session has no Claude Code, Codex or OpenCode client with
   `ENABLE_TOOL_SEARCH=true`. (untested) The context saving at session start rests on the tool search
   behaviour that the task describes.
3. Mode mcp needs Node.js 18 or later. Without `node`, the installer stops before the first write and
   names `--mode skills`. The installer does not fall back on its own.
4. Antigravity and OpenClaw have no MCP config that the installer edits. In mode mcp, these two tools
   get skill copies, and the installer says so.
5. `packs install` without `--tools` and without an installed core uses the default tool list (seven
   tools), as before. The po-skills entry then also lands in the Cursor and Gemini CLI configs.
6. The tool descriptions name fixed task areas (pentest, malware, forensics, cloud, AppSec, reverse
   engineering, logo design). A future pack in another area needs a new description.
7. Prose: 22 of the 95 advisories fall on added lines. Nearly all flag short noun parentheses, which
   Addendum A8 permits. None is a gate finding.
8. The MCP 2026-07-28 pages came from `raw.githubusercontent.com`, because the session network blocks
   `modelcontextprotocol.io`. The server implements no `subscriptions/listen`, because the tool list
   never changes (`listChanged: false`).
9. Unit-test runs rewrite tracked `.pyc` files under `harness/scripts/__pycache__` and
   `skills/*/scripts/__pycache__`. The commit restores them to master.
10. `README.md` still lists no `cyber-skills` or `reverse-skill` row in the packs table, and
    `docs/30-units/installers/README.md` keeps its old `verified` commit. Both gaps predate this change.
