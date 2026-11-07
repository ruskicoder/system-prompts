#!/usr/bin/env python3
"""Geometry lint for a hand-laid-out draw.io diagram.

Reads an uncompressed .drawio file and checks the exact geometry it describes: every edge must be a
fixed polyline (edgeStyle=none, pinned exit and entry points, explicit waypoints), and every edge label
must be its own text cell, so the lint sees what the renderer draws. Checks, by code:

  AUTO     edge left to draw.io's router, so its path is unknown
  DIAG     diagonal segment
  CROSS    two edges cross (jumps do not make a crossing legible)
  RUN      two edges run along each other closer than --min-gap px
  THRU     edge passes through a box that is neither of its ends
  FRAME    edge crosses a frame border it has no reason to cross, or crosses one more than once
  BORDER   edge runs along a box or frame border
  TERM     straight run before an arrowhead or after the source shorter than --min-terminal px
  BENDS    more than --max-bends bends
  LABEL    edge passes through a text label (edge label, icon caption or frame title)
  OVERLAP  label box overlaps another label or a box it does not belong to
  FIT      text wider or taller than its box
  SIZE     text smaller than --min-pt once the canvas is scaled to --print-width-cm
  EXIT     two edges share one attachment point on a box

Exit code 1 when any finding is reported, 0 when clean, 2 when Pillow or a font is missing. Text is
measured with Arial, or the metric-compatible Liberation Sans, looked up in DRAWIO_LINT_FONT_DIR and
then in the usual Linux, macOS and Windows font folders.
"""
import argparse
import html
import math
import re
import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from PIL import ImageFont
except ImportError:  # reported when a font is first needed
    ImageFont = None

FONT_FILES = {False: ["arial.ttf", "Arial.ttf", "LiberationSans-Regular.ttf"],
              True: ["arialbd.ttf", "Arial Bold.ttf", "LiberationSans-Bold.ttf"]}
FONT_DIRS = ["/usr/share/fonts/truetype/msttcorefonts", "/usr/share/fonts/truetype/liberation",
             "/usr/share/fonts/liberation-sans", "/usr/share/fonts/TTF",
             "/Library/Fonts", "/System/Library/Fonts/Supplemental",
             str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts")]
_font_cache = {}


class SetupError(Exception):
    """Pillow or a measuring font is missing."""


def font_path(bold):
    dirs = ([os.environ["DRAWIO_LINT_FONT_DIR"]] if os.environ.get("DRAWIO_LINT_FONT_DIR") else []) + FONT_DIRS
    for d in dirs:
        for name in FONT_FILES[bold]:
            if (Path(d) / name).is_file():
                return str(Path(d) / name)
    raise SetupError("no Arial or Liberation Sans font found; install one or set DRAWIO_LINT_FONT_DIR")


def font(size, bold):
    if ImageFont is None:
        raise SetupError("Pillow is not installed (python3 -m pip install pillow)")
    key = (round(size), bold)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(font_path(bold), key[0])
    return _font_cache[key]


def style_of(s):
    d = {}
    for part in (s or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            d[k] = v
        elif part:
            d[part] = "1"
    return d


def text_lines(value):
    """Visible lines of an HTML or plain label, each with its bold flag."""
    v = value or ""
    v = re.sub(r"<br\s*/?>|</div>|</p>|</li>", "\n", v, flags=re.I)
    out = []
    for raw in v.split("\n"):
        bold = bool(re.search(r"<b>|<strong>", raw, re.I))
        t = html.unescape(re.sub(r"<[^>]+>", "", raw)).strip()
        if t:
            out.append((t, bold))
    return out


def measure(value, size, all_bold):
    lines = text_lines(value)
    if not lines:
        return 0, 0
    w = max(font(size, all_bold or b).getlength(t) for t, b in lines)
    return w, len(lines) * size * 1.2


class Box:
    def __init__(self, id, x, y, w, h, st, value, parent):
        self.id, self.x, self.y, self.w, self.h, self.st, self.value, self.parent = id, x, y, w, h, st, value, parent

    @property
    def x2(self):
        return self.x + self.w

    @property
    def y2(self):
        return self.y + self.h

    def contains_pt(self, p, pad=0):
        return self.x - pad <= p[0] <= self.x2 + pad and self.y - pad <= p[1] <= self.y2 + pad

    def contains_box(self, o):
        return self.x <= o.x and self.y <= o.y and o.x2 <= self.x2 and o.y2 <= self.y2 and o is not self


def load(path):
    root = ET.parse(path).getroot()
    model = root.find(".//mxGraphModel")
    if model is None:
        sys.exit(f"{path}: no uncompressed mxGraphModel (turn off Extras > Compressed)")
    cells = {c.get("id"): c for c in model.iter("mxCell")}
    abs_xy = {}

    def origin(cid):
        c = cells.get(cid)
        if c is None or c.get("vertex") != "1":
            return 0.0, 0.0
        if cid not in abs_xy:
            g = c.find("mxGeometry")
            px, py = origin(c.get("parent"))
            abs_xy[cid] = (px + float(g.get("x", 0)), py + float(g.get("y", 0)))
        return abs_xy[cid]

    boxes, edges = {}, []
    for cid, c in cells.items():
        g = c.find("mxGeometry")
        if c.get("vertex") == "1" and g is not None:
            x, y = origin(cid)
            boxes[cid] = Box(cid, x, y, float(g.get("width", 0)), float(g.get("height", 0)),
                             style_of(c.get("style")), c.get("value", ""), c.get("parent"))
    for cid, c in cells.items():
        if c.get("edge") == "1":
            g = c.find("mxGeometry")
            st = style_of(c.get("style"))
            pts = [(float(p.get("x")), float(p.get("y"))) for p in g.findall("./Array/mxPoint")] if g is not None else []
            ox, oy = origin(c.get("parent"))
            pts = [(x + ox, y + oy) for x, y in pts]
            edges.append(dict(id=cid, src=c.get("source"), tgt=c.get("target"), st=st, pts=pts, value=c.get("value", ""),
                              sp=g.find("./mxPoint[@as='sourcePoint']") if g is not None else None,
                              tp=g.find("./mxPoint[@as='targetPoint']") if g is not None else None))
    FRAMES.clear()
    for b in boxes.values():
        if "text" not in b.st and any(b.contains_box(o) and "text" not in o.st for o in boxes.values()):
            FRAMES.add(b.id)
    return boxes, edges


EPS = 0.5          # coordinates closer than this are the same line
FRAMES = set()     # ids of boxes that hold other boxes, filled by load()


def kind(b):
    """frame: a box holding other boxes, or a declared container; text: a free label; shape: the rest."""
    st = b.st
    if "text" in st:
        return "text"
    if b.id in FRAMES or st.get("container") == "1" or "swimlane" in st or st.get("shape", "").startswith("mxgraph.aws4.group"):
        return "frame"
    return "shape"


def label_box(b):
    """Absolute box of a vertex's visible text, or None when the text sits inside the shape."""
    st = b.st
    size = float(st.get("fontSize", 12))
    bold = st.get("fontStyle", "0").isdigit() and int(st.get("fontStyle", "0")) & 1 == 1
    w, h = measure(b.value, size, bold)
    if not w:
        return None
    k = kind(b)
    if k == "text":
        al = st.get("align", "center")
        x = b.x if al == "left" else b.x2 - w if al == "right" else b.x + (b.w - w) / 2
        va = st.get("verticalAlign", "middle")
        y = b.y if va == "top" else b.y2 - h if va == "bottom" else b.y + (b.h - h) / 2
        return (x, y, x + w, y + h)
    if k == "frame":
        sl, stp = float(st.get("spacingLeft", 8)), float(st.get("spacingTop", 4))
        if st.get("verticalAlign") == "bottom":
            return (b.x + sl, b.y2 - h - float(st.get("spacingBottom", 2)), b.x + sl + w, b.y2)
        return (b.x + sl, b.y + stp, b.x + sl + w, b.y + stp + h)
    if st.get("verticalLabelPosition") == "bottom":
        cx = b.x + b.w / 2
        return (cx - w / 2, b.y2 + 2, cx + w / 2, b.y2 + 2 + h)
    if st.get("labelPosition") == "right":
        sl = float(st.get("spacingLeft", 4))
        cy = b.y + b.h / 2
        return (b.x2 + sl, cy - h / 2, b.x2 + sl + w, cy + h / 2)
    return None


def anchor(b, fx, fy):
    return (b.x + fx * b.w, b.y + fy * b.h)


def path_of(e, boxes):
    st = e["st"]
    if st.get("edgeStyle", "none") not in ("none", ""):
        return None
    pts = list(e["pts"])
    ends = []
    for end, key, pt in (("exit", "src", e["sp"]), ("entry", "tgt", e["tp"])):
        b = boxes.get(e[key])
        if f"{end}X" in st and b is not None:
            ends.append(anchor(b, float(st[f"{end}X"]), float(st[f"{end}Y"])))
        elif pt is not None and b is None:
            ends.append((float(pt.get("x")), float(pt.get("y"))))
        else:
            return None
    return [ends[0]] + pts + [ends[1]]


def segs(path):
    return list(zip(path, path[1:]))


def seg_hits_rect(a, b, r, pad=0.0):
    """Does the axis-parallel segment a-b enter the open rectangle r shrunk by pad?"""
    x1, y1, x2, y2 = r[0] + pad, r[1] + pad, r[2] - pad, r[3] - pad
    if x1 >= x2 or y1 >= y2:
        return False
    if abs(a[1] - b[1]) < EPS:
        lo, hi = sorted((a[0], b[0]))
        return y1 < a[1] < y2 and lo < x2 and hi > x1
    if abs(a[0] - b[0]) < EPS:
        lo, hi = sorted((a[1], b[1]))
        return x1 < a[0] < x2 and lo < y2 and hi > y1
    for t in [i / 40 for i in range(41)]:
        px, py = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
        if x1 < px < x2 and y1 < py < y2:
            return True
    return False


def cross(p, q, r, s):
    """Proper crossing of two segments (shared endpoints and touching do not count)."""
    def orient(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return 0 if abs(v) < 1e-6 else (1 if v > 0 else -1)
    o1, o2, o3, o4 = orient(p, q, r), orient(p, q, s), orient(r, s, p), orient(r, s, q)
    return o1 * o2 < 0 and o3 * o4 < 0


def parallel_run(p, q, r, s, gap):
    """Length over which two axis-parallel segments run closer than gap."""
    if abs(p[1] - q[1]) < EPS and abs(r[1] - s[1]) < EPS and abs(p[1] - r[1]) < gap:
        lo = max(min(p[0], q[0]), min(r[0], s[0])); hi = min(max(p[0], q[0]), max(r[0], s[0]))
        return hi - lo
    if abs(p[0] - q[0]) < EPS and abs(r[0] - s[0]) < EPS and abs(p[0] - r[0]) < gap:
        lo = max(min(p[1], q[1]), min(r[1], s[1])); hi = min(max(p[1], q[1]), max(r[1], s[1]))
        return hi - lo
    return 0


def border_crossings(path, b):
    n = 0
    for a, c in segs(path):
        ina, inc = b.contains_pt(a), b.contains_pt(c)
        if ina != inc:
            n += 1
        elif not ina and seg_hits_rect(a, c, (b.x, b.y, b.x2, b.y2)):
            n += 2
    return n


def lint(path, a):
    boxes, edges = load(path)
    canvas_w = max((b.x2 for b in boxes.values()), default=0) - min((b.x for b in boxes.values()), default=0)
    pt_per_px = a.print_width_cm / 2.54 * 72 / canvas_w if canvas_w else 1
    out = []

    def add(code, where, msg):
        out.append(f"{code:8} {where}: {msg}")

    shapes = {i: b for i, b in boxes.items() if kind(b) == "shape"}
    frames = {i: b for i, b in boxes.items() if kind(b) == "frame"}
    labels = {}
    for i, b in boxes.items():
        lb = label_box(b)
        if lb:
            labels[i] = lb
    paths = {}
    for e in edges:
        p = path_of(e, boxes)
        if p is None:
            add("AUTO", e["id"], "edge is not a fixed polyline (edgeStyle=none, exitX/exitY, entryX/entryY, waypoints)")
            continue
        paths[e["id"]] = p
        if e["value"].strip():
            add("LABEL", e["id"], "label carried on the edge; place it as its own text cell so it can be checked")
    emap = {e["id"]: e for e in edges}

    for eid, p in paths.items():
        e = emap[eid]
        ends = {e["src"], e["tgt"]}
        for a1, b1 in segs(p):
            if abs(a1[0] - b1[0]) > EPS and abs(a1[1] - b1[1]) > EPS:
                add("DIAG", eid, f"diagonal segment {a1} to {b1}")
        bends = len(p) - 2
        if bends > a.max_bends:
            add("BENDS", eid, f"{bends} bends (max {a.max_bends})")
        arrow_end = e["st"].get("endArrow", "classic") != "none"
        arrow_start = e["st"].get("startArrow", "none") != "none"
        first, last = math.dist(*p[:2]), math.dist(*p[-2:])
        if arrow_end and last < a.min_terminal:
            add("TERM", eid, f"last run {last:.0f} px before the arrowhead")
        if (arrow_start or bends) and first < a.min_terminal and arrow_start:
            add("TERM", eid, f"first run {first:.0f} px after the start arrowhead")
        for sid, b in shapes.items():
            if sid in ends or any(b.contains_box(boxes[x]) for x in ends if x in boxes):
                continue
            if any(seg_hits_rect(s, t, (b.x, b.y, b.x2, b.y2), pad=1) for s, t in segs(p)):
                add("THRU", eid, f"passes through box {sid} ({text_lines(b.value)[0][0] if text_lines(b.value) else ''})")
        for fid, f in frames.items():
            inside = [x for x in ends if x in boxes and (f.contains_box(boxes[x]) or x == fid)]
            n = border_crossings(p, f)
            expected = 1 if len(inside) == 1 else 0
            if fid in ends:
                continue
            if n > expected:
                add("FRAME", eid, f"crosses the border of {fid} {n} times (expected {expected})")
        for bid, b in boxes.items():
            for s, t in segs(p):
                for (u, v) in (((b.x, b.y), (b.x2, b.y)), ((b.x, b.y2), (b.x2, b.y2)), ((b.x, b.y), (b.x, b.y2)), ((b.x2, b.y), (b.x2, b.y2))):
                    if parallel_run(s, t, u, v, a.border_gap) > 12:
                        add("BORDER", eid, f"runs along the border of {bid}")
                        break
        for lid, lb in labels.items():
            if any(seg_hits_rect(s, t, lb, pad=-a.label_pad) for s, t in segs(p)):
                add("LABEL", eid, f"passes through the text of {lid} ({text_lines(boxes[lid].value)[0][0]})")

    ids = list(paths)
    for i, x in enumerate(ids):
        for y in ids[i + 1:]:
            for s, t in segs(paths[x]):
                for u, v in segs(paths[y]):
                    if cross(s, t, u, v):
                        add("CROSS", f"{x} x {y}", f"cross near ({(s[0] + t[0]) / 2:.0f}, {(s[1] + t[1]) / 2:.0f})")
                    elif parallel_run(s, t, u, v, a.min_gap) > 1:
                        add("RUN", f"{x} x {y}", f"run closer than {a.min_gap} px")
    seen = {}
    for eid, p in paths.items():
        for key, pt in ((emap[eid]["src"], p[0]), (emap[eid]["tgt"], p[-1])):
            k = (key, round(pt[0]), round(pt[1]))
            if k in seen:
                add("EXIT", f"{seen[k]} and {eid}", f"share the attachment point {pt} on {key}")
            seen[k] = eid

    lids = list(labels)
    for i, x in enumerate(lids):
        r = labels[x]
        for y in lids[i + 1:]:
            q = labels[y]
            if r[0] < q[2] and q[0] < r[2] and r[1] < q[3] and q[1] < r[3]:
                add("OVERLAP", f"{x} x {y}", "label boxes overlap")
        for sid, b in shapes.items():
            if sid == x or b.contains_box(boxes[x]) or boxes[x].contains_box(b) or boxes[x].parent == sid:
                continue
            if kind(boxes[x]) == "shape" and label_box(boxes[x]) is None:
                continue
            if r[0] < b.x2 - 1 and b.x + 1 < r[2] and r[1] < b.y2 - 1 and b.y + 1 < r[3]:
                add("OVERLAP", x, f"text overlaps box {sid}")
    for bid, b in boxes.items():
        st = b.st
        size = float(st.get("fontSize", 12))
        if text_lines(b.value) and size * pt_per_px < a.min_pt:
            add("SIZE", bid, f"{size:.0f} px text prints at {size * pt_per_px:.1f} pt (min {a.min_pt})")
        if kind(b) == "shape" and bid not in labels and text_lines(b.value):
            bold = st.get("fontStyle", "0").isdigit() and int(st.get("fontStyle", "0")) & 1 == 1
            w, h = measure(b.value, size, bold)
            if w > b.w - 2 * float(st.get("spacing", 2)) + 1 or h > b.h + 1:
                add("FIT", bid, f"text {w:.0f}x{h:.0f} px in a {b.w:.0f}x{b.h:.0f} box")
    return out, pt_per_px


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--print-width-cm", type=float, default=24.0, help="printed figure width (A4 landscape body: about 24)")
    ap.add_argument("--min-pt", type=float, default=7.0)
    ap.add_argument("--min-gap", type=float, default=8.0, help="closest two parallel edges may run")
    ap.add_argument("--min-terminal", type=float, default=20.0)
    ap.add_argument("--max-bends", type=int, default=4)
    ap.add_argument("--border-gap", type=float, default=6.0)
    ap.add_argument("--label-pad", type=float, default=2.0, help="clearance kept around label text")
    a = ap.parse_args()
    bad = 0
    for f in a.files:
        try:
            out, k = lint(f, a)
        except SetupError as err:
            print(f"drawio_lint: {err}", file=sys.stderr)
            sys.exit(2)
        print(f"{f}: {len(out)} finding(s); 1 px prints at {k:.2f} pt")
        for line in out:
            print("  " + line)
        bad += len(out)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
