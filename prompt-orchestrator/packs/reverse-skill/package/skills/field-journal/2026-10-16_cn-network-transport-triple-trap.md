---
name: cn-network-transport-triple-trap
description: 'Triple transport pitfall when accessing overseas APIs from within China: Node fetch ignores the proxy, the CF TLS fingerprint, execFile corrupting the UTF-8 request body through GBK'
metadata:
  type: project
---

# Triple Transport Layer Pitfall When Accessing Overseas APIs from Within China

**Date**: 2026-10-16
**Scenario category**: traffic capture analysis / other (network transport layer)
**Target**: `{target_domain}` (an overseas API, accessed through a local proxy)

## Background

This machine cannot reach the overseas target directly and must go through a local proxy (`127.0.0.1:{port}`). In the same period,
`curl` requests consistently succeeded, while native Node `fetch` reported `fetch failed`. Checking one by one confirmed **three independent problems stacked together**.

## Three pitfalls and their criteria

### Pitfall 1: Node fetch (undici) **does not read** the `HTTPS_PROXY` / `HTTP_PROXY` environment variables **by default**

| Call method | Reads the proxy environment variables |
|---|---|
| `curl` | Yes |
| Node `fetch` | **No, not by default** → `fetch failed` |

**Fix (Node 24+)**: `NODE_USE_ENV_PROXY=1 node app.js` or `node --use-env-proxy app.js`

### Pitfall 2: even with the proxy configured, the Node undici **TLS fingerprint does not pass Cloudflare** (403 Just a moment)

At the same moment `curl` returned 200, which shows it is not an IP or proxy problem but the **client fingerprint**.
⇒ **Conclusion: for CF-protected overseas endpoints, do not use Node fetch; use curl directly.**

### Pitfall 3: on Windows, the **arguments of `execFile('curl', args)` are converted through the system code page (GBK/CP936)**, corrupting UTF-8 request bodies

The symptoms are highly misleading:

| Request body content | Result |
|---|---|
| Pure ASCII | **Success** |
| Contains Chinese | Upstream returns `illegal parameter` (the server fails to decode as UTF-8) |
| **Contains Korean** | **"Unexpected" success**: GBK cannot represent Korean, so it is replaced with `?` and falls back to ASCII |

**Fix**: always write the request body to a **temporary file** and use `--data-binary @<file>` (the file written as UTF-8);
**do not** use `-d '<json>'`. Use a file even when the body is ASCII-only today, so the pitfall does not return the day an upper layer adds Chinese.

## Recommended transport layer shape (copy as is)

```js
// use curl as the transport layer; reasons and key points:
//  ① DNS pollution / proxy: curl reads the system proxy, Node fetch does not
//  ② CF challenge: the Node TLS fingerprint is blocked, curl passes
//  ③ Chinese body: arguments on the command line are corrupted by GBK ⇒ write the body to a temporary file + --data-binary @file
//  ④ windowsHide: true, see the "side pitfall" below
const args = [
  '-s', '--compressed', '-m', String(sec), '-A', UA,
  '-X', method, '-w', '\n__HTTP__%{http_code}',
];
if (proxy) args.push('--proxy', proxy);
args.push('--data-binary', '@' + tmpFile);   // ← the body must go through a file
args.push(url);
execFile('curl', args, { windowsHide: true, maxBuffer: 32 * 1024 * 1024 }, cb);
```

**Side pitfall**: on Windows, `execFile` / `spawn` default to **`windowsHide: false`** (note that `exec` defaults to true),
and this machine's default terminal is Windows Terminal ⇒ **every curl call pops up a terminal window and steals the foreground**.
In high-frequency polling this looks like "windows keep popping up and closing". Adding `windowsHide: true` fixes it completely without affecting functionality.

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| Every Node request reports `fetch failed` | undici does not read the proxy environment variables | `NODE_USE_ENV_PROXY=1` | 20 min |
| Still 403 with the proxy configured | The undici TLS fingerprint is blocked by CF | Switch to curl | 25 min |
| POSTs with Chinese report invalid parameters, while ones with Korean succeed | Command line arguments converted through GBK corrupt UTF-8 | Body through a temporary file + `--data-binary @file` | 40 min |
| Terminal windows pop up wildly during frequent requests | `execFile` defaults to `windowsHide:false` | Add `windowsHide:true` | 15 min |

## Reusable patterns

**"Try each of two clients once at the same moment" is the fastest layering criterion**:
`curl` succeeds while Node fails ⇒ the problem is in the **client stack** (proxy / TLS fingerprint), not the network or the target;
only when both fail ⇒ is it a network / target problem. Do not suspect DNS right away.

**"The error changes with the language of the data" is a strong signal of an encoding problem**:
ASCII succeeds / Chinese fails / Korean "unexpectedly" succeeds; this combination basically identifies **code page conversion corrupting UTF-8** directly.

## Improvement suggestions for this package

- The `bootstrap` and documentation layers should add a **general hint**: in the "Windows + within China + overseas API" scenario,
  default to curl as the transport layer and set `windowsHide` explicitly.
- If package examples use Node fetch to reach overseas endpoints, the documentation should state the two limits `NODE_USE_ENV_PROXY` and the CF fingerprint.

## Evolution actions

- [x] Added pitfall records
- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation

## Environment information

- OS: Windows 10.0.22631
- Tool versions: Node v26.7.0 / curl (system version) / PowerShell 5.1
- Target platform/version: overseas API (HTTPS, protected by CDN/WAF)

---

<!-- [Evolution statistics] New patterns this time: 3 (proxy / fingerprint / encoding) | Toolchain problems fixed this time: 3 -->
