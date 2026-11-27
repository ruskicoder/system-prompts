# Report: opt-in pack artex-defense

Branch: `cloud/pack-artex-defense`, started from master at `2aa8101`.

## Result

The opt-in pack `packs/artex-defense` (kind skills) is in place, with Amendment 1 applied. Every acceptance gate that this cloud box can run passes.

- Source: `jiwoochris/artex-global` at commit `06b36d7219244c5e2b6467394f60eca160c785cf`, AGPL-3.0, vetted 2026-11-27. The clone was read-only, and no ARTEX code ran.
- Set `artex-defense` holds the skill `detecting-artex-autonomous-attacks` (55 files).
- The pack ships no ARTEX application code, no agent prompts and none of the offensive skills (`api-recon`, `scopesentry`, `playwright-cli`).
- `references/` holds the 5 atomic and 4 correlation Sigma rules, the Suricata rules, the ATT&CK layer, the indicator CSV and MISP event, the English defence guide `defense-en.md` and the new `artex-security-analysis.md`. The rules and indicators are byte-identical to upstream.
- `scripts/` holds `artex_host_triage.py` (verbatim) and the test harness under `scripts/tests/` with its recorded fixtures and three offline captures.
- SKILL.md has the scope line, the detection guidance (recording-proxy CA, self-update egress, MCP and notifier patterns, enrichment User-Agent, guard marker, destructive-command hunting), the section "Validate the detections" in the required five-step order, and the section "Decide whether to keep or block".
- `references/artex-security-analysis.md` reports 8 findings with `file:line` references at the commit: F1 the recorder accepts every upstream TLS certificate (High), F2 world-readable recorded traffic (High), F3 single-root self-update that runs the staged binary before the swap (Medium), F4 all-interface binds in the image and a published PostgreSQL in `install.sh` (Medium), F5 `curl get.docker.com | sh` plus the docker group (Medium), F6 the setup token in the log (Medium), F7 the session token in the URL query (Low), F8 the limiter table wipe (Low).
- 17 harness files and the guide changed for the pack layout. Each one carries a dated AGPL-3.0 section 5(a) notice, and `NOTICE` lists them. The triage script is unchanged.
- The validator gained one opt-in form. A skill with `upstream-type: document` may name an upstream `.md` document instead of an upstream `SKILL.md`. Design point 7 needs this form, because upstream has no defensive `SKILL.md`. A new validator test covers the form.
- The installers are regenerated. The integrations generator writes no change.

### Fixture review (Amendment B)

No fixture was dropped or replaced. No fixture holds a working exploit payload, shell code, credentials or a live target address.

| Fixture | Content | Decision |
|---|---|---|
| `sigma_match/events/*.json` (5 files) | Web, proxy, file-event, process and application log samples; addresses in 203.0.113.0/24 | Kept |
| `sigma_match/events/correlation/*.json` (4 files) | Timelines on 10.0.0.9, 10.0.0.10, `*.example.test`, `web01`, `web02`, `db02` | Kept |
| Destructive command strings in the fixtures (`rm -rf /`, `rm -rf / --no-preserve-root`, `rm -rf /var/www/html`, `DROP TABLE customers`, `iptables -F`) | Telemetry values that pySigma matches in memory | Kept; no test executes them |
| Guard marker and the guard audit text in the fixtures | Detection signature from `guard/guard.go:148-149` | Kept byte-identical |
| Triage self-test `ss` line with peer 93.184.216.34 | Parsed text that proves a non-listening socket is ignored | Kept; the script never connects to it |
| `suricata/captures/enrich.pcap`, `norma.pcap`, `benign.pcap` | Synthetic plaintext HTTP GETs between 10.10.10.9 and 10.10.10.80, built once offline with the unmodified `gen_pcap.py` | Shipped; the suite replays them and no longer synthesizes traffic |

### CJK in the shipped files

The scan covered U+3000 to U+9FFF, Hangul and full-width forms in every shipped text file. Each hit is the guard audit marker `【ARTEX 平台管控·非目标防御】`, a detection signature that must stay byte-identical. In the event fixtures, the marker is followed by `此操作被禁止`, which is part of the audit text that `guard/guard.go:148-149` writes. The hits are in SKILL.md (1 line), `defense-en.md` (2 lines), the CSV, the MISP event, the Sigma rule, the triage script, three harness checks and 25 fixture lines. The defence guide line that pointed at the Korean edition in Korean was replaced with an English pointer.

## Evidence

Tools in the cloud box:

```
docker 29.9.3 (daemon started for this run), python 3.13.18, jq; no suricata, sigma-cli or tshark on the host
images: mirror.gcr.io/jasonish/suricata:latest, po-local/python:3.12-slim-ccr
  (python:3.12-slim from mirror.gcr.io plus the agent-proxy CA bundle, so pip in containers verifies TLS)
registry-1.docker.io returned 429 Too Many Requests, so the images came from mirror.gcr.io
d3fend.mitre.org: CONNECT tunnel failed, response 403 (session egress policy)
```

Harness run (`scripts/tests/run-all.sh` with `PYTHON_IMAGE=po-local/python:3.12-slim-ccr SURICATA_IMAGE=mirror.gcr.io/jasonish/suricata:latest`):

```
===== detection suites summary =====
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
PASS lines: 166, FAIL lines: 0
```

Checks skipped in this run, each printed as a SKIP line:

```
SKIP  CI leg: /repo/.github/workflows/detections.yml is not shipped in this pack
SKIP  defense-ko.md is not shipped in this pack; ko/en parity not checked
SKIP  d3_fendtag validator: d3fend.mitre.org is unreachable from this network   (template gate, sigma, sigma_lint)
SKIP  ARTEX source tree not shipped; source grounding not checked                (indicators 1/5)
SKIP  ARTEX source tree not shipped; deny-list side not checked, rule side only  (indicators 3/5)
SKIP  source-file grounding of each row (ARTEX source tree not shipped)          (indicators 4/5)
SKIP  CI workflow and pre-commit config not shipped; trigger wiring not checked  (indicators 5/5)
SKIP  CI workflow not shipped in this pack; trigger wiring not checked           (misp 5/5)
```

The `sigma_lint` full-set step stayed live with the `d3_fendtag` exclusion:

```
PASS  full set is live: SigmahqGithubLinkIssue present
PASS  full set is live: SigmahqLogsourceUnknownIssue present
PASS  every reported issue is one of the four documented exclusions
```

Commands that SKILL.md documents:

```
$ python3 scripts/artex_host_triage.py --self-test
RESULT: PASS
$ suricata -r scripts/tests/suricata/captures/enrich.pcap -S references/suricata/artex.rules -k none -l <dir>   (in the Suricata image)
enrich.pcap alerts by sid: {1000001: 35, 1000002: 5}
```

Captures:

```
wrote 385 packets across 35 flows to /out/enrich.pcap (UA='artex-enrich/1.0')
wrote 88 packets across 8 flows to /out/norma.pcap (UA='norma/0.4')
wrote 385 packets across 35 flows to /out/benign.pcap (UA='Mozilla/5.0 ... Firefox/128.0')
d6a7b8e72b4f018df2d95bcd48001a10f373f070e69781ca7961d0a057565238  enrich.pcap
d830db74dfe81548c45c0bb7e3245d1fe04af35ea5fefac7dd276b63e1161b92  norma.pcap
1f024b5db5295c6567bd62f075ca508267de8398eae225ab54b3e2cb5f6255b9  benign.pcap
rebuild: enrich.pcap reproducible (cmp equal)
```

Validators and generators:

```
$ python3 tools/validate_packs.py
pack artex-defense: 1 sets, 1 skills, kind skills
7 packs checked, 0 problems
$ python3 skills/validate_skills.py
Overall Results: 404 passed, 0 failed out of 404 total.
$ python3 tools/generate_installers.py --check
installers are current
$ python3 tools/generate_integrations.py; git status --porcelain
(no change besides the pack, the installers and the three validator files)
$ shellcheck -s bash install/install.sh   (ShellCheck 0.11.0)
SHELLCHECK OK
SKILL.md description: 764 characters
```

Unit tests from the CI step:

```
harness/tests: OK
install: OK
tests/installers: Ran 79 tests, FAILED (failures=1, skipped=6)
skills/academic-writing/scripts: OK
skills/architecture-diagrams/scripts: OK
skills/ci-enforcement/tests: OK (skipped=1)
skills/concision-and-logic/scripts: OK
skills/docs-scaffold/scripts: OK
skills/human/scripts: OK
skills/no-ai-trailer/scripts: OK
skills/skill-creator/scripts: OK
```

The one failure is `FixtureMcpBashTests.test_mode_mcp_without_node_stops_before_writing`. The same test fails the same way on an unmodified master worktree (`rm: command not found`), because the test links the session's rm guard wrapper into its shim folder. The new test `ValidatorTests.test_upstream_document_form` passes.

Install and removal of the set in a temporary HOME:

```
$ HOME=$T/home bash install/install.sh packs install artex-defense --tools claude
==> done: 58 changes
files installed: 55 (repo: 55)
installed copy identical
index entries: [('artex-defense', 'detecting-artex-autonomous-attacks')]
$ HOME=$T/home bash install/install.sh packs remove artex-defense
==> done: 58 changes
files left under HOME: none
```

Gate job steps on `origin/master...HEAD`:

```
rules: registry: 21 rules, every gate rule has a checker
prose: 0 gate finding(s), 22 advisory finding(s)
attribution: 0 gate finding(s), 0 advisory finding(s)
secrets: 0 gate finding(s), 0 advisory finding(s)
unicode: 0 gate finding(s), 0 advisory finding(s)
commits: 0 gate finding(s), 0 advisory finding(s)
models: 0 gate finding(s), 0 advisory finding(s)
new prose self-check (em dash, en dash separator, banned openers): 0 hits in SKILL.md, the analysis, NOTICE and pack.json
```

## Open issues

1. The validator change (`upstream-type: document`) touches a shared gate. Design point 7 asks for `upstream` to name `docs/defense-en.md`. The existing rule requires a `SKILL.md`, and upstream has no defensive `SKILL.md`.
2. `d3fend.mitre.org` is blocked by the session's egress policy. The harness excluded the `d3_fendtag` validator in three places. The shipped rules carry no D3FEND tags, so that validator had nothing to check. On a network that reaches the host, the harness runs the full set unchanged.
3. The pack harness cannot run the upstream checks that need the ARTEX source tree, the upstream CI workflow or the Korean guide. These checks print SKIP. The rule-side checks still run.
4. The harness needs Docker and network access to PyPI and an image registry. In this box, Docker Hub answered 429, so the run used `mirror.gcr.io` images and a local image with the agent-proxy CA.
5. In this cloud box, `test_mode_mcp_without_node_stops_before_writing` fails on master and on this branch for the rm-guard reason above.
6. The CI step "PowerShell scripts in packs parse" did not run locally because pwsh is not installed. The pack ships no `.ps1` file.
7. The security analysis did not cover the `web/` dependencies, `guard/` bypass resistance or the upstream CI workflows. The key file mode of the go-mitmproxy CA is unverified (F2).
8. The commits carry the allowlisted owner identity from `.github/ci-enforcement/identities.txt`, so the commits gate passes. The commits carry no AI trailer.
