"""cad.check — questions you cannot ask an axis-aligned box.

  interference()      real solid-solid overlap, including the notched stringers
                      that verify.py's clash check has to skip
  underside_scan()    ray-cast the stringer underside, to compare with Stair.underside()
  clearance()         true minimum distance between two solids
  ray_cast()          a fastener as a segment: which bodies it crosses, and how deep

Nothing here decides anything. It measures, and spike.py prints the numbers next
to verify.py's so the two can be compared.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from build123d import Axis, Location, Vector
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

TOL = 1e-6
VOL_TOL = 1e-4          # below this an "overlap" is a shared face, not material


# ---------------------------------------------------------------- interference
def _bbox_overlap(a, b, tol=1e-7):
    for (a0, a1), (b0, b1) in zip(a.bbox, b.bbox):
        if min(a1, b1) - max(a0, b0) <= tol:
            return False
    return True


@dataclass
class Clash:
    a: str
    b: str
    volume: float
    box: tuple          # ((x0,x1),(y0,y1),(z0,z1)) of the shared material

    def __str__(self):
        (x0, x1), (y0, y1), (z0, z1) = self.box
        return (f"{self.a} ∩ {self.b}: {self.volume:.2f} cu in  "
                f"(x {x0:.2f}→{x1:.2f}, y {y0:.2f}→{y1:.2f}, z {z0:.2f}→{z1:.2f})")


def interference(pieces, skip_pairs=()):
    """Every pair of solids that shares material. Bounding boxes prefilter, then a
    real boolean — so a notched stringer is tested on its profile, not its bbox."""
    skip = {frozenset(p) for p in skip_pairs}
    out = []
    for a, b in combinations(pieces, 2):
        if a.parent and a.parent == b.parent:      # laminations of one member
            continue
        if frozenset((a.id, b.id)) in skip or not _bbox_overlap(a, b):
            continue
        try:
            common = a.solid & b.solid
        except Exception:
            continue
        if common is None:
            continue
        try:
            vol = common.volume
        except Exception:
            continue
        if vol > VOL_TOL:
            bb = common.bounding_box()
            out.append(Clash(a.id, b.id, vol,
                             ((bb.min.X, bb.max.X), (bb.min.Y, bb.max.Y), (bb.min.Z, bb.max.Z))))
    return out


# ------------------------------------------------------------------- distance
def clearance(a_solid, b_solid):
    """True minimum distance between two solids (0.0 if they touch or overlap)."""
    d = BRepExtrema_DistShapeShape(a_solid.wrapped, b_solid.wrapped)
    d.Perform()
    p1, p2 = d.PointOnShape1(1), d.PointOnShape2(1)
    return d.Value(), (p1.X(), p1.Y(), p1.Z()), (p2.X(), p2.Y(), p2.Z())


# --------------------------------------------------------------- bearing area
AX = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}


def bearing_area(a_solid, b_solid, axis, eps=0.01):
    """How much face two touching solids actually share, in square inches.

    Touching solids boolean to nothing, so this nudges `b` into `a` by `eps` along
    `axis` and divides the sliver's volume by `eps`. Both directions are tried and
    the larger taken, so the caller does not have to know which side b sits on.
    Returns 0.0 when the two only meet on an edge or not at all."""
    d = Vector(AX[axis])
    best = 0.0
    for sign in (1, -1):
        try:
            common = a_solid & (Location(d * (eps * sign)) * b_solid)
        except Exception:
            continue
        if common is None:
            continue
        try:
            best = max(best, common.volume / eps)
        except Exception:
            pass
    return best


# ------------------------------------------------------------------ ray casts
def _hits(solid, start, direction, length):
    """Sorted distances along the ray where it crosses `solid`'s boundary."""
    axis = Axis(tuple(start), tuple(direction))
    d = Vector(direction).normalized()
    s = Vector(start)
    ts = []
    for pnt in solid.find_intersection_points(axis):
        p = pnt[0] if isinstance(pnt, tuple) else pnt
        t = (Vector(p) - s).dot(d)
        if -TOL <= t <= length + TOL:
            ts.append(max(t, 0.0))
    ts.sort()
    # a ray that starts flush on a face reports that face once; drop duplicates
    out = []
    for t in ts:
        if not out or t - out[-1] > 1e-6:
            out.append(t)
    return out


def depth_in(solid, start, direction, length):
    """(depth of material crossed, entry t, exit t) for one body, or None."""
    ts = _hits(solid, start, direction, length)
    if not ts:
        return None
    # pairs of crossings are material; an odd count means the ray ends inside
    spans, i = [], 0
    while i < len(ts):
        t0 = ts[i]
        t1 = ts[i + 1] if i + 1 < len(ts) else length
        spans.append((t0, t1))
        i += 2
    depth = sum(b - a for a, b in spans)
    if depth <= TOL:
        return None
    return depth, spans[0][0], spans[-1][1]


@dataclass
class Fastener:
    id: str
    start: tuple
    direction: tuple
    length: float
    spec: str = ""


@dataclass
class RayHit:
    piece: str
    entry: float
    exit: float
    depth: float


def ray_cast(fastener, pieces):
    """Which bodies the screw crosses, in order, with the depth reached in each."""
    hits = []
    for p in pieces:
        r = depth_in(p.solid, fastener.start, fastener.direction, fastener.length)
        if r:
            depth, t0, t1 = r
            hits.append(RayHit(p.id, t0, t1, depth))
    hits.sort(key=lambda h: h.entry)
    return hits


# ------------------------------------------------------------- stringer probe
def underside_scan(stringer_piece, ys, x=None):
    """z of the stringer's bottom face at each plan y, by casting a ray straight up
    from below. Compares directly with verify.py's Stair.underside(y)."""
    (x0, x1), _, (z0, _) = stringer_piece.bbox
    xm = x if x is not None else (x0 + x1) / 2
    out = {}
    for y in ys:
        ts = _hits(stringer_piece.solid, (xm, y, z0 - 10.0), (0, 0, 1), 200.0)
        out[y] = (z0 - 10.0 + ts[0]) if ts else None
    return out
