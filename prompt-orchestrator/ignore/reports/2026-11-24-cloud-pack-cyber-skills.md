# Report: cyber-skills pack import (2026-11-24)

Branch `cloud/pack-cyber-skills` of ruskicoder/system-prompts, from master `2c4594d`.
Upstream: mukul975/Anthropic-Cybersecurity-Skills at `54a798831d2266a3ca61ce68a7acb80b81160d57` (Apache-2.0), vetted by the leader on 2026-11-24.

## Result

| Step | Status | Where |
|---|---|---|
| 1. Clone and copy | Done: 818 skill folders holding 4478 files | `packs/cyber-skills/skills/` |
| 2. Prose edits | Done: 1796 em dashes replaced, 21 emoji removed, 0 rewordings | 1095 markdown files |
| 3. Front matter and notices | Done: provenance and `modified` keys in 818 SKILL.md, notice line in 277 other markdown files | each SKILL.md |
| 4. pack.json and LICENSE | Done: ten sets, 818 skills | `packs/cyber-skills/pack.json`, `packs/cyber-skills/LICENSE` |
| 5. Checks | Pass, with three documented exceptions (see Open issues 1 to 3) | Evidence below |
| 6. Commit and push | Done: commit `b9e876f`, pushed | `origin/cloud/pack-cyber-skills` |

The commit touches only `prompt-orchestrator/packs/cyber-skills/`. This report is the second commit.

Set sizes, mapped from the upstream `subdomain` key. All 46 upstream subdomains appear in the brief's table, so no skill needed a closest-set choice.

| Set | Label | Skills |
|---|---|---|
| cyber-offense | Offense and red team | 59 |
| cyber-soc-detection | SOC and detection | 93 |
| cyber-hunting-intel | Threat hunting and intel | 110 |
| cyber-forensics-ir | Forensics and incident response | 80 |
| cyber-malware | Malware analysis | 39 |
| cyber-cloud-container | Cloud, containers and DevSecOps | 125 |
| cyber-appsec-api | Application, API and mobile security | 87 |
| cyber-identity-zero-trust | Identity, zero trust and phishing defense | 74 |
| cyber-network-ot-iot | Network, OT, IoT and hardware | 80 |
| cyber-grc-crypto-ai | GRC, vulnerability management, crypto and AI | 71 |
| Total | | 818 |

The pack label is "Cybersecurity skills (mukul975)". The description reads "Community cybersecurity skill collection by mukul975, not affiliated with Anthropic, split into ten opt-in sets by security domain." The upstream URL keeps the upstream repository name because it is the real address.

Edit method:
- Copied per skill: SKILL.md, scripts/, references/, assets/, LICENSE. Skipped: the six SKILL.es.md files and all upstream files outside skills/. One upstream skill (`performing-cloud-native-threat-hunting-with-aws-detective`) ships no LICENSE file, so its folder has none; the pack LICENSE covers it.
- The import masks code fences, inline code and HTML comments, then edits the rest. Replacement rules for em dashes: headings and list labels take a colon; a pair of dashes around an aside takes two commas; a dash before a conjunction, preposition or participle takes a comma; a dash after a sentence that already holds a colon takes a period with the next letter capitalised; every other dash takes a colon. Totals: colon 1649, comma 96, period 46, hand-picked 5 (four commas and one colon in three sentences where the rules produced a fragment).
- A description that changed is re-emitted with the YAML dumper, which quotes it when the new text holds ": ". The importer asserts that every other front-matter key parses to the upstream value.
- Emoji: the only Emoji_Presentation characters in prose were 21 coloured circles in `conducting-gdpr-compliance-assessment/assets/compliance-scorecard.md`. The text symbols U+2610, U+2713 and U+2717 are not emoji and stay.
- No prose-gate rewording was needed. The gate found nothing in the edited files.

## Evidence

Upstream clone:

```
$ git clone https://github.com/mukul975/Anthropic-Cybersecurity-Skills.git /tmp/upstream/repo
$ git -C /tmp/upstream/repo checkout 54a798831d2266a3ca61ce68a7acb80b81160d57
$ git log -1 --format='%H %ad'
54a798831d2266a3ca61ce68a7acb80b81160d57 Mon Aug 31 04:32:42 2026 +0000
$ ls skills | wc -l
818
```

Import run:

```
{"skills": 818, "em": 1796, "emoji": 21,
 "kinds": {"colon": 1649, "comma": 96, "placeholder-kept": 22, "period": 46, "manual": 5}}
edited md: 1095 skipped: 6
```

Check 1 (set membership), check 3 (front matter) and an extra edit-scope check, from a verification script:

```
[1] folders=818 set_total=818 in_multiple_sets=0 folders_without_set=0 set_entries_without_folder=0
[2] master skills/workflows .md names=153 collisions=[] (also checked skills/ subfolder names: [])
[3] SKILL.md checked=818 failing=2 longest_description=1016
    ('performing-red-team-phishing-with-gophish', ["Missing primary title header '# ...' in markdown body"])
    ('performing-ssrf-vulnerability-exploitation', ["Missing primary title header '# ...' in markdown body"])
[4] non-markdown files byte-identical: differ=0; markdown drift beyond allowed edits=0; files not in upstream=0
```

Check 3 tests: name equals folder name, name matches `^[a-z0-9][a-z0-9-]*$`, description present and at most 1024 characters, the seven provenance values, and `validate_skills.validate_agent_skill_dir`. All 818 pass the pack-format rules. The two failures are the in-house H1 rule (Open issue 3). Check 4 compares each markdown file with upstream after removing em dashes, emoji, whitespace and `, : . /`, and compares every other file byte for byte.

Check 2 (name collisions): 0 collisions against the 153 `skills/*.md` and `workflows/*.md` names on master, and 0 against the `skills/` subfolder names.

Check 4 (prose gate on every edited markdown file):

```
$ python3 prompt-orchestrator/skills/ci-enforcement/check.py --advisory-cap 0 prose <1095 edited .md files>
summary: 0 gate finding(s), 1461 advisory finding(s)
exit 0
$ python3 prompt-orchestrator/skills/ci-enforcement/check.py --advisory-cap 0 prose <all 2562 pack .md files>
summary: 9 gate finding(s), 5292 advisory finding(s)
```

The 9 pack-wide hits sit in 8 files that the import did not edit: 8 are the proper noun "Let's Encrypt", and 1 is the exploit name "EternalRomance/Synergy" in a heading (Open issue 4).

Check 5 (em dash grep):

```
$ grep -rn $'—' prompt-orchestrator/packs/cyber-skills | wc -l
510
files with hits by extension: 84 md, 99 py, 1 yar
markdown hits: 304 inside code fences or inline code, 22 table placeholder cells, 0 in prose
```

Check 6 (repository validator on master content):

```
$ python3 prompt-orchestrator/skills/validate_skills.py
Overall Results: 789 passed, 0 failed out of 789 total.
```

Branch checks:

```
$ check.py attribution --base origin/master --head HEAD
summary: 0 gate finding(s), 0 advisory finding(s)
$ check.py commits --base origin/master --head HEAD --allow-file <"both: Do Dang Khoa <149188141+ruskicoder@users.noreply.github.com>">
summary: 0 gate finding(s), 0 advisory finding(s)
$ git ls-remote origin cloud/pack-cyber-skills
b9e876f912bfa621057c2a053c3f8e1682b3e493	refs/heads/cloud/pack-cyber-skills
```

Secrets scan (not required by the brief):

```
$ check.py secrets <all pack files>
summary: 10 gate finding(s), 0 advisory finding(s)
```

All 10 are documentation placeholders: `AKIAIOSFODNN7EXAMPLE` and `AKIAI44QH8DHBEXAMPLE` (AWS documentation examples), `AKIAXXXXXXXXXXXXXXXX`, `AKIAEXPOSEDKEY123456`, and the string `-----BEGIN PRIVATE KEY-----` in a pattern table. No file holds a real credential.

## Open issues

1. Table placeholder cells. 22 cells hold only an em dash, in 6 files (for example `implementing-hipaa-security-rule-safeguards/assets/template.md`). They are not prose, `check.py` exempts them through `PLACEHOLDER_CELL`, and the allowed edits (period, comma, colon) cannot replace an empty cell. They stay, so the literal grep in check 5 is not empty.
2. Em dashes in code files. 99 `.py` files and 1 `.yar` file hold em dashes in comments and strings. Code stays verbatim, so these hits also stay in the grep output.
3. Two SKILL.md files without an H1. `performing-red-team-phishing-with-gophish` and `performing-ssrf-vulnerability-exploitation` start their body at `## When to Use`. The pack format does not require a title, and `validate_skills.py` does not scan `packs/`. A future validator that applies `validate_markdown_file` to pack skills will fail on these two unless it drops the H1 rule for packs.
4. Prose gate on the full pack. A `check.py prose --base master` run on a PR from this branch would report the 9 false positives above. Fix options: exclude `*/packs/*/skills/*` in `DEFAULT_EXCLUDES`, or teach the opener rule that "Let's Encrypt" is a name. Both change `check.py`, which is outside this brief.
5. Gate patterns hidden in SKILL.md bodies. The gate skips files with `origin: third-party`. With that skip bypassed, 15 SKILL.md bodies show 17 gate-pattern hits: 10 "stakeholder" or "leverage platform" phrases, 5 spaced en dashes, 2 "Let's Encrypt". They stay verbatim under the vendored-text rule.
6. Emoji removal in one template. The GDPR scorecard used coloured circles as a status choice. After removal, four status cells and the "Overall Assessment" value are blank to fill in, and the legend still names each level in words.
7. Size. The pack adds 4480 files and 745,065 lines (49 MB). The installer from the parallel session has not been tested against this pack.
8. Git identity. This container's default git identity is an AI identity. The commits use the repository owner's GitHub noreply identity, the same one as every master commit, set per command. The global config is unchanged.
