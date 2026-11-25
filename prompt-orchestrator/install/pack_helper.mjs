#!/usr/bin/env node
// pack_helper.mjs: MCP registration and npm checks for prompt-orchestrator packs.
//
// install.sh and install.ps1 call this helper for packs that carry an "npm" or "mcp" object
// (packs/README.md). It needs Node.js 18 or later and the standard library only.
//
//   node pack_helper.mjs node-check RANGE
//   node pack_helper.mjs platform
//   node pack_helper.mjs npm-check PREFIX NAME VERSION INTEGRITY
//   node pack_helper.mjs mcp-add FORMAT FILE NAME SPEC_B64 PACKAGE_DIR [RECORD_B64 [OTHERS]]
//   node pack_helper.mjs mcp-remove RECORD_B64
//   node pack_helper.mjs skills-index MANIFEST ROOT OUT
//   node pack_helper.mjs hooks-groups staged FILE STAGE SKILL DEST
//   node pack_helper.mjs hooks-groups spec LAUNCHER SPEC
//   node pack_helper.mjs hooks-add FILE GROUPS_B64 [RECORD_B64]
//
// mcp-add prints "status<TAB>file<TAB>record". The status is added, present, foreign or
// conflict. The record is base64 JSON that mcp-remove needs, or "-". mcp-remove prints removed,
// absent or changed. An edit touches only the one server entry: it inserts or deletes one text
// fragment and leaves every other byte of the file as it was. OTHERS lists the records of the other
// entries the installer manages, comma separated. An entry added next to them inherits their claim
// on the server container and the file, so the last removal also removes a container or a file that
// the installer created, whichever entry goes first.
//
// skills-index writes the index of the po-skills MCP server to OUT. It reads the skills that the
// manifest records for the owners pack:<pack>:<set>:mcp under ROOT (<data_home>/skills-mcp) and
// takes each name and description from the SKILL.md front matter. It prints the skill count.
//
// The hooks commands serve a release pack in mode mcp. hooks-groups prints the hook groups as base64
// JSON, or "-" when there are none. Source staged reads a settings file that the release engine wrote
// under the folder STAGE. It keeps each group whose strings name the skill folder STAGE/.../SKILL and
// writes DEST in place of that folder. Source spec builds one group per line of SPEC, "event<TAB>
// matcher<TAB>timeout<TAB>status" (matcher "-" for none), around the command "LAUNCHER" hook.
// hooks-add appends each group to the array hooks.<event> of FILE as one text fragment and prints
// "status<TAB>file<TAB>record" like mcp-add. mcp-remove takes that record too. It deletes the
// fragments in reverse order, so the file returns to its bytes before the install. It also removes a
// hooks object, an event array or a file that hooks-add created, once that part is empty.

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
    return { type: "array", start, end: this.i, items, value: items.map((x) => x.value) };
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

const ownsFile = (r) => Boolean(r.fileOwned || r.created === "file");
const ownsContainer = (r) => Boolean(r.containerOwned || r.created === "container" || r.created === "file");

function jsonAdd(fmt, file, name, entry, old, others) {
  const exists = fs.existsSync(file);
  const text = exists ? fs.readFileSync(file, "utf8") : "";
  if (!text.trim()) {
    const created = JSON.stringify({ [fmt.container]: { [name]: entry } }, null, 2) + "\n";
    if (exists && text) return { status: "conflict", reason: "the file holds only whitespace" };
    return { status: "added", text: created, record: { created: "file", fragment: created, fileOwned: true, containerOwned: true } };
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
  let containerOwned;
  if (box) {
    ins = insertMember(text, box.member.value, name, entry, unit, eol);
    const ours = new Set(others.map((r) => r.name));
    containerOwned = box.member.value.members.every((m) => ours.has(m.key)) && others.some(ownsContainer);
  } else {
    ins = insertMember(text, root, fmt.container, { [name]: entry }, unit, eol);
    created = "container";
    containerOwned = true;
  }
  const next = text.slice(0, ins.at) + ins.fragment + text.slice(ins.at);
  parseJsonc(next);
  return { status: "added", text: next,
    record: { created, fragment: ins.fragment, eol, containerOwned, fileOwned: others.some(ownsFile) } };
}

// After an entry is gone: drop the server container when the installer created it and it is empty,
// then delete the file when the installer created it and it holds an empty object.
function jsonTidy(rec, fmt, text) {
  let next = text;
  let root = parseJsonc(next);
  const box = find(root, fmt.container);
  if (ownsContainer(rec) && box && box.member.value.type === "object" && !box.member.value.members.length) {
    next = removeMember(next, root, box.index);
    root = parseJsonc(next);
  }
  if (ownsFile(rec) && root.type === "object" && !root.members.length) return { status: "removed", unlink: true };
  return { status: "removed", text: next };
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
    return jsonTidy(rec, fmt, text.slice(0, at) + text.slice(at + rec.fragment.length));
  }
  let next;
  if (rec.created !== "none" && box.member.value.members.length === 1) next = removeMember(text, root, box.index);
  else next = removeMember(text, box.member.value, have.index);
  return jsonTidy(rec, fmt, next);
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

function tomlAdd(fmt, file, name, spec, old, others) {
  const exists = fs.existsSync(file);
  const text = exists ? fs.readFileSync(file, "utf8") : "";
  const eol = text.includes("\r\n") ? "\r\n" : "\n";
  const block = tomlBlock(fmt.container, name, spec, eol);
  const entry = { command: spec.command, args: spec.args, env: spec.env || {} };
  if (text.includes(block)) return old && deepEqual(old.entry, entry) ? { status: "present", record: old } : { status: "foreign" };
  if (tomlMentions(text, fmt.container, name)) return { status: "conflict", reason: `${fmt.container}.${name} is already defined` };
  if (!text) return { status: "added", text: block, record: { created: "file", fragment: block, entry, eol, fileOwned: true } };
  const fragment = (text.endsWith("\n") ? "" : eol) + eol + block;
  return { status: "added", text: text + fragment, record: { created: "none", fragment, entry, eol, fileOwned: others.some(ownsFile) } };
}

function tomlRemove(rec, text) {
  const block = tomlBlock(FORMATS.codex.container, rec.name, rec.entry, rec.eol || "\n");
  if (rec.created === "file" && text === rec.fragment) return { status: "removed", unlink: true };
  for (const piece of [rec.fragment, block]) {
    const at = text.lastIndexOf(piece);
    if (at < 0 || text.indexOf(piece) !== at) continue;
    if (!tomlTailOk(text.slice(at + piece.length))) return { status: "changed" };
    const next = text.slice(0, at) + text.slice(at + piece.length);
    if (ownsFile(rec) && !next.trim()) return { status: "removed", unlink: true };
    return { status: "removed", text: next };
  }
  return { status: tomlMentions(text, FORMATS.codex.container, rec.name) ? "changed" : "absent" };
}

// ------------------------------------------------------------------ hook groups (release packs)

function hookArray(text, event) {
  const root = parseJsonc(text);
  if (root.type !== "object") throw new Error("the top level is not an object");
  const box = find(root, "hooks");
  if (box && box.member.value.type !== "object") throw new Error("hooks is not an object");
  const arr = box && find(box.member.value, event);
  if (arr && arr.member.value.type !== "array") throw new Error(`hooks.${event} is not an array`);
  return { root, box, arr };
}

function countGroup(text, event, group) {
  const { arr } = hookArray(text, event);
  return arr ? arr.member.value.items.filter((it) => deepEqual(it.value, group)).length : 0;
}

function insertElement(text, arr, value, unit, eol) {
  const items = arr.items;
  const own = lineIndent(text, arr.start).indent;
  if (items.length) {
    const last = items[items.length - 1];
    const li = lineIndent(text, last.start);
    const indent = li.startsLine ? li.indent : own + unit;
    return { at: last.end, fragment: "," + eol + indent + render(value, unit, indent, eol) };
  }
  const indent = own + unit;
  return { at: arr.start + 1, fragment: eol + indent + render(value, unit, indent, eol) + eol + own };
}

function removeElement(text, arr, index) {
  const items = arr.items;
  if (items.length === 1) return text.slice(0, arr.start + 1) + text.slice(arr.end - 1);
  if (index < items.length - 1) return text.slice(0, items[index].start) + text.slice(items[index + 1].start);
  return text.slice(0, items[index - 1].end) + text.slice(items[index].end);
}

function hookInsert(text, event, group) {
  if (!text.trim()) {
    const created = JSON.stringify({ hooks: { [event]: [group] } }, null, 2) + "\n";
    return { text: created, item: { event, group, created: "file", fragment: created } };
  }
  const { root, box, arr } = hookArray(text, event);
  const eol = text.includes("\r\n") ? "\r\n" : "\n";
  const unit = indentUnit(text, root);
  let ins;
  let created;
  if (arr) {
    ins = insertElement(text, arr.member.value, group, unit, eol);
    created = "none";
  } else if (box) {
    ins = insertMember(text, box.member.value, event, [group], unit, eol);
    created = "event";
  } else {
    ins = insertMember(text, root, "hooks", { [event]: [group] }, unit, eol);
    created = "hooks";
  }
  const next = text.slice(0, ins.at) + ins.fragment + text.slice(ins.at);
  parseJsonc(next);
  return { text: next, item: { event, group, created, fragment: ins.fragment } };
}

// Drop an event array, then the hooks object, then the file, as far as hooks-add created them.
function hookTidy(text, item) {
  let next = text;
  const deep = { none: 0, event: 1, hooks: 2, file: 3 }[item.created] || 0;
  let { root, box, arr } = hookArray(next, item.event);
  if (deep >= 1 && arr && !arr.member.value.items.length) {
    next = removeMember(next, box.member.value, arr.index);
    ({ root, box } = hookArray(next, item.event));
  }
  if (deep >= 2 && box && !box.member.value.members.length) {
    next = removeMember(next, root, box.index);
    root = parseJsonc(next);
  }
  if (deep >= 3 && !root.members.length) return { unlink: true };
  return { text: next };
}

function hookRemoveItem(text, item) {
  if (item.created === "file" && text === item.fragment) return { status: "removed", unlink: true };
  const before = countGroup(text, item.event, item.group);
  if (!before) return { status: "absent", text };
  const at = text.indexOf(item.fragment);
  if (at >= 0 && text.indexOf(item.fragment, at + 1) < 0) {
    const next = text.slice(0, at) + text.slice(at + item.fragment.length);
    try {
      if (countGroup(next, item.event, item.group) === before - 1) return { status: "removed", text: next };
    } catch {
      // the fragment no longer stands alone; fall back to the structure
    }
  }
  const { arr } = hookArray(text, item.event);
  const items = arr.member.value.items;
  let index = -1;
  for (let k = items.length - 1; k >= 0 && index < 0; k--) if (deepEqual(items[k].value, item.group)) index = k;
  const tidy = hookTidy(removeElement(text, arr.member.value, index), item);
  return { status: "removed", ...tidy };
}

function hooksRemove(rec, text) {
  let next = text;
  let removed = false;
  for (const item of [...rec.items].reverse()) {
    const r = hookRemoveItem(next, item);
    if (r.unlink) return { status: "removed", unlink: true };
    if (r.status === "removed") removed = true;
    next = r.text;
  }
  return removed ? { status: "removed", text: next } : { status: "absent" };
}

function escapeStage(stage) {
  return stage.split(/[\\/]+/).filter(Boolean).map(escapeRe).join("[\\\\/]+");
}

function rewrite(value, re, dest) {
  if (typeof value === "string") return value.replace(re, dest);
  if (Array.isArray(value)) return value.map((v) => rewrite(v, re, dest));
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, rewrite(v, re, dest)]));
  return value;
}

function hooksGroups([source, ...args]) {
  const groups = [];
  if (source === "staged") {
    const [file, stage, skill, dest] = args;
    if (!file || !stage || !skill || !dest) die("usage: pack_helper.mjs hooks-groups staged FILE STAGE SKILL DEST");
    const lead = /^[\\/]/.test(stage) ? "[\\\\/]+" : "";
    const flags = process.platform === "win32" ? "gi" : "g";
    const re = new RegExp(`${lead}${escapeStage(stage)}[\\\\/]+(?:[^"']*?[\\\\/]+)?${escapeRe(skill)}(?=[\\\\/]|["']|$)`, flags);
    const hooks = (parseJsonc(fs.readFileSync(file, "utf8")).value || {}).hooks || {};
    for (const [event, list] of Object.entries(hooks)) {
      for (const group of Array.isArray(list) ? list : []) {
        const moved = rewrite(group, re, dest);
        if (!deepEqual(moved, group)) groups.push({ event, group: moved });
      }
    }
  } else if (source === "spec") {
    const [launcher, spec] = args;
    if (!launcher || spec === undefined) die("usage: pack_helper.mjs hooks-groups spec LAUNCHER SPEC");
    const command = `"${launcher}" hook`;
    for (const line of spec.split(/\r?\n/)) {
      if (!line.trim()) continue;
      const [event, matcher, timeout, status] = line.split("\t");
      const hook = { type: "command", command, timeout: Number(timeout), statusMessage: status };
      groups.push({ event, group: matcher && matcher !== "-" ? { matcher, hooks: [hook] } : { hooks: [hook] } });
    }
  } else die("usage: pack_helper.mjs hooks-groups staged|spec ...");
  process.stdout.write(groups.length ? `${b64(groups)}\n` : "-\n");
}

function hooksAdd([file, groupsB64, oldB64]) {
  if (!file || !groupsB64) die("usage: pack_helper.mjs hooks-add FILE GROUPS_B64 [RECORD_B64]");
  const groups = groupsB64 === "-" ? [] : unb64(groupsB64);
  const old = oldB64 && oldB64 !== "-" ? unb64(oldB64) : null;
  let text = fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "";
  const items = [];
  let added = 0;
  try {
    for (const { event, group } of groups) {
      if (text.trim() && countGroup(text, event, group)) {
        const was = old && (old.items || []).find((it) => it.event === event && deepEqual(it.group, group));
        if (was) items.push(was);
        else process.stderr.write(`pack_helper: ${file} already holds a ${event} hook group of its own; the installer leaves it unmanaged\n`);
        continue;
      }
      const r = hookInsert(text, event, group);
      text = r.text;
      items.push(r.item);
      added++;
    }
  } catch (error) {
    process.stderr.write(`pack_helper: cannot edit ${file}: ${error.message}\n`);
    process.stdout.write(`conflict\t${file}\t-\n`);
    return;
  }
  if (added) writeAtomic(file, text);
  const record = items.length ? b64({ format: "hooks", file, name: "hooks", items }) : "-";
  process.stdout.write(`${added ? "added" : items.length ? "present" : "foreign"}\t${file}\t${record}\n`);
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

function mcpAdd([format, file, name, specB64, packageDir, oldB64, othersCsv]) {
  const fmt = FORMATS[format];
  if (!fmt) die(`unknown MCP format ${format}`);
  const spec = expandSpec(unb64(specB64), path.resolve(packageDir));
  const old = oldB64 && oldB64 !== "-" ? unb64(oldB64) : null;
  const resolved = resolveFile(format, file);
  const others = String(othersCsv || "").split(",").filter((x) => x && x !== "-").map(unb64)
    .filter((r) => r.file === resolved && r.format === format && r.name !== name);
  let result;
  try {
    if (fmt.kind === "toml") result = tomlAdd(fmt, resolved, name, spec, old, others);
    else result = jsonAdd(fmt, resolved, name, fmt.entry(spec), old, others);
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
    if (rec.format === "hooks") result = hooksRemove(rec, text);
    else result = FORMATS[rec.format].kind === "toml" ? tomlRemove(rec, text) : jsonRemove(rec, text);
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

// ------------------------------------------------------------------ po-skills index

// Reads the front-matter keys that the skill packs use: plain scalars, single- and double-quoted
// scalars over one or more lines, and the block scalars >, >-, |, |-. Nested maps are skipped.
function frontMatter(text) {
  const m = /^﻿?---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/.exec(text);
  if (!m) return null;
  const lines = m[1].split(/\r?\n/);
  const out = {};
  for (let i = 0; i < lines.length; i++) {
    const km = /^([A-Za-z0-9_-]+):(?:\s+(.*))?$/.exec(lines[i]);
    if (!km) continue;
    const key = km[1];
    let raw = (km[2] || "").replace(/\s+#.*$/, "").trim();
    if (/^[>|][+-]?$/.test(raw)) {
      const block = [];
      while (i + 1 < lines.length && (lines[i + 1].trim() === "" || /^\s/.test(lines[i + 1]))) block.push(lines[++i]);
      const indent = Math.min(...block.filter((l) => l.trim()).map((l) => l.match(/^\s*/)[0].length));
      const body = block.map((l) => l.slice(Number.isFinite(indent) ? indent : 0));
      let value;
      if (raw[0] === "|") value = body.join("\n");
      else {
        value = "";
        for (const l of body) value += l === "" ? "\n" : (value && !value.endsWith("\n") ? " " : "") + l;
      }
      value = value.replace(/\n+$/, "");
      out[key] = raw.endsWith("-") ? value : value + "\n";
      continue;
    }
    const quote = raw[0] === "'" || raw[0] === '"' ? raw[0] : "";
    if (quote) {
      let joined = km[2].trim();
      while (!closed(joined, quote) && i + 1 < lines.length) {
        const next = lines[++i].trim();
        joined += next === "" ? "\n" : (joined.endsWith("\n") ? "" : " ") + next;
      }
      out[key] = unquote(joined, quote);
      continue;
    }
    while (i + 1 < lines.length && /^\s+\S/.test(lines[i + 1]) && !/^\s*-\s/.test(lines[i + 1]) && raw !== "") raw += " " + lines[++i].trim();
    out[key] = raw;
  }
  return out;
}

function closed(text, quote) {
  if (text.length < 2 || !text.endsWith(quote)) return false;
  if (quote === '"') {
    let backslashes = 0;
    for (let k = text.length - 2; k >= 0 && text[k] === "\\"; k--) backslashes++;
    return backslashes % 2 === 0;
  }
  const inner = text.slice(1, -1).replace(/''/g, "");
  return !inner.includes("'");
}

function unquote(text, quote) {
  const inner = text.slice(1, -1);
  if (quote === "'") return inner.replace(/''/g, "'");
  return JSON.parse(`"${inner.replace(/\n/g, "\\n").replace(/\\'/g, "'")}"`);
}

const ABBREVIATIONS = /(?:^|\s)(?:e\.g|i\.e|etc|vs|cf|approx|incl|[A-Za-z])\.$/;

// The first sentence of a description, at most 200 characters.
function summary(description) {
  const flat = String(description).replace(/\s+/g, " ").trim();
  let cut = flat;
  const re = /[.!?](?=\s|$)/g;
  let m;
  while ((m = re.exec(flat))) {
    const head = flat.slice(0, m.index + 1);
    if (ABBREVIATIONS.test(head)) continue;
    cut = head;
    break;
  }
  if (cut.length <= 200) return cut;
  const room = cut.slice(0, 197);
  const space = room.lastIndexOf(" ");
  return (space > 120 ? room.slice(0, space) : room).replace(/[\s,;:]+$/, "") + "...";
}

function skillsIndex([manifest, root, outFile]) {
  if (!manifest || !root || !outFile) die("usage: pack_helper.mjs skills-index MANIFEST ROOT OUT");
  const base = path.resolve(root);
  const skills = [];
  const lines = fs.existsSync(manifest) ? fs.readFileSync(manifest, "utf8").split(/\r?\n/) : [];
  for (const line of lines) {
    const [owner, kind, file] = line.split("\t");
    const om = /^pack:([a-z0-9-]+):([a-z0-9-]+):mcp$/.exec(owner || "");
    if (!om || kind !== "f") continue;
    const parts = path.relative(base, path.resolve(file)).split(/[\\/]/);
    if (parts.length !== 3 || parts[0] !== om[1] || parts[2] !== "SKILL.md") continue;
    const folder = path.join(base, parts[0], parts[1]);
    let fm = null;
    try {
      fm = frontMatter(fs.readFileSync(path.join(folder, "SKILL.md"), "utf8"));
    } catch (error) {
      process.stderr.write(`pack_helper: cannot read ${path.join(folder, "SKILL.md")}: ${error.message}\n`);
    }
    const name = fm && fm.name ? String(fm.name) : parts[1];
    const description = fm && fm.description ? String(fm.description).trim() : "";
    skills.push({ name, pack: om[1], set: om[2], summary: summary(description || name), description, path: folder });
  }
  const order = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  skills.sort((a, b) => order(a.pack, b.pack) || order(a.set, b.set) || order(a.name, b.name));
  const packs = [];
  for (const s of skills) {
    let p = packs.find((x) => x.id === s.pack);
    if (!p) packs.push((p = { id: s.pack, sets: [] }));
    const set = p.sets.find((x) => x.id === s.set);
    if (set) set.count++;
    else p.sets.push({ id: s.set, count: 1 });
  }
  const index = { schema: 1, server: "po-skills", skills, packs };
  fs.writeFileSync(outFile, JSON.stringify(index, null, 1) + "\n", "utf8");
  process.stdout.write(`${skills.length}\n`);
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
  case "skills-index":
    skillsIndex(rest);
    break;
  case "hooks-groups":
    hooksGroups(rest);
    break;
  case "hooks-add":
    hooksAdd(rest);
    break;
  default:
    die("usage: pack_helper.mjs node-check|platform|npm-check|mcp-add|mcp-remove|skills-index|hooks-groups|hooks-add ...");
}
