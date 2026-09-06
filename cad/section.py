"""cad.section — a true section through the kernel model, in the drawings' own view.

One call returns three layers:
  cut     — plane ∩ solids: the closed faces a saw would expose, per piece
  beyond  — hidden-line projection of everything on the far side of the plane
  near    — the same for what sits between the viewer and the plane (Drawing 4
            ghosts the half-wall this way)

Output is in the *inch* (h, v) coordinates drawings/svgview.View takes, so the same
View(scale, margins) as the hand-drawn sheet renders it at the same size on the
same page. Orientation follows the site's stated conventions: plans bed-wall-up
with the window wall left; y–z views bed-wall-left (mirrored); x–z views
window-wall-left, looking toward the bed wall.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from build123d import Box, Compound, Edge, Plane, Pos, Vector
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt
from OCP.TopAbs import TopAbs_ShapeEnum
from OCP.TopExp import TopExp_Explorer

CAM = 4000.0     # far enough that HLR is orthographic in practice
BIG = 8000.0     # half-space cutter


@dataclass
class Layers:
    """Every list is [(piece id, geometry)] — the id survives projection, so a
    sheet can style one member differently from its neighbour."""
    cut: list = field(default_factory=list)         # [(id, [(h, v), ...])] closed loops
    beyond_vis: list = field(default_factory=list)  # [(id, (h0, v0, h1, v1))]
    beyond_hid: list = field(default_factory=list)
    near_vis: list = field(default_factory=list)
    near_hid: list = field(default_factory=list)


# ------------------------------------------------------------------ view frame
def view_frame(axis, look_positive=True):
    """(direction, right, up) in yaml space, plus the camera-u sign.

    `look_positive` puts the camera on the low side of `axis`, looking up it —
    for a section at x that is Drawing 4's angle, with the half-wall in front."""
    if axis == "x":
        right, up = Vector(0, 1, 0), Vector(0, 0, 1)        # bed wall left
    elif axis == "y":
        right, up = Vector(1, 0, 0), Vector(0, 0, 1)        # window wall left
    else:
        right, up = Vector(1, 0, 0), Vector(0, 1, 0)        # plan, bed wall up
    d = {"x": Vector(1, 0, 0), "y": Vector(0, 1, 0), "z": Vector(0, 0, -1)}[axis]
    direction = d if look_positive else -d
    # HLR's camera frame: Z = -direction, Y = up, X = Y × Z. u is along X, so the
    # sign that maps u onto our screen-right is X · right (always ±1 here).
    x_cam = up.cross(-direction)
    return direction, right, up, (1.0 if x_cam.dot(right) > 0 else -1.0)


def _half_space(axis, at, keep_low):
    """A big box covering everything on one side of the plane `axis = at`."""
    span = {a: (-BIG / 2, BIG / 2) for a in "xyz"}
    span[axis] = (at - BIG, at) if keep_low else (at, at + BIG)
    c = {a: (span[a][0] + span[a][1]) / 2 for a in "xyz"}
    s = {a: span[a][1] - span[a][0] for a in "xyz"}
    return Pos(c["x"], c["y"], c["z"]) * Box(s["x"], s["y"], s["z"])


# ----------------------------------------------------------------------- cut
def cut(pieces, axis, at):
    """Plane ∩ solids → closed (h, v) loops, one per exposed face."""
    _, right, up, _ = view_frame(axis)
    normal = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis]
    origin = {"x": (at, 0, 0), "y": (0, at, 0), "z": (0, 0, at)}[axis]
    plane = Plane(origin=origin, z_dir=normal)
    loops = []
    for p in pieces:
        try:
            sec = p.solid & plane
        except Exception:
            continue
        if sec is None:
            continue
        for face in sec.faces():
            if face.area < 1e-6:
                continue
            for wire in [face.outer_wire()] + list(face.inner_wires()):
                pts = _wire_points(wire, right, up)
                if len(pts) >= 3:
                    loops.append((p.id, pts))
    return loops


def _wire_points(wire, right, up):
    edges = wire.edges()
    if not edges:
        return []
    segs = [(tuple(e.vertices()[0]), tuple(e.vertices()[-1])) for e in edges]
    pts, used = [segs[0][0], segs[0][1]], {0}
    while len(used) < len(segs):
        for i, (a, b) in enumerate(segs):
            if i in used:
                continue
            if _same(a, pts[-1]):
                pts.append(b); used.add(i); break
            if _same(b, pts[-1]):
                pts.append(a); used.add(i); break
        else:
            break
    if len(pts) > 1 and _same(pts[0], pts[-1]):
        pts = pts[:-1]
    return [(Vector(p).dot(right), Vector(p).dot(up)) for p in pts]


def _same(a, b, tol=1e-6):
    return all(abs(x - y) < tol for x, y in zip(a, b))


# --------------------------------------------------------------- projection
def project(pieces, axis, at=None, look_positive=True, side=None):
    """Hidden-line projection that keeps member identity.

    Every piece goes into ONE HLR pass, so occlusion is computed across the whole
    assembly — and then each piece's own visible/hidden edges are read back with
    HLRBRep_HLRToShape's per-shape overload. build123d's project_to_viewport()
    wrapper only exposes the whole-assembly query, which is why this drops to OCP.
    The per-shape edge sets partition the whole-assembly set exactly.

    Returns (visible, hidden) as [(piece id, (h0, v0, h1, v1)), ...]."""
    direction, right, up, sign = view_frame(axis, look_positive)
    keep = []
    for p in pieces:
        s = p.solid
        if side is not None:
            keep_low = (side == "near") == look_positive
            try:
                s = s & _half_space(axis, at, keep_low)
            except Exception:
                continue
            if s is None:
                continue
            try:
                if not s.solids() or s.volume < 1e-6:
                    continue
            except Exception:
                continue
        keep.append((p.id, s))
    if not keep:
        return [], []

    algo = HLRBRep_Algo()
    for _pid, s in keep:
        algo.Add(s.wrapped)
    origin = -direction * CAM
    cs = gp_Ax2()
    cs.SetAxis(gp_Ax1(gp_Pnt(*origin), gp_Dir(*(-direction))))
    cs.SetYDirection(gp_Dir(*up))
    algo.Projector(HLRAlgo_Projector(cs))
    algo.Update()
    algo.Hide()
    hlr = HLRBRep_HLRToShape(algo)

    vis_out, hid_out = [], []
    for pid, s in keep:
        for bucket, getters in ((vis_out, (hlr.VCompound, hlr.OutLineVCompound,
                                           hlr.Rg1LineVCompound)),
                                (hid_out, (hlr.HCompound, hlr.OutLineHCompound,
                                           hlr.Rg1LineHCompound))):
            for get in getters:
                for e in _edges_of(get(s.wrapped)):
                    vs = Edge(e).vertices()
                    if len(vs) < 2:
                        continue
                    a, b = vs[0], vs[-1]
                    bucket.append((pid, (sign * a.X, a.Y, sign * b.X, b.Y)))
    return vis_out, hid_out


def _edges_of(compound):
    if compound is None or compound.IsNull():
        return []
    out, ex = [], TopExp_Explorer(compound, TopAbs_ShapeEnum.TopAbs_EDGE)
    while ex.More():
        out.append(ex.Current())
        ex.Next()
    return out


def section(pieces, axis, at, look_positive=True):
    L = Layers()
    L.cut = cut(pieces, axis, at)
    L.beyond_vis, L.beyond_hid = project(pieces, axis, at, look_positive, side="far")
    L.near_vis, L.near_hid = project(pieces, axis, at, look_positive, side="near")
    return L


# --------------------------------------------------------------------- render
STYLE = """
svg{background:#fff}
.cut{fill:#e8dfcf;stroke:#1a1a1a;stroke-width:1.6}
.cutsheet{fill:#cfd8dd;stroke:#1a1a1a;stroke-width:1.6}
.cutfin{fill:#f3e6cf;stroke:#1a1a1a;stroke-width:1.2}
.bvis{stroke:#444;stroke-width:.7;fill:none}
.bhid{stroke:#888;stroke-width:.45;fill:none;stroke-dasharray:3 2.5}
.nvis{stroke:#b06a3b;stroke-width:.5;fill:none;stroke-dasharray:5 3}
.nhid{stroke:#d7b49a;stroke-width:.4;fill:none;stroke-dasharray:2 3}
text{font:10px ui-sans-serif,system-ui,sans-serif;fill:#333}
.ttl{font-size:11px;fill:#111}
"""

CUT_CLASS = {"ply-3/4": "cutsheet", "ply-1/2": "cutsheet", "poplar-3/4": "cutfin"}


def to_svg(layers, view, pieces=None, title="", layers_on=("near", "beyond", "cut")):
    """Render Layers through a drawings/svgview.View — same scale, same margins, so it
    drops onto the sheet the hand-drawn figure came off."""
    stock = {p.id: p.stock for p in (pieces or [])}
    out = []
    if "near" in layers_on:
        for cls, segs in (("nhid", layers.near_hid), ("nvis", layers.near_vis)):
            out += [_seg(view, g, cls) for _pid, g in segs]
    if "beyond" in layers_on:
        for cls, segs in (("bhid", layers.beyond_hid), ("bvis", layers.beyond_vis)):
            out += [_seg(view, g, cls) for _pid, g in segs]
    if "cut" in layers_on:
        for pid, pts in layers.cut:
            cls = CUT_CLASS.get(stock.get(pid.split("#")[0]), "cut")
            pt = " ".join(f"{view.X(h):.2f},{view.Y(v):.2f}" for h, v in pts)
            out.append(f'<polygon class="{cls}" points="{pt}"/>')
    body = "".join(out)
    t = f'<text class="ttl" x="12" y="{view.H - 10:.0f}">{title}</text>' if title else ""
    # the hand-drawn View clips every rect to its own box; do the same here, or the
    # projected far-field runs off the sheet
    cx, cy = view.X(view.h0), view.Y(view.v1)
    cw, ch = (view.h1 - view.h0) * view.s, (view.v1 - view.v0) * view.s
    clip = (f'<clipPath id="vb"><rect x="{cx:.1f}" y="{cy:.1f}" '
            f'width="{cw:.1f}" height="{ch:.1f}"/></clipPath>')
    return (f'<svg viewBox="0 0 {view.W:.0f} {view.H:.0f}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="{title}"><style>{STYLE}</style><defs>{clip}</defs>'
            f'<rect width="{view.W:.0f}" height="{view.H:.0f}" fill="#fff"/>'
            f'{t}<g clip-path="url(#vb)">{body}</g></svg>')


def _seg(view, s, cls):
    h0, v0, h1, v1 = s
    return (f'<line class="{cls}" x1="{view.X(h0):.2f}" y1="{view.Y(v0):.2f}" '
            f'x2="{view.X(h1):.2f}" y2="{view.Y(v1):.2f}"/>')
