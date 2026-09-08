"""cad.view3d — one solid, one viewing direction → the polygons a drawing needs.

`cad/section.py` answers "what does this plane cut?"; this module answers "what
does this piece LOOK like from here?", and it answers it per piece, which is the
whole point: every polygon it returns carries the id of the solid it came from,
so a sheet can hide one component, ghost another and hatch a third without
re-running anything.

Two products per piece:

  faces()     the front-facing faces, projected. On an axis-aligned view that is
              one polygon (a box's face, a stringer's true notched profile); on an
              axonometric it is the two or three faces you can see, each with a
              shade from its own normal. Painter-sorted by depth, they compose
              into a drawing with correct occlusion — and because each piece is
              drawn whole, hiding one leaves no hole in what stood behind it.
              That is why the drawings composite in the browser instead of
              baking one hidden-line pass per toggle combination.

  outline()   the same piece's silhouette: its faces fused into closed loops, for
              a crisp edge over the shaded faces or for a ghosted underlay.

Coordinates are the (h, v) inches drawings/svgview.View takes, so what comes out
drops straight onto a sheet at the sheet's own scale.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from build123d import Box, GeomType, Plane, Polygon, Pos, Vector

from .frame import frame as _frame

# Facet tolerance for curved edges (the ceiling fan is the only one, today).
CURVE_TOL = 0.05
BIG = 8000.0


# ------------------------------------------------------------------ view frame
def frame(direction, up=(0, 0, 1)):
    """(direction, right, up) as build123d Vectors — cad.frame does the arithmetic,
    so the sheets can compute the same frame without importing OCCT.

    `direction` is where the CAMERA LOOKS: a front elevation, whose camera stands
    out in the room and looks at the bed wall, is direction (0, -1, 0)."""
    return tuple(Vector(*v) for v in _frame(direction, up))


def flip(right, mirror):
    return -right if mirror else right


# ------------------------------------------------------------ wire → polygon
def _edge_points(edge):
    """An edge as a point list, straight edges as two points and curves faceted."""
    if edge.geom_type == GeomType.LINE:
        vs = edge.vertices()
        return [tuple(vs[0]), tuple(vs[-1])]
    length = max(edge.length, 1e-9)
    n = max(2, min(64, int(math.ceil(length / max(CURVE_TOL, 1e-3)))))
    return [tuple(edge @ (i / n)) for i in range(n + 1)]


def _wire_loop(wire):
    """A wire as an ordered 3D point loop. Edges come back unordered, so chain
    them on shared endpoints the way cad.section does, but keep curve facets."""
    segs = [_edge_points(e) for e in wire.edges()]
    if not segs:
        return []
    pts, used = list(segs[0]), {0}
    while len(used) < len(segs):
        for i, s in enumerate(segs):
            if i in used:
                continue
            if _same(s[0], pts[-1]):
                pts += s[1:]; used.add(i); break
            if _same(s[-1], pts[-1]):
                pts += s[-2::-1]; used.add(i); break
        else:
            break
    if len(pts) > 1 and _same(pts[0], pts[-1]):
        pts = pts[:-1]
    return pts


def _same(a, b, tol=1e-6):
    return all(abs(x - y) < tol for x, y in zip(a, b))


def _to2d(pts, right, up):
    return [(Vector(*p).dot(right), Vector(*p).dot(up)) for p in pts]


def _hull(pts):
    """Convex hull of projected points (monotone chain).

    Used only for a CURVED face, whose boundary wire is a seam plus arcs and does
    not trace the silhouette. Exact for a convex face — the ceiling fan's rim is
    the only curved surface in this model, and a cylinder is convex."""
    pts = sorted(set((round(h, 9), round(v, 9)) for h, v in pts))
    if len(pts) < 3:
        return pts

    def half(seq):
        out = []
        for p in seq:
            while len(out) >= 2 and _cross(out[-2], out[-1], p) <= 0:
                out.pop()
            out.append(p)
        return out[:-1]

    return half(pts) + half(pts[::-1])


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _area(pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                   for i in range(len(pts)))) / 2


# ----------------------------------------------------------------- front faces
@dataclass
class Facet:
    """One projected face. `loops[0]` is the outer boundary, the rest are holes."""
    loops: list
    shade: float          # 0 (dark) … 1 (light), from the face's own normal
    depth: float          # distance toward the camera; larger is farther
    normal: tuple


LIGHT = Vector(-0.35, -0.6, 1.0)      # over the reader's shoulder, from above


def faces(solid, direction, right, up, eps=1e-7):
    """The faces pointing at the camera, projected into (h, v).

    A curved face (the ceiling fan's rim is the only one in this model) has no one
    normal, so it is never culled — its outer wire already traces the silhouette
    the camera sees, and the shade falls back to a mid tone."""
    d, lt = Vector(*direction), (LIGHT / LIGHT.length)
    out = []
    for f in solid.faces():
        planar = f.geom_type == GeomType.PLANE
        try:
            n = f.normal_at(f.center())
        except Exception:
            planar, n = False, -d
        if planar and -n.dot(d) <= eps:
            continue
        if planar:
            loops = []
            for w in [f.outer_wire()] + list(f.inner_wires()):
                pts = _to2d(_wire_loop(w), right, up)
                if len(pts) >= 3 and _area(pts) > 1e-7:
                    loops.append(pts)
            pts3 = _wire_loop(f.outer_wire())
        else:
            verts, _tris = f.tessellate(CURVE_TOL)
            pts3 = [tuple(v) for v in verts]
            hull = _hull(_to2d(pts3, right, up))
            loops = [hull] if len(hull) >= 3 and _area(hull) > 1e-7 else []
        if not loops:
            continue
        depth = max(Vector(*p).dot(d) for p in pts3)
        shade = 0.5 + 0.5 * max(0.0, n.dot(lt)) if planar else 0.75
        out.append(Facet(loops, shade, depth, (n.X, n.Y, n.Z)))
    return out


# ------------------------------------------------------------------- outline
def outline(facets):
    """The piece's silhouette: its FRONT faces fused into closed loops.

    Front faces alone tile the silhouette exactly — a solid's near side is what you
    see — so this fuses one or three polygons instead of all six, and a notched
    stringer still comes back as its one true profile rather than the rectangles it
    was built from. `facets` is what faces() returned for the same view."""
    acc = None
    for fc in facets:
        pts = fc.loops[0]
        if len(pts) < 3 or _area(pts) < 1e-7:
            continue
        poly = Polygon(*pts, align=None)
        acc = poly if acc is None else acc + poly
    if acc is None:
        return []
    try:
        acc = acc.clean()
    except Exception:
        pass
    loops = []
    for f in acc.faces():
        for w in [f.outer_wire()] + list(f.inner_wires()):
            pts = [(v.X, v.Y) for v in w.vertices()]
            if len(pts) >= 3:
                loops.append(_order(pts, w))
    return [l for l in loops if l]


def _order(pts, wire):
    """Vertices come back unordered; walk the wire's edges instead."""
    seq = [(p[0], p[1]) for p in _wire_loop(wire)]
    return seq if len(seq) >= 3 else pts


# -------------------------------------------------------------- half-space clip
def half_space(axis, at, keep_low):
    span = {a: (-BIG / 2, BIG / 2) for a in "xyz"}
    span[axis] = (at - BIG, at) if keep_low else (at, at + BIG)
    c = {a: (span[a][0] + span[a][1]) / 2 for a in "xyz"}
    s = {a: span[a][1] - span[a][0] for a in "xyz"}
    return Pos(c["x"], c["y"], c["z"]) * Box(s["x"], s["y"], s["z"])


def clipped(solid, axis, at, keep_low):
    """`solid` restricted to one side of a plane, or None if nothing is left."""
    try:
        s = solid & half_space(axis, at, keep_low)
        if s is None or not s.solids() or s.volume < 1e-6:
            return None
        return s
    except Exception:
        return None


# ------------------------------------------------------------------- sections
def cut_loops(solid, axis, at, right, up):
    """plane ∩ solid → the closed faces a saw would expose, in (h, v)."""
    normal = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis]
    origin = {"x": (at, 0, 0), "y": (0, at, 0), "z": (0, 0, at)}[axis]
    try:
        sec = solid & Plane(origin=origin, z_dir=normal)
    except Exception:
        return []
    if sec is None:
        return []
    out = []
    for f in sec.faces():
        if f.area < 1e-6:
            continue
        for w in [f.outer_wire()] + list(f.inner_wires()):
            pts = _to2d(_wire_loop(w), right, up)
            if len(pts) >= 3:
                out.append(pts)
    return out
