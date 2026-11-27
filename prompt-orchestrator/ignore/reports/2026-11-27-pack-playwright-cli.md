# Report: opt-in pack playwright-cli

Branch: `cloud/pack-playwright-cli`, started from master at `2aa8101`.

## Result

The opt-in pack `packs/playwright-cli` (kind skills) is in place, and every acceptance gate that this cloud box can run passes.

- Source: `microsoft/playwright-cli` at commit `dc5f4d5616ab5a28ded12fd7101a4d49bd59a820`, Apache-2.0, vetted 2026-11-27.
- Set `playwright-cli` holds the skill `skills/playwright-cli` (SKILL.md plus 10 reference files).
- The `npm` object pins `@playwright/cli` 0.1.25 with integrity `sha512-v1qjq3/ssK2lf9z/+Cu0gHGXm2uDgAQwq5fWPCBM1SxkJqcB0FOyvbbsTrpPn4j4WJey8bLTYT4tEB8o4FbwBw==`. The npm registry returns the same integrity for 0.1.25. The node range is `>=20.0.0`, taken from the `engines` field of the package and its two dependencies.
- The dependencies of `@playwright/cli` 0.1.25 are exact alpha pins: `playwright` 1.66.0-alpha-2026-11-18 and `playwright-core` 1.66.0-alpha-2026-11-18.
- Edit 1: SKILL.md no longer runs `npm install -g @playwright/cli@latest`. The skill names the binary in the private prefix for Linux, macOS and Windows, runs the binary with `NO_UPDATE_NOTIFIER=1` and asks the user before an install step.
- Edit 2: `references/pr-attachments.md` has the section "Approval before posting". The agent drafts the text and the attachment, then asks the user before `gh pr create`, `gh pr comment`, `gh pr edit`, `gh issue create` or `gh issue comment`.
- Edit 3: 20 prose em dashes are rewritten. The upstream files hold 23 em dashes. The other 3 sit inside code fences (SKILL.md 2, video-recording.md 1) and stay verbatim under the rule on code fences.
- The front matter gains the third-party fields. `allowed-tools` keeps the upstream grant `Bash(playwright-cli:*) Bash(npx playwright:*) Bash(npx --no-install playwright:*)`.
- `LICENSE` holds the upstream Apache-2.0 text. `NOTICE` lists each change with an Apache-2.0 section 4(b) statement.
- `install/install.sh` and `install/install.ps1` are regenerated. The integrations generator writes no change.

## Evidence

Integrity check against the registry:

```
$ curl -fsS https://registry.npmjs.org/@playwright%2Fcli/0.1.25 | python3 -c '...'
version: 0.1.25
integrity: sha512-v1qjq3/ssK2lf9z/+Cu0gHGXm2uDgAQwq5fWPCBM1SxkJqcB0FOyvbbsTrpPn4j4WJey8bLTYT4tEB8o4FbwBw==
deps: {"playwright": "1.66.0-alpha-2026-11-18", "playwright-core": "1.66.0-alpha-2026-11-18"}
engines (cli, playwright, playwright-core): {'node': '>=20'}
```

Upstream checkout and em dash count:

```
$ git rev-parse HEAD
dc5f4d5616ab5a28ded12fd7101a4d49bd59a820
upstream: prose em dashes 20, fence em dashes 3
pack after edits: prose em dashes remaining 0, fence 3
```

Validators and generators:

```
$ python3 tools/validate_packs.py
pack playwright-cli: 1 sets, 1 skills, kind skills
7 packs checked, 0 problems
$ python3 skills/validate_skills.py
Overall Results: 404 passed, 0 failed out of 404 total.
$ python3 tools/generate_installers.py --check
installers are current
$ python3 tools/generate_integrations.py; git status --porcelain
(no change besides the pack and the two installers)
$ shellcheck -s bash install/install.sh   (ShellCheck 0.11.0 from the shellcheck-py wheel in a scratch venv)
SHELLCHECK OK
```

Unit tests from the CI step:

```
harness/tests: OK
install: OK
tests/installers: Ran 78 tests, FAILED (failures=1, skipped=6)
skills/academic-writing/scripts: OK
skills/architecture-diagrams/scripts: OK
skills/ci-enforcement/tests: OK (skipped=1)
skills/concision-and-logic/scripts: OK
skills/docs-scaffold/scripts: OK
skills/human/scripts: OK
skills/no-ai-trailer/scripts: OK
skills/skill-creator/scripts: OK
```

The one failure is `FixtureMcpBashTests.test_mode_mcp_without_node_stops_before_writing`. The same test fails the same way on an unmodified master worktree:

```
$ (master worktree) python3 -B -m unittest test_skills_mcp.FixtureMcpBashTests.test_mode_mcp_without_node_stops_before_writing
rm: command not found
FAILED (failures=1)
```

Install and removal of the set in a temporary HOME:

```
$ HOME=$T/home bash install/install.sh packs install playwright-cli --tools claude
  $ npm install --prefix .../packages/playwright-cli @playwright/cli@0.1.25 --omit=optional --ignore-scripts --save-exact
added 3 packages in 1s
  @playwright/cli@0.1.25 matches the pinned integrity
==> done: 15 changes
$ NO_UPDATE_NOTIFIER=1 .../node_modules/.bin/playwright-cli --version
0.1.25
package-lock.json: @playwright/cli 0.1.25, playwright 1.66.0-alpha-2026-11-18, playwright-core 1.66.0-alpha-2026-11-18
$ HOME=$T/home bash install/install.sh packs remove playwright-cli
==> done: 15 changes
files left under HOME: none
```

Gate job steps on `origin/master...HEAD`:

```
rules: registry: 21 rules, every gate rule has a checker
prose: 0 gate finding(s), 0 advisory finding(s)
attribution: 0 gate finding(s), 0 advisory finding(s)
secrets: 0 gate finding(s), 0 advisory finding(s)
unicode: 0 gate finding(s), 0 advisory finding(s)
commits: 0 gate finding(s), 0 advisory finding(s)
models: 0 gate finding(s), 0 advisory finding(s)
```

## Open issues

1. In this cloud box, `test_mode_mcp_without_node_stops_before_writing` fails on master and on this branch. The test links the first `rm` on PATH into a shim folder. Here the first `rm` is the session's rm guard wrapper, and the wrapper does not run from the shim. CI on GitHub runners has no such wrapper.
2. The CI step "PowerShell scripts in packs parse" did not run locally because pwsh is not installed. The pack ships no `.ps1` file.
3. The commits on this branch carry the allowlisted owner identity from `.github/ci-enforcement/identities.txt`, so the commits gate passes. The commits carry no AI trailer.
4. The pinned `@playwright/cli` 0.1.25 depends on alpha builds of `playwright` and `playwright-core`. A later pack update can move to a release with stable dependencies.
