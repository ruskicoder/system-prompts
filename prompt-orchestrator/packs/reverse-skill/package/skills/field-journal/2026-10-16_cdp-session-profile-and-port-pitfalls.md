---
name: cdp-session-profile-and-port-pitfalls
description: 'Two operational pitfalls of CDP debugging sessions: a profile in the temporary directory gets cleaned by the system and the login state is lost; a port in LISTENING state is not necessarily CDP'
metadata:
  type: project
---

# Two Operational Pitfalls of CDP Debugging Sessions

**Date**: 2026-10-16
**Scenario category**: other (operating a browser forensics environment)

## Background

Digging into "post-login features" depended on a Chrome with a debugging port. CDP dropped midway, and the investigation exposed two pitfalls,
neither of them code problems but **environment criterion** problems.

## Pitfall 1: the debugging Chrome profile lives in the system temporary directory → it gets cleaned, and the login state disappears with it

This project's original launch logic used `path.join(os.tmpdir(), "rea-chrome-cdp")`.
**After the system cleans the temporary directory, that profile is gone**, and **the user's earlier login state in that window disappears with it**.

**Symptom**: the CDP port disappears → relaunch → the page redirects to the login page → `me_status: 401`.

**Fix**:
- A debugging profile that must **keep the login state long term** should not live in `%TEMP%`; put it in a **stable directory** (such as `data/` inside the project or `%LOCALAPPDATA%`).
- If a temporary profile is unavoidable, accept that "each restart needs a new login", and **explicitly confirm the login state** in the flow before starting work.

**Criterion**: before starting, `GET /api/me` (or an equivalent identity endpoint); `401` means the login state is gone, so do not rush to dig further.

## Pitfall 2: a port in LISTENING **does not mean** it is a CDP endpoint

In the test, **9222 was LISTENING**, which led to the wrong verdict "a debugging port is already running" and direct reuse;
the result was that `/json/version` **returned empty** and CDP calls failed with `Unexpected end of JSON input`.

**Cause**: 9222 was held by **the everyday Chrome main process** (which provides no debugging interface).

**Criteria (both must hold)**:
```bash
# ① the port is listening
netstat -ano | grep ":9222.*LISTENING"
# ② and it really is CDP: check for the Browser field
curl -s http://127.0.0.1:9222/json/version     # expect: {"Browser":"Chrome/...","Protocol-Version":"1.3",...}
```
**Checking only ① leads to a wrong verdict**. If ② returns empty / non-JSON ⇒ it is not CDP.

**Why not just switch ports**: you cannot look only at the default port; when the debugging port is taken, Chrome **moves on** (9222→9223…),
so the right approach is to **scan a range for the one that really answers CDP** rather than fixating on 9222.

## Appendix: the right way to launch a debugging Chrome with a login state

```bash
chrome.exe --remote-debugging-port=<port> \
           --user-data-dir=<a stable directory, not %TEMP%> \
           --no-first-run --no-default-browser-check \
           --new-window <target URL>
```
- **A separate `--user-data-dir` is mandatory**: an already running Chrome swallows the debugging arguments, and the port does not take effect.
- **To launch from the Windows command line** use `cmd /c start "" "chrome.exe" ...`; `Start-Process` in some shells
  or commands containing backticks easily break on paths/arguments (in the test it reported a shell syntax error).

## Collaboration discipline (observations together with the user)

"Open the window first, then ask the person to act": the observation window is **live**, and actions that already happened cannot be captured afterwards.
So **open the window first**, tell the user in the same reply "starting now, please act in the same tab",
and read the results in one go after the user replies that they are done. The reverse order (talk first, open later) puts the user's actions outside the window and wastes a round.

## Evolution actions

- [x] Added pitfall records

## Environment information

- OS: win32 x64 | Browser: Chrome 155

---

<!-- [Evolution statistics] New patterns this time: 2 (profile persistence criterion / CDP port double criterion) | Toolchain problems fixed this time: 2 -->
