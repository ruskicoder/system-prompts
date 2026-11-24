#!/usr/bin/env node
// pack_helper.mjs: MCP registration and npm checks for prompt-orchestrator packs.
//
// install.sh and install.ps1 call this helper for packs that carry an "npm" or "mcp" object
// (packs/README.md). It needs Node.js 18 or later and the standard library only.
//
//   node pack_helper.mjs node-check RANGE
//   node pack_helper.mjs platform
//   node pack_helper.mjs npm-check PREFIX NAME VERSION INTEGRITY
//   node pack_helper.mjs mcp-add FORMAT FILE NAME SPEC_B64 PACKAGE_DIR [RECORD_B64]
//   node pack_helper.mjs mcp-remove RECORD_B64
//
// mcp-add prints "status<TAB>file<TAB>record". The status is added, present, foreign or
// conflict. The record is base64 JSON that mcp-remove needs, or "-". mcp-remove prints removed,
// absent or changed. An edit touches only the one server entry: it inserts or deletes one text
// fragment and leaves every other byte of the file as it was.

import fs from "node:fs";
import path from "node:path";

const FORMATS = {
  claude: { kind: "json", container: "mcpServers", entry: (s) => withEnv({ type: "stdio", command: s.command, args: s.args }, "env", s.env) },
  cursor: { kind: "json", container: "mcpServers", entry: (s) => withEnv({ command: s.command, args: s.args }, "env", s.env) },
  gemini: { kind: "json", container: "mcpServers", entry: (s) => withEnv({ command: s.command, args: s.args }, "env", s.env) },
  opencode: {
    kind: "json",
    container: "mcp",
    entry: (s) => {
      const out = withEnv({ type: "local", command: [s.command, ...s.args] }, "environment", s.env);
      out.enabled = true;
      return out;
    },
  },
  codex: { kind: "toml", container: "mcp_servers" },
};

function withEnv(obj, key, env) {
  if (env && Object.keys(env).length) obj[key] = env;
  return obj;
}

function die(message, code = 2) {
  process.stderr.write(`pack_helper: ${message}\n`);
  process.exit(code);
}

const b64 = (value) => Buffer.from(JSON.stringify(value), "utf8").toString("base64");
const unb64 = (text) => JSON.parse(Buffer.from(text, "base64").toString("utf8"));

// ------------------------------------------------------------------ versions

function parseVersion(text) {
  const m = /^v?(\d+)\.(\d+)\.(\d+)/.exec(String(text).trim());
  if (!m) return null;
  return [Number(m[1]), Number(m[2]), Number(m[3])];
}

function compare(a, b) {
  for (let i = 0; i < 3; i++) if (a[i] !== b[i]) return a[i] < b[i] ? -1 : 1;
  return 0;
}

// Supports the subset that pack.json uses: alternatives joined by ||, each ^X.Y.Z, >=X.Y.Z or X.Y.Z.
function satisfies(version, range) {
  const v = parseVersion(version);
  if (!v) return false;
  return range.split("||").some((part) => {
    const p = part.trim();
    if (p.startsWith("^")) {
      const base = parseVersion(p.slice(1));
      return base && v[0] === base[0] && compare(v, base) >= 0;
    }
    if (p.startsWith(">=")) {
      const base = parseVersion(p.slice(2));
      return base && compare(v, base) >= 0;
    }
    const base = parseVersion(p);
    return base && compare(v, base) === 0;
  });
}

// ------------------------------------------------------------------ JSON with comments

class Parser {
  constructor(text) {
    this.text = text;
    this.i = text.charCodeAt(0) === 0xfeff ? 1 : 0;
  }

  fail(what) {
    throw new Error(`${what} at offset ${this.i}`);
  }

  ws() {
    const t = this.text;
    for (;;) {
      const c = t[this.i];
      if (c === " " || c === "\t" || c === "\r" || c === "\n") this.i++;
      else if (c === "/" && t[this.i + 1] === "/") {
        while (this.i < t.length && t[this.i] !== "\n") this.i++;
      } else if (c === "/" && t[this.i + 1] === "*") {
        const end = t.indexOf("*/", this.i + 2);
        if (end < 0) this.fail("unclosed comment");
        this.i = end + 2;
      } else return;
    }
  }

  value() {
    this.ws();
    const c = this.text[this.i];
    if (c === "{") return this.object();
    if (c === "[") return this.array();
    if (c === '"') return this.string();
    const m = /^(?:true|false|null|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)/.exec(this.text.slice(this.i, this.i + 64));
    if (!m) this.fail("unexpected token");
    const start = this.i;
    this.i += m[0].length;
    return { type: "literal", start, end: this.i, value: JSON.parse(m[0]) };
  }

  string() {
    const start = this.i;
    const t = this.text;
    this.i++;
    while (this.i < t.length && t[this.i] !== '"') this.i += t[this.i] === "\\" ? 2 : 1;
    if (this.i >= t.length) this.fail("unclosed string");
    this.i++;
    return { type: "string", start, end: this.i, value: JSON.parse(t.slice(start, this.i)) };
  }

  array() {
    const start = this.i++;
    const items = [];
    for (;;) {
      this.ws();
      if (this.text[this.i] === "]") break;
      items.push(this.value());
      this.ws();
      if (this.text[this.i] === ",") this.i++;
      else if (this.text[this.i] !== "]") this.fail("expected , or ]");
    }
    this.i++;
    return { type: "array", start, end: this.i, value: items.map((x) => x.value) };
  }

  object() {
    const start = this.i++;
    const members = [];
    for (;;) {
      this.ws();
      if (this.text[this.i] === "}") break;
      if (this.text[this.i] !== '"') this.fail("expected a key");
      const key = this.string();
      this.ws();
      if (this.text[this.i] !== ":") this.fail("expected :");
      this.i++;
      const value = this.value();
      const member = { key: key.value, keyStart: key.start, valueEnd: value.end, value, comma: -1 };
      this.ws();
      if (this.text[this.i] === ",") {
        member.comma = this.i;
        this.i++;
      } else if (this.text[this.i] !== "}") this.fail("expected , or }");
      members.push(member);
    }
    const close = this.i++;
    const value = {};
    for (const m of members) value[m.key] = m.value.value;
    return { type: "object", start, close, end: this.i, members, value };
  }
}

function parseJsonc(text) {
  const p = new Parser(text);
  const root = p.value();
  p.ws();
  if (p.i !== text.length) p.fail("trailing content");
  return root;
}

function deepEqual(a, b) {
  return JSON.stringify(canonical(a)) === JSON.stringify(canonical(b));
}

function canonical(v) {
  if (Array.isArray(v)) return v.map(canonical);
  if (v && typeof v === "object") return Object.fromEntries(Object.keys(v).sort().map((k) => [k, canonical(v[k])]));
  return v;
}

function lineIndent(text, pos) {
  let s = pos;
  while (s > 0 && text[s - 1] !== "\n") s--;
  let e = s;
  while (text[e] === " " || text[e] === "\t") e++;
  return { indent: text.slice(s, e), startsLine: e === pos };
}

function indentUnit(text, root) {
  const first = root.members[0];
  if (first) {
    const own = lineIndent(text, root.start).indent;
    const m = lineIndent(text, first.keyStart);
    if (m.startsLine && m.indent.length > own.length) return m.indent.slice(own.length);
  }
  return "  ";
}

function render(value, unit, indent, eol) {
  return JSON.stringify(value, null, unit).split("\n").join(eol + indent);
}

function memberIndent(text, obj, unit) {
  const last = obj.members[obj.members.length - 1];
  if (last) {
    const li = lineIndent(text, last.keyStart);
    if (li.startsLine) return li.indent;
  }
  return lineIndent(text, obj.start).indent + unit;
}

function insertMember(text, obj, key, value, unit, eol) {
  const indent = memberIndent(text, obj, unit);
  const member = JSON.stringify(key) + ": " + render(value, unit, indent, eol);
  if (obj.members.length) {
    const at = obj.members[obj.members.length - 1].valueEnd;
    return { at, fragment: "," + eol + indent + member };
  }
  const at = obj.start + 1;
  return { at, fragment: eol + indent + member + eol + lineIndent(text, obj.start).indent };
}

function find(obj, key) {
  const members = obj && obj.type === "object" ? obj.members : [];
  for (let k = members.length - 1; k >= 0; k--) if (members[k].key === key) return { member: members[k], index: k };
  return null;
}

function removeMember(text, obj, index) {
  const ms = obj.members;
  if (ms.length === 1) return text.slice(0, obj.start + 1) + text.slice(obj.close);
  if (index < ms.length - 1) return text.slice(0, ms[index].keyStart) + text.slice(ms[index + 1].keyStart);
  return text.slice(0, ms[index - 1].valueEnd) + text.slice(ms[index].valueEnd);
}

function jsonAdd(fmt, file, name, entry, old) {
  const exists = fs.existsSync(file);
  const text = exists ? fs.readFileSync(file, "utf8") : "";
  if (!text.trim()) {
    const created = JSON.stringify({ [fmt.container]: { [name]: entry } }, null, 2) + "\n";
    if (exists && text) return { status: "conflict", reason: "the file holds only whitespace" };
    return { status: "added", text: created, record: { created: "file", fragment: created } };
  }
  const root = parseJsonc(text);
  if (root.type !== "object") return { status: "conflict", reason: "the top level is not an object" };
  const eol = text.includes("\r\n") ? "\r\n" : "\n";
  const unit = indentUnit(text, root);
  const box = find(root, fmt.container);
  if (box && box.member.value.type !== "object") return { status: "conflict", reason: `${fmt.container} is not an object` };
  const have = box && find(box.member.value, name);
  if (have) {
    if (!deepEqual(have.member.value.value, entry)) return { status: "conflict", reason: `the ${name} entry differs from the pinned one` };
    return old && deepEqual(old.entry, entry) ? { status: "present", record: old } : { status: "foreign" };
  }
  let ins;
  let created = "none";
  if (box) ins = insertMember(text, box.member.value, name, entry, unit, eol);
  else {
    ins = insertMember(text, root, fmt.container, { [name]: entry }, unit, eol);
    created = "container";
  }
  const next = text.slice(0, ins.at) + ins.fragment + text.slice(ins.at);
  parseJsonc(next);
  return { status: "added", text: next, record: { created, fragment: ins.fragment, eol } };
}

function jsonRemove(rec, text) {
  const fmt = FORMATS[rec.format];
  const root = parseJsonc(text);
  const box = find(root, fmt.container);
  const have = box && find(box.member.value, rec.name);
  if (!have) return { status: "absent" };
  if (!deepEqual(have.member.value.value, rec.entry)) return { status: "changed" };
  if (rec.created === "file" && text === rec.fragment) return { status: "removed", unlink: true };
  const at = text.indexOf(rec.fragment);
  if (at >= 0 && text.indexOf(rec.fragment, at + 1) < 0 && at <= have.member.keyStart && have.member.valueEnd <= at + rec.fragment.length) {
    const next = text.slice(0, at) + text.slice(at + rec.fragment.length);
    parseJsonc(next);
    return { status: "removed", text: next };
  }
  let next;
  if (rec.created !== "none" && box.member.value.members.length === 1) next = removeMember(text, root, box.index);
  else next = removeMember(text, box.member.value, have.index);
  parseJsonc(next);
  return { status: "removed", text: next };
}

// ------------------------------------------------------------------ TOML (Codex)

const tomlString = (s) => JSON.stringify(String(s));
const tomlKey = (k) => (/^[A-Za-z0-9_-]+$/.test(k) ? k : JSON.stringify(k));

function tomlBlock(container, name, spec, eol) {
  const lines = [
    `[${container}.${tomlKey(name)}]`,
    `command = ${tomlString(spec.command)}`,
    `args = [${spec.args.map(tomlString).join(", ")}]`,
  ];
  const env = Object.entries(spec.env || {});
  if (env.length) lines.push(`env = { ${env.map(([k, v]) => `${tomlKey(k)} = ${tomlString(v)}`).join(", ")} }`);
  return lines.join(eol) + eol;
}

function escapeRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function tomlMentions(text, container, name) {
  const n = `(?:${escapeRe(name)}|"${escapeRe(name)}"|'${escapeRe(name)}')`;
  const header = new RegExp(`^\\s*\\[\\s*${container}\\s*\\.\\s*${n}\\s*[\\].]`);
  const parent = new RegExp(`^\\s*\\[\\s*${container}\\s*\\]\\s*(?:#.*)?$`);
  const anyHeader = /^\s*\[/;
  const dotted = new RegExp(`^\\s*${container}\\s*[.=]`);
  const keyLine = new RegExp(`^\\s*${n}\\s*[.=]`);
  let inParent = false;
  let seenHeader = false;
  for (const line of text.split(/\r?\n/)) {
    if (header.test(line)) return true;
    if (anyHeader.test(line)) {
      seenHeader = true;
      inParent = parent.test(line);
      continue;
    }
    if (!seenHeader && dotted.test(line)) return true;
    if (inParent && keyLine.test(line)) return true;
  }
  return false;
}

function tomlTailOk(rest) {
  for (const line of rest.split(/\r?\n/)) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    return t.startsWith("[");
  }
  return true;
}

function tomlAdd(fmt, file, name, spec, old) {
  const exists = fs.existsSync(file);
  const text = exists ? fs.readFileSync(file, "utf8") : "";
  const eol = text.includes("\r\n") ? "\r\n" : "\n";
  const block = tomlBlock(fmt.container, name, spec, eol);
  const entry = { command: spec.command, args: spec.args, env: spec.env || {} };
  if (text.includes(block)) return old && deepEqual(old.entry, entry) ? { status: "present", record: old } : { status: "foreign" };
  if (tomlMentions(text, fmt.container, name)) return { status: "conflict", reason: `${fmt.container}.${name} is already defined` };
  if (!text) return { status: "added", text: block, record: { created: "file", fragment: block, entry, eol } };
  const fragment = (text.endsWith("\n") ? "" : eol) + eol + block;
  return { status: "added", text: text + fragment, record: { created: "none", fragment, entry, eol } };
}

function tomlRemove(rec, text) {
  const block = tomlBlock(FORMATS.codex.container, rec.name, rec.entry, rec.eol || "\n");
  if (rec.created === "file" && text === rec.fragment) return { status: "removed", unlink: true };
  for (const piece of [rec.fragment, block]) {
    const at = text.lastIndexOf(piece);
    if (at < 0 || text.indexOf(piece) !== at) continue;
    if (!tomlTailOk(text.slice(at + piece.length))) return { status: "changed" };
    return { status: "removed", text: text.slice(0, at) + text.slice(at + piece.length) };
  }
  return { status: tomlMentions(text, FORMATS.codex.container, rec.name) ? "changed" : "absent" };
}

// ------------------------------------------------------------------ files

function target(file) {
  try {
    return fs.realpathSync(file);
  } catch {
    return file;
  }
}

function writeAtomic(file, text) {
  const real = target(file);
  let mode = 0o644;
  try {
    mode = fs.statSync(real).mode & 0o777;
  } catch {
    // new file
  }
  const tmp = path.join(path.dirname(real), `.${path.basename(real)}.po-${process.pid}`);
  fs.writeFileSync(tmp, text, { encoding: "utf8", mode });
  fs.chmodSync(tmp, mode);
  fs.renameSync(tmp, real);
}

function resolveFile(format, file) {
  if (format !== "opencode" || fs.existsSync(file)) return file;
  const jsonc = file.replace(/\.json$/, ".jsonc");
  return jsonc !== file && fs.existsSync(jsonc) ? jsonc : file;
}

function expandSpec(spec, packageDir) {
  const sub = (s) => String(s).split("{PACKAGE}").join(packageDir);
  return {
    command: sub(spec.command),
    args: (spec.args || []).map(sub),
    env: Object.fromEntries(Object.entries(spec.env || {}).map(([k, v]) => [k, sub(v)])),
  };
}

// ------------------------------------------------------------------ commands

function mcpAdd([format, file, name, specB64, packageDir, oldB64]) {
  const fmt = FORMATS[format];
  if (!fmt) die(`unknown MCP format ${format}`);
  const spec = expandSpec(unb64(specB64), path.resolve(packageDir));
  const old = oldB64 && oldB64 !== "-" ? unb64(oldB64) : null;
  const resolved = resolveFile(format, file);
  let result;
  try {
    if (fmt.kind === "toml") result = tomlAdd(fmt, resolved, name, spec, old);
    else result = jsonAdd(fmt, resolved, name, fmt.entry(spec), old);
  } catch (error) {
    result = { status: "conflict", reason: `cannot parse ${resolved}: ${error.message}` };
  }
  if (result.status === "added") {
    if (fmt.kind !== "toml") result.record.entry = fmt.entry(spec);
    writeAtomic(resolved, result.text);
  }
  if (result.reason) process.stderr.write(`pack_helper: ${result.reason}\n`);
  const record = result.record ? b64({ format, file: resolved, name, ...result.record }) : "-";
  process.stdout.write(`${result.status}\t${resolved}\t${record}\n`);
}

function mcpRemove([recB64]) {
  const rec = unb64(recB64);
  if (!fs.existsSync(rec.file)) {
    process.stdout.write("absent\n");
    return;
  }
  const text = fs.readFileSync(rec.file, "utf8");
  let result;
  try {
    result = FORMATS[rec.format].kind === "toml" ? tomlRemove(rec, text) : jsonRemove(rec, text);
  } catch (error) {
    process.stderr.write(`pack_helper: cannot parse ${rec.file}: ${error.message}\n`);
    result = { status: "changed" };
  }
  if (result.unlink) fs.unlinkSync(target(rec.file));
  else if (result.text !== undefined) writeAtomic(rec.file, result.text);
  process.stdout.write(`${result.status}\n`);
}

function npmCheck([prefix, name, version, integrity]) {
  let lock;
  let pkg;
  try {
    lock = JSON.parse(fs.readFileSync(path.join(prefix, "package-lock.json"), "utf8"));
    pkg = JSON.parse(fs.readFileSync(path.join(prefix, "node_modules", name, "package.json"), "utf8"));
  } catch {
    process.stdout.write("absent\n");
    process.exit(3);
  }
  const entry = (lock.packages || {})[`node_modules/${name}`];
  if (!entry) {
    process.stdout.write("absent\n");
    process.exit(3);
  }
  if (entry.version !== version || pkg.version !== version) {
    process.stdout.write(`version ${entry.version || "?"}/${pkg.version || "?"}, pinned ${version}\n`);
    process.exit(4);
  }
  if (entry.integrity !== integrity) {
    process.stdout.write(`integrity ${entry.integrity || "none"}, pinned ${integrity}\n`);
    process.exit(4);
  }
  process.stdout.write("ok\n");
}

const [command, ...rest] = process.argv.slice(2);
switch (command) {
  case "node-check":
    if (!satisfies(process.versions.node, rest[0] || "")) {
      process.stdout.write(`Node.js ${process.versions.node} does not satisfy ${rest[0]}\n`);
      process.exit(1);
    }
    process.stdout.write("ok\n");
    break;
  case "platform":
    process.stdout.write(`${process.platform}-${process.arch}\n`);
    break;
  case "npm-check":
    npmCheck(rest);
    break;
  case "mcp-add":
    mcpAdd(rest);
    break;
  case "mcp-remove":
    mcpRemove(rest);
    break;
  default:
    die("usage: pack_helper.mjs node-check|platform|npm-check|mcp-add|mcp-remove ...");
}
