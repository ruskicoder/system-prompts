"""Self-tests for drawio_lint.py. Run:
    python3 -B -m unittest discover -s skills/architecture-diagrams/scripts -v
Needs Pillow and Arial or Liberation Sans; skips otherwise.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
LINT = HERE / "drawio_lint.py"

try:
    sys.path.insert(0, str(HERE))
    import drawio_lint  # noqa: E402

    drawio_lint.font(12, False)
    READY = True
except Exception:  # Pillow or a font missing
    READY = False

BOX = '<mxCell id="{id}" value="{v}" style="rounded=0;whiteSpace=wrap;fontSize={fs};" vertex="1" parent="{p}"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
FRAME = '<mxCell id="{id}" value="{v}" style="rounded=0;container=1;verticalAlign=top;align=left;spacingLeft=8;fontSize=14;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
TEXT = '<mxCell id="{id}" value="{v}" style="text;fontSize={fs};align=center;verticalAlign=middle;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
EDGE = ('<mxCell id="{id}" value="{v}" style="edgeStyle={es};exitX={ex};exitY={ey};entryX={nx};entryY={ny};endArrow=classic;" '
        'edge="1" parent="1" source="{s}" target="{t}"><mxGeometry relative="1" as="geometry"><Array as="points">{pts}</Array></mxGeometry></mxCell>')


def box(id, x, y, w=120, h=60, v="Service", fs=16, p="1"):
    return BOX.format(id=id, x=x, y=y, w=w, h=h, v=v, fs=fs, p=p)


def edge(id, s, t, ex=1, ey=0.5, nx=0, ny=0.5, pts=(), v="", es="none"):
    p = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in pts)
    return EDGE.format(id=id, s=s, t=t, ex=ex, ey=ey, nx=nx, ny=ny, pts=p, v=v, es=es)


def doc(*cells):
    body = "".join(cells)
    return (f'<mxfile><diagram id="d"><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>{body}'
            f"</root></mxGraphModel></diagram></mxfile>")


def run(xml, *args):
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "fig.drawio"
        f.write_text(xml)
        r = subprocess.run([sys.executable, "-B", str(LINT), str(f), "--print-width-cm", "12", *args],
                           capture_output=True, text=True)
        return r.returncode, r.stdout


def codes(out):
    return {line.split()[0] for line in out.splitlines()[1:] if line.strip()}


CLEAN = doc(box("a", 0, 0), box("b", 300, 0), edge("e1", "a", "b"),
            TEXT.format(id="l1", v="HTTPS", fs=14, x=180, y=0, w=60, h=20))


@unittest.skipUnless(READY, "Pillow or Arial/Liberation Sans not available")
class Lint(unittest.TestCase):
    def test_clean_figure_passes(self):
        rc, out = run(CLEAN)
        self.assertEqual(rc, 0, out)
        self.assertIn("0 finding(s)", out)

    def test_router_edge_is_auto(self):
        rc, out = run(doc(box("a", 0, 0), box("b", 300, 0), edge("e1", "a", "b", es="orthogonalEdgeStyle")))
        self.assertEqual(rc, 1)
        self.assertIn("AUTO", codes(out))

    def test_router_edge_also_reports_its_label(self):
        xml = doc(box("a", 0, 0), box("b", 300, 0), edge("e1", "a", "b", v="uses", es="orthogonalEdgeStyle"))
        self.assertEqual({"AUTO", "LABEL"}, set(codes(run(xml)[1])) & {"AUTO", "LABEL"})

    def test_diagonal(self):
        rc, out = run(doc(box("a", 0, 0), box("b", 300, 200), edge("e1", "a", "b")))
        self.assertIn("DIAG", codes(out))

    def test_crossing(self):
        xml = doc(box("a", 0, 0), box("b", 400, 0), box("c", 200, -200), box("d", 200, 200),
                  edge("e1", "a", "b"), edge("e2", "c", "d", ex=0.5, ey=1, nx=0.5, ny=0))
        rc, out = run(xml)
        self.assertIn("CROSS", codes(out))

    def test_edge_through_a_box(self):
        xml = doc(box("a", 0, 0), box("m", 200, 0), box("b", 400, 0), edge("e1", "a", "b"))
        self.assertIn("THRU", codes(run(xml)[1]))

    def test_label_on_the_edge(self):
        xml = doc(box("a", 0, 0), box("b", 300, 0), edge("e1", "a", "b", v="HTTPS"))
        self.assertIn("LABEL", codes(run(xml)[1]))

    def test_edge_through_a_text_label(self):
        xml = doc(box("a", 0, 0), box("b", 300, 0), edge("e1", "a", "b"),
                  TEXT.format(id="l1", v="HTTPS", fs=14, x=180, y=20, w=60, h=20))
        self.assertIn("LABEL", codes(run(xml)[1]))

    def test_short_terminal_run(self):
        xml = doc(box("a", 0, 0), box("b", 300, 100), edge("e1", "a", "b", nx=0, ny=0.5, pts=((290, 30), (290, 130))))
        self.assertIn("TERM", codes(run(xml)[1]))

    def test_shared_attachment_point(self):
        xml = doc(box("a", 0, 0), box("b", 300, 0), box("c", 300, 200),
                  edge("e1", "a", "b"), edge("e2", "a", "c", pts=((200, 30), (200, 230))))
        self.assertIn("EXIT", codes(run(xml)[1]))

    def test_small_print_size(self):
        xml = doc(box("a", 0, 0, fs=8), box("b", 1800, 0), edge("e1", "a", "b"))
        self.assertIn("SIZE", codes(run(xml)[1]))

    def test_too_many_bends(self):
        pts = ((140, 30), (140, 100), (180, 100), (180, 140), (220, 140), (220, 30))
        xml = doc(box("a", 0, 0), box("b", 300, 0), edge("e1", "a", "b", pts=pts))
        self.assertIn("BENDS", codes(run(xml)[1]))

    def test_text_does_not_fit(self):
        xml = doc(box("a", 0, 0, w=60, v="A very long service name"), box("b", 300, 0), edge("e1", "a", "b"))
        self.assertIn("FIT", codes(run(xml)[1]))

    def test_needless_frame_crossing(self):
        xml = doc(FRAME.format(id="f", v="Cloud", x=120, y=-100, w=140, h=260),
                  box("a", 0, 0), box("b", 400, 0), edge("e1", "a", "b"))
        self.assertIn("FRAME", codes(run(xml)[1]))

    def test_compressed_file_is_refused(self):
        rc, out = run('<mxfile><diagram id="d">compressedpayload</diagram></mxfile>')
        self.assertNotEqual(rc, 0)



@unittest.skipUnless(READY, "Pillow or Arial/Liberation Sans not available")
class FontLookup(unittest.TestCase):
    def setUp(self):
        self.saved = (list(drawio_lint.FONT_DIRS), os.environ.get("DRAWIO_LINT_FONT_DIR"))

    def tearDown(self):
        drawio_lint.FONT_DIRS[:] = self.saved[0]
        if self.saved[1] is None:
            os.environ.pop("DRAWIO_LINT_FONT_DIR", None)
        else:
            os.environ["DRAWIO_LINT_FONT_DIR"] = self.saved[1]

    def test_override_folder_is_used_first(self):
        real = Path(drawio_lint.font_path(False))
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(real, Path(tmp) / real.name)
            os.environ["DRAWIO_LINT_FONT_DIR"] = tmp
            self.assertEqual(Path(drawio_lint.font_path(False)).parent, Path(tmp))

    def test_missing_font_is_a_setup_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["DRAWIO_LINT_FONT_DIR"] = tmp
            drawio_lint.FONT_DIRS[:] = []
            with self.assertRaises(drawio_lint.SetupError):
                drawio_lint.font_path(False)


if __name__ == "__main__":
    unittest.main()
