"""cad.model — dimensions.yaml → build123d solids.

Rules:
  · Stair geometry is NOT re-derived. `Stair` (verify.py) and `stringer_pts()`
    (drawings/model.py) are imported and used as-is.
  · Extents are framing extents, exactly as the yaml states them.
  · Anything not in the yaml (treads, risers, the soffit panel, the header's
    laminations) is derived here and flagged `derived=True` so the report can
    say which solids the yaml does not actually contain.

Coordinates are the yaml's: x from the window wall, y from the bed wall,
z above the finished floor. Inches throughout (build123d is unitless).
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from build123d import Box, Plane, Polygon, Pos, extrude  # noqa: E402

import drawings.model as dm  # noqa: E402  (loads the yaml once; gives M, ST, DER, stringer_pts)

ST = dm.ST
M = dm.M
T = dm.T                      # tread thickness
LAND = dm.LAND                # finished landing top
STAIR = dm.d["stair"]
WIDTH_X = (float(M["kicker"].x[0]), float(M["kicker"].x[1]))   # stair width, wall to wall: 107 → 131


# --------------------------------------------------------------------- pieces
@dataclass
class Piece:
    """One solid. `id` matches the yaml member id where there is one."""
    id: str
    assembly: str
    solid: object
    stock: str | None = None
    derived: bool = False       # not a member in dimensions.yaml
    note: str = ""
    parent: str | None = None   # for laminations: the yaml member they come from

    @property
    def bbox(self):
        bb = self.solid.bounding_box()
        return ((bb.min.X, bb.max.X), (bb.min.Y, bb.max.Y), (bb.min.Z, bb.max.Z))

    @property
    def volume(self):
        return self.solid.volume


def box(x, y, z):
    """A solid from framing extents [x0,x1],[y0,y1],[z0,z1]."""
    dx, dy, dz = x[1] - x[0], y[1] - y[0], z[1] - z[0]
    return Pos((x[0] + x[1]) / 2, (y[0] + y[1]) / 2, (z[0] + z[1]) / 2) * Box(dx, dy, dz)


def prism_yz(pts, x0, x1):
    """Extrude a (y, z) profile between x0 and x1. Plane.YZ's local (u,v) is (y,z)."""
    face = Plane.YZ * Polygon(*pts, align=None)
    # Plane.YZ's face normal points at -x, so extrude along +x explicitly.
    solid = extrude(face, amount=x1 - x0, dir=(1, 0, 0))
    return Pos(x0, 0, 0) * solid


# ------------------------------------------------------------------ the scope
# The spike's scope, from cad/BRIEF.md: stair + landing, with the half-wall as
# context. Everything else in the yaml (platform, screen, room fixtures) is out.
SCOPE = {
    "stair":    ["stringer_a", "stringer_b", "stringer_c", "kicker"],
    "landing":  ["lnd_ledger_bedwall", "lnd_ledger_rightwall", "lnd_side_member",
                 "lnd_joist[0]", "lnd_joist[1]", "lnd_rim",
                 "lnd_blocking[0]", "lnd_blocking[1]", "lnd_ply"],
    "half_wall": ["hw_header", "hw_king_a", "hw_king_b", "hw_trimmer_a", "hw_trimmer_b",
                  "hw_sheath_stair_a", "hw_sheath_stair_head", "hw_sheath_stair_b",
                  "hw_top_plate_1", "hw_top_plate_2", "hw_bottom_plate"],
}

# A "2x10 sandwich" header is two 2x10s over a 1/2 ply flitch — 1.5 + 0.5 + 1.5 = 3.5,
# which is what the lumber table gives. The yaml carries it as one 3.5" box; the
# kernel splits it so a fastener ray can report the depth reached in each ply.
# ASSUMED build-up (the drawings never state the lay-up order); flagged in the report.
LAMINATIONS = {
    "header-2x10-sandwich": [("2x10-loft", 1.5), ("ply-1/2", 0.5), ("2x10-stair", 1.5)],
    "2x10x2": [("2x10-a", 1.5), ("2x10-b", 1.5)],
}


def _member_pieces(mid, assembly, split_laminations=True):
    m = M[mid]
    stock = m.stock
    lam = LAMINATIONS.get(stock) if split_laminations else None
    if not lam:
        return [Piece(mid, assembly, box(m.x, m.y, m.z), stock)]
    # split along the thinnest axis (the lay-up direction)
    axis = min("xyz", key=lambda a: m.size(a))
    lo = m.ext(axis)[0]
    out = []
    for name, t in lam:
        ext = {a: list(map(float, m.ext(a))) for a in "xyz"}
        ext[axis] = [lo, lo + t]
        out.append(Piece(f"{mid}#{name}", assembly, box(ext["x"], ext["y"], ext["z"]),
                         stock, note=f"lamination of {mid}", parent=mid))
        lo += t
    return out


# ----------------------------------------------------------------- stringers
def stringer_solid(mid):
    """The true notched profile from drawings.stringer_pts(), extruded through the
    stringer's own x thickness. The yaml's z extent for a `kind: stringer` member is
    a bbox placeholder and is deliberately ignored — as verify.py ignores it."""
    m = M[mid]
    return prism_yz(dm.stringer_pts(), float(m.x[0]), float(m.x[1]))


# ------------------------------------------------------- treads/risers (Rev V)
# Neither is a member in dimensions.yaml. Both are derived here exactly as
# drawings/model.py:draw_treads() draws them, so a kernel section can be compared
# with Drawing 4 like for like. `riser_scheme` selects between the two readings of
# the Rev V note — see cad/check.py and the report.
def tread_pieces(scheme="standard", x0=None, x1=None):
    x0 = WIDTH_X[0] if x0 is None else x0
    x1 = WIDTH_X[1] if x1 is None else x1
    out = []
    for i in range(1, ST.n_treads + 1):
        ty = tread_extents(i, scheme)
        out.append(Piece(f"tread[{i}]", "stair",
                         box((x0, x1), ty, (ST.riser_z[i] - T, ST.riser_z[i])),
                         "ply-3/4", derived=True,
                         note=f"{ST.n_treads - i + 1} from the top; 1/8 nose past the riser"))
    return out


RISER_T = 0.75          # riser board thickness


def riser_extents(i, scheme):
    """(y, z) of riser i, the face at the downhill edge of tread i.

    `standard`  — the builder's detail (2026-09-04): the riser is applied to the
                  exposed DOWNHILL side of the plumb notch, its bottom edge on the
                  stringer's horizontal cut for the tread below, its top at the
                  underside of the tread above. The tread below butts its face —
                  a simple butt joint, nothing notched.
    `as-drawn`  — what drawings/model.py:draw_treads() draws today: recessed behind
                  the plumb face, i.e. into solid stringer.
    `on-tread`  — the Rev V note read literally: bottom on top of the tread below."""
    y1 = ST.tread_y(i)[1]
    bottom_cut = (ST.riser_z[i - 1] - T) if i > 1 else 0.0
    if scheme == "as-drawn":
        return (y1 - RISER_T, y1), (bottom_cut, ST.riser_z[i] - T)
    if scheme == "on-tread":
        return (y1, y1 + RISER_T), ((ST.riser_z[i - 1] if i > 1 else 0.0), ST.riser_z[i] - T)
    return (y1, y1 + RISER_T), (bottom_cut, ST.riser_z[i] - T)


def tread_extents(i, scheme):
    """(y0, y1) of tread i's board. Under `standard` the board starts where the
    riser behind it ends, and noses 1/8 past the riser in front of it."""
    y0, y1 = ST.tread_y(i)
    nose = float(STAIR["tread_board_width"]) - ST.run          # 0.125
    if scheme == "standard":
        return (y0 + RISER_T, y1 + RISER_T + nose)
    return (y0, y0 + float(STAIR["tread_board_width"]))


def riser_pieces(scheme="standard", x0=None, x1=None):
    x0 = WIDTH_X[0] if x0 is None else x0
    x1 = WIDTH_X[1] if x1 is None else x1
    out = []
    for i in range(1, ST.n_treads + 1):
        y, z = riser_extents(i, scheme)
        out.append(Piece(f"riser[{i}]", "stair", box((x0, x1), y, z), "ply-3/4",
                         derived=True, note=f"riser scheme: {scheme}"))
    # riser 6: the landing face, from tread 5's cut up to the landing deck's underside.
    ry = ((ST.y_riser_top - RISER_T, ST.y_riser_top) if scheme == "as-drawn"
          else (ST.y_riser_top, ST.y_riser_top + RISER_T))
    out.append(Piece("riser[6]", "stair",
                     box((x0, x1), ry, (ST.riser_z[ST.n_treads] - T, LAND - T)),
                     "ply-3/4", derived=True, note="landing face"))
    return out


# --------------------------------------------------------------- soffit panel
def soffit_piece():
    """The nook soffit: one 3/4 panel, flat at the finished ceiling to y_meet, then
    riding the stringer undersides. Vertical thickness, exactly as verify.py's
    check_stair_and_nook() models it. Not a member in dimensions.yaml."""
    y0, y1 = dm.NOOK_Y
    ym, top = dm.Y_MEET, dm.CEIL + dm.PANEL
    pts = [(y0, dm.CEIL), (y0, top), (ym, top),
           (y1, dm.U(y1)), (y1, dm.U(y1) - dm.PANEL), (ym, dm.CEIL)]
    return Piece("soffit_panel", "nook", prism_yz(pts, *WIDTH_X), "ply-3/4",
                 derived=True, note="flat to y_meet, then raked on the stringer undersides")


# ------------------------------------------------------------------- assembly
def build(riser_scheme="standard", laminations=True, with_soffit=True):
    """Every solid in the spike's scope. Returns a list of Piece."""
    pieces = []
    for assembly, ids in SCOPE.items():
        for mid in ids:
            if M[mid].kind == "stringer":
                pieces.append(Piece(mid, assembly, stringer_solid(mid), M[mid].stock,
                                    note="true notched profile, not the yaml bbox"))
            else:
                pieces.extend(_member_pieces(mid, assembly, laminations))
    pieces += tread_pieces(riser_scheme) + riser_pieces(riser_scheme)
    if with_soffit:
        pieces.append(soffit_piece())
    return pieces


def by_id(pieces):
    return {p.id: p for p in pieces}
