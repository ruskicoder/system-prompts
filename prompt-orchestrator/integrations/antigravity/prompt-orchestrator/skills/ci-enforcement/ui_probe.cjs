// UI probe for check.py ui. Reads a job on stdin, prints raw measurements as JSON on stdout.
// Judging happens in check.py, so the rules stay in one place and can be unit-tested without a browser.
//
// Job: {"urls": [...], "viewports": [{label, width, height, scale}], "schemes": ["light", "dark"]}
// Needs playwright and axe-core resolvable by require() (a local node_modules or NODE_PATH).
"use strict";

const fs = require("fs");

// Resolve from the working directory first (CI installs there), then NODE_PATH, then this folder.
const SEARCH = [process.cwd(), ...(process.env.NODE_PATH || "").split(":").filter(Boolean), ...module.paths];

function resolve(name) {
  return require.resolve(name, { paths: SEARCH });
}

function need(name) {
  try {
    return require(resolve(name));
  } catch (err) {
    process.stderr.write(`cannot load ${name}: install it (npm install --no-save ${name}) or set NODE_PATH\n`);
    process.exit(2);
  }
}

const { chromium } = need("playwright");
need("axe-core");
const axeSource = fs.readFileSync(resolve("axe-core/axe.min.js"), "utf8");

const TARGETS = 'a[href], button, input:not([type="hidden"]), select, textarea, summary, [role="button"], [role="link"], [role="checkbox"], [role="radio"], [role="switch"], [role="tab"], [role="menuitem"], [onclick], [tabindex]:not([tabindex="-1"])';

function measureTargets(selector) {
  const describe = (el) => {
    if (el.id) return `#${el.id}`;
    const name = (el.getAttribute("aria-label") || el.textContent || "").trim().slice(0, 30);
    return `${el.tagName.toLowerCase()}${name ? `("${name}")` : ""}`;
  };
  const inlineInText = (el) => {
    if (getComputedStyle(el).display !== "inline") return false;
    const parent = el.parentElement;
    if (!parent) return false;
    return Array.from(parent.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim().length > 0);
  };
  const out = [];
  for (const el of document.querySelectorAll(selector)) {
    const style = getComputedStyle(el);
    if (style.visibility === "hidden" || style.display === "none" || el.closest("[inert], [aria-hidden='true']")) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    out.push({ selector: describe(el), x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height, inline: inlineInText(el) });
  }
  return out;
}

async function main() {
  const job = JSON.parse(fs.readFileSync(0, "utf8"));
  const browser = await chromium.launch();
  const results = [];
  try {
    for (const scheme of job.schemes || ["light"]) {
      for (const vp of job.viewports) {
        const context = await browser.newContext({
          viewport: { width: vp.width, height: vp.height },
          deviceScaleFactor: vp.scale || 1,
          colorScheme: scheme,
        });
        const page = await context.newPage();
        for (const url of job.urls) {
          const row = { url, viewport: vp, scheme };
          try {
            await page.goto(url, { waitUntil: "load", timeout: 60000 });
            await page.addScriptTag({ content: axeSource });
            const axe = await page.evaluate(async () => {
              const r = await window.axe.run(document, {
                runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] },
              });
              return r.violations.map((v) => ({ id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length }));
            });
            row.axe = axe;
            row.targets = await page.evaluate(measureTargets, TARGETS);
            Object.assign(row, await page.evaluate(() => ({
              scrollWidth: document.documentElement.scrollWidth,
              clientWidth: document.documentElement.clientWidth,
            })));
          } catch (err) {
            row.error = String(err && err.message ? err.message.split("\n")[0] : err);
          }
          results.push(row);
        }
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
  process.stdout.write(JSON.stringify(results));
}

main().catch((err) => {
  process.stderr.write(`${err && err.stack ? err.stack : err}\n`);
  process.exit(2);
});
