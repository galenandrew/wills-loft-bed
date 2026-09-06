"""
drawings.model — load dimensions.yaml once and expose everything a sheet module needs.

Sheet modules do `from .model import *` so their figure code reads exactly as it
did in the single-file generator: M (members), ST (stair), DER (verify.py's
derived dict), the room/nook/screen constants, fr(), m(), ids(), R(), View.

The yaml path comes from the LOFT_YAML environment variable (build.py sets it);
default dimensions.yaml in the repo root, whatever the cwd.
"""
import os, sys, html, json, math, datetime, glob, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path: sys.path.insert(0, ROOT)
import yaml
from verify import expand, Stair, compute_derived, RAKED, rake_pts, rake_range, rake_z
from fractions import Fraction
from .svgview import View

def fr(v):
    """53.75 → 53¾ · 15.155 → 15.16 — sixteenths where they are exact, else two decimals."""
    if v is None: return "—"
    v = float(v); n = round(v * 16); f = Fraction(n, 16)
    if abs(n / 16 - v) > 0.004: return f"{v:.2f}".rstrip("0").rstrip(".")
    whole, rem = divmod(abs(f), 1); sign = "-" if v < 0 else ""
    uni = {Fraction(1, 2): "½", Fraction(1, 4): "¼", Fraction(3, 4): "¾"}
    if rem == 0: return f"{sign}{int(whole)}"
    part = uni.get(rem, f"{rem.numerator}/{rem.denominator}")
    return f"{sign}{int(whole)}{part}" if whole and rem in uni else (f"{sign}{int(whole)} {part}" if whole else f"{sign}{part}")

YAML = os.environ.get("LOFT_YAML") or os.path.join(ROOT, "dimensions.yaml")

d = yaml.safe_load(open(YAML)); M = expand(d["members"]); room = d["room"]
lumber = {k: (v[0], v[1]) for k, v in d["lumber"].items()}
d["stair"]["_stringer_depth"] = lumber[d["stair"]["stringer_stock"]][1]
ST = Stair(d["stair"], float(d["expected"]["deck_top"])); T = ST.t
DER = compute_derived(d, M, ST, room)
REV = str(d["rev"])
nook = d["nook"]; HB = float(nook["header_bottom"]); JAMB = float(nook.get("wrap", 0)); CEIL = HB - JAMB
PANEL = float(nook["soffit_panel_thickness"]); NOOK_Y = [float(a) for a in nook["opening_y"]]
CEILING = float(room["ceiling"]); RX, RY = float(room["x"]), float(room["y"])
MAT = d["mattress"]; SCR = d["screen"]
DECK = float(d["expected"]["deck_top"]); LAND = ST.riser_z[ST.n_treads + 1]
# The mattress bay is a FINISHED dimension: the ledge's front face to the beam's inner
# wrap, not to the rough LVL. BEAMSTOCK names the beam in prose so no sheet types it.
BAY = float(M["beam_wrap_inner"].y[0]) - float(M["ledge_front_rail"].y[1])
BEAM_FIN_TOP = float(M["beam_wrap_top"].z[1])
_bt, _bd = lumber[M["beam"].stock]
# Name the beam the way every other member is named: NOMINAL in prose and labels
# (2x14 LVL, as 2x4 is a 2x4), ACTUAL wherever the builder needs the real section.
# Both come off the yaml — the stock key is the nominal, the lumber table the actual.
BEAMSTOCK = M["beam"].stock.replace("lvl-", "").replace("x", "×") + " LVL"
BEAM_ACTUAL = f"{fr(_bt)} × {fr(_bd)}"
def U(y): return ST.underside(y)
Y_MEET = ST.y_riser_top - (CEIL + PANEL - U(ST.y_riser_top)) / ST.tan
def soffit(y): return CEIL if y <= Y_MEET else U(y) - PANEL
def m(i): return M[i]
def ids(prefix): return [k for k in M if k == prefix or k.startswith(prefix + "[")]
def R(v, mem, h, vv, cls="lum", extra=""):
    """Project a member's box onto the (h, vv) axes. A `kind: raked` member has no
    honest box, so on a y-z view it is drawn from its true profile instead."""
    if mem.kind == "raked" and (h, vv) == ("y", "z"):
        v.poly(rake_pts(mem, ST, nook), cls, extra); return
    v.rect(*mem.ext(h), *mem.ext(vv), cls, extra)

def RAKE(mem, y): return rake_z(mem, y, ST, nook)
HATCH = 'fill="url(#hatch)"'
E = html.escape

# finished-opening jambs (derived, not members)
JAMB_Y = [NOOK_Y[0] + JAMB, NOOK_Y[1] - JAMB]

# --------------------------------------------------------------------------- kernel sections
# A sheet that wants a TRUE section asks the plane what it cuts, instead of listing
# members and projecting their boxes by hand. Geometry still comes from the yaml —
# cad/ builds solids from it (and imports Stair/stringer_pts, never re-derives them).
#
# Importing build123d costs ~2.7 s against a build that is otherwise 0.06 s, and the
# edit hook runs the build on every Write/Edit. So cut results are cached on disk,
# keyed by a hash of EVERY input that can change them — the yaml, verify.py (Stair),
# this module (stringer_pts and the tread/riser layout) and all of cad/. Touch any of
# them and the cache misses and the kernel runs; touch a label or a caption and it
# hits, build123d is never imported, and the build stays at 0.06 s.
#
# LOFT_KERNEL_NOCACHE=1 forces a real run. `python3 -m cad` never uses the cache.
CACHE_DIR = os.path.join(ROOT, ".kernel-cache")
KERNEL_INPUTS = ([YAML, os.path.join(ROOT, "verify.py"), os.path.abspath(__file__)]
                 + sorted(glob.glob(os.path.join(ROOT, "cad", "*.py"))))
CACHE_HITS = []

def _kernel_key(*args):
    h = hashlib.sha256()
    for f in KERNEL_INPUTS:
        h.update(open(f, "rb").read())
    h.update(repr(args).encode())
    return h.hexdigest()[:16]

_PIECES = None

def kernel_pieces():
    global _PIECES
    if _PIECES is None:
        from cad.model import build
        _PIECES = build()
    return _PIECES

def _cached_cut(axis, at):
    """The kernel's cut loops for this plane, from disk if nothing upstream moved."""
    key = _kernel_key("cut", axis, at)
    path = os.path.join(CACHE_DIR, f"cut-{key}.json")
    if not os.environ.get("LOFT_KERNEL_NOCACHE") and os.path.exists(path):
        CACHE_HITS.append(f"{axis}={fr(at)}")
        return [(pid, [tuple(p) for p in pts]) for pid, pts in json.load(open(path))]
    from cad.section import cut as _cut
    loops = _cut(kernel_pieces(), axis, at)
    os.makedirs(CACHE_DIR, exist_ok=True)
    json.dump([[pid, [list(p) for p in pts]] for pid, pts in loops], open(path, "w"))
    return loops


def _piece_stock():
    """id → stock, cached alongside the cut so styling never forces a kernel build."""
    key = _kernel_key("stock")
    path = os.path.join(CACHE_DIR, f"stock-{key}.json")
    if not os.environ.get("LOFT_KERNEL_NOCACHE") and os.path.exists(path):
        return json.load(open(path))
    d_ = {p.id: p.stock for p in kernel_pieces()}
    os.makedirs(CACHE_DIR, exist_ok=True)
    json.dump(d_, open(path, "w"))
    return d_


def cut_class(pid):
    """Default cut styling: framing lumber hatched, sheet goods and finish plain.
    A sheet can override any of it via kernel_cut(cls=...)."""
    stock = _piece_stock().get(pid)
    return ("fin", "") if stock in ("ply-3/4", "ply-1/2", "poplar-3/4") else ("lum", HATCH)

def kernel_cut(v, axis, at, skip=(), cls=None, extra=None, order=("lum", "fin")):
    """Draw the model's true section on `axis = at` into View v.

    `skip` names members this sheet deliberately leaves out (Drawing 4 omits the
    nook soffit — that is Drawing 5's story). `cls`/`extra` override the default
    class or SVG attributes per member id. Returns the ids drawn, so a sheet can
    assert it got what it expected."""
    drawn = []
    for pid, pts in _cached_cut(axis, at):
        base = pid.split("#")[0]
        stem = base.split("[")[0]
        if base in skip or stem in skip or any(
                s.endswith("*") and stem.startswith(s[:-1]) for s in skip):
            continue
        c, ex = cut_class(pid)
        c = (cls or {}).get(base, (cls or {}).get(base.split("[")[0], c))
        ex = (extra or {}).get(base, ex)
        drawn.append((order.index(c) if c in order else len(order), pid, pts, c, ex))
    for _k, pid, pts, c, ex in sorted(drawn, key=lambda r: r[0]):
        v.poly(pts, c, ex)
    return [pid for _k, pid, _p, _c, _e in sorted(drawn, key=lambda r: r[0])]

# --------------------------------------------------------------------------- stair profile
KICK = M["kicker"]
# Rev W: the stringers' floor seat runs over the kicker, so they are notched to hook
# over it. True when the kicker's downhill face is the stringer's bottom plumb cut and
# it sits on the floor; if the kicker ever moves, the profile falls back to a flat seat.
NOTCH_KICKER = abs(KICK.y[1] - ST.y_bottom) < 0.011 and KICK.z[0] < 0.011

def stringer_pts():
    top = LAND - ST.deck_t
    pts = []
    if ST.top_run > 0:
        y_edge = ST.y_riser_top - (top - (LAND - T)) / ST.tan
        pts = [(ST.y_top, U(ST.y_top)), (ST.y_top, top), (y_edge, top), (ST.y_riser_top, LAND - T)]
    else:
        pts = [(ST.y_top, U(ST.y_top)), (ST.y_top, ST.riser_z[ST.n_treads] - T)]
    foot = KICK.z[1] if NOTCH_KICKER else 0
    for i in range(ST.n_treads, 0, -1):
        y0, y1 = ST.tread_y(i)
        pts += [(y0, ST.riser_z[i] - T), (y1, ST.riser_z[i] - T), (y1, (ST.riser_z[i - 1] - T) if i > 1 else foot)]
    if NOTCH_KICKER:
        pts += [(KICK.y[0], KICK.z[1]), (KICK.y[0], 0)]
    pts += [(ST.y_riser_top + U(ST.y_riser_top) / ST.tan, 0)]
    return pts

# Rev W — tread/riser joinery. The exposed face of every plumb notch is its DOWNHILL
# side (material is uphill of it), so the riser board goes in front of the cut, its
# bottom edge on the stringer's horizontal cut for the tread below. The tread below
# starts where that riser ends and butts its face: a simple butt joint, riser behind
# the tread, nothing notched. The board is still tread_board_width wide, so the
# nosing-to-nosing going stays exactly stair.run.
RISER_T = 0.75                                                # 3/4 ply, same as the treads
NOSE = float(d["stair"]["tread_board_width"]) - ST.run        # 1/8 past the riser face

def tread_y_board(i):
    """tread i's BOARD extent in y (not the stringer's run — that is ST.tread_y)."""
    y0, y1 = ST.tread_y(i)
    return y0 + RISER_T, y1 + RISER_T + NOSE

def riser_y(i):
    """riser i's y extent: applied to the downhill face of the plumb notch at tread i's foot."""
    y1 = ST.tread_y(i)[1]
    return y1, y1 + RISER_T

# Rev AC — stringer A's outer face is skinned in 3/4 ply, closing the understair cavity
# on the room side; the boards that pass it run wider and lap it, the boards uphill of
# the half-wall's end butt the wall and stay 24. Board 3 straddles the step and is
# notched. Rev AE: the two faces are no longer 3/4 apart. Stringer A moved out onto the
# half-wall framing, taking the skin with it, so the finished face past the wall's end
# is at 105.5 while the wall's own face is still 107 — a 1 1/2 step, and it falls on the
# END CAP's face at y 50.75, not on the skin's start (the skin now runs behind the cap's
# notched corner to y 50). All of it still comes off the members.
SKIN = M["stringer_a_skin"]
SKIRT = M["hw_sheath_stair"]                                   # the half wall's stair face
SKIN_X0, SKIN_Y0 = float(SKIN.x[0]), float(SKIN.y[0])          # 105.5, 50
STEP_Y = float(M["hw_end_cap"].y[1])                           # 50.75 — where a board steps
STAIR_X = (float(SKIRT.x[1]), float(M["kicker"].x[1]))         # 107 -> 131, the finished 24

def board_rects(y0, y1):
    """A tread or riser board as (x0, x1, y0, y1) pieces. One rect uphill of the wall's
    end (24 wide, butting the skirt), one past it (25 1/2, lapping the skin), and both
    for the one board that straddles the end cap — that is its notch."""
    if y1 <= STEP_Y + 1e-9:
        return [(STAIR_X[0], STAIR_X[1], y0, y1)]
    if y0 >= STEP_Y - 1e-9:
        return [(SKIN_X0, STAIR_X[1], y0, y1)]
    return [(STAIR_X[0], STAIR_X[1], y0, STEP_Y), (SKIN_X0, STAIR_X[1], STEP_Y, y1)]

def skin_pts():
    """The skin's true y-z outline: stringer A's stepped top edge over the skin's own
    y extent, carried down to the floor — the cavity is open below the stringer too."""
    y0, y1 = float(SKIN.y[0]), float(SKIN.y[1])
    top = []
    for i in range(ST.n_treads, 0, -1):                        # runs in increasing y
        a, b = ST.tread_y(i)
        if b <= y0 or a >= y1:
            continue
        z = ST.riser_z[i] - T
        top += [(max(a, y0), z), (min(b, y1), z)]
    return [(y0, 0.0)] + top + [(y1, 0.0)]

def draw_treads(v):
    for i in range(1, ST.n_treads + 1):
        v.rect(*tread_y_board(i), ST.riser_z[i] - T, ST.riser_z[i], "fin")
        v.rect(*riser_y(i), (ST.riser_z[i - 1] - T) if i > 1 else 0, ST.riser_z[i] - T, "fin")
    # riser 6 — the landing face, tread 5's cut up to the landing deck's underside
    v.rect(ST.y_riser_top, ST.y_riser_top + RISER_T, ST.riser_z[ST.n_treads] - T, LAND - T, "fin")

def half_wall_yz(v, cut=True):
    """half-wall framing in a y–z view (bed wall left)."""
    for k in ("hw_bottom_plate_a", "hw_bottom_plate_b", "hw_king_a", "hw_king_b",
              "hw_top_plate_1", "hw_top_plate_2"): R(v, m(k), "y", "z", "lum")
    for k in ("hw_trimmer_a", "hw_trimmer_b"): R(v, m(k), "y", "z", "lum2")
    for k in ("hw_jamb_ply_a", "hw_jamb_ply_b"): R(v, m(k), "y", "z", "sheet")
    R(v, m("hw_header"), "y", "z", "lum", HATCH if cut else "")
    R(v, m("hw_rake_nailer"), "y", "z", "lum2")
    # Rev X: the opening is ply-wrapped, and its head follows the rake. The wrap is
    # drawn from the members themselves, so nothing here is hand-kept.
    R(v, m("nk_soffit_flat"), "y", "z", "fin"); R(v, m("nk_soffit_rake"), "y", "z", "fin")
    R(v, m("nk_wrap_bedwall"), "y", "z", "fin"); R(v, m("nk_wrap_shortwall"), "y", "z", "fin")

# The stair's FINISHED extent — the bottom tread's nosing, 7/8 past the framing line
# at ST.y_bottom because the riser board stands 3/4 proud of the plumb cut. Clearances
# (the gap to the dresser, the plan dims) are measured from this; framing layout from
# ST.y_bottom. Rev W.
Y_FIN = tread_y_board(1)[1]

# --------------------------------------------------------------------------- named values for content/ placeholders
# content/*.yaml prose may say {nook_fin_w}; unknown names raise KeyError at build time — that is deliberate.
VALS = {k: fr(v) for k, v in DER.items() if not isinstance(v, (list, tuple))}
VALS.update({
    "rev": REV, "deck": fr(DECK), "landing": fr(LAND), "ceiling": fr(CEILING), "room_x": fr(RX), "room_y": fr(RY),
    "nook_rough_w": fr(NOOK_Y[1] - NOOK_Y[0]), "nook_rough_h": fr(HB), "nook_fin_w": fr(JAMB_Y[1] - JAMB_Y[0]), "nook_fin_h": fr(CEIL),
    "panel_top": fr(CEIL + PANEL), "y_meet": fr(Y_MEET), "throat": fr(ST.throat), "riser": f"{ST.R:.3f}", "run": fr(ST.run),
    "angle": f"{math.degrees(ST.angle):.2f}", "n_risers": str(ST.n_risers), "n_treads": str(ST.n_treads),
    "plumb_lo": fr(ST.plumb_cut()[0]), "plumb_hi": fr(ST.plumb_cut()[1]), "top_run": fr(ST.top_run), "tread_t": fr(T),
    "beam_above_deck": fr(BEAM_FIN_TOP - DECK), "beam_stock": BEAMSTOCK, "beam_actual": BEAM_ACTUAL,
    # centre to centre of the two bearings: 1 1/2 into the 3 seat at the window wall,
    # 1 3/4 into the 3 1/2 of top plate at the half-wall end.
    "beam_span": fr((float(M["hw_top_plate_2"].x[1]) + float(M["hw_top_plate_2"].x[0])) / 2
                    - (float(M["beam_tongue"].x[0]) + float(M["beam_tongue"].x[1])) / 2),
    "beam_clear_span": fr(float(M["hw_top_plate_2"].x[0]) - float(M["beam_tongue"].x[1])),
    "bay": fr(BAY), "bay_slack": fr(BAY - float(MAT["size"][0])),
    "mattress_t": fr(float(MAT["thickness"])), "mattress_top": fr(DECK + float(MAT["thickness"])),
    "ledge_h": fr(float(M["ledge_lid"].z[1]) - DECK),
    "ledge_well_w": fr(float(M["ledge_front_rail"].y[0]) - float(M["rear_ledger"].y[1])),
    "ledge_well_h": fr(float(M["ledge_front_rail"].z[1]) - DECK), "slat_count": str(SCR["slat_count"]),
    "stair_fin": fr(Y_FIN), "landing_fin": fr(m("lnd_ply").y[1]), "riser_t": fr(RISER_T),
    "board_w": fr(STAIR_X[1] - STAIR_X[0]), "board_w_skin": fr(STAIR_X[1] - SKIN_X0),
    "skin_y0": fr(SKIN_Y0), "skin_y1": fr(float(SKIN.y[1])), "step_y": fr(STEP_Y),
})

# ---------------------------------------------------------------- prose values
_EIGHTHS = {"1/8": "\u215b", "3/8": "\u215c", "5/8": "\u215d", "7/8": "\u215e"}


def frp(v):
    """fr() for prose: eighths as one glyph (48 3/8 -> 48 3/8 with the glyph), the way
    the hand-written tables in content/ have always spelled them. Prose only —
    sheet labels keep fr() so no figure moves."""
    t = fr(v)
    for a, b in _EIGHTHS.items():
        if t.endswith(" " + a): return t[:-len(a) - 1] + b
        if t == a: return b
    return t


class _Members:
    """`{m:<id>.<x|y|z><0|1>}` is one framing extent, `{m:<id>.size.<x|y|z>}` a size —
    so prose can quote the model without a named VALS entry for every number.
    An unknown id or a malformed path raises, exactly as an unknown placeholder
    name does: prose must not drift silently."""

    def __format__(self, spec):
        parts = spec.split(".")
        if len(parts) >= 3 and parts[-2] == "size":
            mid, ax = ".".join(parts[:-2]), parts[-1]
            if mid not in M: raise KeyError(f"{{m:{spec}}}: no member {mid!r}")
            if ax not in ("x", "y", "z"): raise KeyError(f"{{m:{spec}}}: axis must be x, y or z")
            return frp(M[mid].size(ax))
        mid, tok = ".".join(parts[:-1]), parts[-1]
        if mid not in M: raise KeyError(f"{{m:{spec}}}: no member {mid!r}")
        if len(tok) != 2 or tok[0] not in "xyz" or tok[1] not in "01":
            raise KeyError(f"{{m:{spec}}}: want <id>.<x|y|z><0|1> or <id>.size.<x|y|z>")
        return frp(float(getattr(M[mid], tok[0])[int(tok[1])]))


def _oc(prefix, a, b):
    """centre spacing of two repeated members, for an '@ N o.c.' claim."""
    return (float(M[f"{prefix}[{b}]"].x[0]) - float(M[f"{prefix}[{a}]"].x[0])) / (b - a)


# Derived quantities the structure table states in prose. Each one used to be typed
# by hand; each is checked against the model on every build now.
VALS.update({
    "beam_notch_depth": frp(float(M["beam_tongue"].z[0]) - float(M["beam"].z[0])),
    "beam_seat_area": f"{M['beam_tongue'].size('x') * M['beam'].size('y'):.2f}",
    "beam_db": f"{M['beam'].size('z') / M['beam'].size('y'):g}",
    "joist0_len": frp(M["deck_joist[0]"].size("y") + M["deck_joist_tail"].size("y")),
    "joist_oc": frp(_oc("deck_joist", 1, 2)),
    "hw_fin_w": frp(STAIR_X[0] - float(M["hw_sheath_loft_a"].x[0])),
    "hw_stair_fin": frp(STAIR_X[0] - float(M["hw_bottom_plate_a"].x[0])),
    "slat_oc": f"{_oc('slat', 0, SCR['slat_count'] - 1):.3g}",
    "slat_clear2": f"{DER['slat_clear']:.2f}",
    "m": _Members(),
})
