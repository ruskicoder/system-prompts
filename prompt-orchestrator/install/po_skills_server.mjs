#!/usr/bin/env node
// po_skills_server.mjs: the po-skills MCP server. It serves the opt-in pack skills that the
// prompt-orchestrator installer copies in mode mcp, so no pack skill sits in a tool's skills folder.
//
//   node server.mjs [--index FILE]
//
// The server speaks MCP over stdio: one JSON-RPC message per line on stdin and stdout. It answers
// the 2026-07-28 revision (server/discover, protocol version in each request's _meta) and the
// earlier revisions that open with initialize (2025-11-25, 2025-06-18, 2025-03-26, 2024-11-05).
// It reads the index file that the installer builds (default: index.json next to this file) and
// rereads it only when the file changes. It needs Node.js 18 or later and no packages.

import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";

const NAME = "po-skills";
const VERSION = "1.0.0";
const MODERN = ["2026-07-28"];
const LEGACY = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"];
const META = "io.modelcontextprotocol/";
const UNSUPPORTED_VERSION = -32022;
const LIMIT_MAX = 50;

const INSTRUCTIONS =
  "Opt-in skill packs (security, offense, malware, forensics, cloud, reverse engineering, logo design). " +
  "Before such a task, call search_skills, then load_skill on the best match and follow its SKILL.md. " +
  "Read references and run scripts from the folder it returns.";

const TOOLS = [
  {
    name: "search_skills",
    title: "Search pack skills",
    description:
      "Search skills: pentest, red team, malware, forensics, incident response, cloud, AppSec, reverse engineering, logo design. Ranked name, pack, set, summary.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Keywords, for example: ntlm relay" },
        pack: { type: "string", description: "Only this pack id" },
        limit: { type: "integer", minimum: 1, maximum: LIMIT_MAX, default: 10 },
      },
      required: ["query"],
      additionalProperties: false,
    },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  {
    name: "load_skill",
    title: "Load a pack skill",
    description:
      "Load skill: full SKILL.md text and the absolute skill folder path, so you can read its references and run its scripts. Takes a name from search_skills.",
    inputSchema: {
      type: "object",
      properties: { name: { type: "string", description: "Skill name from search_skills" } },
      required: ["name"],
      additionalProperties: false,
    },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  {
    name: "list_packs",
    title: "List installed packs",
    description: "List packs: installed skill packs and their sets with skill counts.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
];

const STOP = new Set(["a", "an", "and", "the", "for", "with", "to", "of", "in", "on", "or", "how", "skill", "skills"]);

// ------------------------------------------------------------------ index

function indexPath(argv) {
  const at = argv.indexOf("--index");
  if (at >= 0 && argv[at + 1]) return path.resolve(argv[at + 1]);
  return path.join(path.dirname(fileURLToPath(import.meta.url)), "index.json");
}

const INDEX_FILE = indexPath(process.argv.slice(2));
let cache = { stamp: null, index: null, error: null };

function tokens(text) {
  return String(text).toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
}

function loadIndex() {
  let stat;
  try {
    stat = fs.statSync(INDEX_FILE);
  } catch {
    cache = { stamp: null, index: null, error: `no index at ${INDEX_FILE}; install a pack in mode mcp` };
    return cache;
  }
  const stamp = `${stat.mtimeMs}:${stat.size}`;
  if (cache.stamp === stamp) return cache;
  try {
    const data = JSON.parse(fs.readFileSync(INDEX_FILE, "utf8"));
    const skills = (data.skills || []).map((s) => ({
      ...s,
      nameTokens: tokens(s.name),
      descTokens: new Set(tokens(s.description)),
      where: tokens(`${s.pack} ${s.set}`),
    }));
    const byName = new Map(skills.map((s) => [s.name, s]));
    cache = { stamp, index: { skills, byName, packs: data.packs || [] }, error: null };
  } catch (error) {
    cache = { stamp, index: null, error: `cannot read ${INDEX_FILE}: ${error.message}` };
  }
  return cache;
}

function score(skill, words, phrase) {
  let total = 0;
  let hits = 0;
  for (const w of words) {
    let best = 0;
    if (skill.nameTokens.includes(w)) best = 4;
    else if (w.length >= 3 && skill.nameTokens.some((t) => t.startsWith(w))) best = 2;
    if (skill.descTokens.has(w)) best = Math.max(best, 1.5);
    else if (best < 0.75 && w.length >= 3) {
      for (const t of skill.descTokens) if (t.startsWith(w)) { best = 0.75; break; }
    }
    if (skill.where.includes(w)) best = Math.max(best, 0.5);
    if (best > 0) hits++;
    total += best;
  }
  if (!total) return 0;
  if (hits === words.length) total *= 1.5;
  if (phrase && skill.name.includes(phrase)) total += 3;
  return total;
}

// ------------------------------------------------------------------ tools

class ToolError extends Error {}

function text(body) {
  return { content: [{ type: "text", text: body }] };
}

function searchSkills(index, args) {
  if (typeof args.query !== "string" || !args.query.trim()) throw new ToolError("query must be a non-empty string");
  let limit = args.limit === undefined ? 10 : args.limit;
  if (!Number.isInteger(limit) || limit < 1) throw new ToolError("limit must be a positive integer");
  limit = Math.min(limit, LIMIT_MAX);
  if (args.pack !== undefined && typeof args.pack !== "string") throw new ToolError("pack must be a string");
  const words = tokens(args.query).filter((w) => !STOP.has(w));
  if (!words.length) throw new ToolError("query holds no search words");
  const phrase = words.length > 1 ? words.join("-") : "";
  const ranked = [];
  for (const skill of index.skills) {
    if (args.pack && skill.pack !== args.pack) continue;
    const s = score(skill, words, phrase);
    if (s > 0) ranked.push([s, skill]);
  }
  ranked.sort((a, b) => b[0] - a[0] || (a[1].name < b[1].name ? -1 : 1));
  const top = ranked.slice(0, limit);
  if (!top.length) return text(`No skill matches "${args.query}". Try other words, or call list_packs.`);
  const lines = top.map(([, s], i) => `${i + 1}. ${s.name} (pack ${s.pack}, set ${s.set}): ${s.summary}`);
  lines.push("", "Call load_skill with a name to read the skill.");
  return text(lines.join("\n"));
}

function loadSkill(index, args) {
  if (typeof args.name !== "string" || !args.name) throw new ToolError("name must be a non-empty string");
  const skill = index.byName.get(args.name);
  if (!skill) throw new ToolError(`no installed skill is named ${args.name}; call search_skills first`);
  let body;
  try {
    body = fs.readFileSync(path.join(skill.path, "SKILL.md"), "utf8");
  } catch (error) {
    throw new ToolError(`cannot read ${path.join(skill.path, "SKILL.md")}: ${error.message}; reinstall pack ${skill.pack}`);
  }
  const head = [
    `Skill: ${skill.name} (pack ${skill.pack}, set ${skill.set})`,
    `Folder: ${skill.path}`,
    "Relative paths in SKILL.md start at this folder. Read references and run scripts from there.",
    "",
  ];
  return text(head.join("\n") + body);
}

function listPacks(index) {
  if (!index.packs.length) return text("No pack is installed in mode mcp.");
  const lines = [];
  for (const p of index.packs) {
    const total = p.sets.reduce((n, s) => n + s.count, 0);
    lines.push(`${p.id}: ${total} skills`);
    for (const s of p.sets) lines.push(`  ${p.id}:${s.id}: ${s.count} skills`);
  }
  return text(lines.join("\n"));
}

function callTool(params) {
  const name = params && params.name;
  const tool = TOOLS.find((t) => t.name === name);
  if (!tool) return { error: { code: -32602, message: `Unknown tool: ${name}` } };
  const args = params.arguments === undefined ? {} : params.arguments;
  if (!args || typeof args !== "object" || Array.isArray(args)) return { error: { code: -32602, message: "arguments must be an object" } };
  const { index, error } = loadIndex();
  try {
    if (!index) throw new ToolError(error);
    if (name === "search_skills") return { result: searchSkills(index, args) };
    if (name === "load_skill") return { result: loadSkill(index, args) };
    return { result: listPacks(index) };
  } catch (failure) {
    if (!(failure instanceof ToolError)) throw failure;
    return { result: { ...text(failure.message), isError: true } };
  }
}

// ------------------------------------------------------------------ protocol

function capabilities() {
  return { tools: { listChanged: false } };
}

function negotiate(requested) {
  if (LEGACY.includes(requested)) return requested;
  return LEGACY[0];
}

function modernVersion(params) {
  const meta = params && typeof params === "object" ? params._meta : undefined;
  return meta && typeof meta === "object" ? meta[`${META}protocolVersion`] : undefined;
}

function decorate(result, modern) {
  if (!modern) return result;
  return { ...result, resultType: "complete", _meta: { [`${META}serverInfo`]: { name: NAME, version: VERSION } } };
}

function handle(method, params) {
  const requested = modernVersion(params);
  const modern = requested !== undefined;
  if (modern && !MODERN.includes(requested)) {
    return { error: { code: UNSUPPORTED_VERSION, message: "Unsupported protocol version",
      data: { supported: [...MODERN, ...LEGACY], requested } } };
  }
  switch (method) {
    case "initialize": {
      // A legacy client opens with initialize: answer its revision, or the newest legacy one.
      return { result: { protocolVersion: negotiate(params && params.protocolVersion), capabilities: capabilities(),
        serverInfo: { name: NAME, title: "prompt-orchestrator skill packs", version: VERSION }, instructions: INSTRUCTIONS } };
    }
    case "server/discover":
      return { result: decorate({ supportedVersions: [...MODERN, ...LEGACY], capabilities: capabilities(),
        instructions: INSTRUCTIONS, ttlMs: 3600000, cacheScope: "public" }, true) };
    case "ping":
      return { result: decorate({}, modern) };
    case "tools/list": {
      const result = { tools: TOOLS };
      if (modern) Object.assign(result, { ttlMs: 3600000, cacheScope: "public" });
      return { result: decorate(result, modern) };
    }
    case "tools/call": {
      const out = callTool(params);
      return out.error ? out : { result: decorate(out.result, modern) };
    }
    default:
      return { error: { code: -32601, message: `Method not found: ${method}` } };
  }
}

function respond(message) {
  if (!message || typeof message !== "object" || Array.isArray(message) || message.jsonrpc !== "2.0" || typeof message.method !== "string") {
    const id = message && typeof message === "object" && "id" in message ? message.id : null;
    if (message && typeof message === "object" && !("method" in message) && ("result" in message || "error" in message)) return null;
    return { jsonrpc: "2.0", id, error: { code: -32600, message: "Invalid Request" } };
  }
  const notification = !("id" in message);
  if (notification) return null; // notifications/initialized, notifications/cancelled and others need no answer
  let out;
  try {
    out = handle(message.method, message.params);
  } catch (error) {
    process.stderr.write(`po-skills: ${error.stack || error}\n`);
    out = { error: { code: -32603, message: "Internal error" } };
  }
  return { jsonrpc: "2.0", id: message.id, ...out };
}

function onLine(line) {
  if (!line.trim()) return;
  let parsed;
  try {
    parsed = JSON.parse(line);
  } catch {
    send({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } });
    return;
  }
  if (Array.isArray(parsed)) {
    // JSON-RPC batches: 2025-03-26 allows them, later revisions do not send them.
    const replies = parsed.map(respond).filter(Boolean);
    if (replies.length) send(replies);
    return;
  }
  const reply = respond(parsed);
  if (reply) send(reply);
}

function send(message) {
  process.stdout.write(JSON.stringify(message) + "\n");
}

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity, terminal: false });
rl.on("line", onLine);
rl.on("close", () => process.exit(0));
