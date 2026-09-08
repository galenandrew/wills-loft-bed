"""sheets.geometry — a named view of the kernel model, cached on disk.

A ViewSpec says where the camera is and, for a section, where the plane cuts.
`view(spec)` returns one record per solid:

    id · component · layer · stock
    faces    the front faces, projected: [(pts, shade, depth)]
    outline  those faces fused — the piece's silhouette
    cut      plane ∩ piece, for a section
    near     the silhouette of whatever part of the piece stands between the
             viewer and the cut plane (the ghosted overlay a section wants)

Nothing here decides how a piece is drawn; that is the sheet's business. This
just answers, once and cheaply, what shape every piece is from a given angle.

The kernel costs ~3 s to import and ~0.2 s a view, and the edit hook rebuilds the
site on every Write. So results are cached under .kernel-cache, keyed by a hash of
every input that can change them — the yaml, verify.py, drawings/model.py, cad/*
and this package. Touch a label and the cache hits; touch geometry and it misses
and the kernel runs. LOFT_KERNEL_NOCACHE=1 forces a real run.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".kernel-cache")

INPUTS = ([os.environ.get("LOFT_YAML") or os.path.join(ROOT, "dimensions.yaml"),
           os.path.join(ROOT, "verify.py"),
           os.path.join(ROOT, "drawings", "model.py")]
          + sorted(glob.glob(os.path.join(ROOT, "cad", "*.py")))
          + sorted(glob.glob(os.path.join(ROOT, "sheets", "taxonomy.py")))
          + [os.path.abspath(__file__)])

MISSES = []          # view keys that actually ran the kernel, for the build report


@dataclass(frozen=True)
class ViewSpec:
    """direction is where the camera LOOKS. `mirror` flips h, for the plan, whose
    stated convention (bed wall up, window wall left) is the mirror of the
    right-handed frame — see the axis note in CLAUDE.md."""
    key: str
    direction: tuple
    up: tuple = (0, 0, 1)
    mirror: bool = False
    cut: tuple | None = None            # (axis, at) — keep what is BEYOND the plane
    depth: float | None = None          # …but only this far beyond it
    near: bool = False                  # also silhouette what stands in front of it
    context: bool = True

    def ident(self):
        return (self.key, self.direction, self.up, self.mirror, self.cut,
                self.depth, self.near, self.context)


def _key(spec):
    h = hashlib.sha256()
    for f in INPUTS:
        h.update(open(f, "rb").read())
    h.update(repr(spec.ident()).encode())
    return h.hexdigest()[:16]


def view(spec):
    """[record] for every solid, far to near. Records are plain dicts so they
    round-trip through the cache unchanged."""
    path = os.path.join(CACHE, f"view-{spec.key}-{_key(spec)}.json")
    if not os.environ.get("LOFT_KERNEL_NOCACHE") and os.path.exists(path):
        return json.load(open(path))
    recs = _extract(spec)
    os.makedirs(CACHE, exist_ok=True)
    json.dump(recs, open(path, "w"), separators=(",", ":"))
    MISSES.append(spec.key)
    return recs


def _r(pts):
    return [[round(h, 4), round(v, 4)] for h, v in pts]


def _extract(spec):
    from cad.model import build
    from cad import view3d as V
    from sheets import taxonomy as tx

    pieces = build(context=spec.context)
    tx.check(pieces)
    d, right, up = V.frame(spec.direction, spec.up)
    right = V.flip(right, spec.mirror)

    recs = []
    for p in pieces:
        solid = p.solid
        cut = []
        near = []
        if spec.cut:
            axis, at = spec.cut
            cut = _r_loops(V.cut_loops(solid, axis, at, right, up))
            # "beyond" is the side the camera does NOT stand on: looking up an
            # axis (+d) the camera stands low, so the far side is the high one.
            keep_low = spec.direction[{"x": 0, "y": 1, "z": 2}[axis]] < 0
            far = V.clipped(solid, axis, at, keep_low)
            # A detail wants a SLAB, not the whole field behind the plane: without
            # it, a section at the beam's seat draws every joist, block and rail
            # between the cut and the far wall on top of each other, and the joint
            # the sheet exists for disappears into the pile.
            if far is not None and spec.depth:
                back = at - spec.depth if keep_low else at + spec.depth
                far = V.clipped(far, axis, back, not keep_low)
            if spec.near:
                n = V.clipped(solid, axis, at, not keep_low)
                if n is not None:
                    near = _r_loops(V.outline(V.faces(n, d, right, up)))
            solid = far
        if solid is None:
            if not cut and not near:
                continue
            facets, out = [], []
        else:
            facets = V.faces(solid, d, right, up)
            out = _r_loops(V.outline(facets))
        recs.append({
            "id": p.id, "component": tx.component(p), "layer": tx.layer(p),
            "stock": p.stock, "assembly": p.assembly, "derived": p.derived,
            "faces": [{"pts": _r(f.loops[0]),
                       "holes": [_r(l) for l in f.loops[1:]],
                       "shade": round(f.shade, 3), "depth": round(f.depth, 4)}
                      for f in facets],
            "outline": out, "cut": cut, "near": near,
        })
    return recs


def _r_loops(loops):
    return [_r(l) for l in loops]


def projector(spec):
    """A function (x, y, z) → (h, v) in this view's own inches, for the handful of
    things a sheet draws that are not solids: a floor plane on an isometric, a
    door swing, a light symbol, a leader that has to start on a real member."""
    from cad.frame import frame, flip, project
    _d, right, up = frame(spec.direction, spec.up)
    right = flip(right, spec.mirror)
    return lambda x, y, z: project((x, y, z), right, up)


def bounds(recs, what=("faces", "cut", "near")):
    """(h0, h1, v0, v1) over everything drawn — so a sheet can frame itself off the
    model instead of off hand-typed numbers."""
    hs, vs = [], []
    for r in recs:
        for f in r["faces"] if "faces" in what else []:
            for h, v in f["pts"]:
                hs.append(h); vs.append(v)
        for k in ("cut", "near"):
            if k in what:
                for loop in r[k]:
                    for h, v in loop:
                        hs.append(h); vs.append(v)
    return (min(hs), max(hs), min(vs), max(vs)) if hs else (0, 0, 0, 0)
