# Browser and Desktop Automation Quick Reference

> Covers common commands and patterns for Playwright (browser automation) and OpenReverse (Windows desktop automation).
> Aimed at penetration testing, reverse engineering and automated collection scenarios.

---

## Playwright / agent-browser command quick reference

### Navigation and lifecycle

```bash
# Open a page
agent-browser open "https://target.com/login"

# Wait for the page to finish loading
agent-browser wait --load networkidle

# Close the browser (mandatory, or the process leaks)
agent-browser close
```

### Page snapshot

```bash
# Full accessibility tree (for debugging)
agent-browser snapshot

# Interactive elements only (recommended, returns @e1, @e2... references)
agent-browser snapshot -i
```

### Element interaction

```bash
# Click
agent-browser click @e1

# Fill a text box
agent-browser fill @e2 "admin"

# Type character by character (suits inputs with JS listeners)
agent-browser type @e2 "password123"

# Key press
agent-browser press Enter
agent-browser press Tab
agent-browser press Escape

# Scroll
agent-browser scroll down 500
agent-browser scroll up 300
```

### Getting information

```bash
# Get element text
agent-browser get text @e1

# Get the page title
agent-browser get title

# Get the current URL
agent-browser get url
```

### Wait strategies

```bash
# Wait for an element to appear
agent-browser wait @e1

# Wait a fixed time (milliseconds)
agent-browser wait 2000

# Wait for network idle
agent-browser wait --load networkidle

# Wait for navigation to finish
agent-browser wait --load domcontentloaded
```

---

## Common penetration testing patterns

### Automated login

```bash
agent-browser open "https://target.com/login"
agent-browser snapshot -i
agent-browser fill @username "admin"
agent-browser fill @password "password123"
agent-browser click @login_button
agent-browser wait --load networkidle
agent-browser get url                    # confirm the redirect to the admin area
```

### XSS payload injection

```bash
agent-browser open "https://target.com/search"
agent-browser snapshot -i
agent-browser fill @search_input "<script>alert(1)</script>"
agent-browser click @search_button
agent-browser wait --load networkidle
agent-browser snapshot                   # check whether the payload is rendered
```

### Bulk form submission (with a script)

```powershell
$payloads = @("' OR 1=1--", "<img src=x onerror=alert(1)>", "{{7*7}}")
foreach ($p in $payloads) {
    agent-browser open "https://target.com/form"
    agent-browser snapshot -i
    agent-browser fill @input "$p"
    agent-browser click @submit
    agent-browser wait --load networkidle
    agent-browser snapshot              # check the response
}
agent-browser close
```

### Cookie / LocalStorage extraction

```bash
# Through the Playwright API (Node.js script mode)
# agent-browser does not expose cookies directly; use script mode
```

```javascript
// playwright-extract.js
const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    await page.goto('https://target.com');
    
    // Extract cookies
    const cookies = await context.cookies();
    console.log(JSON.stringify(cookies, null, 2));
    
    // Extract localStorage
    const storage = await page.evaluate(() => JSON.stringify(localStorage));
    console.log(storage);
    
    await browser.close();
})();
```

### Screenshot evidence

```bash
# agent-browser mode
agent-browser open "https://target.com/admin"
agent-browser wait --load networkidle
# Screenshot support depends on the agent-browser version
```

```javascript
// playwright script mode
await page.screenshot({ path: 'evidence.png', fullPage: true });
```

---

## Playwright Node.js API quick reference

### Basic template

```javascript
const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({
        headless: true,           // headless mode
        // proxy: { server: 'http://127.0.0.1:8080' }  // route through the Burp proxy
    });
    const context = await browser.newContext({
        ignoreHTTPSErrors: true,  // ignore certificate errors
        userAgent: 'Mozilla/5.0 ...',
    });
    const page = await context.newPage();
    
    await page.goto('https://target.com');
    // ... operations ...
    
    await browser.close();
})();
```

### Common selectors

```javascript
// CSS selector
await page.click('#login-btn');
await page.fill('input[name="username"]', 'admin');

// Text selector
await page.click('text=Submit');
await page.click('button:has-text("Login")');

// XPath
await page.click('xpath=//button[@type="submit"]');

// Combination
await page.click('form >> input[type="submit"]');
```

### Network interception

```javascript
// Intercept requests
await page.route('**/api/**', route => {
    console.log('API call:', route.request().url());
    route.continue();
});

// Modify requests
await page.route('**/api/auth', route => {
    route.continue({
        headers: { ...route.request().headers(), 'X-Admin': 'true' }
    });
});

// Intercept responses
await page.route('**/api/user', async route => {
    const response = await route.fetch();
    const json = await response.json();
    json.role = 'admin';  // tamper with the response
    route.fulfill({ response, json });
});
```

### Waits and assertions

```javascript
// Wait for an element
await page.waitForSelector('#result');
await page.waitForSelector('.error', { state: 'visible' });

// Wait for a network request
const [response] = await Promise.all([
    page.waitForResponse('**/api/login'),
    page.click('#login-btn'),
]);
console.log(response.status(), await response.json());

// Wait for navigation
await Promise.all([
    page.waitForNavigation(),
    page.click('a[href="/admin"]'),
]);
```

---

## OpenReverse desktop automation quick reference

### Mode choice

| Mode | Command prefix | Suited to |
|------|---------|---------|
| UIA | `openreverse uia ...` | Standard Windows controls (buttons, text boxes, lists) |
| CUA | `openreverse cua ...` | Complex/non-standard GUIs (IDA disassembly view, custom-rendered interfaces) |

### UIA mode (structured control operations)

```bash
# Start the application
openreverse uia launch "C:\Tools\x64dbg\x64dbg.exe"

# Get the window tree
openreverse uia tree

# Click a button
openreverse uia click "Button:Open"

# Fill a text box
openreverse uia fill "Edit:FilePath" "C:\sample.exe"

# Choose a menu
openreverse uia menu "File > Open"

# Get control text
openreverse uia get-text "Edit:Output"
```

### CUA mode (vision-driven interaction)

```bash
# Screenshot the current screen
openreverse cua screenshot

# Click screen coordinates
openreverse cua click 500 300

# Double-click
openreverse cua dblclick 500 300

# Type text
openreverse cua type "search string"

# Key press
openreverse cua key "ctrl+g"    # IDA: Go to address
openreverse cua key "F5"        # IDA: Decompile
openreverse cua key "F9"        # x64dbg: Run
```

### Network observation (mitmproxy)

```bash
# Start proxy mode observation
openreverse network start --mode proxy --port 8888

# Start local capture mode
openreverse network start --mode local --filter "target.exe"

# Get the captured requests
openreverse network list

# Export as HAR
openreverse network export har output.har

# Stop observing
openreverse network stop
```

---

## Reverse engineering tool automation combinations

### IDA Pro automation (OpenReverse + ida-reverse)

```text
Scenario: batch analysis of several samples

1. openreverse cua launch "ida64.exe"
2. For each sample:
   a. openreverse cua key "ctrl+o"        # open the file dialog
   b. openreverse uia fill "Edit:FileName" "sample_N.exe"
   c. openreverse uia click "Button:Open"
   d. Wait for the analysis to finish (poll the IDA title bar)
   e. Extract the results with the ida-reverse MCP tools
   f. openreverse cua key "ctrl+w"        # close the database
```

### x64dbg automated debugging

```text
Scenario: automated breakpoint setup and data collection

1. openreverse uia launch "x64dbg.exe"
2. openreverse cua key "F3"               # open a file
3. openreverse uia fill "Edit:FileName" "target.exe"
4. openreverse uia click "Button:Open"
5. openreverse cua key "ctrl+g"           # Go to address
6. openreverse cua type "0x401000"
7. openreverse cua key "F2"               # set a breakpoint
8. openreverse cua key "F9"               # run
9. openreverse cua screenshot             # screenshot to save the state
```

---

## Common problems and fixes

| Problem | Cause | Fix |
|------|------|------|
| agent-browser unresponsive | Process leak | Run `agent-browser close` first, then open again |
| Element reference invalid | The page refreshed | Run `snapshot -i` again to get new references |
| Form filling has no effect | JS listens for input events | Use `type` instead of `fill` |
| HTTPS certificate error | Self-signed certificate | Playwright: `ignoreHTTPSErrors: true` |
| Page load timeout | Slow network/many resources | Increase the timeout or use `domcontentloaded` |
| UIA cannot find the control | The application uses owner-drawn controls | Switch to CUA mode |
| CUA click offset | Resolution/DPI mismatch | Take a screenshot first to confirm coordinates |

---

## Installation and dependencies

### Playwright

```powershell
# Install Node.js (if missing)
winget install OpenJS.NodeJS.LTS

# Install Playwright
npm install -g playwright
npx playwright install          # download the browser engines

# Install the agent-browser CLI
npm install -g agent-browser
```

### OpenReverse

```powershell
git clone https://github.com/zhexulong/openreverse.git
cd openreverse
npm install
npm run init:agents -- --target=all <project path>

# Optional: CUA runtime
npm run install:cua-runtime
npm run doctor:cua-runtime

# Optional: network observation
npm run install:mitmproxy
npm run doctor:network
```

---

## Related resources

| Resource | Description | Link |
|------|------|------|
| Playwright official documentation | API reference | https://playwright.dev/docs/intro |
| OpenReverse | Desktop automation framework | https://github.com/zhexulong/openreverse |
| mitmproxy | HTTP/HTTPS proxy | https://mitmproxy.org/ |
| Windows UI Automation | UIA documentation | https://learn.microsoft.com/en-us/windows/win32/winauto/entry-uiauto-win32 |
