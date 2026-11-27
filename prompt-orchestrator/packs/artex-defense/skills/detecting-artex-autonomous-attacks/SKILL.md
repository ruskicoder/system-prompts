---
name: detecting-artex-autonomous-attacks
description: >
  Detect, validate and contain ARTEX autonomous penetration-testing activity on networks and hosts
  that the reader owns or is authorized to defend. Bundles the upstream Sigma and Suricata rules,
  the ATT&CK Navigator layer, the indicator CSV and MISP event, a read-only host-triage script, an
  offline rule test harness with recorded fixtures, the English defence guide and a security
  analysis with file:line findings. Use when hunting for ARTEX enrichment probes, self-update
  egress, the recording-proxy CA, the guard audit marker or destructive-command activity, when
  validating these detections against your own logs and captures, or when deciding how to contain
  an ARTEX instance found on your network. Ships no ARTEX code, no agent prompts and no attack
  tooling.
domain: cybersecurity
subdomain: threat-detection
tags:
- artex
- autonomous-attack-detection
- sigma
- suricata
- threat-hunting
- incident-response
mitre_attack:
- T1595
- T1592
- T1105
- T1059
- T1485
- T1561.002
- T1489
- T1557
origin: third-party
vetting: passed
vetted: '2026-11-27'
license: AGPL-3.0
upstream: https://github.com/jiwoochris/artex-global/blob/06b36d7219244c5e2b6467394f60eca160c785cf/docs/defense-en.md
upstream-commit: 06b36d7219244c5e2b6467394f60eca160c785cf
upstream-type: document
---

# Detecting ARTEX autonomous attacks

## Scope

This skill covers detection, validation and hardening on assets that the reader owns or is authorized to defend. The pack ships no ARTEX code, no agent prompts and no attack tooling. Validation uses recorded fixtures and the reader's own data. The harness never generates attack traffic and never runs ARTEX.

ARTEX is an autonomous penetration-testing platform (`github.com/jiwoochris/artex-global`, AGPL-3.0). The upstream README (`README.md:21` at the commit below) states that, in October 2026, several Korean news outlets reported that investigators had found indications that the upstream ARTEX was used in personal-data breaches targeting Korean financial institutions. Treat an ARTEX instance that nobody in your organization authorized as an incident.

## Files in this skill

Paths are relative to this skill folder.

| Path | Content |
|---|---|
| `references/defense-en.md` | Upstream defence guide (English), with links adjusted to this layout |
| `references/artex-security-analysis.md` | Security analysis with `file:line` findings and recommendations |
| `references/sigma/*.yml` | Five atomic Sigma rules |
| `references/sigma/correlation/*.yml` | Four Sigma correlation rules |
| `references/suricata/artex.rules` | Suricata rules, sids 1000001 to 1000003 |
| `references/attack/artex_navigator_layer.json` | ATT&CK Navigator layer of the detection coverage |
| `references/indicators/artex_indicators.csv` | Indicator list with source and rule columns |
| `references/indicators/artex_indicators.misp.json` | The same indicators as a MISP event |
| `scripts/artex_host_triage.py` | Read-only host-triage script (Python standard library) |
| `scripts/tests/` | Rule test harness, recorded event fixtures and offline captures |

## Detect ARTEX activity

Static fingerprints can change at the operator's discretion. The absence of a fingerprint does not prove safety. Combine the signals below with the behavioural detection in `references/defense-en.md` sections 2 and 4.

### Target side

- **Enrichment probes.** ARTEX sends short `GET` requests with the User-Agent `artex-enrich/1.0` and reads only the page title. Deploy `references/sigma/artex_enrich_user_agent.yml` on web server logs and Suricata sids 1000001 and 1000002 on plaintext HTTP or at a TLS-terminating point. The correlation rules `artex_enrich_scan_velocity.yml` and `artex_enrich_fanout.yml` catch the burst and the fan-out across many hosts.
- **Worker WebFetch.** Suricata sid 1000003 matches the `norma/` User-Agent prefix of the norma SDK. Other tools built on that SDK share the prefix, so treat a hit as a supporting clue.
- **Behaviour.** For one source that chains enumeration, probing and authentication attempts in a short window, start from the generic Sigma template in `references/defense-en.md` section 4.2 and tune it to your baseline.

### Host and egress side

- **Recording-proxy CA.** On first start, the recorder writes `<data-dir>/traffic/_ca/mitmproxy-ca-cert.pem`. `references/sigma/artex_recording_proxy_ca.yml` matches the `_ca` and `mitmproxy-ca-cert.pem` pair in file-creation telemetry. A process environment that carries a proxy variable together with a CA variable that points at `mitmproxy-ca-cert.pem` is a stronger tell, and the triage script checks that pair in `/proc`.
- **Self-update egress.** The self-updater sends the User-Agent `artex-selfupdate` and connects only to the hosts on its allow-list (`api.github.com`, `github.com`, `objects.githubusercontent.com`, `release-assets.githubusercontent.com` and `raw.githubusercontent.com`). Deploy `references/sigma/artex_selfupdate_egress.yml` on egress proxy logs. The web UI triggers the release check, so the egress appears when an operator opens the dashboard.
- **Guard audit marker.** ARTEX writes the marker `【ARTEX 平台管控·非目标防御】` to its audit log when its guard blocks a tool call. Deploy `references/sigma/artex_guard_audit_framing.yml` on application logs, and `correlation/artex_guard_block_burst.yml` to separate a live run from a document that quotes the marker.
- **Destructive-command hunting.** `references/sigma/destructive_command_hunting.yml` mirrors the guard deny-list (`rm -rf`, `mkfs`, `DROP DATABASE`, `FLUSHALL` and related commands) on process-creation logs. Administrators run the same commands, so tune an allow-list and treat a hit as a lead. `correlation/artex_guard_marker_then_destructive.yml` raises the priority when the marker and a destructive command appear on one host within 30 minutes.
- **MCP client.** In the MCP `initialize` request, ARTEX identifies as `"clientInfo": {"name": "artex", "version": "0.2"}` and sends `MCP-Protocol-Version: 2025-06-18`. Search the request logs of MCP servers that you operate. The pack ships no rule for this pattern.
- **Notifier webhooks.** ARTEX can post findings to Telegram (`api.telegram.org/bot<token>/sendMessage`), DingTalk, Feishu or WeCom bot webhooks, generic webhooks and email. Hunt for these destinations in egress logs only from hosts that show another ARTEX indicator, because chat-bot webhooks are common in legitimate tooling. The pack ships no rule for this pattern.
- **Listeners and data.** Defaults are the admin UI on port 8787, the recorder on `127.0.0.1:8788`, and a PostgreSQL schema with `exploration_nodes` and `agent_prompts`. The triage script checks the listeners, the data folder, log markers, the schema and process environments.

## Validate the detections

Run the five steps in order. Steps 1 and 2 use the fixtures in this skill. Steps 3 to 5 use your own data.

1. **Lint the Sigma rules and match them against the bundled fixtures.** The harness needs Docker, and network access to PyPI and the image registry. Each suite runs in a container and writes nothing outside its own scratch folder.

   ```bash
   scripts/tests/run-all.sh
   ```

   `PYTHON_IMAGE` and `SURICATA_IMAGE` override the default images. The harness prints `SKIP` for checks that need files this pack does not ship (the ARTEX source tree, the upstream CI workflow and the Korean guide). On a network that cannot reach `d3fend.mitre.org`, the harness excludes the `d3_fendtag` validator and prints `SKIP`. The bundled rules carry no D3FEND tags. Read the summary at the end. A `RESULT: PASS` line means that every suite and gate passed.

2. **Test the Suricata rules offline, first on the bundled captures and then on captures from your own network.** The bundled captures were built offline from synthetic HTTP requests between private addresses. They carry no exploit payload.

   ```bash
   suricata -r scripts/tests/suricata/captures/enrich.pcap -S references/suricata/artex.rules -k none -l /tmp/artex-suricata
   ```

   Expect 35 alerts for sid 1000001 and at least one for sid 1000002 in `/tmp/artex-suricata/eve.json`. `norma.pcap` yields 8 alerts for sid 1000003, and `benign.pcap` yields none. The `-k none` option is needed only for the synthetic captures, whose checksums are not valid. Then replay captures from your own network:

   ```bash
   suricata -r <capture.pcap> -S artex.rules
   ```

3. **Convert the Sigma rules for your SIEM and replay your own logs.** Use `sigma-cli` with the backend of your SIEM, and pass the atomic rules together with the correlation rules, because a correlation rule needs its base rules.

   ```bash
   sigma convert -t splunk --without-pipeline references/sigma/
   ```

   The upstream harness measured whole-tree conversion on `splunk`, `eql` and `loki`. The `lucene` and `kusto` backends convert the atomic rules only. On those products, write the correlations natively. Map the field names (`cs-user-agent`, `c-useragent`, `TargetFilename`, `CommandLine`) to your schema with a processing pipeline. Run each query over a retained window of your own logs and record hits, false positives and tuning changes.

4. **Run the triage script on hosts that you own.** The script is read-only. It prints findings as leads, and a quiet result is not a clean bill of health.

   ```bash
   python3 scripts/artex_host_triage.py --self-test
   ```

   ```bash
   sudo python3 scripts/artex_host_triage.py --data-dir <artex-data-dir> --log /var/log/syslog --log-dir <app-log-dir> --json
   ```

   Run as root to read every `/proc/<pid>/environ`. For a forensic image, pass `--ports-from` and `--proc-from` with captured listings. A DSN in `--pg-dsn` or `ARTEX_PG_DSN` makes the script connect to that database with `psql`. Without a DSN, the script prints the read-only query for you to run.

5. **Map the ATT&CK layer to your log sources and list the coverage gaps.** Load `references/attack/artex_navigator_layer.json` into ATT&CK Navigator. For each technique, mark whether you collect the log source that its rule needs, and list the techniques whose log source you do not collect.

   | Rule | Log source | Techniques |
   |---|---|---|
   | `artex_enrich_user_agent.yml` and its two correlations | web server access logs | T1595, T1592 |
   | `artex_selfupdate_egress.yml` | egress proxy logs | T1105 |
   | `artex_guard_audit_framing.yml` and `artex_guard_block_burst.yml` | application or audit logs | T1059 |
   | `artex_recording_proxy_ca.yml` | file-creation telemetry | T1557 |
   | `destructive_command_hunting.yml` | process-creation logs | T1485, T1561.002, T1489 |
   | Suricata sids 1000001 to 1000003 | network sensor on plaintext HTTP or after TLS termination | T1595, T1592 |

## Decide whether to keep or block

Start with ownership. Ask the asset owner and the security team whether anyone authorized the instance in writing. Without written authorization, handle the finding as an incident and follow the steps below. With authorization, keep the instance only after the hardening in `references/artex-security-analysis.md` (findings F1 to F8) is in place.

Containment for an unauthorized instance:

1. Preserve evidence before any change. Copy the data folder (`traffic/_ca`, `traffic/_index/index.sqlite`, `traffic/_blobs`, `tasks/`, `transcripts/`), the PostgreSQL database and the container logs.
2. Isolate the host at the network layer and stop the ARTEX process or container. Keep the host powered on until memory capture is complete, if your process requires it.
3. Rotate the credentials of every system that the host reached. The recorder stores request and response bodies, which can include those credentials (analysis F1 and F2).

Indicators to block at egress:

- Requests with the User-Agent `artex-selfupdate`, and requests to `/repos/jiwoochris/artex-global/` on `api.github.com` and to `github.com/jiwoochris/artex-global/releases/` at a TLS-inspecting proxy. Do not block the GitHub hosts as a whole.
- Pulls of the image `ghcr.io/jiwoochris/artex-global` at your registry proxy.
- Chat-bot webhook destinations (Telegram, DingTalk, Feishu, WeCom) from the affected host, unless a business owner approved them.
- On inbound web traffic, tag the User-Agents `artex-enrich/1.0` and `norma/` as high risk. Block on them only together with the behavioural rules, because an operator can change them.

Setup token and recording-proxy CA trust:

- The setup token gates the first admin login only. A restart without `ARTEX_SETUP_TOKEN` draws a new random token, and a new `ARTEX_SETUP_TOKEN` value replaces a pinned one. After setup, change the admin password through the UI or `reset-password.sh`. The password change invalidates every issued session token (analysis F6 and F7).
- ARTEX passes its CA to worker tools through environment variables. Search the system trust store, the browser stores and the environment of running processes for `mitmproxy-ca-cert.pem`, and remove every trust entry that you did not add on purpose. For an authorized instance, stop ARTEX, preserve the old `_ca` folder, delete the folder and start ARTEX again, so that the recorder generates a new CA.

Escalate to incident response when any of the following holds:

- Nobody authorized the instance.
- `artex_guard_marker_then_destructive` fires, or a destructive command ran on a production host near an ARTEX run.
- The recorded traffic store holds credentials, tokens or personal data of your organization or its customers.
- Enrichment fan-out, self-update egress or the MCP client identity appears from a host that should not run ARTEX.

For incidents in Korea, `references/defense-en.md` section 7 lists the official channels and the statutory reporting deadlines.

## Limits

- The rules rest on fingerprints in the ARTEX source at commit `06b36d7219244c5e2b6467394f60eca160c785cf`. A later ARTEX version can change them.
- The harness checks that the rules and the bundled fixtures agree. A tuning change still needs validation on your own logs (step 3).

## License

AGPL-3.0, from `jiwoochris/artex-global` at commit `06b36d7219244c5e2b6467394f60eca160c785cf`. The `LICENSE` file in this folder holds the license text. `NOTICE` in the pack folder lists the files that prompt-orchestrator modified.
