# [seed] JS Signature Reverse Engineering (Webpack + AES + Timestamp)

## Scenario classification
JS signing

## Target overview
Recover the generation algorithm of the `sign` parameter of a web application's interface and reproduce it locally.

## Complete execution chain

1. Browser traffic capture → POST requests carry `sign` and `timestamp` parameters
2. Search the JS source for "sign" → located a webpack-bundled chunk file
3. Set a breakpoint where sign is assigned → hit, inspect the call stack
4. Walk back the call stack → found the signing function (in a webpack module)
5. Analyze the signing logic: `sign = HmacSHA256(sorted_params + timestamp, secret_key)`
6. Key source: hard-coded in another webpack module
7. Reproduce locally in Node.js → the generated sign matches the browser's
8. Verify: request the interface with the reproduced sign → normal data returned

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| Searching "sign" gives too many results | Variable names are minified after webpack bundling | Search for `sign=` instead, or find the request in the network panel and walk back via the initiator | 15min |
| Breakpoint hit but the code is unreadable | webpack minification + variable name obfuscation | Format with Chrome's Pretty Print, plus the SourceMap (if any) | 10min |
| Local reproduction result differs | Wrong parameter sort order | Read the sort logic in the source carefully (alphabetical by key + special character handling) | 30min |
| Wrong timestamp precision | The server uses seconds, I used milliseconds | `Math.floor(Date.now() / 1000)` | 5min |
| Key not found | The key is imported by require from another chunk file | console.log the key variable at the breakpoint | 10min |

## Toolchain findings

- The initiator column of Chrome DevTools locates the signing function faster than searching the source
- For webpack-bundled code, Pretty Print + breakpoints beat reading it raw
- If a SourceMap (.map file) exists, recover the original code directly
- The Node.js `crypto` module reproduces most signing algorithms directly

## Key code/commands

```javascript
// Node.js reproduction
const crypto = require('crypto');

function generateSign(params, timestamp, secretKey) {
    // 1. sort parameters alphabetically by key
    const sorted = Object.keys(params).sort().map(k => `${k}=${params[k]}`).join('&');
    // 2. append the timestamp
    const message = sorted + '&timestamp=' + timestamp;
    // 3. HMAC-SHA256
    return crypto.createHmac('sha256', secretKey).update(message).digest('hex');
}

const params = { user_id: '123', action: 'query' };
const timestamp = Math.floor(Date.now() / 1000);
const secretKey = 'hardcoded_key_from_webpack';
console.log(generateSign(params, timestamp, secretKey));
```

## Improvement suggestions for this package

- js-reverse's env-patching.md should add "how to handle dependencies between webpack chunks"
- Suggest adding a quick reference for "identifying common signing algorithms" (HMAC-SHA256 vs MD5 vs custom)

## Reusable patterns/script snippets

**Standard flow for JS signature reverse engineering**:
```text
1. Capture traffic and find the signed request
2. Locate the signing function with the initiator/call stack
3. Analyze the signing logic (parameter sorting + concatenation + encryption)
4. Find the key source (hard-coded/returned by an interface/derived from time)
5. Reproduce in Node.js
6. Compare and verify
```

**Common signing patterns**:
```text
- HmacSHA256(sorted_params, key) → the most common
- MD5(params + salt + timestamp) → older systems
- AES(JSON.stringify(params), key) → encryption rather than signing
- RSA sign → rare, usually financial
```

## Evolution actions
- [ ] No routing matrix update needed
- [ ] No bootstrap-manifest update needed
- [ ] No sub-skill documentation update needed

## Environment information
- OS: Windows
- Tool versions: Chrome DevTools, Node.js 20+
- Target platform: Web (Webpack-bundled SPA)

## Redaction requirements
This entry is seed data, written from public technical patterns, with no real target involved.

---
<!-- [Community contribution] Seed data, no PR needed -->
