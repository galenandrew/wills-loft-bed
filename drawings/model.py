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
def stringer_pts():
    top = LAND - ST.deck_t
    pts = []
    if ST.top_run > 0:
        y_edge = ST.y_riser_top - (top - (LAND - T)) / ST.tan
        pts = [(ST.y_top, U(ST.y_top)), (ST.y_top, top), (y_edge, top), (ST.y_riser_top, LAND - T)]
    else:
        pts = [(ST.y_top, U(ST.y_top)), (ST.y_top, ST.riser_z[ST.n_treads] - T)]
    for i in range(ST.n_treads, 0, -1):
        y0, y1 = ST.tread_y(i)
        pts += [(y0, ST.riser_z[i] - T), (y1, ST.riser_z[i] - T), (y1, (ST.riser_z[i - 1] - T) if i > 1 else 0)]
    pts += [(ST.y_riser_top + U(ST.y_riser_top) / ST.tan, 0)]
    return pts

def draw_treads(v):
    for i in range(1, ST.n_treads + 1):
        y0, y1 = ST.tread_y(i)
        v.rect(y0, y0 + float(d["stair"]["tread_board_width"]), ST.riser_z[i] - T, ST.riser_z[i], "fin")
        # riser drops all the way to the stringer's own notch corner, so its face butts flush against the tread below
        v.rect(y1 - 0.75, y1, (ST.riser_z[i - 1] - T) if i > 1 else 0, ST.riser_z[i] - T, "fin")
    # riser 6, under the landing: same convention, recessed under the landing's own 1/8 nose
    v.rect(ST.y_riser_top - 0.75, ST.y_riser_top, ST.riser_z[ST.n_treads] - T, LAND - T, "fin")

def half_wall_yz(v, cut=True):
    """half-wall framing in a y–z view (bed wall left)."""
    for k in ("hw_bottom_plate", "hw_king_a", "hw_king_b", "hw_top_plate_1", "hw_top_plate_2"): R(v, m(k), "y", "z", "lum")
    for k in ("hw_trimmer_a", "hw_trimmer_b"): R(v, m(k), "y", "z", "lum2")
    R(v, m("hw_header"), "y", "z", "lum", HATCH if cut else "")
    if JAMB:
        v.rect(NOOK_Y[0], NOOK_Y[1], CEIL, HB, "fin")
        v.rect(NOOK_Y[0], JAMB_Y[0], 0, CEIL, "fin"); v.rect(JAMB_Y[1], NOOK_Y[1], 0, CEIL, "fin")

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
})
