# Report: rea MCP pack with a verified Frida set (branch cloud/pack-rea)

## Result

The opt-in pack `packs/rea` exists on branch `cloud/pack-rea`, based on master 313617d. It has two sets:

- `rea` installs `rea-agents@6.10.1` into `<data_home>/packages/rea/` with
  `npm install --prefix <prefix> rea-agents@6.10.1 --omit=optional --ignore-scripts --save-exact`.
  The installer then compares the version and integrity in `package-lock.json` with the pins. It
  registers the MCP server `rea` as `node <prefix>/node_modules/rea-agents/scripts/rea.mjs mcp` with
  `NO_UPDATE_NOTIFIER=1` for Claude Code, Codex, Cursor, Gemini CLI and OpenCode. It also copies the
  vendored skill `reverse-engineer-anything` into each tool's skills folder.
- `rea-frida` requires `rea`. It downloads the Frida binding archive, or reads it from
  `--bundle rea=DIR`, and checks the archive's sha256 against the digest pinned for the platform. Then it
  installs `frida@17.23.2` with `--ignore-scripts`, checks the frida integrity and extracts
  `build/frida_binding.node` into `node_modules/frida/build/`. A digest mismatch or an unpinned platform
  stops the install before npm runs. Nothing runs prebuild-install or make.

The vetting conditions hold:

1. Every place pins `rea-agents@6.10.1`: pack.json, the MCP command and the vendored skill. The
   validator rejects `@latest` and `npx` in an `mcp` object.
2. `NO_UPDATE_NOTIFIER=1` is in the server env of every client entry. npm itself also runs with
   `NO_UPDATE_NOTIFIER=1`.
3. No entry sets auto-approval. The validator allows only `set`, `name`, `command`, `args` and `env` in
   `mcp`. The Gemini entry has no `trust` field, and the Codex entry has no
   `default_tools_approval_mode`.
4. In `references/desktop-build.md` the lines on autonomous decisions, the $4 measuring default and
   licence acceptance on the user's behalf now defer to the user and the harness approval rules.
   `packs/rea/NOTICE` records each edit.
5. Without `rea-frida`, npm runs with `--omit=optional`, so Frida is absent. A bare pack name skips the
   add-on set. If the prefix ever holds frida without its set, the installer stops.

Engine changes, all reusable by other packs:

- Three new pack keys: `npm` (pinned packages in a private prefix, with an optional pinned native
  `binding`), `mcp` (one server per pack) and set `requires`. `packs/README.md` documents all three and
  the new manifest kinds `m` and `n`. The validator checks them.
- `install/spec.json` gives each supported tool an `"mcp": {"format", "file"}` entry.
- `install/pack_helper.mjs` is one Node.js helper that both installers call. It inserts or deletes one
  text fragment in JSON, JSONC or TOML. It keeps comments, key order, indentation and CRLF line endings,
  and it writes atomically. Removal leaves the rest of each file byte-identical. The helper leaves an
  entry that the user changed, or a conflicting entry, in place with a warning.
- Set requirements: the installer refuses `rea:rea-frida` while `rea:rea` is neither selected nor
  installed. In the menu, checking `rea-frida` also checks `rea`, and unchecking `rea` also unchecks
  `rea-frida`. `packs remove rea:rea` removes `rea-frida` first.
- npm runs with a throwaway cache inside the installer's temporary folder, so nothing stays in `~/.npm`.

Commits on the branch: 26a793c (pack and engine), 05da38f (verified base before an add-on set, doc
wording), 973c589 (test portability), and the commit that adds this report.

## Evidence

Tarball and asset checks, run in a scratch folder:

```text
$ npm view rea-agents@6.10.1 dist.integrity
sha512-3AWrfFEXppvC98FWhZR2Tzulnqs5xJQrSKmAub6+QME/I58Pr3h8pHqqwM30z2DvlnIx/8Hsu8woMngfi4SNyg==
$ openssl dgst -sha512 -binary rea-agents-6.10.1.tgz | base64 -w0
3AWrfFEXppvC98FWhZR2Tzulnqs5xJQrSKmAub6+QME/I58Pr3h8pHqqwM30z2DvlnIx/8Hsu8woMngfi4SNyg==
$ npm view frida@17.23.2 dist.integrity
sha512-gRCmmTUFdEILyHRN1b66erRoXafwsfWTqXyoBBqkSCFX0Ue7Jhvs/KhA3JO0XrgITNlPd91QAGsFvWzh0mhVgg==
$ sha256sum frida-v17.23.2-napi-v8-*.tar.gz      (downloaded from github.com/frida/frida/releases/download/17.23.2/)
9fa8f668ce91eb03713e8564de4f8fbde232233ee91d729c16773fde11dbae95  frida-v17.23.2-napi-v8-linux-x64.tar.gz
850fba220a2d9b6aae282ac6dde37f48847e73597b7a06d648737ff9addc3340  frida-v17.23.2-napi-v8-darwin-arm64.tar.gz
e9dbc08d386130610430137f0bb31d90af7b08c0f5710942d4313368ada930ea  frida-v17.23.2-napi-v8-win32-x64.tar.gz
$ tar tzvf frida-v17.23.2-napi-v8-linux-x64.tar.gz
-rwxr-xr-x root/root 112775824 2026-10-09 13:26 build/frida_binding.node
```

The upstream skill at commit 8bb01b51 is `.agents/skills/reverse-engineer-anything/` (read through
raw.githubusercontent.com). Its eight reference files are byte-identical to the tarball copy. Its
SKILL.md differs in two `npx -y rea-agents@latest` lines, which the tarball pins to 6.10.1, and in one
`tool_count` metadata line. The upstream LICENSE at that commit equals the tarball LICENSE.

Real install in a temporary HOME. The five client configs existed before the run. The output shows `~`
for the temporary HOME:

```text
$ install.sh packs install rea --tools claude,codex,cursor,gemini,opencode
added 1 package in 11s
  rea-agents@6.10.1 matches the pinned integrity
  MCP server rea -> ~/.claude.json
  MCP server rea -> ~/.codex/config.toml
  MCP server rea -> ~/.cursor/mcp.json
  MCP server rea -> ~/.gemini/settings.json
  MCP server rea -> ~/.config/opencode/opencode.json
==> done: 42 changes
$ (re-run)
==> no change: everything is already in place
frida absent from the prefix
.claude.json: 1 rea key line(s)
.codex/config.toml: 1 rea key line(s)
.cursor/mcp.json: 1 rea key line(s)
.gemini/settings.json: 1 rea key line(s)
.config/opencode/opencode.json: 1 rea key line(s)
$ install.sh packs install rea:rea-frida --tools claude,codex,cursor,gemini,opencode
  frida-v17.23.2-napi-v8-linux-x64.tar.gz matches the pinned sha256
  $ npm install --prefix ~/.local/share/prompt-orchestrator/packages/rea frida@17.23.2 --ignore-scripts --save-exact
added 41 packages in 3s
  frida@17.23.2 matches the pinned integrity
  binding -> ~/.local/share/prompt-orchestrator/packages/rea/node_modules/frida/build/frida_binding.node
==> done: 1 changes
$ node -e "const f=require(process.argv[1]); console.log('require(frida):', typeof f.getDevice)" <prefix>/node_modules/frida
require(frida): function
$ (re-run both sets)
==> no change: everything is already in place
$ install.sh packs remove rea
==> done: 44 changes
byte-identical: .claude.json
byte-identical: .codex/config.toml
byte-identical: .cursor/mcp.json
byte-identical: .gemini/settings.json
byte-identical: .config/opencode/opencode.json
data home removed
```

The installed server answers an MCP `initialize` call:

```text
$ printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize",...}' | node <prefix>/node_modules/rea-agents/scripts/rea.mjs mcp
{"result":{"protocolVersion":"2025-06-18","capabilities":{...},"serverInfo":{"name":"rea","version":"6.10.1"},...
```

Steps of `.github/workflows/prompt-orchestrator-ci.yml`, run locally on HEAD:

```text
generated drift: 0 files                      (python3 -B tools/generate_integrations.py, then git status)
Overall Results: 389 passed, 0 failed out of 389 total.   (skills/validate_skills.py)
6 packs checked, 0 problems                   (tools/validate_packs.py)
installers are current                        (tools/generate_installers.py --check)
shellcheck: clean                             (shellcheck 0.10.0 -s bash install/install.sh)
harness/tests: Ran 30 tests  OK
install: Ran 7 tests  OK
tests/installers: Ran 54 tests  OK (skipped=3)
skills/academic-writing/scripts: Ran 11 tests  OK
skills/architecture-diagrams/scripts: Ran 17 tests  OK
skills/ci-enforcement/tests: Ran 35 tests  OK (skipped=1)
skills/concision-and-logic/scripts: Ran 9 tests  OK
skills/docs-scaffold/scripts: Ran 15 tests  OK
skills/human/scripts: Ran 5 tests  OK
skills/no-ai-trailer/scripts: Ran 12 tests  OK
skills/skill-creator/scripts: Ran 10 tests  OK
gate prose: summary: 0 gate finding(s), 66 advisory finding(s)
gate secrets: summary: 0 gate finding(s), 0 advisory finding(s)
gate unicode: summary: 0 gate finding(s), 0 advisory finding(s)
gate attribution: summary: 0 gate finding(s), 0 advisory finding(s)
gate commits: summary: 0 gate finding(s), 0 advisory finding(s)
gate models: summary: 0 gate finding(s), 0 advisory finding(s)
gate rules: registry: 21 rules, every gate rule has a checker
```

The three skips in `tests/installers` are the two pwsh flows and the opt-in network test. The network
test passed separately:

```text
$ PO_TEST_NETWORK=1 python3 -B -m unittest discover -s tests/installers -t tests/installers -p test_mcp_packs.py -k ReaNetworkTests
Ran 1 test in 17.833s
OK
```

New tests in `tests/installers/test_mcp_packs.py` (22 tests). `fixtures/bin/npm` is a fake npm without
network access:

- Helper: each of the five formats adds, re-runs as `present` and removes to the original bytes. The
  fixtures include a Gemini file with a comment and a trailing comma, a Codex file without a final
  newline, and an OpenCode file with CRLF endings. Further cases: a new file is created and deleted, an
  existing `opencode.jsonc` is preferred, a conflicting entry stays untouched, an identical entry that
  the user owns stays unmanaged, an entry the user changed is kept, a file that was reformatted after
  install loses only the entry, Codex keys added after the block keep the block, the npm-check exit
  codes are 0, 3 and 4, and the Node range check works.
- Bash flows with the rea pack: each config gains exactly one `rea` entry with the pinned command,
  args and env. A re-run reports `no change` and makes no npm call. The one npm call carries
  `--omit=optional --ignore-scripts` and no frida. `packs remove rea` restores each config
  byte-identical. Further flows: `rea:rea-frida` alone is refused and writes nothing; an integrity
  mismatch refuses and writes no config; a fixture asset with a wrong digest refuses, leaves no binding
  and no frida, and makes no frida npm call.
- A pack copy with a fixture digest: both sets install, re-run without change and remove set by set.
  In the menu, checking `rea-frida` checks `rea` as well.
- Validator: range pins, `npx` and `@latest`, an extra key such as `trust`, bad `requires`, an empty
  set without npm, and a bad digest each fail.
- PowerShell: the same rea flow, for a machine with pwsh. It was skipped here.

## Open issues

1. Only three Frida digests are pinned: linux-x64, darwin-arm64 and win32-x64. They match the leader's
   values and the downloaded assets. This session could not read the other platform digests from the
   GitHub releases API. api.github.com and the github.com release pages for frida/frida answer 403 here
   ("GitHub access to this repository is not enabled for this session"). The auto-mode classifier denied
   the request to attach frida/frida. The installer refuses `rea-frida` on darwin-x64, linux-arm64,
   win32-arm64 and every other unpinned platform. See the question below.
2. pwsh is not installed in this container. The classifier denied installing it, so I did not run
   `install.ps1`. The PowerShell runtime mirrors the bash logic. Its text passes the delimiter check,
   and `ReaPowerShellTests` runs the full flow wherever pwsh exists. shellcheck ran from a wheel that I
   unpacked in the scratch folder, because no system install was allowed.
3. developers.openai.com, cursor.com and opencode.ai do not resolve here. The formats come from primary
   sources that were reachable: Codex `codex-rs/config/src/mcp_types.rs` on main, the published
   `@opencode-ai/sdk` 1.19.6 types, rea 6.10.1's own client registry (`dist/application/SupportedClients.js`,
   which covers Cursor), and the Claude Code and Gemini CLI docs.
4. The engine ignores `CLAUDE_CONFIG_DIR`, `GEMINI_CLI_HOME`, `OPENCODE_CONFIG_DIR` and `OPENCODE_CONFIG`,
   the same way the existing spec does for skills. A running Claude Code session rewrites
   `~/.claude.json` and can race with the installer, so close Claude Code before an install or removal.
5. The MCP command is the bare `node`, as the design asked. A GUI client such as Cursor on macOS with a
   version manager may not find `node` on its PATH.
6. The pack and skill use `vetted: 2026-11-24`. The leader vetted Frida on 2026-11-25, and the validator
   rejects a date after today (2026-11-24 here).
7. A bare pack name now skips sets with `requires`. This extends pack format v1, which other sessions
   share. Only sets with `requires` change behaviour, and only `rea-frida` has it today.
8. The rea bash tests run on a pack copy that accepts any Node.js from 18 on, because the CI runner's
   preinstalled Node.js may be older than rea's range. The real range check has its own unit test.
9. The README layout row for `packs/` still lists three packs. The row predates this branch and also
   omits cyber-skills and reverse-skill. I left it alone to avoid a conflict with parallel sessions.
10. `npm uninstall frida` for `packs remove rea:rea-frida` ran with network here. Its offline behaviour
    is untested.
11. Commits use the repository owner's noreply identity, the identity that the `commits` gate allows.
    The commits carry no AI trailer.

QUESTION FOR THE LEADER: Should the pack pin Frida binding digests for more platforms
(darwin-x64, linux-arm64, win32-arm64)? Recommended answer: yes. A session with GitHub access to
frida/frida reads those digests from the releases API and adds them to `packs/rea/pack.json`. Until then
the installer refuses `rea-frida` on those platforms, which is the safe default. Without an answer, the
pack stays as it is.
