# 2026-06-29 burp-mcp-full Full Test and Fixes

## Scenario classification
BurpSuite extension development/testing

## Target overview
A full runtime availability test of the burp-mcp-full extension (Burp Suite Professional MCP Full Control, 63 tools) that found and fixed 3 bugs + 1 race condition in the bridge layer.

## Complete execution chain

1. Static verification: checked the consistency of the 63 tools across the Java dispatch table / getToolList() / bridge buildToolDefinitions
2. Build: build.bat automates fat-jar packaging (JDK 21, montoya-api 2025.5, gson 2.11.0, nanohttpd 2.3.1)
3. Load: loaded the extension in Burp Suite Professional 2026.4.2 and confirmed [MCP] Server started
4. Runtime tests: called 127.0.0.1:9876 directly through a node http client in 5 batches:
   - Batch 1: 30 read-only/encoding/query tools (no side effects)
   - Batch 2: network sending (send_request / repeater / intruder, target scanme.nmap.org)
   - Batch 3: 7 Intruder variants (attack/async/wordlist/pitchfork/cluster_bomb/battering_ram/with_options, small-range enumeration)
   - Batch 4: Scope/configuration/rules/handler/add_issue/compare
   - Batch 5: crawl + proxy_clear
5. Found and fixed 3 bugs; regression verification passed

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| `scan()` request_count always 0 | AuditConfiguration does not accept a seed URL, and the code missed calling addRequest | Parse host/port/path from the url, build a GET HttpRequest and feed it to activeAudit.addRequest() | 2h (including verification) |
| `send_to_intruder()` reports HttpRequest must have an HttpService | Used the HttpRequest.httpRequest(raw) overload without a service | Added buildRequestWithService(): parse host/port/https from the Host header with a regex → HttpService, using the httpRequest(HttpService, raw) overload | 20min |
| `set_upstream_proxy()` NPE on missing parameters | params.get("proxy_host") returns null → .getAsString() NPE | Added a null check: if (!params.has("proxy_host")) return a clear error | 5min |
| mcp-bridge.js API async race: the 4th of 4 quick requests lost its response | process.exit(0) on stdin close killed unfinished HTTP requests | pending counter + stdinClosed flag → exit only after every request completes | 1h (including mock tests) |
| curl HTTP_CODE=000 cannot probe the port | curl is blocked by the sandbox on this machine | Probe with the node http module instead | 5min |
| Wrong guess of the Montoya API Audit package path | Inferred from the online javadoc that Audit lives in the scanner package | Decompiled the real montoya-api-2025.5.jar with javap and confirmed it lives in the scanner.audit package | 30min |
| File encoding broke Edit tool matching | Chinese content in UTF-8 with BOM displayed with mismatched encoding in the terminal | Did the replacement with Python using utf-8-sig | 10min |

## Toolchain findings

- In montoya-api 2025.5, Audit is `burp.api.montoya.scanner.audit.Audit` (not scanner.Audit)
- The AuditConfiguration factory methods do not accept seed URLs; seeds must be fed through Audit.addRequest(HttpRequest)
- The HttpRequest.httpRequest(raw) overload without a service is enough for Repeater, but Intruder requires an HttpService
- Intruder.sendToIntruder(HttpRequest) requires the request to have a service attached
- major()/minor()/build() of api.burpSuite().version() went from deprecation to removal in 2025.5; use buildNumber()/edition()/toString() instead
- send_request goes through http.sendRequest() and does not enter the proxy history
- curl on this machine is blocked by the sandbox; probe with node http
- The IDA MCP port is not fixed at 13337 (it increments between instances), but the Burp MCP port is configurable through a system property/env and fixed

## Key code/commands

### Full test script pattern
```javascript
const http = require('http');
function call(tool, params={}, timeoutMs=30000) {
  return new Promise((resolve) => {
    const body = JSON.stringify({tool, params});
    const req = http.request({hostname:'127.0.0.1',port:9876,path:'/',method:'POST',
      headers:{'Content-Type':'application/json','Content-Length':Buffer.byteLength(body)}}, (res)=>{
      let d=''; res.on('data',c=>d+=c); res.on('end',()=>{ try{resolve(JSON.parse(d));}catch(e){resolve({__raw:d.slice(0,200)});} });
    });
    req.on('error', e => resolve({__err: e.message}));
    req.on('timeout', () => { req.destroy(); resolve({__timeout:true}); });
    req.setTimeout(timeoutMs);
    req.write(body); req.end();
  });
}
```

### buildRequestWithService (core fix)
```java
private HttpRequest buildRequestWithService(String rawRequest) {
    java.util.regex.Matcher m = java.util.regex.Pattern.compile(
            "(?im)^Host:\\s*([^:\r\n]+)(?::(\\d+))?\\s*$").matcher(rawRequest);
    if (!m.find()) return HttpRequest.httpRequest(rawRequest);
    String host = m.group(1).trim();
    boolean isHttps = rawRequest.contains("https://") || rawRequest.contains(":443");
    int port = m.group(2) != null ? Integer.parseInt(m.group(2))
              : (isHttps ? 443 : 80);
    HttpService svc = HttpService.httpService(host, port, isHttps);
    return HttpRequest.httpRequest(svc, rawRequest);
}
```

### Bridge layer race condition fix (mcp-bridge.js)
```javascript
let pending = 0;
let stdinClosed = false;
rl.on('line', async (line) => { ... pending++; ... finally { pending--; if (stdinClosed && pending === 0) process.exit(0); } });
rl.on('close', () => { stdinClosed = true; if (pending === 0) process.exit(0); });
```

### scan() seed fix
```java
// Build a GET seed request from the URL and feed it to the audit
java.net.URL u = new java.net.URL(url);
String host = u.getHost();
boolean isHttps = "https".equalsIgnoreCase(u.getProtocol());
int port = u.getPort() > 0 ? u.getPort() : (isHttps ? 443 : 80);
String path = (u.getPath() == null || u.getPath().isEmpty()) ? "/" : u.getPath();
String pathQuery = u.getQuery() != null ? path + "?" + u.getQuery() : path;
HttpService svc = HttpService.httpService(host, port, isHttps);
HttpRequest seedReq = HttpRequest.httpRequest(svc,
    "GET " + pathQuery + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\n\r\n");
activeAudit.addRequest(seedReq);
```

## Improvement suggestions for this package

- The routing matrix already covers BurpSuite MCP, no change needed
- `burpsuite-mcp-guide.md` gained a changelog entry (3 fixes + the bridge layer + full verification results)
- The tool table was updated for Scanner (new mode parameter for scan) and Intruder (Host header requirement of send_to_intruder)
- No new bootstrap entry needed (the build script build.bat is self-contained)
- The IDA MCP port is not fixed; note it in the MCP service management table

## Reusable patterns/script snippets

- The full availability test script pattern for 63 tools (see the key code above). Applies to regression tests of any HTTP-based MCP extension.
- The buildRequestWithService pattern: parse the HttpService from the Host header. Applies to every Montoya API scenario that must build HttpRequest + HttpService from a raw request.

## Evolution actions
- [x] Updated the routing matrix (routing already covered, no change needed)
- [ ] Updated tool-index (uses .template, no change needed)
- [ ] Updated bootstrap-manifest (no new tools)
- [x] Updated sub-skill documentation (changelog appended to burpsuite-mcp-guide.md)
- [x] Added a pitfall record (this entry)
- [ ] No update needed

## Environment information
- OS: Windows 11 Pro for Workstations 10.0.26200
- Tool versions: JDK 21.0.11+10 / Burp Suite Professional 2026.4.2 (20260402000047704)
- Target platform: montoya-api 2025.5 / gson 2.11.0 / nanohttpd 2.3.1
- Test target: scanme.nmap.org (authorized test site)

## Redaction requirements
The test target is the public test site scanme.nmap.org, so no redaction is needed. No real domains/IPs/tokens/usernames are included.

## Index sync (last step before submission)

After writing this journal, you must update `_index.md` in sync:

1. Add a row (with date and keywords) to the matching subsection of "By scenario"
2. Update the counts and the "last updated" date in "Cumulative statistics"

---
<!-- [Community contribution] When done, ask the user whether to open a PR to the main repository. The process is in CONTRIBUTE-BACK.md -->
