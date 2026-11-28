# ARTEX security analysis for defenders

This analysis reviews ARTEX (`jiwoochris/artex-global`, AGPL-3.0) at commit `06b36d7219244c5e2b6467394f60eca160c785cf`. It serves two readers. The first reader finds an ARTEX instance on a network that they own or are authorized to defend. The second reader runs ARTEX for an authorized internal test and wants to harden the deployment. Every `file:line` reference points at the upstream commit above. This pack ships no ARTEX source code.

The review covers the five areas that the pack scope names (self-update, the recording proxy and its CA, the default bind address, the Docker install path, and the authentication and setup-token handling). It also lists the MCP client and notifier patterns that a defender can observe.

## Summary

| ID | Severity | Finding | Main reference |
|---|---|---|---|
| F1 | High | The recording proxy accepts every upstream TLS certificate | `traffic/traffic.go:206` |
| F2 | High | Recorded traffic and the CA folder use world-readable modes | `traffic/traffic.go:177-178`, `traffic/traffic.go:552` |
| F3 | Medium | Self-update trusts one GitHub release and runs the staged binary before the swap | `selfupdate/stage.go:66`, `selfupdate/bootstrap.go:184` |
| F4 | Medium | The container image binds every interface, and the local install publishes PostgreSQL | `Dockerfile:45`, `install.sh:70` |
| F5 | Medium | The installer pipes an unpinned Docker script into `sh` and grants the docker group | `install.sh:22-23` |
| F6 | Medium | The first-run setup token goes to the server log in plain text | `server/auth.go:292` |
| F7 | Low | The session token is accepted in the URL query string | `server/auth.go:445-452` |
| F8 | Low | The failed-login limiter clears its whole table at 10,000 entries | `server/auth.go:372` |

## F1. The recording proxy accepts every upstream TLS certificate (High)

Evidence:

- `traffic/traffic.go:204-208` starts the go-mitmproxy recorder with `SslInsecure: true` and `CaRootPath` under `_ca`.
- `agent/worker.go:204-220` (`proxyEnv`) gives every worker tool `HTTP_PROXY` and `HTTPS_PROXY` set to the recorder, plus `SSL_CERT_FILE`, `CURL_CA_BUNDLE`, `REQUESTS_CA_BUNDLE`, `GIT_SSL_CAINFO` and `NODE_EXTRA_CA_CERTS` set to the recorder CA.

The worker tools trust the recorder CA. The recorder does not verify the certificate of the real upstream server. A party on the network path between the ARTEX host and its target can therefore present any certificate and read or change the worker traffic. That traffic can carry credentials and session tokens that the run collects.

Defender impact: an ARTEX host holds and relays target secrets with weak transport protection. Treat a discovered ARTEX host as a credential store.

Recommendations:

1. Upstream fix: set `SslInsecure` to false so that the recorder verifies upstream certificates, and add an explicit per-target exception only for lab targets with self-signed certificates.
2. Deployment: run ARTEX only on an isolated segment, so that no untrusted party sits on the path to the target.
3. Response: after you find an unauthorized ARTEX host, rotate the credentials of every system that the host reached.

## F2. Recorded traffic and the CA folder use world-readable modes (High)

Evidence:

- `traffic/traffic.go:177-178` creates the traffic folder, `_index`, `_blobs` and `_ca` with mode `0o755`.
- `traffic/traffic.go:545-552` writes each recorded body to `_blobs/sha256/<xx>/<hash>.bin` with mode `0o644`.
- `traffic/traffic.go:189-194` keeps the exchange index in `_index/index.sqlite`.
- The CA private key file is written by go-mitmproxy v1.9.2 (`go.mod:11`). (unverified) This review did not read the library code, so the key file mode is not confirmed.

On a shared host, a local user can read recorded request and response bodies. The bodies can hold target credentials, tokens and personal data.

Recommendations:

1. Upstream fix: create the folders with `0o700` and the files with `0o600`, and encrypt the blob store at rest.
2. Deployment: run ARTEX under a dedicated account on a host with no other users.
3. Response: on a suspected host, collect the data folder as breach evidence before you remove it. The triage script reports the CA, the index and the blob store (`scripts/artex_host_triage.py --data-dir <dir>`).

## F3. Self-update trusts one GitHub release and runs the staged binary before the swap (Medium)

Evidence:

- `selfupdate/github.go:19` hard-codes the release repository `jiwoochris/artex-global`.
- `selfupdate/github.go:27-33` limits update traffic to `api.github.com`, `github.com`, `objects.githubusercontent.com`, `release-assets.githubusercontent.com` and `raw.githubusercontent.com`. `selfupdate/github.go:81-89` rejects non-HTTPS URLs and hosts outside that list, also on redirects.
- `selfupdate/stage.go:66` and `selfupdate/stage.go:131` fetch `SHA256SUMS` from the same release as the binary. `selfupdate/stage.go:90-92` compares the download with that file.
- `selfupdate/stage.go:99` calls `smokeTest`, and `selfupdate/bootstrap.go:177-184` executes the staged binary with `-h` before the swap.
- `selfupdate/github.go:101` and `selfupdate/stage.go:227` send the User-Agent `artex-selfupdate`.
- `server/update.go:95-120` queries the latest release through a cache when the web UI asks for the update state.

The host allow-list and the checksum protect against transport tampering. Both artifacts come from the same release, so the checksum gives no protection when the release account is compromised. No release signature exists. A compromised release runs code on each updating host during the smoke test.

Recommendations:

1. Upstream fix: sign releases (for example with cosign or minisign) and verify the signature with a pinned public key before the smoke test.
2. Deployment: pin a version and update by hand from a verified artifact. Keep the selfupdate checks enabled when automatic update is used.
3. Detection: alert on the User-Agent `artex-selfupdate` at egress with `references/sigma/artex_selfupdate_egress.yml`. The web UI triggers the check, so the egress appears when an operator opens the dashboard.

## F4. The container image binds every interface, and the local install publishes PostgreSQL (Medium)

Evidence:

- `cmd/artex/main.go:55` sets the server default to `127.0.0.1:8787`, and `cmd/artex/main.go:57` sets the recorder default to `127.0.0.1:8788`.
- `Dockerfile:43` exposes 8787 and 8788, and `Dockerfile:45` starts the server with `-addr :8787 -proxy :8788` inside the container.
- `docker-compose.yml:46` publishes 8787 on `${ARTEX_BIND:-127.0.0.1}`, and `docker-compose.yml:47` publishes 8788 on `127.0.0.1`.
- `install.sh:70` starts PostgreSQL with `-p 5432:5432`, and `install.sh:73` sets `DB_SSL=disable`.

The compose file keeps both ports on loopback by default. A plain `docker run -p 8787:8787 -p 8788:8788` of the same image publishes both ports on every host interface, because Docker binds a published port on all interfaces when no address is given. Port 8788 then serves an open forward proxy that decrypts TLS (F1). The local install path publishes the database that stores the asset graph and the findings on every interface, without TLS.

Recommendations:

1. Deployment: use the compose file, keep `ARTEX_BIND` at `127.0.0.1`, and reach the UI through an SSH tunnel or an authenticated reverse proxy. Publish PostgreSQL on `127.0.0.1` only.
2. Upstream fix: start the image with `-proxy 127.0.0.1:8788` and publish the database on loopback in `install.sh`.
3. Detection: on hosts you own, look for listeners on 8787 and 8788 with the triage script, and for a PostgreSQL schema with `exploration_nodes` and `agent_prompts` (indicator `postgres-exploration-schema`).

## F5. The installer pipes an unpinned Docker script into `sh` and grants the docker group (Medium)

Evidence:

- `install.sh:21` asks whether to install Docker, with "y" as the default answer.
- `install.sh:22` runs `curl -fsSL https://get.docker.com | sh`.
- `install.sh:23` runs `sudo usermod -aG docker "$USER"`.

The script from `get.docker.com` is neither pinned nor verified before it runs. Membership in the docker group gives root-equivalent control of the host.

Recommendations:

1. Deployment: install Docker from the distribution packages or the vendor repository with signed packages before running ARTEX, and answer "n" at the prompt.
2. Deployment: run Docker commands through `sudo` instead of adding the account to the docker group, or use rootless Docker.
3. Detection: the `curl ... | sh` pattern is generic. Hunt for it in process-creation logs as a lead, not as an ARTEX fingerprint.

## F6. The first-run setup token goes to the server log in plain text (Medium)

Evidence:

- `server/auth.go:42` sets the token length to 32, and `server/auth.go:107` draws the characters with `crypto/rand`.
- `server/auth.go:286-292` generates the token when `ARTEX_SETUP_TOKEN` is unset and writes it to the log at `server/auth.go:292`.
- `server/auth.go:281-283` uses `ARTEX_SETUP_TOKEN` when set and does not print the value.
- `server/auth.go:302` compares tokens in constant time, and `server/auth.go:433-440` warns when the server listens beyond loopback before setup.
- `install.sh:57` tells the operator to read the token with `docker compose logs artex | grep -F '[auth]'`.

Until the admin password is set, the token from the log completes the first-run setup. Container logs often reach a log shipper or a SIEM. A reader of those logs can take over a reachable instance before its owner finishes setup.

Recommendations:

1. Deployment: set `ARTEX_SETUP_TOKEN` from a secret store, or set `ARTEX_ADMIN_PASSWORD`, so that no token reaches the log. Finish setup before you change `ARTEX_BIND`.
2. Rotation: the token lives in process memory. A restart without `ARTEX_SETUP_TOKEN` draws a new token. A new value of `ARTEX_SETUP_TOKEN` replaces a pinned token. After setup, the token no longer applies.
3. Detection: keep `[auth]` lines out of shared log indexes, or restrict access to them.

## F7. The session token is accepted in the URL query string (Low)

Evidence:

- `server/auth.go:445-452` reads the token from the `Authorization` header, the `artex_token` cookie or the `token` query parameter. The query form serves server-sent events.
- `server/auth.go:27` sets the token lifetime to seven days.
- `server/auth.go:139-152` derives the signing key from the stored password hash, so a password change invalidates every earlier token.

A token in a URL can reach proxy logs, access logs and the `Referer` header. The token stays valid for seven days.

Recommendations:

1. Upstream fix: issue a short-lived, single-purpose ticket for the event stream.
2. Response: after a suspected leak, change the admin password (through the UI or `reset-password.sh`). The change invalidates every issued token. Deleting `jwt.key` (`server/auth.go:25`) also invalidates every issued token, at the next start.

## F8. The failed-login limiter clears its whole table at 10,000 entries (Low)

Evidence:

- `server/auth.go:337-340` allows five free failures per client address and then a doubling cooldown up to ten minutes.
- `server/auth.go:370-373` replaces the whole client table when the table holds 10,000 entries.

A client that sends failures from many source addresses can clear the cooldown of every other client.

Recommendation: evict the oldest entries instead of the whole table, and keep the admin UI off public networks (F4).

## Observable patterns without a shipped rule

The pack ships no Sigma or Suricata rule for the patterns below. Use them as hunting leads.

| Pattern | Evidence | Where to look |
|---|---|---|
| MCP client identity `"clientInfo": {"name": "artex", "version": "0.2"}` in the MCP `initialize` request | `mcphttp/client.go:250` | Request logs of MCP servers that you operate |
| MCP header `MCP-Protocol-Version: 2025-06-18` and the `Mcp-Session-Id` header | `mcphttp/client.go:31`, `mcphttp/client.go:381`, `mcphttp/client.go:437` | Egress or reverse-proxy logs with header capture |
| Notifier egress to `api.telegram.org/bot<token>/sendMessage` | `notify/telegram.go:93` (base URL), `notify/telegram.go:97` (path) | Egress proxy logs from a host that also shows other ARTEX indicators |
| Notifier egress to DingTalk, Feishu or WeCom bot webhooks, and to generic webhooks | Operator-configured URLs, signed for DingTalk and Feishu (`notify/dingtalk.go:113-123`, `notify/feishu.go:92-94`) | Egress proxy logs, correlated with the indicators above |

At dial time, the notifier refuses loopback, link-local, unspecified and multicast destinations and allows RFC 1918 private addresses on purpose (`notify/http.go:47-55`, `notify/http.go:66`). Chat-bot webhooks are common in legitimate tooling, so treat a hit as a lead only when another ARTEX indicator appears on the same host.

## Method and limits

- The reviewer read the cited files at the commit above and ran no ARTEX code.
- Line numbers apply to that commit only.
- The review did not cover `web/` dependencies, `guard/` bypass resistance or the CI workflows. These areas remain open.
