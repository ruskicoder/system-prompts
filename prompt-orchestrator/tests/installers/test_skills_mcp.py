"""Tests for pack mode mcp: the po-skills MCP server, its index and the install flows.

Run with: python3 -B -m unittest discover -s tests/installers -t tests/installers -v

The server tests drive install/po_skills_server.mjs over stdio with JSON-RPC. The index for those
tests comes from install/pack_helper.mjs skills-index over every cyber-skills skill (818). The flows
install packs in a temporary HOME with the bash and PowerShell installers and need Node.js.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import unittest
from pathlib import Path

from test_installers import BASH, FIXTURES, PWSH, ROOT, Sandbox, files_under, files_under_without_pwsh, generate

sys.path.insert(0, str(ROOT / "tools"))
import validate_packs  # noqa: E402

NODE = shutil.which("node")
HELPER = ROOT / "install" / "pack_helper.mjs"
SERVER = ROOT / "install" / "po_skills_server.mjs"
SPEC = json.loads((ROOT / "install" / "spec.json").read_text(encoding="utf-8"))
NAME = SPEC["skills_mcp"]["name"]
MODERN = "2026-07-28"
META = "io.modelcontextprotocol/protocolVersion"
TOOLS = ("claude", "codex", "opencode")
# Config files a user already has for the three tools of the acceptance flow.
CONFIGS = {
    ".claude.json": '{\n  "numStartups": 7,\n  "mcpServers": {\n    "other": {"command": "x", "args": []}\n  }\n}\n',
    ".codex/config.toml": 'model = "o3"\n\n[mcp_servers.other]\ncommand = "y"',
    ".config/opencode/opencode.json": '{\r\n  "$schema": "https://opencode.ai/config.json"\r\n}\r\n',
}
SKILL_DIRS = (".claude/skills", ".agents/skills", ".config/opencode/skills")


def pack_json(pack_id: str) -> dict:
    return json.loads((ROOT / "packs" / pack_id / "pack.json").read_text(encoding="utf-8"))


def pack_skills(pack_id: str, sets: tuple[str, ...] | None = None) -> set[str]:
    return {skill for s in pack_json(pack_id)["sets"] if sets is None or s["id"] in sets for skill in s["skills"]}


def build_index(base: Path, packs: tuple[str, ...]) -> Path:
    """Index of the given repository packs, built by the helper from a manifest that records them."""
    root = base / "skills-mcp"
    root.mkdir(parents=True)
    lines = []
    for pack_id in packs:
        os.symlink(ROOT / "packs" / pack_id / "skills", root / pack_id)
        for entry in pack_json(pack_id)["sets"]:
            lines += [f"pack:{pack_id}:{entry['id']}:mcp\tf\t{root / pack_id / skill / 'SKILL.md'}\t-\t-"
                      for skill in entry["skills"]]
    lines.append(f"pack:{packs[0]}:payload\tf\t{root / 'stray' / 'x' / 'SKILL.md'}\t-\t-")
    (base / "manifest.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    index = root / "index.json"
    subprocess.run([NODE, str(HELPER), "skills-index", str(base / "manifest.tsv"), str(root), str(index)],
                   check=True, capture_output=True, text=True)
    return index


class Session:
    """One po-skills server process and a JSON-RPC client over its stdio."""

    def __init__(self, case: unittest.TestCase, *args: str, server: Path = SERVER):
        self.proc = subprocess.Popen([NODE, str(server), *args], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, encoding="utf-8")
        case.addCleanup(self.close)
        self.next_id = 0

    def close(self):
        if self.proc.poll() is None:
            self.proc.stdin.close()
            self.proc.wait(timeout=10)
        self.proc.stdout.close()
        self.proc.stderr.close()

    def raw(self, line: str) -> dict:
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()
        return json.loads(self.proc.stdout.readline())

    def request(self, method: str, params: dict | None = None, modern: bool = False) -> dict:
        self.next_id += 1
        params = dict(params or {})
        if modern:
            params["_meta"] = {META: MODERN, "io.modelcontextprotocol/clientCapabilities": {}}
        reply = self.raw(json.dumps({"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params}))
        assert reply["id"] == self.next_id, reply
        return reply

    def notify(self, method: str) -> None:
        self.proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method}) + "\n")
        self.proc.stdin.flush()

    def call(self, tool: str, arguments: dict, modern: bool = False) -> dict:
        return self.request("tools/call", {"name": tool, "arguments": arguments}, modern)["result"]


def text_of(result: dict) -> str:
    return "".join(c["text"] for c in result["content"])


# ---------------------------------------------------------------------------------- server

@unittest.skipUnless(NODE, "node not installed")
class ServerTests(unittest.TestCase):
    """The server over stdio with the full cyber-skills index."""

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="po skills server ")
        cls.index = build_index(Path(cls.temporary.name), ("cyber-skills",))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def session(self) -> Session:
        return Session(self, "--index", str(self.index))

    def test_initialize_list_search_and_load(self):
        s = self.session()
        init = s.request("initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
                                        "clientInfo": {"name": "test", "version": "1"}})["result"]
        self.assertEqual("2025-11-25", init["protocolVersion"])
        self.assertEqual(NAME, init["serverInfo"]["name"])
        self.assertIn("tools", init["capabilities"])
        self.assertLess(len(init["instructions"]), 300)
        s.notify("notifications/initialized")
        tools = s.request("tools/list")["result"]["tools"]
        self.assertEqual(["search_skills", "load_skill", "list_packs"], [t["name"] for t in tools])
        for tool in tools:
            self.assertLess(len(tool["description"]), 200, tool["name"])
            self.assertEqual("object", tool["inputSchema"]["type"])

        found = text_of(s.call("search_skills", {"query": "ntlm relay"}))
        first = re.match(r"1\. (\S+) \(pack (\S+), set (\S+)\): (.+)", found.splitlines()[0])
        self.assertIsNotNone(first, found)
        name, pack, set_id, summary = first.groups()
        self.assertEqual("cyber-skills", pack)
        self.assertIn("ntlm", name)
        self.assertIn(name, pack_skills("cyber-skills", (set_id,)))
        self.assertLessEqual(len(summary), 200)
        self.assertLessEqual(len(found.splitlines()), 12)

        loaded = s.call("load_skill", {"name": name})
        self.assertNotIn("isError", loaded)
        body = text_of(loaded)
        folder = Path(re.search(r"^Folder: (.+)$", body, re.M).group(1))
        self.assertTrue(folder.is_absolute())
        self.assertTrue(folder.is_dir())
        self.assertTrue((folder / "SKILL.md").is_file())
        self.assertIn(f"name: {name}", body)
        self.assertTrue(body.endswith((folder / "SKILL.md").read_text(encoding="utf-8")))

        listing = text_of(s.call("list_packs", {}))
        self.assertIn("cyber-skills: 818 skills", listing)
        self.assertIn("cyber-skills:cyber-malware: 39 skills", listing)

    def test_version_negotiation(self):
        s = self.session()
        self.assertEqual("2025-11-25", s.request("initialize", {"protocolVersion": "2099-01-01"})["result"]["protocolVersion"])
        self.assertEqual("2024-11-05", s.request("initialize", {"protocolVersion": "2024-11-05"})["result"]["protocolVersion"])

    def test_modern_requests(self):
        s = self.session()
        found = s.request("server/discover", modern=True)["result"]
        self.assertIn(MODERN, found["supportedVersions"])
        self.assertEqual("complete", found["resultType"])
        self.assertEqual(NAME, found["_meta"]["io.modelcontextprotocol/serverInfo"]["name"])
        self.assertIn("ttlMs", found)
        listed = s.request("tools/list", modern=True)["result"]
        self.assertEqual("complete", listed["resultType"])
        self.assertEqual(3, len(listed["tools"]))
        result = s.call("search_skills", {"query": "kerberoasting", "limit": 3}, modern=True)
        self.assertEqual("complete", result["resultType"])
        self.assertIn("kerberoast", text_of(result))
        error = s.raw(json.dumps({"jsonrpc": "2.0", "id": 9, "method": "tools/list",
                                  "params": {"_meta": {META: "1900-01-01"}}}))["error"]
        self.assertEqual(-32022, error["code"])
        self.assertEqual("1900-01-01", error["data"]["requested"])
        self.assertIn(MODERN, error["data"]["supported"])

    def test_errors(self):
        s = self.session()
        self.assertEqual(-32602, s.request("tools/call", {"name": "nope", "arguments": {}})["error"]["code"])
        self.assertTrue(s.call("search_skills", {})["isError"])
        self.assertTrue(s.call("search_skills", {"query": "ntlm", "limit": 0})["isError"])
        missing = s.call("load_skill", {"name": "no-such-skill"})
        self.assertTrue(missing["isError"])
        self.assertIn("search_skills", text_of(missing))
        self.assertEqual(-32601, s.request("resources/list")["error"]["code"])
        parse = s.raw("{not json")
        self.assertEqual((None, -32700), (parse["id"], parse["error"]["code"]))
        s.notify("notifications/cancelled")
        self.assertEqual({}, s.request("ping")["result"])
        self.assertIn("No skill matches", text_of(s.call("search_skills", {"query": "zzqx"})))
        only = text_of(s.call("search_skills", {"query": "malware", "pack": "cyber-skills", "limit": 2}))
        self.assertEqual(2, sum(1 for line in only.splitlines() if re.match(r"\d+\. ", line)))

    def test_index_changes_are_read_and_a_missing_index_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index.json"
            data = json.loads(self.index.read_text(encoding="utf-8"))
            index.write_text(json.dumps(data), encoding="utf-8")
            s = Session(self, "--index", str(index))
            self.assertIn("818 skills", text_of(s.call("list_packs", {})))
            data["skills"] = data["skills"][:5]
            data["packs"] = [{"id": "cyber-skills", "sets": [{"id": "cyber-offense", "count": 5}]}]
            index.write_text(json.dumps(data) + "\n", encoding="utf-8")
            self.assertIn("cyber-skills: 5 skills", text_of(s.call("list_packs", {})))
            index.unlink()
            gone = s.call("list_packs", {})
            self.assertTrue(gone["isError"])
            self.assertIn("no index", text_of(gone))

    @unittest.skipUnless(sys.platform.startswith("linux"), "reads /proc")
    def test_startup_and_memory_with_the_full_index(self):
        start = time.perf_counter()
        s = self.session()
        s.request("initialize", {"protocolVersion": "2025-11-25"})
        self.assertIn("cyber-skills", text_of(s.call("search_skills", {"query": "ntlm relay"})))
        elapsed = time.perf_counter() - start
        status = Path(f"/proc/{s.proc.pid}/status").read_text()
        rss_mb = int(re.search(r"VmHWM:\s+(\d+) kB", status).group(1)) / 1024
        print(f"\npo-skills with 818 skills: first search answered after {elapsed:.3f} s, peak RSS {rss_mb:.1f} MB",
              file=sys.stderr)
        self.assertLess(elapsed, 1.0)
        self.assertLess(rss_mb, 100)


# ---------------------------------------------------------------------------------- helper

@unittest.skipUnless(NODE, "node not installed")
class TwoServersOneConfigTests(unittest.TestCase):
    """A pack's own server and po-skills in one config: both removal orders restore the bytes."""

    FILES = {"claude": ".claude.json", "codex": "config.toml", "cursor": "mcp.json", "gemini": "settings.json",
             "opencode": "opencode.json"}
    BEFORE = {
        "absent": None,
        "no container": {"json": '// mine\n{\n    "theme": "Dracula",\n}\n', "toml": 'model = "o3"'},
        "empty container": {"json": '{"mcpServers": {}, "mcp": {}}\n', "toml": 'model = "o3"\n'},
    }

    def helper(self, *args: str) -> list[str]:
        proc = subprocess.run([NODE, str(HELPER), *args], capture_output=True, text=True)
        self.assertEqual(0, proc.returncode, proc.stderr)
        return proc.stdout.rstrip("\n").split("\t")

    def add(self, fmt: str, path: Path, name: str, others: list[str]) -> str:
        import base64  # noqa: PLC0415
        spec = base64.b64encode(json.dumps({"command": "node", "args": [f"/x/{name}.mjs"], "env": {}}).encode()).decode()
        status, _, record = self.helper("mcp-add", fmt, str(path), name, spec, "/x", "-", ",".join(others) or "-")
        self.assertEqual("added", status)
        return record

    def test_both_orders_for_each_format(self):
        for fmt, rel in self.FILES.items():
            for label, before in self.BEFORE.items():
                for order in ("first added goes first", "last added goes first"):
                    with self.subTest(fmt=fmt, before=label, order=order), tempfile.TemporaryDirectory() as tmp:
                        path = Path(tmp) / rel
                        text = None if before is None else before["toml" if fmt == "codex" else "json"]
                        if text is not None:
                            path.write_bytes(text.encode())
                        rea = self.add(fmt, path, "rea", [])
                        skills = self.add(fmt, path, NAME, [rea])
                        for record in ([rea, skills] if order.startswith("first") else [skills, rea]):
                            self.assertEqual(["removed"], self.helper("mcp-remove", record))
                        if text is None:
                            self.assertFalse(path.exists())
                        else:
                            self.assertEqual(text.encode(), path.read_bytes())

    def test_a_user_entry_keeps_the_container_and_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mcp.json"
            rea = self.add("cursor", path, "rea", [])
            data = json.loads(path.read_text())
            data["mcpServers"]["mine"] = {"command": "x"}
            path.write_text(json.dumps(data, indent=2) + "\n")
            skills = self.add("cursor", path, NAME, [rea])
            self.helper("mcp-remove", rea)
            self.helper("mcp-remove", skills)
            self.assertEqual({"mcpServers": {"mine": {"command": "x"}}}, json.loads(path.read_text()))


# ---------------------------------------------------------------------------------- index

@unittest.skipUnless(NODE, "node not installed")
class IndexTests(unittest.TestCase):
    def test_index_matches_the_front_matter_of_every_pack_skill(self):
        try:
            import yaml  # noqa: F401, PLC0415
        except ImportError:
            self.skipTest("PyYAML not installed; block scalars need it for the comparison")
        packs = tuple(p for p in ("claude-red-offense", "cyber-skills", "logo-design", "rea", "reverse-skill"))
        with tempfile.TemporaryDirectory() as tmp:
            index = json.loads(build_index(Path(tmp), packs).read_text(encoding="utf-8"))
            expected = set().union(*(pack_skills(p) for p in packs))
            self.assertEqual(expected, {s["name"] for s in index["skills"]})
            for skill in index["skills"]:
                data = validate_packs.read_front_matter(Path(skill["path"]) / "SKILL.md")
                self.assertEqual(str(data["description"]).strip(), skill["description"], skill["name"])
                self.assertTrue(0 < len(skill["summary"]) <= 200, skill["name"])
                self.assertNotIn("\n", skill["summary"])
            counts = {(p["id"], s["id"]): s["count"] for p in index["packs"] for s in p["sets"]}
            self.assertEqual(39, counts[("cyber-skills", "cyber-malware")])
            self.assertEqual(818, sum(n for (p, _), n in counts.items() if p == "cyber-skills"))


# ---------------------------------------------------------------------------------- bash flows

def write_configs(home: Path) -> None:
    for rel, text in CONFIGS.items():
        path = home / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode())


def server_entries(home: Path) -> dict[str, int]:
    """How often each config names the po-skills server, parsed and as raw text."""
    claude = json.loads((home / ".claude.json").read_text(encoding="utf-8"))
    opencode = json.loads((home / ".config/opencode/opencode.json").read_text(encoding="utf-8"))
    codex_text = (home / ".codex/config.toml").read_text(encoding="utf-8")
    codex = tomllib.loads(codex_text)
    return {
        "claude": list(claude.get("mcpServers", {})).count(NAME),
        "codex": list(codex.get("mcp_servers", {})).count(NAME),
        "opencode": list(opencode.get("mcp", {})).count(NAME),
        "claude_text": (home / ".claude.json").read_text(encoding="utf-8").count(f'"{NAME}"'),
        "codex_text": codex_text.count(f"[mcp_servers.{NAME}]"),
        "opencode_text": (home / ".config/opencode/opencode.json").read_text(encoding="utf-8").count(f'"{NAME}"'),
    }


@unittest.skipUnless(BASH and NODE, "bash and node required")
class AcceptanceBashTests(unittest.TestCase):
    """The committed install/install.sh with the real packs in mode mcp."""

    tools = ("--tools", ",".join(TOOLS))

    def test_mode_mcp_install_rerun_switch_and_removal(self):
        box = Sandbox(self, ROOT / "install" / "install.sh")
        write_configs(box.home)
        first = box.run("packs", "install", "claude-red-offense", "cyber-skills:cyber-malware", *self.tools)
        self.assertIn(f"MCP server {NAME} ->", first.stdout)
        root = box.data / "skills-mcp"
        installed = pack_skills("claude-red-offense") | pack_skills("cyber-skills", ("cyber-malware",))
        for rel in SKILL_DIRS:
            self.assertFalse((box.home / rel).exists(), rel)
        self.assertEqual({"claude": 1, "codex": 1, "opencode": 1, "claude_text": 1, "codex_text": 1, "opencode_text": 1},
                         server_entries(box.home))
        entry = json.loads((box.home / ".claude.json").read_text())["mcpServers"][NAME]
        self.assertEqual(("stdio", "node", [str(root / "server.mjs")]), (entry["type"], entry["command"], entry["args"]))
        index = json.loads((root / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(installed, {s["name"] for s in index["skills"]})
        for skill in index["skills"]:
            self.assertEqual(root / skill["pack"] / skill["name"], Path(skill["path"]))
            self.assertTrue((Path(skill["path"]) / "SKILL.md").is_file())

        again = box.run("packs", "install", "claude-red-offense", "cyber-skills:cyber-malware", *self.tools)
        self.assertIn("==> no change", again.stdout)
        listing = box.run("packs", "list").stdout
        self.assertIn("[x] cyber-skills:cyber-malware (39 skills) [mcp]", listing)
        self.assertIn("[ ] cyber-skills:cyber-offense (59 skills)", listing)

        # the installed server answers from data_home without --index
        s = Session(self, server=root / "server.mjs")
        self.assertIn("(pack claude-red-offense", text_of(s.call("search_skills", {"query": "sql injection"})))

        box.run("packs", "install", "logo-design", "--mode", "skills", *self.tools)
        for rel in SKILL_DIRS:
            self.assertTrue((box.home / rel / "logo-design" / "SKILL.md").is_file(), rel)
        self.assertIn("==> no change", box.run("packs", "install", "logo-design", *self.tools).stdout)
        box.run("packs", "install", "logo-design", "--mode", "mcp", *self.tools)
        for rel in SKILL_DIRS:
            self.assertFalse((box.home / rel).exists(), rel)
        self.assertTrue((root / "logo-design" / "logo-design" / "SKILL.md").is_file())
        index = json.loads((root / "index.json").read_text(encoding="utf-8"))
        self.assertIn("logo-design", {s["name"] for s in index["skills"]})
        self.assertEqual(1, server_entries(box.home)["claude_text"])

        box.run("packs", "remove", "claude-red-offense", "cyber-skills")
        index = json.loads((root / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(["logo-design"], [s["name"] for s in index["skills"]])
        box.run("packs", "remove", "logo-design")
        for rel, text in CONFIGS.items():
            self.assertEqual(text.encode(), (box.home / rel).read_bytes(), rel)
        self.assertFalse(box.data.exists())
        box.run("uninstall")
        self.assertEqual(set(CONFIGS), {p for p in files_under(box.home) if (box.home / p).is_file()})


@unittest.skipUnless(BASH and NODE, "bash and node required")
class FixtureMcpBashTests(unittest.TestCase):
    """Mode mcp edge cases with the fixture packs."""

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="po mcp fixture ")
        cls.out = Path(cls.temporary.name)
        generate(cls.out, FIXTURES)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def sandbox(self) -> Sandbox:
        return Sandbox(self, self.out / "install.sh")

    def test_tool_without_mcp_config_gets_copies_and_package_entry_skill_is_served(self):
        box = self.sandbox()
        proc = box.run("packs", "install", "fixture-skills:alpha,fixture-package", "--tools", "claude,antigravity")
        self.assertIn("Antigravity has no MCP config that the installer edits: it gets skill copies", proc.stdout)
        self.assertTrue((box.home / ".gemini" / "config" / "skills" / "fixture-one" / "SKILL.md").is_file())
        self.assertFalse((box.home / ".claude" / "skills").exists())
        root = box.data / "skills-mcp"
        self.assertTrue((root / "fixture-package" / "fixture-entry" / "SKILL.md").is_file())
        self.assertEqual("payload data\n", (box.data / "packages" / "fixture-package" / "data" / "info.txt").read_text())
        self.assertIn(NAME, json.loads((box.home / ".claude.json").read_text())["mcpServers"])
        names = {s["name"] for s in json.loads((root / "index.json").read_text())["skills"]}
        self.assertEqual({"fixture-one", "fixture-two", "fixture-entry"}, names)
        box.run("uninstall")
        self.assertEqual([], files_under(box.home))

    def test_switch_to_skills_unregisters_the_last_server(self):
        box = self.sandbox()
        box.run("packs", "install", "fixture-skills", "--tools", "claude,codex")
        self.assertTrue((box.home / ".claude.json").is_file())
        box.run("packs", "install", "fixture-skills", "--tools", "claude,codex", "--mode", "skills")
        self.assertTrue((box.home / ".claude" / "skills" / "fixture-one" / "SKILL.md").is_file())
        self.assertTrue((box.home / ".agents" / "skills" / "fixture-three" / "SKILL.md").is_file())
        self.assertFalse((box.data / "skills-mcp").exists())
        self.assertFalse((box.home / ".claude.json").exists())
        self.assertFalse((box.home / ".codex" / "config.toml").exists())
        self.assertIn("[x] fixture-skills:alpha (2 skills) [skills]", box.run("packs", "list").stdout)
        box.run("uninstall")
        self.assertEqual([], files_under(box.home))

    def test_uninstall_of_one_tool_removes_its_entry_only(self):
        box = self.sandbox()
        box.run("packs", "install", "fixture-skills:beta", "--tools", "claude,codex")
        box.run("uninstall", "--tools", "codex")
        self.assertFalse((box.home / ".codex").exists())
        self.assertIn(NAME, json.loads((box.home / ".claude.json").read_text())["mcpServers"])
        self.assertTrue((box.data / "skills-mcp" / "fixture-skills" / "fixture-three" / "SKILL.md").is_file())
        box.run("uninstall")
        self.assertEqual([], files_under(box.home))

    def test_dry_run_writes_nothing(self):
        box = self.sandbox()
        proc = box.run("packs", "install", "fixture-skills", "--tools", "claude", "--dry-run")
        self.assertIn(f"register {NAME} for: claude", proc.stdout)
        self.assertEqual([], files_under(box.home))

    def test_mode_mcp_without_node_stops_before_writing(self):
        box = self.sandbox()
        # Link every command on PATH except node into one folder: on merged-/usr systems node
        # shares /usr/bin with coreutils, so dropping whole PATH folders would hide tr and friends.
        shim = box.tmp / "path-without-node"
        shim.mkdir()
        for d in os.environ.get("PATH", "").split(os.pathsep):
            if not d or not Path(d).is_dir():
                continue
            for entry in Path(d).iterdir():
                target = shim / entry.name
                if entry.name in ("node", "nodejs") or target.exists() or target.is_symlink():
                    continue
                if entry.is_file() and os.access(entry, os.X_OK):
                    target.symlink_to(entry)
        path = str(shim)
        if shutil.which("node", path=path):
            self.skipTest("node cannot be hidden from PATH here")
        box.env = lambda: {"PATH": path, "HOME": str(box.home), "TMPDIR": str(box.tmp), "LANG": "C"}
        proc = box.run("packs", "install", "fixture-skills", "--tools", "claude", ok=False)
        self.assertNotEqual(0, proc.returncode)
        self.assertIn("mode mcp needs Node.js", proc.stderr)
        self.assertEqual([], files_under(box.home))
        box.run("packs", "install", "fixture-skills", "--tools", "claude", "--mode", "skills")
        self.assertTrue((box.home / ".claude" / "skills" / "fixture-one" / "SKILL.md").is_file())

    def test_unknown_mode_fails(self):
        self.assertIn("--mode needs mcp or skills", self.sandbox().run("--mode", "copy", "--yes", ok=False).stderr)


# ---------------------------------------------------------------------------------- PowerShell

@unittest.skipUnless(PWSH and NODE, "pwsh and node required")
class AcceptancePowerShellTests(unittest.TestCase):
    def test_flow(self):
        temporary = tempfile.TemporaryDirectory(prefix="po pwsh skills mcp ")
        self.addCleanup(temporary.cleanup)
        home = Path(temporary.name) / "home"
        home.mkdir()
        write_configs(home)
        env = {"PATH": os.environ.get("PATH", ""), "HOME": str(home), "USERPROFILE": str(home),
               "LOCALAPPDATA": str(home / "AppData" / "Local")}

        def run(*args):
            proc = subprocess.run([PWSH, "-NoProfile", "-File", str(ROOT / "install" / "install.ps1"), *args],
                                  capture_output=True, text=True, env=env, timeout=900)
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            return proc

        tools = ("--tools", ",".join(TOOLS))
        run("packs", "install", "claude-red-offense", "cyber-skills:cyber-malware", *tools)
        root = home / "AppData" / "Local" / "prompt-orchestrator" / "skills-mcp"
        for rel in SKILL_DIRS:
            self.assertFalse((home / rel).exists(), rel)
        self.assertEqual({"claude": 1, "codex": 1, "opencode": 1, "claude_text": 1, "codex_text": 1, "opencode_text": 1},
                         server_entries(home))
        installed = pack_skills("claude-red-offense") | pack_skills("cyber-skills", ("cyber-malware",))
        self.assertEqual(installed, {s["name"] for s in json.loads((root / "index.json").read_text())["skills"]})
        self.assertIn("no change", run("packs", "install", "claude-red-offense", "cyber-skills:cyber-malware", *tools).stdout)

        run("packs", "install", "logo-design", "--mode", "skills", *tools)
        self.assertTrue((home / ".claude" / "skills" / "logo-design" / "SKILL.md").is_file())
        run("packs", "install", "logo-design", "--mode", "mcp", *tools)
        for rel in SKILL_DIRS:
            self.assertFalse((home / rel).exists(), rel)
        self.assertIn("[x] logo-design:logo-design (1 skills) [mcp]", run("packs", "list").stdout)

        run("packs", "remove", "claude-red-offense", "cyber-skills", "logo-design")
        for rel, text in CONFIGS.items():
            self.assertEqual(text.encode(), (home / rel).read_bytes(), rel)
        run("uninstall")
        self.assertEqual(set(CONFIGS), {p for p in files_under_without_pwsh(home) if (home / p).is_file()})


# ---------------------------------------------------------------------------------- validator

class ValidatorTests(unittest.TestCase):
    def test_pack_server_may_not_take_the_po_skills_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            packs = Path(tmp)
            shutil.copytree(ROOT / "packs" / "rea", packs / "rea")
            path = packs / "rea" / "pack.json"
            data = json.loads(path.read_text())
            data["mcp"]["name"] = NAME
            path.write_text(json.dumps(data))
            errors = validate_packs.load_packs(packs)[1]
        self.assertTrue(any("installer's own MCP server" in e for e in errors), errors)

    def test_description_form_the_index_cannot_read_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            packs = Path(tmp)
            shutil.copytree(FIXTURES, packs, dirs_exist_ok=True)
            md = packs / "fixture-skills" / "skills" / "fixture-one" / "SKILL.md"
            text = md.read_text()
            md.write_text(re.sub(r"(?m)^description: .*$", "description: &anchor Fixture skill.", text, count=1))
            errors = validate_packs.load_packs(packs)[1]
        self.assertTrue(any("po-skills index" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
