---
name: browser-automation
description: |
  Unified automation entry. Covers browser automation (Playwright) and Windows desktop application automation (OpenReverse).
  Browser scenarios: open web pages, click, fill forms, crawl, screenshot, automated login, pentest page interaction.
  Desktop scenarios: drive GUI tools such as IDA/x64dbg, Windows UI Automation, vision-driven interaction, desktop application network capture.
  Trigger keywords: browser automation, desktop automation, open a web page, fill forms, crawl, screenshot, automated login, Playwright, agent-browser, headless, OpenReverse, UIA, CUA, desktop operation, Windows automation.
---

# Automation (Desktop & Browser Automation)

## ACTION REQUIRED (execute right after reading)

1. `NOW`: confirm whether the current task falls within this skill's scope
2. `NOW`: read `../tool-index.md` and check tool availability and actual paths
3. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
4. `ACT`: enter the first step of the "Workflow" and execute it; do not stop at a confirmation state

## Scope

Use this skill when the task falls into one of these scenarios:

### Browser scenarios (Playwright / agent-browser)
- Open a web page and operate page elements (click, fill forms, submit)
- Crawl page content or take screenshots
- Automated login flows
- Interact with web pages during penetration testing (submit payloads, trigger XSS)
- Automated handling of CAPTCHA pages
- Bulk form submission

### Desktop application scenarios (OpenReverse)
- Operate Windows desktop applications (IDA Pro, x64dbg, Wireshark and others)
- Vision-driven interaction is needed (CUA mode)
- Structured UI operation is needed (UIA mode)
- Network traffic observation of desktop applications (built-in mitmproxy)
- GUI operation of automated reverse engineering tools
- Black-box testing of desktop software

### Division of work with other tools

| Scenario | What to use |
|------|--------|
| Operate web pages (in the browser) | **Playwright / agent-browser** |
| Operate desktop applications (Windows GUI) | **OpenReverse** |
| Capture analysis, HTTP request capture | anything-analyzer or the OpenReverse network lane |
| JS breakpoints, hooks, CDP debugging | jshookmcp |
| Locate signing algorithms, environment patching reproduction | js-reverse |

Quick rule:
- Target is a web page → Playwright
- Target is a Windows desktop application → OpenReverse
- Both needed → combine them

---

## Part 1: Browser automation (Playwright / agent-browser)

### Core workflow

```bash
# 1. Open the page
agent-browser open <url>

# 2. Get interactive elements (returns @e1, @e2... references)
agent-browser snapshot -i

# 3. Operate elements by reference
agent-browser click @e1
agent-browser fill @e2 "text"

# 4. Close when done
agent-browser close
```

### Command reference

```bash
# Navigation
agent-browser open <url>
agent-browser close

# Page snapshot
agent-browser snapshot        # full accessibility tree
agent-browser snapshot -i     # interactive elements only (recommended)

# Interaction
agent-browser click @e1
agent-browser fill @e2 "text"
agent-browser type @e2 "text"
agent-browser press Enter
agent-browser scroll down 500

# Get information
agent-browser get text @e1
agent-browser get title
agent-browser get url

# Wait
agent-browser wait @e1
agent-browser wait 2000
agent-browser wait --load networkidle
```

### Notes
- You must run `agent-browser close`, or the process leaks
- Take a snapshot before operating; do not guess element references
- After submitting a form, use `wait --load networkidle` until the page is stable

---

## Part 2: Desktop application automation (OpenReverse)

### Overview

[OpenReverse](https://github.com/zhexulong/openreverse) is a desktop interaction and evidence collection framework for AI agents. It supports:
- **UIA mode**: Windows UI Automation, structured desktop control operation
- **CUA mode**: vision-driven interaction (Computer Use Agent), suited to complex GUIs
- **Network observation**: built-in mitmproxy proxy + local capture

### Interaction mode choice

| Mode | Suited to | Underlying layer |
|------|---------|------|
| UIA | The target application has standard Windows controls (buttons, text boxes, lists) | Windows UI Automation API |
| CUA | The target application has a complex UI or non-standard controls (IDA's disassembly view, custom-rendered interfaces) | Visual recognition + mouse and keyboard |

### Network observation modes

| Mode | Suited to |
|------|---------|
| Proxy Lane | The target application can be configured to use a proxy (recommended) |
| Local Lane | The target application cannot use a proxy and needs local capture |

### Installation and configuration

```bash
# 1. Clone the project
git clone https://github.com/zhexulong/openreverse.git
cd openreverse

# 2. Install dependencies
npm install

# 3. Connect the agent host (Claude Code / Codex / Zed)
npm run init:agents -- --target=all /path/to/project

# 4. Install the CUA runtime (if vision-driven mode is needed)
npm run install:cua-runtime
npm run doctor:cua-runtime

# 5. Install network observation dependencies (if capture is needed)
npm run install:mitmproxy
npm run doctor:network
```

### Common combinations

| Need | Configuration |
|------|------|
| Operate desktop applications only | UIA or CUA, no network lane |
| Operate desktop applications + capture | UIA/CUA + proxy lane |
| Operate desktop applications + local capture | UIA/CUA + local lane |

### Reverse engineering scenario examples

```text
Scenario: automate IDA Pro for batch analysis

1. Open IDA Pro in OpenReverse CUA mode
2. Load the target binary automatically
3. Wait for the analysis to finish
4. Export the function list through UI operations
5. Observe IDA's network behavior with the network lane at the same time (such as Lumina requests)
```

```text
Scenario: automate x64dbg debugging

1. Start x64dbg in OpenReverse UIA mode
2. Load the target program
3. Set breakpoints
4. Run and observe register/memory changes
5. Save screenshots as evidence
```

---

## On-Demand Bootstrap

### Automation boundaries

| Tool | Auto-installable | Install method | Notes |
|------|-----------|---------|------|
| Playwright | ✓ | npm + npx playwright install | Browser automation engine |
| agent-browser CLI | ✓ | npm install -g agent-browser | Browser operation CLI |
| Node.js | ✓ | winget | Prerequisite |
| OpenReverse | ✗ | Manual clone + npm install | Experimental, heavy dependencies |
| mitmproxy | ✗ | Manual install | OpenReverse network observation dependency |

### Bootstrap triggers

- Browser operation without Playwright → automatic bootstrap
- Desktop operation that needs OpenReverse → guide the user through a manual install (give complete steps)

### OpenReverse manual install guide

If the AI detects that desktop application automation is needed but OpenReverse is not installed:

```markdown
⚠️ **OpenReverse is needed for desktop application automation**

**Install steps**:
1. `git clone https://github.com/zhexulong/openreverse.git`
2. `cd openreverse && npm install`
3. `npm run init:agents -- --target=all <your project path>`
4. For vision mode: `npm run install:cua-runtime`
5. For network observation: `npm run install:mitmproxy`

**Verify**: `npm run doctor:cua-runtime` and `npm run doctor:network`
```

---

## Routing context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**When to use**: any task that needs automated operation of a browser or desktop application
**Downstream exits**:
- Captured requests need analysis → `anything-analyzer` or `js-reverse`
- JS debugging/hooks needed → `jshookmcp`
- Signing algorithm needs reconstruction → `js-reverse`
- The desktop application is a reverse engineering tool → `ida-reverse/`

**Sibling modules**: `js-reverse` (JS may need analysis after browser operation), `ida-reverse` (OpenReverse can automate the IDA GUI)


## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
