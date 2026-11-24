# BurpSuite MCP Full Control Extension

Full control of all core BurpSuite features over the MCP protocol. Cross-platform support for Windows / Linux (Kali) / macOS.

## Quick start

### 1. Build the extension

**Windows**:
```cmd
cd burp-mcp-full
build.bat
```

**Linux / Kali / macOS**:
```bash
cd burp-mcp-full
chmod +x build.sh
./build.sh
```

The build script automatically detects JDK 21+, downloads the dependencies (montoya-api 2025.5 / gson / nanohttpd), compiles, packs the extension descriptor (`META-INF/extensions/burp-extension.properties`) into the jar and builds a fat jar. No Gradle needed.

Output: `build/libs/burp-mcp-full.jar`.

### 2. Load into Burp

```
Burp Suite → Extensions → Add → Java → choose build/libs/burp-mcp-full.jar
```

After loading, the Output tab shows:
```
[MCP] Server started on http://127.0.0.1:9876
```

### 3. Authentication (enabled by default since v2)

At start, the extension generates a random token and writes it to `~/.burp-mcp-token`. `mcp-bridge.js` reads that file automatically and sends the `Authorization: Bearer <token>` header with every request, so no manual configuration is needed.

When a fixed token is needed (for example several clients share it), use:
- JVM option: `-Dburp.mcp.token=<token>`
- Environment variable: `BURP_MCP_TOKEN=<token>` (also used on the bridge side)

Every `/health`, `/tools` and `/` (POST) request must carry that header, otherwise the response is 403. CORS is narrowed to allow only the `http://127.0.0.1` origin.

### 4. Configure the MCP client

In any MCP client (Claude Code / Kiro / Cursor / Cline / Windsurf), add (stdio mode):

```json
{
  "mcpServers": {
    "burpsuite": {
      "command": "node",
      "args": ["<path of this directory>/mcp-bridge.js"]
    }
  }
}
```

### 5. Start using it

Tell the AI: "Analyze the requests in the Burp proxy history and find security vulnerabilities"

## Feature list

The extension exposes 78 tools. Common categories follow (for the full list see `getToolList()` in `src/main/java/com/burpmcp/McpHttpServer.java`, or call `GET http://127.0.0.1:9876/tools` with the Authorization header):

| Category | Tools |
|------|------|
| Proxy history | `proxy_history`, `proxy_detail`, `proxy_history_filtered`, `proxy_websocket`, `proxy_clear`, `search_history`, `highlight`, `annotate`, `compare` |
| Send requests | `send_request`, `send_to_repeater`, `repeater_send`, `repeater_modify_send`, `send_to_intruder` |
| Intruder attacks | `intruder_attack`, `intruder_attack_async`, `intruder_attack_wordlist`, `intruder_pitchfork`, `intruder_cluster_bomb`, `intruder_battering_ram`, `intruder_with_options`, `payload_process` |
| Scanning / crawling | `scan` (active/passive), `scan_active`, `scan_results`, `scan_issue_detail`, `crawl`, `sequencer` |
| Scope / Sitemap | `sitemap`, `target_info`, `get_scope`, `add_to_scope`, `remove_from_scope`, `add_issue` |
| Interception / rules | `intercept_toggle`, `register_http_handler`, `remove_http_handler`, `register_proxy_rule`, `remove_proxy_rule` |
| Encoding and decoding | `encode`, `decode`, `convert_request`, `export_request`, `generate_csrf_poc`, `extract_from_response`, `token_analysis` |
| Collaborator | `collaborator_generate`, `collaborator_poll` |
| Configuration | `export_config`, `import_config`, `set_upstream_proxy`, `set_dns_override`, `set_http2`, `cookie_jar`, `save_project`, `burp_version`, `extensions_list`, `log` |

> Scanning and crawling (`scan`, `scan_active`, `crawl`) need **Burp Professional**. The Community edition returns an explicit license error. Manually added issues (`add_issue`) are written to the Site map.

## Key tool parameters

### `intruder_attack`: automated enumeration attack

| Parameter | Description |
|------|------|
| `url_template` | URL template; the placeholder defaults to `@@` |
| `placeholder` | Placeholder string (default `@@`) |
| `from` / `to` | Enumeration start and end values |
| `pad_digits` | Number of zero-padding digits (0 means no padding) |
| `method` | HTTP method (default GET) |
| `body_template` | Request body template (with placeholder) |
| `headers` | Request header object |
| `success_length_not` | Hit condition: response length ≠ this value |
| `success_contains` | Hit condition: response body contains this string |

### `scan`: start an audit

| Parameter | Description |
|------|------|
| `url` | Target URL (required, added to scope automatically) |
| `mode` | `active` (default) or `passive` |

After start, poll issues and the active audit state (request count, error count, insertion point count) with `scan_results`.

### `register_proxy_rule`: proxy request interception rule

| Parameter | Description |
|------|------|
| `url_contains` | Hit condition: the URL contains this string |
| `intercept` | `true` intercepts / `false` lets it pass (default true) |

Deregister a rule with `remove_proxy_rule` (based on `Registration.deregister()`, which really unloads it from Burp).

## Call examples

### View the proxy history
```json
POST http://127.0.0.1:9876
{"tool": "proxy_history", "params": {"limit": 10, "url_filter": "personalblog"}}
```

### Send a request
```json
POST http://127.0.0.1:9876
{"tool": "send_request", "params": {"method": "GET", "url": "https://example.com/api/test"}}
```

### Automated enumeration attack (core feature)
```json
POST http://127.0.0.1:9876
{
  "tool": "intruder_attack",
  "params": {
    "url_template": "https://target.com/api/verify?code=@@",
    "method": "POST",
    "from": 0,
    "to": 999999,
    "pad_digits": 6,
    "success_length_not": 176,
    "headers": {"User-Agent": "Mozilla/5.0"}
  }
}
```

### Toggle interception
```json
POST http://127.0.0.1:9876
{"tool": "intercept_toggle", "params": {"enable": false}}
```

## Port configuration

Listens on `127.0.0.1:9876` by default. To change it (for example when it conflicts with the official PortSwigger MCP extension on the same port):

1. **Burp side**: pass the JVM option `-Dburp.mcp.port=9877` when starting Burp, or set the environment variable `BURP_MCP_PORT=9877`.
2. **Bridge side**: set the environment variables `BURP_MCP_PORT=9877` and `BURP_MCP_HOST=127.0.0.1` in the MCP client configuration.

Both sides must use the same port. If Burp is not running or the port is unreachable, the bridge returns explicit connection error guidance on `tools/list` and `tools/call`.

## Troubleshooting

| Symptom | Check |
|------|------|
| No "[MCP] Server started" in the Burp Output | The port is taken or the extension failed to load; check the Burp Errors panel |
| The MCP client reports "Burp MCP not connected" | Confirm Burp is running and the extension is loaded; confirm both sides use the same port |
| Scan returns "requires Burp Professional" | Expected; the Community edition does not support the Scanner API |
| `remove_http_handler` / `remove_proxy_rule` has no effect | Confirm that the earlier `register_*` returned success=true |

## Build from source (Gradle optional)

```bash
cd burp-mcp-full
gradle jar      # needs Gradle 8.7+ installed locally
# Output: build/libs/burp-mcp-full.jar
```

> `build.bat` / `build.sh` are recommended (no dependencies, they download the jars automatically). The Gradle path is only an alternative. This package does not ship `gradle/wrapper/gradle-wrapper.jar`, because its checksum did not match the published checksum for the Gradle 8.7 wrapper. Run `gradle wrapper --gradle-version 8.7` with a local Gradle install to regenerate the jar before you use `gradlew` / `gradlew.bat`.
