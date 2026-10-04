"""Self-test for docs_scaffold.py. Run: python3 -B -m unittest discover -s <this dir> -v"""

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docs_scaffold as ds  # noqa: E402

GIT = shutil.which("git")


def sh(cwd, *args):
    subprocess.run(("git", "-c", "user.name=t", "-c", "user.email=t@example.com",
                    "-c", "commit.gpgsign=false") + args,
                   cwd=str(cwd), check=True, capture_output=True, text=True)


def sh_out(cwd, *args):
    return subprocess.run(("git",) + args, cwd=str(cwd), capture_output=True, text=True).stdout


@unittest.skipUnless(GIT, "git unavailable")
class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="docs scaffold ")
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        sh(self.dir, "init", "-q")
        (self.dir / "src").mkdir()
        (self.dir / "src" / "a.py").write_text("x = 1\n")
        sh(self.dir, "add", ".")
        sh(self.dir, "commit", "-q", "-m", "init")

    def run_cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = ds.main(["--project", str(self.dir)] + list(args))
        return code, out.getvalue()

    def init(self, kind="embedded"):
        code, out = self.run_cli("init", "--type", kind)
        self.assertEqual(0, code, out)
        return ds.find_project(type("A", (), {"project": str(self.dir), "root": None})())

    def findings(self, proj, check=None, sev=None):
        found, _ = ds.run_checks(proj)
        return [f for f in found if (check is None or f[1] == check) and (sev is None or f[0] == sev)]

    def commit(self, msg="change"):
        sh(self.dir, "add", "-A")
        sh(self.dir, "commit", "-q", "-m", msg)

    def test_frontmatter_roundtrip(self):
        value = {"date": "2026-01-02", "reason": 'wrong, see "x": y', "superseded_by": "none"}
        text = ds.set_frontmatter("# Body\n", "deprecated", value)
        fm, body = ds.split_doc(text)
        self.assertEqual(value, fm["deprecated"])
        self.assertIn("# Body", body)
        self.assertEqual(["a", "b c"], ds.parse_value('[a, "b c"]'))

    def test_embedded_init_is_clean_and_tracks_specs(self):
        proj = self.init()
        self.assertEqual([], [f for f in self.findings(proj) if f[0] != "info"])
        self.assertIn("/ignore/", (self.dir / ".gitignore").read_text())
        self.assertTrue((self.dir / "ignore" / "README.md").is_file())
        self.assertTrue((self.dir / "ignore" / "sessions").is_dir())
        self.assertNotIn("ignore/", sh_out(self.dir, "status", "--porcelain"))
        self.assertEqual((self.dir / ".kiro" / "specs").resolve(), proj.changes)
        code, out = self.run_cli("init", "--type", "embedded")
        self.assertEqual(2, code)

    def test_standalone_init_keeps_changes_in_docs(self):
        proj = self.init("standalone")
        self.assertEqual(proj.root / "70-work" / "changes", proj.changes)
        self.run_cli("new", "change", "Login Flow")
        self.assertTrue((proj.changes / "login-flow" / "tasks.md").is_file())
        self.assertEqual([], [f for f in self.findings(proj) if f[0] != "info"])

    def test_standalone_tree_at_repo_root_with_trailing_options(self):
        code, out = self.run_cli("init", "--type", "standalone", "--root", ".")
        self.assertEqual(0, code, out)
        self.assertTrue((self.dir / "90-meta" / "manifest.json").is_file())
        self.assertTrue((self.dir / "70-work" / "changes").is_dir())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(0, ds.main(["check", "--project", str(self.dir)]))
        self.assertIn("0 error, 0 warn", out.getvalue())

    def test_check_is_warn_only(self):
        self.init()
        (self.dir / "docs" / "INDEX.md").unlink()
        code, out = self.run_cli("check")
        self.assertEqual(0, code)
        self.assertIn("warn-only", out)
        self.assertTrue((self.dir / "ignore" / "health.md").is_file())

    def test_staleness_and_verify(self):
        proj = self.init()
        self.run_cli("new", "unit", "core")
        readme = proj.root / "30-units" / "core" / "README.md"
        readme.write_text(ds.set_frontmatter(readme.read_text(), "sources", ["src/**"]))
        self.assertTrue(any("never verified" in f[3] for f in self.findings(proj, "stale")))
        self.commit()
        code, out = self.run_cli("verify", str(readme.parent))
        self.assertEqual(0, code, out)
        self.assertEqual([], self.findings(proj, "stale"))
        (self.dir / "src" / "a.py").write_text("x = 2\n")
        stale = self.findings(proj, "stale")
        self.assertEqual(1, len(stale))
        self.assertIn("src/a.py", stale[0][3])

    def test_unverifiable_repo_in_standalone(self):
        proj = self.init("standalone")
        proj.m["repos"] = {"app": {"path_env": "DOCS_SCAFFOLD_TEST_MISSING"}}
        proj.manifest_path.write_text(ds.json.dumps(proj.m))
        proj = ds.Project(proj.project, proj.manifest_path)
        self.run_cli("new", "unit", "core")
        readme = proj.root / "30-units" / "core" / "README.md"
        readme.write_text(ds.set_frontmatter(readme.read_text(), "sources", ["app:src/**"]))
        self.assertTrue(any("unverifiable" in f[3] for f in self.findings(proj, "stale")))

    def test_gaps_coverage_links_and_ids(self):
        proj = self.init()
        self.run_cli("new", "unit", "core")
        (proj.root / "30-units" / "core" / "tests.md").unlink()
        req = proj.root / "10-context" / "requirements.md"
        req.write_text(req.read_text() + "\n- REQ-1: the system SHALL work.\n")
        design = proj.root / "30-units" / "core" / "design.md"
        design.write_text(ds.set_frontmatter(design.read_text(), "traces", ["REQ-1", "REQ-9"])
                          + "\nSee [missing](nope.md).\n")
        glossary = proj.root / "glossary.md"
        glossary.write_text(ds.set_frontmatter(glossary.read_text(), "status", "n/a"))
        dup = proj.root / "80-guides" / "dup.md"
        dup.write_text(ds.render_doc("readme", "guide", "draft", "dup", "# Dup\n\ntext"))
        self.assertTrue(any("required document missing" in f[3] for f in self.findings(proj, "gap")))
        self.assertTrue(any("na_reason" in f[3] for f in self.findings(proj, "gap")))
        coverage = self.findings(proj, "coverage")
        self.assertEqual(["REQ-1"], [f[2] for f in coverage])
        self.assertIn("test", coverage[0][3])
        self.assertTrue(self.findings(proj, "trace"))
        self.assertTrue(self.findings(proj, "link"))
        self.assertTrue(self.findings(proj, "duplicate-id", "error"))

    def test_generated_out_of_date_then_index(self):
        proj = self.init()
        doc = proj.root / "10-context" / "overview.md"
        doc.write_text(ds.set_frontmatter(doc.read_text(), "summary", "changed"))
        self.assertTrue(self.findings(proj, "generated"))
        self.run_cli("index")
        self.assertEqual([], self.findings(proj, "generated"))

    def test_closed_records_lock(self):
        proj = self.init()
        self.run_cli("new", "investigation", "Slow login")
        record = next((proj.root / "70-work" / "investigations").glob("*.md"))
        record.write_text(ds.set_frontmatter(record.read_text(), "status", "closed"))
        self.assertTrue(any("not locked" in f[3] for f in self.findings(proj, "immutable")))
        self.run_cli("index")
        self.assertEqual([], self.findings(proj, "immutable"))
        record.write_text(record.read_text() + "\nedit\n")
        self.assertTrue(self.findings(proj, "immutable", "error"))

    def test_deprecate_moves_locks_and_relinks(self):
        proj = self.init()
        self.run_cli("new", "unit", "core")
        old = proj.root / "30-units" / "core" / "design.md"
        new = proj.root / "30-units" / "core" / "design-v2.md"
        new.write_text(ds.render_doc("units.core.design-v2", "design", "draft", "v2", "# V2\n\ntext"))
        linker = proj.root / "80-guides" / "howto.md"
        linker.write_text(ds.render_doc("guides.howto", "guide", "draft", "how", "# How\n\n[d](../30-units/core/design.md)"))
        code, out = self.run_cli("deprecate", str(old), "--reason", "wrong, flows mismatch",
                                 "--superseded-by", "units.core.design-v2")
        self.assertEqual(0, code, out)
        self.assertFalse(old.exists())
        moved = next((proj.root / ".deprecated").glob("*-design/design.md"))
        fm, _ = ds.split_doc(moved.read_text())
        self.assertEqual("wrong, flows mismatch", fm["deprecated"]["reason"])
        self.assertIn("design-v2.md", linker.read_text())
        self.assertEqual([], self.findings(proj, sev="error"))
        moved.write_text(moved.read_text() + "tamper\n")
        self.assertTrue(self.findings(proj, "immutable", "error"))
        linker.write_text(linker.read_text() + f"\n[old](../.deprecated/{moved.parent.name}/design.md)\n")
        self.assertTrue(self.findings(proj, "deprecated-link", "error"))

    def test_deprecate_keep_copies_before_edit(self):
        proj = self.init()
        doc = proj.root / "20-architecture" / "system.md"
        code, out = self.run_cli("deprecate", str(doc), "--reason", "scope changed", "--keep")
        self.assertEqual(0, code, out)
        self.assertTrue(doc.is_file())
        self.assertEqual(1, len(list((proj.root / ".deprecated").glob("*-system/system.md"))))

    def test_session_journal_is_append_only(self):
        proj = self.init()
        self.assertEqual(0, self.run_cli("session", "start", "--goal", "test")[0])
        (self.dir / "src" / "a.py").write_text("x = 3\n")
        self.assertEqual(0, self.run_cli("session", "log", "--action", "edit a.py", "--result", "ok")[0])
        self.commit()
        code, out = self.run_cli("session", "resync")
        self.assertEqual(0, code, out)
        self.assertEqual(0, self.run_cli("session", "sync")[0])
        self.assertIn("hash", (proj.root / "70-work" / "STATUS.md").read_text())
        entries = ds.journal(proj)
        self.assertEqual(4, len(entries))
        self.assertIn("commits since last entry: ", entries[2]["body"])
        self.assertEqual([], ds.verify_chain(entries))
        self.assertEqual([], self.findings(proj, "journal"))
        self.run_cli("session", "start")
        self.assertEqual(2, len(list((proj.ignore / "sessions").glob("*.md"))))
        self.assertEqual([], ds.verify_chain(ds.journal(proj)))
        first = entries[0]["file"]
        text = first.read_text()
        first.write_text(text.replace("edit a.py", "edit b.py"))
        self.assertTrue(any("modified" in f[3] for f in self.findings(proj, "journal")))
        first.write_text(text.split("### 002")[0])
        self.assertTrue(self.findings(proj, "journal", "error"))

    def test_log_requires_session(self):
        self.init()
        self.assertEqual(2, self.run_cli("session", "log", "--action", "x")[0])


if __name__ == "__main__":
    unittest.main()
