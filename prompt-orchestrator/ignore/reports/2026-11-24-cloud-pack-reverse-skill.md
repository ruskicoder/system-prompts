# Report: reverse-skill package port (branch cloud/pack-reverse-skill)

## Result

Commit `182f2a7` on `cloud/pack-reverse-skill` ports zhaoxuya520/reverse-skill at `b972ad0e90f26d8f044828f004da22a4a585da12` (MIT) into `prompt-orchestrator/packs/reverse-skill/` as a pack of kind `package`. The commit touches only that folder. Its base is master `2c4594d`.

- `package/` holds the full upstream tree without `.git`, with the same relative layout. That includes the routing scripts, case-init and ops gates, bootstrap installers, MCP registration, the Kali and Docker setups, burp-mcp-full, the CTF sandbox orchestrator, plugins, examples and every skill.
- `pack.json` follows pack format v1 with one set, `reverse-skill`, and `"package": {"payload": "package"}`.
- `skills/reverse-skill/SKILL.md` carries the third-party front matter, with upstream set to the `skills/SKILL.md` blob at the commit. Its body:
  - names the three payload paths
  - sends the agent to `README_AI.md` first
  - keeps the upstream consent gates
  - states that the host rules (communication tone, approval for installs and global config changes) override the package rules, including the "no further confirmation" text in the precedent files
- `LICENSE` is the upstream MIT text. Upstream ships no NOTICE.
- Chinese removal:
  - 379 upstream text files held CJK text.
  - 325 files were translated in place, and `docs/QUICKSTART_zh.md` became `docs/QUICKSTART.md`.
  - 47 payloader files with Chinese file names were renamed to English slugs and translated.
  - 8 Chinese duplicates were deleted: README_zh.md, RULES_zh.md, skills/routing_zh.md, docs/OVERVIEW_zh.md, docs/UV-AND-DOWNLOAD-SECURITY_zh.md, .marvis/SKILL_zh.md, the Chinese src-hunter README.md, and the Chinese half of the .marvis description.
  - Content that only the Chinese copies held went into RULES.md and skills/routing.md.
  - The router keywords in `skills/config/routing.json` were translated.
- Removed marketing:
  - the logo image `reverse-skill.png`
  - the shields.io and trendshift badges
  - the star history image and `skills/scripts/update-star-history.ps1`
  - the sponsor section, `docs/assets/sponsors/` and `.github/FUNDING.yml`
  - the linux.do links
  - xquik-mcp and every other functional reference stay.
- Gradle wrapper jar: deleted, because its sha256 did not match the published Gradle 8.7 wrapper checksum `cb0da6751c2b753a16ac168bb354870ebb1e162e9083f116729cec9c781156b8`. `gradle-wrapper.properties` stays. `burp-mcp-full/README.md` and the entry skill say that `gradle wrapper --gradle-version 8.7` regenerates the jar.
- The port also changed these derived files:
  - `skills/INDEX.md`, regenerated with a Python port of `extract-summaries.ps1` (same format, BOM and order)
  - `PAYLOAD_SHA256` in `skills/scripts/verify-repository-security.py`, now `1d2cfb879459a0fa991f6c79895d61d150ac1d86f20a9192b12c4b08d85212d0`, the sha256 of the translated `waf-bypass.md`
- Commit author and committer: `Do Dang Khoa <149188141+ruskicoder@users.noreply.github.com>`, the identity on master. The local git config named an AI identity, so I set the author per commit instead. The message has no AI trailer.

All required checks pass except the two items listed under Open issues: pwsh is absent, and two upstream tests stop on this environment's rm guard.

## Evidence

All commands ran on 2026-11-24 in the session container.

CJK search over the pack (file contents):

```
$ cd prompt-orchestrator/packs/reverse-skill
$ LC_ALL=C.UTF-8 grep -rnP '[\x{3000}-\x{30FF}\x{3400}-\x{4DBF}\x{4E00}-\x{9FFF}\x{FF00}-\x{FFEF}]' . | wc -l
0
```

Shell, Python, JSON and YAML syntax:

```
bash -n over every .sh file:            sh files=23 fail=0
python3 -m py_compile over every .py:   py files=13 fail=0
python3 -m json.tool over every .json:  json files=11 fail=0
yaml.safe_load_all over .yml/.yaml:     yaml files 46 fail 0
node --check over the 2 .js files:      no errors
```

The first JSON run failed on `kali/scripts/bootstrap-manifest.json` line 237, because the translation had dropped a trailing comma. I fixed it, and a scan of every translated code line for a changed trailing delimiter then found 0 more cases.

PowerShell: `which pwsh` returns nothing, so the 40 `.ps1` files were not parsed with `[System.Management.Automation.Language.Parser]::ParseFile`. A quote-balance heuristic over the changed `.ps1` lines flagged 6 lines. All 6 are false positives: a `'# ...'` string literal that the heuristic read as a comment.

Upstream tests, run from a git-initialized copy of `package/`:

| Test | Result |
|------|--------|
| skills/scripts/test-routing.sh | TOTAL=221 PASS=221 FAIL=0, plus the default-root regression |
| skills/scripts/test-docker-assets.sh | TOTAL FAIL=0 |
| skills/scripts/test-bash-workflow.sh | TOTAL=5 PASS=5 FAIL=0 |
| skills/scripts/test-apk-decode-manifest.sh | TOTAL=2 PASS=2 FAIL=0 |
| kali/scripts/test-pwntools-discovery.sh | passed |
| skills/case-review/tests/test_review_case.py | Ran 20 tests, OK |
| skills/scripts/tests/test_verify_doc_links.py | Ran 6 tests, OK (after a fix, see below) |
| skills/ida-reverse/scripts/test-apply-asm-patch.py | TOTAL FAIL=0 |
| skills/scripts/test-bootstrap-manifest.sh | rc=1, `rm: command not found` |
| skills/scripts/test-client-neutral-bootstrap.sh | rc=127, `rm: command not found` |

Totals: 8 test scripts pass and 2 fail. The 2 failures stop the same way on pristine upstream in a separate copy (`rc=1` and `rc=127`, `rm: command not found`). Both tests symlink `command -v rm` into an isolated bin folder, and in this session that resolves to the session rm guard. The README names `test-routing.ps1`, which needs pwsh. `test-routing.sh` covers the same 221 cases.

`test_verify_doc_links.py` first failed 1 of 6 tests. The translation had renamed the staged test file `docs/中文.md` to `docs/документ.md`, but the percent-encoded link still pointed at the old name. The link now uses `docs/%D0%B4%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82.md`. The test still covers percent-encoded non-ASCII names.

Routing, with the upstream Chinese hint on pristine upstream and the English hint on the port:

| Upstream hint (Chinese) | Upstream PRIMARY | Port hint (English) | Port PRIMARY |
|------|------|------|------|
| 逆向这个 APK，分析签名校验 | skills/apk-reverse/SKILL.md | Reverse this APK and analyze its signature check | skills/apk-reverse/SKILL.md |
| 分析这个 Windows PE 二进制 exe 的反汇编 | skills/ida-reverse/SKILL.md | Analyze the disassembly of this Windows PE binary exe | skills/ida-reverse/SKILL.md |
| 前端 JS 加密参数逆向 | skills/js-reverse/SKILL.md | Reverse the frontend JS encrypted parameter | skills/js-reverse/SKILL.md |

The Chinese hints appear only in this report, which sits outside the pack.

Links:

```
$ python3 skills/scripts/verify-doc-links.py        # in a git-initialized copy
OK verify-doc-links: all internal Markdown links resolve
$ python3 skills/scripts/verify-repository-security.py
OK verify-repository-security: tracked=618 executable_sources=83 binary_like=0 agent_entries=3 symlinks=0
```

An independent scan of every `.md` under `package/` found 398 relative links and flagged 4:

- 2 point at `skills/tool-index.md`. That file is gitignored and generated on the first run, the same as upstream. The upstream verifier accepts these links.
- 2 are false positives in `ssti-template-injection.md`. The scanner read the JavaScript payload text `[...]("child_process")` as a link.

Prose gate on the entry skill:

```
$ python3 prompt-orchestrator/skills/ci-enforcement/check.py prose prompt-orchestrator/packs/reverse-skill/skills/reverse-skill/SKILL.md
summary: 0 gate finding(s), 0 advisory finding(s)
```

Attribution gate on the commit:

```
$ python3 prompt-orchestrator/skills/ci-enforcement/check.py attribution --base 2c4594d --head HEAD
summary: 0 gate finding(s), 0 advisory finding(s)
```

Gradle wrapper:

```
gradle-wrapper.properties: distributionUrl gradle-8.7-bin.zip
published wrapper checksum for 8.7: cb0da6751c2b753a16ac168bb354870ebb1e162e9083f116729cec9c781156b8
upstream jar sha256: different, so the jar was deleted
```

Front matter: all 102 YAML front matter blocks in the package parse. Seven files needed quoting after em dash replacement put `: ` inside an unquoted value. One of them, `2026-05-16_pentest-personalblog-fun-mass-assignment.md`, was already invalid upstream.

## Open issues

1. pwsh is absent and its install was denied, so none of the 40 `.ps1` files was parsed with the PowerShell parser. The translated `.ps1` files need a `ParseFile` run on a machine with pwsh, and `test-routing.ps1` should run there too.
2. `test-bootstrap-manifest.sh` and `test-client-neutral-bootstrap.sh` were not exercised. Upstream fails the same way in this container because of the session rm guard. Run both on a normal Linux host.
3. Some translations change matching behavior, and each needs review by someone who uses them:
   - Fingerprints that matched Chinese page titles are now English descriptions such as "(Chinese title)".
   - The hydra failure string `失败` became `fail`.
   - The Japanese line in a jailbreak example was romanized.
   - Pinyin and dialect examples were adapted to English.
   - These payloads now target English-language targets only.
4. `.marvis/SKILL_en.md` became `.marvis/SKILL.md`. No upstream file names either path, so I could not confirm which file name the Marvis client loads.
5. The precedent files (`precedent-auth.md`, `precedent-pentest.md`, `precedent-reverse.md`) keep their upstream text in translation, including "may run without further confirmation". The entry skill states that host approval rules override that text. The package files themselves still say it.
6. `skills/INDEX.md` shows the `src-hunter` summary with a leading single quote, because that front matter value is now quoted YAML and `extract-summaries.ps1` copies the raw value. Rerunning the PowerShell script gives the same output.
7. The pack is not installable until the installer change from the parallel session lands. I could not test an install to `<data_home>/packages/reverse-skill/`. The scripts ran from a copy of `package/` at another path and found their root.
