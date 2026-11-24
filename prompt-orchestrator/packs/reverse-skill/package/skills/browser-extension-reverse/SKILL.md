---
name: browser-extension-reverse
description: Use for authorized reverse engineering of browser extensions (Chrome/Firefox) including manifest analysis, background workers, and extension-based credential or traffic logic recovery.
---

# Browser Extension Reverse Engineering

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md`
2. `NOW`: confirm that the target is a **browser extension** (crx/xpi/unpacked directory), not regular web page JS (regular → `js-reverse/`)
3. `NEXT`: unpack the extension; read the manifest
4. `ACT`: permission surface → background scripts → network/storage hooks

## When to use

- Chrome/Edge MV2/MV3 extension analysis
- Firefox extensions
- Malicious extension IOCs, supply chain extension poisoning investigation
- Reconstruct signing/crypto/proxy logic implemented by an extension

## Workflow

### 1. Package

```text
□ Unpack the crx / take the extension directory from the profile
□ manifest.json: permissions, host_permissions, background, content_scripts
□ Assess excessive permissions (<all_urls>, webRequest, debugger)
```

### 2. Logic

```text
□ service_worker / background entry
□ content_script injection points and world (isolated)
□ chrome.storage / IndexedDB keys
□ Same as `js-reverse`: Observe the network and message passing (runtime.sendMessage)
```

### 3. Dynamic

```text
□ Load the unpacked directory in developer mode
□ Check chrome://extensions for errors
□ Attach DevTools to the service worker
□ Frida/browser CDP (jshookmcp) when needed
```

## Toolchain

| Tool | Purpose |
|------|------|
| Unpacker/jq | manifest |
| Chrome DevTools | worker debugging |
| js-reverse toolchain | Deep JS |
| YARA | Malicious extension rules |

## References

- `references/extension-analysis.md`
- field-journal entries related to extension recovery
- `../js-reverse/` `../malware-analysis/`

## Routing context

**Upstream**: MASTER R30  
**Downstream**: heavily obfuscated JS → `js-reverse`; poisoning investigation → supply-chain / malware

## Task completion self-check

- [ ] Did I list the permission surface and entry scripts?
- [ ] Did I reconstruct the key data flows?
- [ ] Checklist?