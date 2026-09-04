"""
drawings.model — load dimensions.yaml once and expose everything a sheet module needs.

Sheet modules do `from .model import *` so their figure code reads exactly as it
did in the single-file generator: M (members), ST (stair), DER (verify.py's
derived dict), the room/nook/screen constants, fr(), m(), ids(), R(), View.

The yaml path comes from the LOFT_YAML environment variable (build.py sets it);
default dimensions.yaml in the repo root, whatever the cwd.
"""
import os, sys, html, json, math, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "tools")):
    if p not in sys.path: sys.path.insert(0, p)
import yaml
from verify import expand, Stair, compute_derived
from fractions import Fraction
from svgview import View

def fr(v):
    """53.75 → 53¾ · 49.714 → 49.71 — sixteenths or two decimals, never sevenths."""
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
nook = d["nook"]; HB = float(nook["header_bottom"]); JAMB = float(nook.get("head_jamb", 0)); CEIL = HB - JAMB
PANEL = float(nook["soffit_panel_thickness"]); NOOK_Y = [float(a) for a in nook["opening_y"]]
CEILING = float(room["ceiling"]); RX, RY = float(room["x"]), float(room["y"])
MAT = d["mattress"]; SCR = d["screen"]
DECK = float(d["expected"]["deck_top"]); LAND = ST.riser_z[ST.n_treads + 1]
def U(y): return ST.underside(y)
Y_MEET = ST.y_riser_top - (CEIL + PANEL - U(ST.y_riser_top)) / ST.tan
def soffit(y): return CEIL if y <= Y_MEET else U(y) - PANEL
def m(i): return M[i]
def ids(prefix): return [k for k in M if k == prefix or k.startswith(prefix + "[")]
def R(v, mem, h, vv, cls="lum", extra=""): v.rect(*mem.ext(h), *mem.ext(vv), cls, extra)
HATCH = 'fill="url(#hatch)"'
E = html.escape

# finished-opening jambs (derived, not members)
JAMB_Y = [NOOK_Y[0] + JAMB, NOOK_Y[1] - JAMB]

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

def draw_treads(v):
    for i in range(1, ST.n_treads + 1):
        v.rect(*tread_y_board(i), ST.riser_z[i] - T, ST.riser_z[i], "fin")
        v.rect(*riser_y(i), (ST.riser_z[i - 1] - T) if i > 1 else 0, ST.riser_z[i] - T, "fin")
    # riser 6 — the landing face, tread 5's cut up to the landing deck's underside
    v.rect(ST.y_riser_top, ST.y_riser_top + RISER_T, ST.riser_z[ST.n_treads] - T, LAND - T, "fin")

def half_wall_yz(v, cut=True):
    """half-wall framing in a y–z view (bed wall left)."""
    for k in ("hw_bottom_plate", "hw_king_a", "hw_king_b", "hw_top_plate_1", "hw_top_plate_2"): R(v, m(k), "y", "z", "lum")
    for k in ("hw_trimmer_a", "hw_trimmer_b"): R(v, m(k), "y", "z", "lum2")
    R(v, m("hw_header"), "y", "z", "lum", HATCH if cut else "")
    if JAMB:
        v.rect(NOOK_Y[0], NOOK_Y[1], CEIL, HB, "fin")
        v.rect(NOOK_Y[0], JAMB_Y[0], 0, CEIL, "fin"); v.rect(JAMB_Y[1], NOOK_Y[1], 0, CEIL, "fin")

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
    "beam_above_deck": fr(m("beam").z[1] - DECK), "slat_count": str(SCR["slat_count"]),
    "stair_fin": fr(Y_FIN), "landing_fin": fr(m("lnd_ply").y[1]), "riser_t": fr(RISER_T),
})
