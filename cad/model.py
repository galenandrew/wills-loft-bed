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
WIDTH_X = dm.STAIR_X          # the finished board width, skirt face to right wall: 107 → 131


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
# Five assemblies, as the builder splits them. The landing is part of the STAIR — it
# is the top step — not a thing of its own. The nook's *framing* is the half-wall's
# rough opening and stays with the half-wall; what belongs to the nook is its lining
# and the two nailer walls that carry it. `loft` is the deck the bed sits on plus the
# beam and the boxed ledge; `screen` is the guard above the beam.
SCOPE = {
    "loft":      ["rear_ledger", "side_ledger",
                  *[f"ledger_blocking[{i}]" for i in range(8)], "ledger_blocking_last",
                  *[f"deck_joist[{i}]" for i in range(9)], "deck_rim",
                  "beam", "deck_ply",
                  "beam_wrap_face", "beam_wrap_underside",
                  "ledge_front_rail", "ledge_lid"],
    "screen":    ["screen_top_plate", *[f"slat[{i}]" for i in range(23)]],
    "stair":     ["stringer_a", "stringer_b", "stringer_c", "kicker",
                  "lnd_ledger_bedwall", "lnd_ledger_rightwall", "lnd_side_member",
                  "lnd_joist[0]", "lnd_joist[1]", "lnd_rim",
                  "lnd_blocking[0]", "lnd_blocking[1]", "lnd_ply",
                  "stringer_a_skin", "stringer_a_skin_cleat"],
    "half_wall": ["hw_bottom_plate_a", "hw_bottom_plate_b",
                  "hw_king_a", "hw_king_b", "hw_trimmer_a", "hw_trimmer_b",
                  "hw_jamb_ply_a", "hw_jamb_ply_b",
                  "hw_header", "hw_top_plate_1", "hw_top_plate_2", "hw_rake_nailer",
                  "hw_sheath_loft_a", "hw_sheath_loft_head",
                  "hw_sheath_stair", "hw_end_cap"],
    "nook":      ["nk_bedwall_stud[0]", "nk_bedwall_stud[1]",
                  "nk_bedwall_stud[2]", "nk_bedwall_cap",
                  "nk_shortwall_strut[0]", "nk_shortwall_strut[1]",
                  "nk_shortwall_strut[2]",
                  "nk_wrap_bedwall", "nk_wrap_shortwall",
                  "nk_soffit_flat", "nk_soffit_rake"],
}

# Context, not the build: the mattress and the three things already in the room. They
# are what the clearance questions are asked *against* (headroom over the mattress, the
# fan over the screen), so the kernel needs them — but they are not material to cut and
# a section sheet must never hatch a dresser. build() leaves them out unless asked.
CONTEXT = ["desk", "dresser", "fan"]

# A "2x10 sandwich" header is two 2x10s over a 1/2 ply flitch — 1.5 + 0.5 + 1.5 = 3.5,
# which is what the lumber table gives. The yaml carries it as one 3.5" box; the
# kernel splits it so a fastener ray can report the depth reached in each ply.
# ASSUMED build-up (the drawings never state the lay-up order); flagged in the report.
LAMINATIONS = {
    "header-2x10-sandwich": [("2x10-loft", 1.5), ("ply-1/2", 0.5), ("2x10-stair", 1.5)],
    "2x10x2": [("2x10-a", 1.5), ("2x10-b", 1.5)],
}

# The inverse of LAMINATIONS: yaml rows that are ONE piece on the bench. The boxed
# ledge's front rail is a single 107 board notched 1 1/2 (x) x 5 (z) over the side
# ledger at the window wall; dimensions.yaml has no notch primitive, so it carries the
# board as the full-depth body plus the tongue left above the notch. Fusing the two
# boxes gives the L-shaped solid the board actually is — one solid, one volume, and a
# clash or ray cast sees the notch instead of a square end 1 1/2 short of the wall.
# Rev AD adds three more: the two faces of the half-wall are one board each side of a
# single seam, and the yaml carries each board as the two or three rectangles it is made
# of (a raked head panel is not a box, and the ledge and beam ends stand above the deck).
# As with the front rail, the fused rows are NOT listed in SCOPE — they are covered by
# NOTCH_PARTS, and listing them too would build them a second time and clash with the
# board they are part of. The stair face carries ledge_end_cap and beam_end_cap, so that
# one board is reported under half_wall even though both ends belong to the loft.
NOTCHED = {
    "ledge_front_rail": ["ledge_front_rail_tongue"],
    # the nook face: a 4 1/4 stile, then one 45 3/4 x 53 3/4 board with the opening in it
    "hw_sheath_loft_head": ["hw_sheath_loft_b"],
    # the stair face: floor-to-ledge-top on the bed-wall side, floor-to-beam-top beyond
    # Rev AE: the stair face is ONE skirt board, floor-to-ledge and floor-to-beam ends included
    "hw_sheath_stair": ["ledge_end_cap", "beam_end_cap"],
    # and the wall's end cap is one board with a corner cut out of it for stringer A
    "hw_end_cap": ["hw_end_cap_foot"],
}
NOTCH_PARTS = {p for parts in NOTCHED.values() for p in parts}


def notched_solid(mid):
    """One member id plus the yaml rows that are the rest of the same piece, fused.

    A row may be raked (the half-wall faces are), so each is built the way build()
    would build it on its own rather than assumed to be a box."""
    solid = _row_solid(mid)
    for part in NOTCHED[mid]:
        solid = solid + _row_solid(part)
    return solid


def _row_solid(mid):
    """The solid for ONE yaml row, by its kind — box unless the row says otherwise."""
    if mid in PROFILED:
        return profiled_solid(mid)
    if M[mid].kind == "stringer":
        return stringer_solid(mid)
    if M[mid].kind == "raked":
        return raked_solid(mid)
    m = M[mid]
    return box(m.x, m.y, m.z)


def _member_pieces(mid, assembly, split_laminations=True):
    m = M[mid]
    stock = m.stock
    if mid in NOTCHED:
        rows = ", ".join([mid] + NOTCHED[mid])
        return [Piece(mid, assembly, notched_solid(mid), stock,
                      note=f"one notched board; the yaml carries it as {rows}")]
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


# --------------------------------------------------------------- raked members
def raked_solid(mid):
    """`kind: raked` — the true y-z profile from verify.rake_pts(), extruded through
    the member's own x extent. Same treatment the stringers get, and the same source:
    verify.py owns the profile, nothing here re-derives it."""
    m = M[mid]
    return prism_yz(dm.rake_pts(m, ST, dm.nook), float(m.x[0]), float(m.x[1]))


# ------------------------------------------------------------------ profiled
# Members whose true outline is a y-z polygon rather than a box or a rake band.
# The polygon comes from drawings/model.py — nothing here re-derives it.
PROFILED = {"stringer_a_skin": lambda: dm.skin_pts()}


def profiled_solid(mid):
    m = M[mid]
    return prism_yz(PROFILED[mid](), float(m.x[0]), float(m.x[1]))


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
def board_solid(y0, y1, z, x0=None, x1=None):
    """A tread or riser board. Rev AC: it is 24 3/4 where it laps the skin on stringer
    A's face and 24 where it butts the half-wall, so the one board that straddles the
    wall's end comes out L-shaped — the notch, fused into one solid."""
    rects = dm.board_rects(y0, y1) if (x0 is None and x1 is None) else \
        [((WIDTH_X[0] if x0 is None else x0), (WIDTH_X[1] if x1 is None else x1), y0, y1)]
    solid = None
    for bx0, bx1, by0, by1 in rects:
        b = box((bx0, bx1), (by0, by1), z)
        solid = b if solid is None else solid + b
    return solid, len(rects) > 1


def tread_pieces(scheme="standard", x0=None, x1=None):
    out = []
    for i in range(1, ST.n_treads + 1):
        ty = tread_extents(i, scheme)
        solid, notched = board_solid(*ty, (ST.riser_z[i] - T, ST.riser_z[i]), x0, x1)
        out.append(Piece(f"tread[{i}]", "stair", solid, "ply-3/4", derived=True,
                         note=f"{ST.n_treads - i + 1} from the top; 1/8 nose past the riser"
                              + ("; notched 3/4 at the half-wall end" if notched else "")))
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
    out = []
    for i in range(1, ST.n_treads + 1):
        y, z = riser_extents(i, scheme)
        solid, notched = board_solid(*y, z, x0, x1)
        out.append(Piece(f"riser[{i}]", "stair", solid, "ply-3/4", derived=True,
                         note=f"riser scheme: {scheme}"
                              + ("; notched 3/4 at the half-wall end" if notched else "")))
    # riser 6: the landing face, from tread 5's cut up to the landing deck's underside.
    ry = ((ST.y_riser_top - RISER_T, ST.y_riser_top) if scheme == "as-drawn"
          else (ST.y_riser_top, ST.y_riser_top + RISER_T))
    out.append(Piece("riser[6]", "stair",
                     board_solid(*ry, (ST.riser_z[ST.n_treads] - T, LAND - T), x0, x1)[0],
                     "ply-3/4", derived=True, note="landing face"))
    return out


# --------------------------------------------------------------------- context
def mattress_piece():
    """The mattress: not a member, and not in the room either until it is bought.
    Placed as Drawing 1 draws it — 2 in off the window wall, against the ledge at
    y = 8, sitting on the finished deck. `mattress.thickness` is still ASSUMED 6."."""
    mat = dm.d["mattress"]
    long_, wide = float(mat["size"][1]), float(mat["size"][0])
    t = float(mat["thickness"])
    return Piece("mattress", "context",
                 box((2.0, 2.0 + long_), (8.0, 8.0 + wide), (dm.DECK, dm.DECK + t)),
                 None, derived=True,
                 note="thickness ASSUMED 6 in; still a field measurement owed")


def context_pieces():
    out = [Piece(mid, "context", box(M[mid].x, M[mid].y, M[mid].z), M[mid].stock,
                 note="existing room fixture, not part of the build")
           for mid in CONTEXT]
    return out + [mattress_piece()]


# ------------------------------------------------------------------- assembly
def build(riser_scheme="standard", laminations=True, context=False):
    """Every solid in scope. Returns a list of Piece. `context=True` adds the
    mattress and the room's existing fixtures, which are measured against but
    never drawn or cut."""
    pieces = []
    for assembly, ids in SCOPE.items():
        for mid in ids:
            if mid in NOTCHED:
                pieces.extend(_member_pieces(mid, assembly, laminations))
            elif mid in PROFILED:
                pieces.append(Piece(mid, assembly, profiled_solid(mid), M[mid].stock,
                                    note="true stepped outline, not the yaml bbox"))
            elif M[mid].kind == "stringer":
                pieces.append(Piece(mid, assembly, stringer_solid(mid), M[mid].stock,
                                    note="true notched profile, not the yaml bbox"))
            elif M[mid].kind == "raked":
                pieces.append(Piece(mid, assembly, raked_solid(mid), M[mid].stock,
                                    note="true raked profile, not the yaml bbox"))
            else:
                pieces.extend(_member_pieces(mid, assembly, laminations))
    pieces += tread_pieces(riser_scheme) + riser_pieces(riser_scheme)
    _assert_full_coverage()
    if context:
        pieces += context_pieces()
    return pieces


def _assert_full_coverage():
    """Every member in dimensions.yaml is either in an assembly, part of a notched
    piece, or room context. A member added to the yaml and not to SCOPE would
    otherwise be silently absent from the kernel."""
    covered = {mid for ids in SCOPE.values() for mid in ids} | NOTCH_PARTS | set(CONTEXT)
    missing = sorted(set(M) - covered)
    if missing:
        raise AssertionError(f"members in dimensions.yaml but not in cad SCOPE: {missing}")


def by_id(pieces):
    return {p.id: p for p in pieces}
