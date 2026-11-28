# Review: pack branches playwright-cli and artex-defense

Reviewer: fresh-context cloud session, 2026-11-28. Base `origin/master` at `2aa81014`.

| Branch | Head | Commits on top of master |
|---|---|---|
| `cloud/pack-playwright-cli` | `c17271ab` | `befb2282`, `c17271ab` |
| `cloud/pack-artex-defense` | `a6dcd1ba` | `4eaffe00`, `31e29d36`, `a6dcd1ba` |
| `cloud/review-fixes-1128` (new) | `92ac6272` | `c17271ab` plus `92ac6272` |

Both pack branches start at the current master tip. A merge of `origin/master` into each branch reports `Already up to date`.

## Verdict

| Branch | Verdict |
|---|---|
| `cloud/pack-playwright-cli` | Blocked by finding B1 (missing Apache-2.0 section 4(b) notices in the five modified files). `cloud/review-fixes-1128` targets this branch and carries the fix. With that fix merged, the branch is ready to merge. |
| `cloud/pack-artex-defense` | Ready to merge. The review found no Blocking issue. Suggestions S5 to S8 and the Nits can follow in a later change. |

Every CI step passes on each branch, on each branch merged with master, on the combined tree and on the fix branch. The one exception is the known rm-guard test, which fails only with the session rm wrapper first on PATH (Evidence, test 2).

## Findings

### Blocking

**B1. playwright-cli: the modified files carry no change notice (Apache-2.0 section 4(b)).**
`packs/playwright-cli/NOTICE:23-25` states that the modified files carry a notice that prompt-orchestrator changed them. None of the five files carries a notice. These files are `SKILL.md`, `references/pr-attachments.md`, `references/session-management.md`, `references/test-generation.md` and `references/video-recording.md`. Section 4(b) asks for a prominent notice in each modified file. The fix is on `cloud/review-fixes-1128` at `92ac6272` and targets `cloud/pack-playwright-cli`. The fix adds one dated HTML comment to each of the five files, after the front matter in `SKILL.md`, and rewords the NOTICE header to describe the comments. The artex-defense pack uses the same comment form for `defense-en.md`. Full CI passes on the fix branch.

### Suggestion

**S1. playwright-cli `SKILL.md:429`: the example breaks without XDG_DATA_HOME.**
The command quotes `"$XDG_DATA_HOME/prompt-orchestrator/..."`. With XDG_DATA_HOME unset, as on most Linux and macOS hosts, the path becomes `/prompt-orchestrator/...` and the command fails. Use `"${XDG_DATA_HOME:-$HOME/.local/share}/prompt-orchestrator/packages/playwright-cli/node_modules/.bin/playwright-cli"`.

**S2. playwright-cli `SKILL.md:4` and `SKILL.md:422`: the grant does not match the documented invocation.**
The installer puts the binary in the private prefix and not on PATH. Each example in the skill runs a bare `playwright-cli`. `SKILL.md:422` tells the agent to run the prefix binary with `NO_UPDATE_NOTIFIER=1`. The grant `Bash(playwright-cli:*)` does not match a command that starts with `NO_UPDATE_NOTIFIER=1 "/full/path/..."`, so each call asks for permission. The effect is extra prompts and no wider access. One shell line fixes both points: `export PATH="<prefix>/node_modules/.bin:$PATH" NO_UPDATE_NOTIFIER=1`. After that line, the bare examples run and match the grant. The upstream source (`playwright-cli.js`, `checkForUpdates`) confirms that `NO_UPDATE_NOTIFIER` turns off the npm update check.

**S3. playwright-cli `references/test-generation.md:159`: one upstream step fetches an `@latest` build.**
The step `npm init playwright@latest` contradicts `SKILL.md:432` ("do not fetch an `@latest` build"). The rule at `SKILL.md:422` to ask the user before an install step covers this case only when the agent reads both files together. Add a note in the reference file, or name the exception in NOTICE.

**S4. playwright-cli: alpha dependencies.**
`@playwright/cli` 0.1.25 pins `playwright` and `playwright-core` at `1.66.0-alpha-2026-11-18`. The pack report lists this point. A later pack update can move to stable dependencies.

**S5. artex-defense `SKILL.md:89`: the network list for the harness is incomplete.**
SKILL.md names PyPI and the image registry. The harness also reaches two more hosts. `sigma/check.sh:27`, `sigma_lint/check.sh:36` and `check-defense-template.py:139-140` probe `d3fend.mitre.org` (a pack change). pySigma 3.1.0 also downloads the ATT&CK data from `github.com/mitre-attack/attack-stix-data`. In this session, that URL returned 403 and three checks failed (`sigma`, `sigma_lint` and the defence template gate). No script in `scripts/` sends traffic to a target or to an ARTEX host. Name the ATT&CK data host in SKILL.md, so operators on filtered networks can allow it.

**S6. artex-defense `SKILL.md:100`: the Suricata command fails as written.**
Suricata 8.0.8 stops with `The logging directory "/tmp/artex-suricata" ... doesn't exist` when the folder is missing. Put `mkdir -p /tmp/artex-suricata` before the command. On `SKILL.md:106`, `-S artex.rules` also differs from the path on line 100 (`references/suricata/artex.rules`).

**S7. artex-defense `scripts/tests/suricata/run.sh:31`: the Suricata image is unpinned.**
The default image is `jasonish/suricata:latest`, and the Python images use the tag `python:3.12-slim`. This default comes from upstream. A digest pin would make the harness repeatable.

**S8. artex-defense: the validator change is safe.**
The change at `tools/validate_packs.py:144-152` keeps the `SKILL.md` suffix rule for skills without `upstream-type`. With `upstream-type: document`, the URL still has to start with `<pack upstream>/blob/<upstream-commit>/` and end in `.md`. The validator rejects other values of `upstream-type`. In-house packs skip this branch of the check. On the combined tree, the validator checks 8 packs with 0 problems, and `test_upstream_document_form` passes. No other pack uses `upstream-type`, so the change loosens no other pack's check. This item needs no action. It records the review result for the shared gate.

### Nit

| ID | Where | Point |
|---|---|---|
| N1 | playwright-cli `SKILL.md:426` | On Windows, npm writes `playwright-cli.cmd` and `playwright-cli.ps1` in `.bin`. The extensionless name in the Windows path is the POSIX shim. Name `playwright-cli.cmd`. |
| N2 | playwright-cli `SKILL.md:422` | New prose "Ask the user before any install step" uses a sweeping quantifier (Addendum A2). |
| N3 | playwright-cli report | The report gives 0 prose advisories for the gate. My run gives 4. The 4 advisories sit in the report file, which the report run predates. |
| N4 | artex-defense `pack.json:7`, `SKILL.md:34` | `AGPL-3.0` is a deprecated SPDX id. Upstream states only "AGPL-3.0". Keep the upstream wording, or pick `AGPL-3.0-only` or `AGPL-3.0-or-later` as a leader decision. |
| N5 | artex-defense `references/artex-security-analysis.md:80` | `DB_SSL=disable` is on `install.sh:73` at the commit. The analysis cites `install.sh:72`. |
| N6 | artex-defense `references/artex-security-analysis.md:158` | `notify/telegram.go:93` is the base URL line. The `/bot<token>/sendMessage` path is built on `notify/telegram.go:97`. |
| N7 | artex-defense `scripts/artex_host_triage.py:750` | The self-test peer `93.184.216.34` is a public address (formerly example.com), outside RFC 5737. The script parses the text only. The script is verbatim upstream, and NOTICE describes the address correctly. |

### Checks with no finding

| Area | Result |
|---|---|
| playwright-cli pack.json | Matches pack format v1. `npm.node` `>=20.0.0` matches the `engines` of the three packages. The set holds one skill. |
| playwright-cli npm pin | The registry `dist.integrity` for 0.1.25 equals the pin. My own SHA-512 of `cli-0.1.25.tgz` equals the pin. |
| playwright-cli vendored text | `diff -r` against upstream `dc5f4d56` shows only the changes that NOTICE lists. The 20 prose em dash rewrites match the per-file counts (1, 1, 15, 3). The 3 em dashes in code fences stay. `LICENSE` is byte-identical to upstream. Upstream ships no NOTICE file, so section 4(d) does not apply. |
| artex-defense file map | Of the 55 shipped files, 31 are byte-identical to upstream `06b36d72`. 18 files differ, and NOTICE lists all 18. Each of the 18 carries a dated section 5(a) notice. 6 files are new (SKILL.md, the analysis, the three captures and LICENSE). The 10 upstream README files under `detections/` are not shipped. Both `LICENSE` copies equal the upstream text. Upstream carries no copyright line to preserve. |
| artex-defense scope | The pack holds no ARTEX application code, no agent prompts and no files from upstream `skills/`. The sources are `detections/` and `docs/defense-en.md`. SKILL.md:44 limits use to assets the reader owns or is authorized to defend. |
| artex-defense fixtures | The event fixtures use 203.0.113.0/24, 10.0.0.0/8, 127.0.0.1 and `*.example.test` hosts. The three captures hold only 10.10.10.9 and 10.10.10.80 with `Host: shop.example.test`. The SHA-256 of each capture equals the NOTICE value. |
| artex-defense analysis | I compared the cited lines below against upstream `06b36d72`, covering all eight findings. F1 (`traffic.go:204-208`), F2 (`traffic.go:177-178`, `545-552`), F3 (`stage.go:66`, `90-92`, `99`, `bootstrap.go:177-184`), F4 (`Dockerfile:43-45`, `main.go:55-57`, `docker-compose.yml:46-47`), F5 (`install.sh:21-23`), F6 (`auth.go:42`, `281-292`), F7 (`auth.go:27`, `445-452`), F8 (`auth.go:337-341`, `370-373`), the MCP lines (`client.go:31`, `250`), `README.md:21` and `guard/guard.go:148-149` match. N5 and N6 list the two offsets. |
| Wording | New prose in both packs holds no em dash, no en dash and no spaced hyphen. Upstream text in `defense-en.md` keeps its em dashes as quoted source. |
| Attribution | `ai_trailer.py check` finds nothing in the 5 commits. The added lines hold no `Co-Authored-By`, `Generated with` or session link. |

## Evidence

### Tools

| Tool | Version | Source |
|---|---|---|
| Python | 3.13.18 | preinstalled |
| PyYAML | 6.0.2 | scratch venv, `pip install "pyyaml==6.0.2"` as in the workflow |
| ShellCheck | 0.9.0 | Ubuntu 24.04 apt |
| PowerShell | 7.7.0 | packages.microsoft.com apt repository |
| Node.js, npm | 22.23.5, 10.9.9 | preinstalled |
| Docker | 29.9.3 | preinstalled, daemon started for the harness |
| Suricata | 8.0.8 | `mirror.gcr.io/jasonish/suricata:latest` |

### Test 1: CI steps per branch

The script `run_ci.sh` runs each step of `prompt-orchestrator-ci.yml` in workflow order. The quality job steps run on the checkout. The gate job steps use the checker and the allowlists from a master checkout. The `--event` file holds the head commit subject as the title and an empty body. Each run used a fresh worktree with `/usr/bin` first on PATH (see test 2).

| Tree | Head | Result |
|---|---|---|
| master (baseline) | `2aa81014` | PASS, 6 packs |
| playwright-cli | `c17271ab` | PASS, 7 packs |
| playwright-cli plus master | `c17271ab` (no merge needed) | PASS |
| artex-defense | `a6dcd1ba` | PASS, 7 packs |
| artex-defense plus master | `a6dcd1ba` (no merge needed) | PASS |
| combined (test 3) | `5dbe4d3a` | PASS, 8 packs |
| `cloud/review-fixes-1128` | `92ac6272` | PASS, 7 packs |

Step output for artex-defense (the other runs match, except where noted):

```
Generated integrations match their sources: rc=0
Skill, workflow and harness validator: Overall Results: 404 passed, 0 failed out of 404 total.
Pack format validator: 7 packs checked, 0 problems
PowerShell scripts in packs parse: Parsed 42 .ps1 files under packs/, 0 blocking parse errors
Generated installers match the spec and the packs: installers are current
Shell check of the generated bash installer: shellcheck clean
[harness/tests] Ran 30 tests OK
[install] Ran 7 tests OK
[tests/installers] Ran 79 tests OK (skipped=1)      (78 on playwright-cli and master)
[skills/academic-writing/scripts] Ran 11 tests OK
[skills/architecture-diagrams/scripts] Ran 17 tests OK (skipped=17)   (same on master)
[skills/ci-enforcement/tests] Ran 35 tests OK (skipped=1)
[skills/concision-and-logic/scripts] Ran 9 tests OK
[skills/docs-scaffold/scripts] Ran 15 tests OK
[skills/human/scripts] Ran 5 tests OK
[skills/no-ai-trailer/scripts] Ran 12 tests OK
[skills/skill-creator/scripts] Ran 10 tests OK
rules: registry: 21 rules, every gate rule has a checker
prose: 0 gate finding(s), 48 advisory finding(s)   (22 at 31e29d36; playwright-cli: 4)
attribution, secrets, unicode, commits, models: 0 gate finding(s), 0 advisory finding(s)
```

With pwsh installed, the installer suite skips one test (`PO_TEST_NETWORK=1` Frida download). The pack reports skipped 6 tests because pwsh was missing. The pwsh installer tests now run and pass on both branches.

### Test 2: the rm-guard test

The test links each command on PATH into one shim folder. In this session, the first `rm` on PATH is the rm guard wrapper `/root/.claude/rm-guard/.../refuse/rm`. The wrapper runs the next `rm` on PATH. Inside the shim folder, no other `rm` exists, so the install step fails with `rm: command not found` and exit 127. With `/usr/bin` first on PATH, the shim links `/usr/bin/rm` and the test passes.

```
== master 2aa81014 PATH=default   first rm on PATH: /root/.claude/rm-guard/.../refuse/rm   FAILED (failures=1)
== master 2aa81014 PATH=system    first rm on PATH: /usr/bin/rm                            OK
== pw c17271ab PATH=default       FAILED (failures=1)
== pw c17271ab PATH=system        OK
== artex a6dcd1ba PATH=default    FAILED (failures=1)
== artex a6dcd1ba PATH=system     OK
```

### Test 3: combined tree

Only `install/install.sh` conflicts. Git merges `install/install.ps1` cleanly, and the result equals the regenerated file. After `generate_installers.py`, `PO_PACKS` lists `artex-defense claude-red-offense cyber-skills logo-design playwright-cli procable rea reverse-skill`. Full CI passes on the combined tree with 8 packs. For the commits gate, the allow file added the identity of my two local scratch merge commits. The pack commits pass with the repository allowlist alone. The fix commit also merges onto the combined tree with no conflict, and the validator and the installer check stay clean.

### Test 4: artex-defense harness and triage self-test

Command, from the skill folder:

```bash
PYTHON_IMAGE=po-local/python:3.12-slim-ccr SURICATA_IMAGE=mirror.gcr.io/jasonish/suricata:latest bash scripts/tests/run-all.sh
```

Containers reach PyPI only through the session proxy. A test-only `docker` shim adds `--network host` to `docker run`. The image `po-local/python:3.12-slim-ccr` is `python:3.12-slim` plus the proxy CA. The first run failed `sigma`, `sigma_lint` and the defence template gate, because pySigma's ATT&CK URL (`github.com/mitre-attack/attack-stix-data/raw/...`) returned 403 here. `raw.githubusercontent.com` serves the same file with 200. The test image then carried a `sitecustomize.py` that rewrites that one URL prefix to the raw host. The pack files stayed unchanged, and `git status` stayed clean after the run.

```
  PASS  sigma
  PASS  sigma_match
  PASS  sigma_lint
  PASS  sigma_backends
  PASS  suricata
  PASS  attack
  PASS  indicators
  PASS  misp
RESULT: PASS
EXIT=0
PASS lines: 166  FAIL lines: 0
```

SKIP lines (10):

```
SKIP  CI leg: /repo/.github/workflows/detections.yml is not shipped in this pack
SKIP  defense-ko.md is not shipped in this pack; ko/en parity not checked
SKIP  d3_fendtag validator: d3fend.mitre.org is unreachable from this network   (defence template gate)
SKIP  d3_fendtag validator: d3fend.mitre.org is unreachable from this network   (sigma)
SKIP  d3_fendtag validator: d3fend.mitre.org is unreachable from this network   (sigma_lint)
SKIP  ARTEX source tree not shipped; source grounding not checked
SKIP  ARTEX source tree not shipped; deny-list side not checked, rule side only
SKIP  source-file grounding of each row (ARTEX source tree not shipped)
SKIP  CI workflow and pre-commit config not shipped; trigger wiring not checked
SKIP  CI workflow not shipped in this pack; trigger wiring not checked          (misp)
```

`d3fend.mitre.org` answers `403 Forbidden (agent proxy: no rule or network setting allows this host)` here, as in the pack report.

```
$ python3 scripts/artex_host_triage.py --self-test
RESULT: PASS        (exit 0, 23 PASS lines, 0 FAIL lines)
```

The Suricata replay from SKILL.md step 2 (with the log folder created first, see S6):

```
enrich: {1000001: 35, 1000002: 5}
norma:  {1000003: 8}
benign: {}
d6a7b8e7...7565238  enrich.pcap   d830db74...6b92  norma.pcap   1f024b5d...55b9  benign.pcap   (equal to NOTICE)
```

The `artex-defense` set also installs and removes cleanly in a temporary HOME. In mode mcp, the install reports 58 changes. The 55 installed files equal the pack folder, and the index lists `('artex-defense', 'detecting-artex-autonomous-attacks')`. Removal leaves 0 entries under HOME.

### Test 5: playwright-cli install and removal

```
$ HOME=$T/home bash install/install.sh packs install playwright-cli --tools claude --yes
  $ npm install --prefix .../packages/playwright-cli @playwright/cli@0.1.25 --omit=optional --ignore-scripts --save-exact
added 3 packages in 1s
  @playwright/cli@0.1.25 matches the pinned integrity
==> done: 15 changes
$ NO_UPDATE_NOTIFIER=1 .../node_modules/.bin/playwright-cli --version
0.1.25
package-lock.json: @playwright/cli 0.1.25, playwright 1.66.0-alpha-2026-11-18, playwright-core 1.66.0-alpha-2026-11-18
$ HOME=$T/home bash install/install.sh packs remove playwright-cli --yes
==> done: 15 changes
entries left under HOME (files and folders): 0
```

In mode skills, the install reports 12 changes. The copy in `~/.claude/skills/playwright-cli` equals the pack folder, and removal leaves 0 entries.

## Merge recipe

The recipe merges the playwright-cli branch with the fix first. Without the fix, name `origin/cloud/pack-playwright-cli` in the third command.

```bash
git fetch origin master cloud/pack-playwright-cli cloud/pack-artex-defense cloud/review-fixes-1128
```

```bash
git checkout -B merge-packs origin/master
```

```bash
git merge --no-ff origin/cloud/review-fixes-1128 -m "merge: playwright-cli pack with the 4(b) notice fix"
```

```bash
git merge --no-ff origin/cloud/pack-artex-defense -m "merge: artex-defense pack"
```

The second merge stops on `prompt-orchestrator/install/install.sh`. Regenerate both installers and finish the merge:

```bash
cd prompt-orchestrator && python3 tools/generate_installers.py && python3 tools/generate_installers.py --check
```

```bash
git add install/install.sh install/install.ps1 && git commit --no-edit
```

Then drop the two branch reports under `prompt-orchestrator/ignore/reports/`, as earlier merges did, and run the CI steps again. `cloud/review-fixes-1128` already contains `cloud/pack-playwright-cli`, so `origin/cloud/review-fixes-1128` replaces `origin/cloud/pack-playwright-cli` in the recipe. The merge commits need an identity from `.github/ci-enforcement/identities.txt` to pass the commits gate.

## Open issues

1. Master tracks 12 `__pycache__/*.cpython-313.pyc` files under `harness/scripts`, `skills/human/scripts` and `skills/no-ai-trailer/scripts`. The unit tests rewrite them. A second CI run in the same checkout then fails the step "Generated integrations match their sources". CI uses a fresh checkout, so CI does not see this failure. The issue exists before both branches.
2. The cloud rm guard wrapper breaks `test_mode_mcp_without_node_stops_before_writing` in each cloud session. The test can skip the wrapper, for example by linking the last `rm` on PATH, or the cloud runs can put `/usr/bin` first.
3. In this session, the artex harness needs two workarounds. The proxy refuses `github.com/<repo>/raw/` for pySigma's ATT&CK data, and `d3fend.mitre.org` is blocked. GitHub runners and open networks need neither workaround.
4. The pack report for artex-defense lists the analysis gaps (`web/` dependencies, `guard/` bypass resistance, upstream CI, go-mitmproxy key file mode). This review did not close them.

QUESTION FOR THE LEADER: should the playwright-cli merge take `cloud/review-fixes-1128` (the B1 notice fix) in place of `cloud/pack-playwright-cli`? Recommended answer: yes, merge `cloud/review-fixes-1128`, because the fix is the branch plus one commit and its full CI passes.
