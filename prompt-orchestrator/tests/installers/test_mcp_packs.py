"""Tests for npm and MCP packs: install/pack_helper.mjs, the rea pack and its rea-frida set.

Run with: python3 -B -m unittest discover -s tests/installers -t tests/installers -v

The flows put fixtures/bin/npm (a fake npm without network) first on PATH and need Node.js for
the helper. PO_TEST_NETWORK=1 adds a run with the real npm and the real Frida release asset.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import tarfile
import tempfile
import tomllib
import unittest
from pathlib import Path

from test_installers import BASH, FIXTURES, PWSH, ROOT, Sandbox, files_under, files_under_without_pwsh, generate

NODE = shutil.which("node")
HELPER = ROOT / "install" / "pack_helper.mjs"
FAKE_BIN = FIXTURES.parent / "bin"
REA = json.loads((ROOT / "packs" / "rea" / "pack.json").read_text(encoding="utf-8"))
PINNED = {p["name"]: p["integrity"] for p in REA["npm"]["packages"]}
MCP_TOOLS = ("claude", "codex", "cursor", "gemini", "opencode")
SPEC_B64 = base64.b64encode(json.dumps({k: REA["mcp"][k] for k in ("command", "args", "env")}).encode()).decode()

# Config files a user already has, one per client. The Gemini file carries a comment and the
# Codex file has no final newline, so the edits must keep both as they are.
CONFIGS = {
    ".claude.json": '{\n  "numStartups": 7,\n  "mcpServers": {\n    "other": {"command": "x", "args": []}\n  }\n}\n',
    ".codex/config.toml": 'model = "o3"\n\n[mcp_servers.other]\ncommand = "y"',
    ".cursor/mcp.json": '{"mcpServers": {}}\n',
    ".gemini/settings.json": '// my Gemini settings\n{\n    "theme": "Dracula",\n}\n',
    ".config/opencode/opencode.json": '{\r\n  "$schema": "https://opencode.ai/config.json"\r\n}\r\n',
}


def node_platform() -> str:
    return subprocess.run([NODE, str(HELPER), "platform"], capture_output=True, text=True, check=True).stdout.strip()


def strip_comments(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//")).replace(",\n}", "\n}")


def rea_entries(home: Path, prefix: Path) -> dict[str, list]:
    """Every rea entry per client config, normalised to (command, args, env)."""
    out = {}
    for tool, rel, key in (("claude", ".claude.json", "mcpServers"), ("cursor", ".cursor/mcp.json", "mcpServers"),
                           ("gemini", ".gemini/settings.json", "mcpServers"), ("opencode", ".config/opencode/opencode.json", "mcp")):
        data = json.loads(strip_comments((home / rel).read_text(encoding="utf-8")))
        found = [v for k, v in data.get(key, {}).items() if k == "rea"]
        if tool == "opencode":
            found = [(v["command"][0], v["command"][1:], v.get("environment")) for v in found]
        else:
            found = [(v["command"], v["args"], v.get("env")) for v in found]
        out[tool] = found
    text = (home / ".codex/config.toml").read_text(encoding="utf-8")
    table = tomllib.loads(text).get("mcp_servers", {})
    out["codex"] = [(v["command"], v["args"], v.get("env")) for k, v in table.items() if k == "rea"]
    out["codex_headers"] = text.count("[mcp_servers.rea]")
    return out


def pinned_entry(prefix: Path) -> tuple:
    args = [a.replace("{PACKAGE}", str(prefix)) for a in REA["mcp"]["args"]]
    return (REA["mcp"]["command"], args, REA["mcp"]["env"])


def frida_asset(path: Path, payload: bytes) -> str:
    """Write a tar.gz that holds build/frida_binding.node and return its sha256."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        info = tarfile.TarInfo("build/frida_binding.node")
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    path.write_bytes(buf.getvalue())
    return hashlib.sha256(buf.getvalue()).hexdigest()


# ---------------------------------------------------------------------------------- helper

@unittest.skipUnless(NODE, "node not installed")
class HelperTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="po helper ")
        self.addCleanup(temporary.cleanup)
        self.dir = Path(temporary.name)

    def helper(self, *args: str) -> list[str]:
        proc = subprocess.run([NODE, str(HELPER), *args], capture_output=True, text=True)
        self.assertEqual(0, proc.returncode, proc.stderr)
        return proc.stdout.rstrip("\n").split("\t")

    def add(self, fmt: str, file: Path, old: str = "-") -> list[str]:
        return self.helper("mcp-add", fmt, str(file), "rea", SPEC_B64, str(self.dir / "pkg"), old)

    def test_each_format_adds_reruns_and_restores_bytes(self):
        files = {"claude": ".claude.json", "codex": ".codex/config.toml", "cursor": ".cursor/mcp.json",
                 "gemini": ".gemini/settings.json", "opencode": ".config/opencode/opencode.json"}
        for fmt, rel in files.items():
            with self.subTest(fmt=fmt):
                path = self.dir / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(CONFIGS[rel].encode())
                status, resolved, record = self.add(fmt, path)
                self.assertEqual(("added", str(path)), (status, resolved))
                self.assertNotEqual(CONFIGS[rel].encode(), path.read_bytes())
                self.assertEqual("present", self.add(fmt, path, record)[0])
                self.assertEqual(["removed"], self.helper("mcp-remove", record))
                self.assertEqual(CONFIGS[rel].encode(), path.read_bytes())

    def test_new_file_is_created_and_deleted(self):
        path = self.dir / "new" / "mcp.json"
        path.parent.mkdir()
        status, _, record = self.add("cursor", path)
        self.assertEqual("added", status)
        self.assertIn('"NO_UPDATE_NOTIFIER": "1"', path.read_text())
        self.assertEqual(["removed"], self.helper("mcp-remove", record))
        self.assertFalse(path.exists())

    def test_opencode_prefers_an_existing_jsonc(self):
        jsonc = self.dir / "opencode.jsonc"
        jsonc.write_text("{\n  // mine\n  \"model\": \"x\"\n}\n")
        status, resolved, record = self.add("opencode", self.dir / "opencode.json")
        self.assertEqual(("added", str(jsonc)), (status, resolved))
        self.assertFalse((self.dir / "opencode.json").exists())
        self.helper("mcp-remove", record)
        self.assertEqual("{\n  // mine\n  \"model\": \"x\"\n}\n", jsonc.read_text())

    def test_a_different_entry_is_a_conflict_and_stays(self):
        path = self.dir / "mcp.json"
        original = '{"mcpServers": {"rea": {"command": "npx", "args": ["-y", "rea-agents@latest", "mcp"]}}}\n'
        path.write_text(original)
        self.assertEqual("conflict", self.add("cursor", path)[0])
        self.assertEqual(original, path.read_text())
        toml = self.dir / "config.toml"
        toml.write_text('[mcp_servers.rea]\ncommand = "npx"\n')
        self.assertEqual("conflict", self.add("codex", toml)[0])
        self.assertEqual('[mcp_servers.rea]\ncommand = "npx"\n', toml.read_text())

    def test_identical_foreign_entry_is_left_unmanaged(self):
        path = self.dir / "mcp.json"
        path.write_text("{}\n")
        record = self.add("cursor", path)[2]
        self.assertEqual("foreign", self.add("cursor", path)[0])
        self.helper("mcp-remove", record)

    def test_an_entry_changed_after_install_is_kept(self):
        path = self.dir / "mcp.json"
        path.write_text("{}\n")
        record = self.add("cursor", path)[2]
        path.write_text(path.read_text().replace('"NO_UPDATE_NOTIFIER": "1"', '"NO_UPDATE_NOTIFIER": "0"'))
        changed = path.read_text()
        self.assertEqual(["changed"], self.helper("mcp-remove", record))
        self.assertEqual(changed, path.read_text())

    def test_reformatted_file_still_loses_only_the_entry(self):
        path = self.dir / ".claude.json"
        path.write_text('{"a": 1, "mcpServers": {"other": {"command": "x"}}}\n')
        record = self.add("claude", path)[2]
        data = json.loads(path.read_text())
        path.write_text(json.dumps(data, indent=4) + "\n")
        self.helper("mcp-remove", record)
        self.assertEqual({"a": 1, "mcpServers": {"other": {"command": "x"}}}, json.loads(path.read_text()))

    def test_codex_keys_after_the_block_keep_it(self):
        path = self.dir / "config.toml"
        path.write_text('model = "o3"\n')
        record = self.add("codex", path)[2]
        path.write_text(path.read_text() + 'startup_timeout_sec = 30\n')
        self.assertEqual(["changed"], self.helper("mcp-remove", record))

    def test_npm_check_and_node_range(self):
        prefix = self.dir / "prefix"
        (prefix / "node_modules" / "rea-agents").mkdir(parents=True)
        (prefix / "node_modules" / "rea-agents" / "package.json").write_text('{"version": "6.10.1"}')
        lock = {"packages": {"node_modules/rea-agents": {"version": "6.10.1", "integrity": PINNED["rea-agents"]}}}
        (prefix / "package-lock.json").write_text(json.dumps(lock))
        args = [NODE, str(HELPER), "npm-check", str(prefix), "rea-agents", "6.10.1", PINNED["rea-agents"]]
        self.assertEqual(0, subprocess.run(args, capture_output=True).returncode)
        self.assertEqual(4, subprocess.run(args[:-1] + ["sha512-" + "A" * 86 + "=="], capture_output=True).returncode)
        self.assertEqual(3, subprocess.run(args[:3] + [str(self.dir / "none")] + args[4:], capture_output=True).returncode)
        ok = subprocess.run([NODE, str(HELPER), "node-check", ">=1.0.0 || ^99.0.0"], capture_output=True)
        no = subprocess.run([NODE, str(HELPER), "node-check", "^99.0.0"], capture_output=True)
        self.assertEqual((0, 1), (ok.returncode, no.returncode))


# ---------------------------------------------------------------------------------- bash flows

class FakeNpmSandbox(Sandbox):
    def __init__(self, case, installer, integrity=None):
        super().__init__(case, installer)
        self.integrity = dict(PINNED, **(integrity or {}))
        self.log = self.base / "npm.log"

    def env(self) -> dict:
        env = super().env()
        env["PATH"] = f"{FAKE_BIN}{os.pathsep}{env['PATH']}"
        env["FAKE_NPM_INTEGRITY"] = json.dumps(self.integrity)
        env["FAKE_NPM_LOG"] = str(self.log)
        return env

    def write_configs(self) -> None:
        for rel, text in CONFIGS.items():
            path = self.home / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode())


def rea_copy(base: Path, digest: str | None = None) -> Path:
    """packs/rea copied into base/packs for the fake npm.

    The copy accepts any Node.js from 18 on, so the flows also run where the installed Node.js is
    older than rea needs; HelperTests covers the range check. With a digest, the copy pins it as
    the binding digest for this platform.
    """
    packs = base / "packs"
    shutil.copytree(ROOT / "packs" / "rea", packs / "rea")
    pack_json = packs / "rea" / "pack.json"
    data = json.loads(pack_json.read_text())
    data["npm"]["node"] = ">=18.0.0"
    if digest:
        data["npm"]["packages"][1]["binding"]["sha256"] = {node_platform(): digest}
    pack_json.write_text(json.dumps(data, indent=2))
    return packs


@unittest.skipUnless(BASH and NODE, "bash and node required")
class ReaBashTests(unittest.TestCase):
    """The rea pack (pins, skill, MCP server) with the fake npm."""

    tools = ("--tools", ",".join(MCP_TOOLS))

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="po rea pack ")
        base = Path(cls.temporary.name)
        cls.installer = base / "out" / "install.sh"
        generate(cls.installer.parent, rea_copy(base))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_rea_set_registers_once_reruns_clean_and_removes_byte_identical(self):
        box = FakeNpmSandbox(self, self.installer)
        box.write_configs()
        prefix = box.data / "packages" / "rea"
        first = box.run("packs", "install", "rea", *self.tools)
        self.assertIn("rea-agents@6.10.1 matches the pinned integrity", first.stdout)
        entries = rea_entries(box.home, prefix)
        for tool in MCP_TOOLS:
            self.assertEqual([pinned_entry(prefix)], entries[tool], tool)
        self.assertEqual(1, entries["codex_headers"])
        self.assertFalse((prefix / "node_modules" / "frida").exists())
        # mode mcp (the default): the skill sits in skills-mcp and po-skills serves it
        self.assertIn("origin: third-party", (box.data / "skills-mcp" / "rea" / "reverse-engineer-anything" / "SKILL.md").read_text())
        for skills in (".claude/skills", ".agents/skills", ".cursor/skills", ".config/opencode/skills"):
            self.assertFalse((box.home / skills / "reverse-engineer-anything").exists(), skills)
        self.assertIn('"po-skills"', (box.home / ".claude.json").read_text())
        calls = box.log.read_text().splitlines()
        self.assertEqual(1, len(calls))
        self.assertIn("rea-agents@6.10.1 --omit=optional --ignore-scripts", calls[0])
        self.assertNotIn("frida", calls[0])

        self.assertIn("==> no change", box.run("packs", "install", "rea", *self.tools).stdout)
        self.assertEqual(1, len(box.log.read_text().splitlines()))
        self.assertIn("[x] rea:rea (1 skills) [mcp]", box.run("packs", "list").stdout)

        box.run("packs", "remove", "rea")
        for rel, text in CONFIGS.items():
            self.assertEqual(text.encode(), (box.home / rel).read_bytes(), rel)
        self.assertFalse(box.data.exists())
        box.run("uninstall")
        self.assertEqual(set(CONFIGS), {p for p in files_under(box.home) if (box.home / p).is_file()})

    def test_bare_pack_name_skips_frida_and_frida_alone_is_refused(self):
        box = FakeNpmSandbox(self, self.installer)
        proc = box.run("packs", "install", "rea:rea-frida", *self.tools, ok=False)
        self.assertNotEqual(0, proc.returncode)
        self.assertIn("needs set rea:rea", proc.stderr)
        self.assertEqual([], files_under(box.home))

    def test_integrity_mismatch_refuses_and_writes_no_config(self):
        box = FakeNpmSandbox(self, self.installer, integrity={"rea-agents": "sha512-" + "B" * 86 + "=="})
        box.write_configs()
        proc = box.run("packs", "install", "rea", *self.tools, ok=False)
        self.assertIn("fails the pinned check", proc.stderr)
        self.assertFalse((box.data / "packages" / "rea").exists())
        for rel, text in CONFIGS.items():
            self.assertEqual(text.encode(), (box.home / rel).read_bytes(), rel)

    def test_frida_wrong_digest_refuses_and_leaves_no_binding(self):
        box = FakeNpmSandbox(self, self.installer)
        bundle = box.base / "bundle"
        bundle.mkdir()
        frida_asset(bundle / f"frida-v17.23.2-napi-v8-{node_platform()}.tar.gz", b"not the pinned binding")
        box.run("packs", "install", "rea", *self.tools)
        proc = box.run("packs", "install", "rea:rea-frida", *self.tools, "--bundle", f"rea={bundle}", ok=False)
        self.assertNotEqual(0, proc.returncode)
        self.assertIn("refusing to install rea:rea-frida", proc.stderr)
        frida = box.data / "packages" / "rea" / "node_modules" / "frida"
        self.assertFalse(frida.exists())
        self.assertNotIn("frida", box.log.read_text())
        box.run("uninstall")


@unittest.skipUnless(BASH and NODE, "bash and node required")
class ReaFridaFixtureTests(unittest.TestCase):
    """packs/rea with this platform's binding digest set to a fixture asset."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="po rea ")
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        self.bundle = base / "bundle"
        self.bundle.mkdir()
        self.payload = b"fixture frida binding\n"
        digest = frida_asset(self.bundle / f"frida-v17.23.2-napi-v8-{node_platform()}.tar.gz", self.payload)
        packs = rea_copy(base, digest)
        self.out = base / "out"
        generate(self.out, packs)

    def test_both_sets_install_rerun_and_remove(self):
        box = FakeNpmSandbox(self, self.out / "install.sh")
        box.write_configs()
        args = ("--tools", "claude,codex", "--no-core", "--no-harness", "--packs", "rea:rea,rea-frida",
                "--bundle", f"rea={self.bundle}", "--yes")
        proc = box.run(*args)
        self.assertIn("matches the pinned sha256", proc.stdout)
        prefix = box.data / "packages" / "rea"
        binding = prefix / "node_modules" / "frida" / "build" / "frida_binding.node"
        self.assertEqual(self.payload, binding.read_bytes())
        self.assertIn("frida@17.23.2 --omit=optional --ignore-scripts", box.log.read_text())
        self.assertIn("==> no change", box.run(*args).stdout)
        listing = box.run("packs", "list").stdout
        self.assertIn("[x] rea:rea-frida (0 skills)", listing)
        self.assertIn("Needs set rea.", listing)

        box.run("packs", "remove", "rea:rea-frida")
        self.assertFalse((prefix / "node_modules" / "frida").exists())
        self.assertTrue((prefix / "node_modules" / "rea-agents").is_dir())
        box.run(*args)
        box.run("packs", "remove", "rea:rea")
        self.assertFalse(prefix.exists())
        for rel in (".claude.json", ".codex/config.toml"):
            self.assertEqual(CONFIGS[rel].encode(), (box.home / rel).read_bytes(), rel)

    def test_tui_offers_frida_with_rea(self):
        box = FakeNpmSandbox(self, self.out / "install.sh")
        # tools: claude only; core: off; harness: off; packs: set 2 (rea-frida) selects rea too; review: install
        answers = "\n".join(["n", "1", "", "c", "", "h", "", "2", "", ""]) + "\n"
        proc = box.run("tui", "--bundle", f"rea={self.bundle}", stdin=answers)
        self.assertIn("packs: rea:rea rea:rea-frida", proc.stdout)
        self.assertIn("A set that needs another set selects both.", proc.stdout)
        self.assertTrue((box.data / "packages" / "rea" / "node_modules" / "frida" / "build" / "frida_binding.node").is_file())
        box.run("uninstall")
        self.assertEqual([], files_under(box.home))


@unittest.skipUnless(BASH and NODE and shutil.which("npm") and os.environ.get("PO_TEST_NETWORK") == "1",
                     "set PO_TEST_NETWORK=1 to install rea and Frida from the network")
class ReaNetworkTests(unittest.TestCase):
    def test_real_install_loads_frida(self):
        if node_platform() not in REA["npm"]["packages"][1]["binding"]["sha256"]:
            self.skipTest(f"no pinned Frida digest for {node_platform()}")
        box = Sandbox(self, ROOT / "install" / "install.sh")
        env = box.env()
        for key in ("HTTPS_PROXY", "https_proxy", "SSL_CERT_FILE", "NODE_EXTRA_CA_CERTS", "npm_config_cafile"):
            if os.environ.get(key):
                env[key] = os.environ[key]
        box.env = lambda: env
        box.run("packs", "install", "rea:rea,rea-frida", "--tools", "claude")
        prefix = box.data / "packages" / "rea"
        probe = subprocess.run([NODE, "-e", "const f = require(process.argv[1]); process.stdout.write(typeof f.getDevice)",
                                str(prefix / "node_modules" / "frida")], capture_output=True, text=True, cwd=box.base)
        self.assertEqual("function", probe.stdout, probe.stderr)
        self.assertIn("==> no change", box.run("packs", "install", "rea:rea,rea-frida", "--tools", "claude").stdout)
        box.run("uninstall")
        self.assertFalse(box.data.exists())


# ---------------------------------------------------------------------------------- validator

class McpValidatorTests(unittest.TestCase):
    def errors(self, change) -> list[str]:
        import validate_packs  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as tmp:
            packs = rea_copy(Path(tmp))
            pack_json = packs / "rea" / "pack.json"
            data = json.loads(pack_json.read_text())
            change(data)
            pack_json.write_text(json.dumps(data))
            return validate_packs.load_packs(packs)[1]

    def test_rea_pack_is_valid(self):
        self.assertEqual([], self.errors(lambda d: None))

    def test_version_range_and_latest_fail(self):
        def edit(d):
            d["npm"]["packages"][0]["version"] = "^6.10.1"
            d["mcp"]["args"] = ["-y", "rea-agents@latest", "mcp"]
            d["mcp"]["command"] = "npx"
        errors = self.errors(edit)
        self.assertTrue(any("exact X.Y.Z pin" in e for e in errors))
        self.assertTrue(any("no npx and no @latest" in e for e in errors))

    def test_auto_approval_key_fails(self):
        errors = self.errors(lambda d: d["mcp"].update(trust=True))
        self.assertTrue(any("mcp must have exactly the keys" in e for e in errors))

    def test_requires_and_empty_skills_rules(self):
        def edit(d):
            d["sets"][1]["requires"] = ["nope"]
            d["npm"]["packages"].pop()
        errors = self.errors(edit)
        self.assertTrue(any("requires must list other sets" in e for e in errors))
        self.assertTrue(any("unless the set installs an npm package" in e for e in errors))

    def test_bad_binding_digest_fails(self):
        errors = self.errors(lambda d: d["npm"]["packages"][1]["binding"]["sha256"].update({"linux-x64": "sha256:abc"}))
        self.assertTrue(any("64 lowercase hex" in e for e in errors))


# ---------------------------------------------------------------------------------- PowerShell

@unittest.skipUnless(PWSH and NODE, "pwsh and node required")
class ReaPowerShellTests(unittest.TestCase):
    def test_flow(self):
        temporary = tempfile.TemporaryDirectory(prefix="po pwsh rea ")
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        out = base / "out"
        generate(out, rea_copy(base))
        home = base / "home"
        home.mkdir()
        for rel, text in CONFIGS.items():
            (home / rel).parent.mkdir(parents=True, exist_ok=True)
            (home / rel).write_bytes(text.encode())
        env = {"PATH": f"{FAKE_BIN}{os.pathsep}{os.environ.get('PATH', '')}", "HOME": str(home), "USERPROFILE": str(home),
               "LOCALAPPDATA": str(home / "AppData" / "Local"), "FAKE_NPM_INTEGRITY": json.dumps(PINNED)}

        def run(*args):
            proc = subprocess.run([PWSH, "-NoProfile", "-File", str(out / "install.ps1"), *args], capture_output=True,
                                  text=True, env=env, timeout=900)
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            return proc

        run("packs", "install", "rea", "--tools", ",".join(MCP_TOOLS))
        prefix = home / "AppData" / "Local" / "prompt-orchestrator" / "packages" / "rea"
        entries = rea_entries(home, prefix)
        for tool in MCP_TOOLS:
            self.assertEqual([pinned_entry(prefix)], entries[tool], tool)
        self.assertIn("no change", run("packs", "install", "rea", "--tools", ",".join(MCP_TOOLS)).stdout)
        run("packs", "remove", "rea")
        for rel, text in CONFIGS.items():
            self.assertEqual(text.encode(), (home / rel).read_bytes(), rel)
        run("uninstall")
        self.assertEqual(set(CONFIGS), {p for p in files_under_without_pwsh(home) if (home / p).is_file()})


if __name__ == "__main__":
    unittest.main()
