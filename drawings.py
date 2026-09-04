#!/usr/bin/env python3
"""
drawings.py — render loft-bed-drawings.html from dimensions.yaml.

    python3 drawings.py                      # dimensions.yaml → loft-bed-drawings.html
    python3 drawings.py other.yaml out.html

Every rectangle is a member's extents projected in the stated direction; every
schedule number comes from verify.py's own computation. Labels and dimension
strings are anchored to member extents, so they move with the data and cannot
drift from it. Prose (captions, structure table, open items) lives in the
NOTES section at the bottom of this file and is the only hand-written content.

VIEW CONVENTIONS (stated on the sheet)
  plan       x to the right, y DOWN the page — bed wall at the top, as Drawing 1 always has
  x–z views  looking toward the bed wall: window wall on the left
  y–z views  bed wall on the LEFT, y to the right. Sections cut at a given x
             are drawn mirrored where necessary so the bed wall stays left.
"""
import sys, html, json, math, datetime
sys.path.insert(0, "."); sys.path.insert(0, "tools")
import yaml
from verify import expand, Stair, compute_derived
from fractions import Fraction

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
from svgview import View

YAML = sys.argv[1] if len(sys.argv) > 1 else "dimensions.yaml"
OUT = sys.argv[2] if len(sys.argv) > 2 else "loft-bed-drawings.html"

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
        v.rect(y1 - 0.75, y1, ST.riser_z[i - 1] if i > 1 else 0, ST.riser_z[i] - T, "fin")
    v.rect(ST.y_riser_top, ST.y_riser_top + 0.75, ST.riser_z[ST.n_treads], LAND, "fin")   # riser 6 on the rim face

def half_wall_yz(v, cut=True):
    """half-wall framing in a y–z view (bed wall left)."""
    for k in ("hw_bottom_plate", "hw_king_a", "hw_king_b", "hw_top_plate_1", "hw_top_plate_2"): R(v, m(k), "y", "z", "lum")
    for k in ("hw_trimmer_a", "hw_trimmer_b"): R(v, m(k), "y", "z", "lum2")
    R(v, m("hw_header"), "y", "z", "lum", HATCH if cut else "")
    if JAMB:
        v.rect(NOOK_Y[0], NOOK_Y[1], CEIL, HB, "fin")
        v.rect(NOOK_Y[0], JAMB_Y[0], 0, CEIL, "fin"); v.rect(JAMB_Y[1], NOOK_Y[1], 0, CEIL, "fin")

# =========================================================================== D1 floor plan
def d1():
    v = View(-6, RX + 6, -9, RY + 6, 3.3, ml=70, mr=80, mt=30, mb=54, vdown=True)
    v.rect(0, RX, 0, RY, "room")
    # loft
    v.rect(0, m("beam_wrap_face").x[1], 0, m("beam_wrap_face").y[1], "deck")
    v.rect(0, m("beam_wrap_face").x[1], 0, 8, "ledge")
    v.rect(MAT["size"][1] and 2, 2 + MAT["size"][1], 8, 8 + MAT["size"][0], "matt")
    R(v, m("beam"), "x", "y", "beamplan"); R(v, m("beam_wrap_face"), "x", "y", "fin")
    v.rect(m("hw_sheath_loft_a").x[0], m("hw_sheath_stair_a").x[1], 0, m("hw_end_cap").y[1], "hid")
    # landing + stair
    v.rect(107, RX, 0, ST.landing, "landing")
    for i in range(1, ST.n_treads + 1):
        y0, y1 = ST.tread_y(i); v.rect(107, RX, y0, y1, "tread")
    # existing
    dk = m("desk"); v.rect(*dk.x, *dk.y, "dashfill")
    dr = m("dresser"); v.rect(*dr.x, *dr.y, "exist")
    door = room["door"]; hy = float(door["y"][1]); w = float(door["width"])
    pts = [(RX - w * math.sin(a * math.pi / 2 / 24), hy - w * math.cos(a * math.pi / 2 / 24)) for a in range(25)]
    v.path(pts, "ghostl"); v.line(RX, hy, RX - w, hy, "door")
    fan = m("fan"); cx, cy, r = (fan.x[0] + fan.x[1]) / 2, (fan.y[0] + fan.y[1]) / 2, (fan.x[1] - fan.x[0]) / 2
    v.out.append(f'<circle class="ghostl" cx="{v.X(cx):.1f}" cy="{v.Y(cy):.1f}" r="{r*v.s:.1f}" fill="none"/>')
    win = room["window"]; v.line(-1.2, float(win["y"][0]), -1.2, float(win["y"][1]), "window")
    # labels
    v.text(50, 4, "8w × 8h BOXED LEDGE — full 107, capped at the deck end", "labs", "middle", dy=4)
    v.text(39.5, 27, f"Twin mattress {MAT['size'][0]} × {MAT['size'][1]}", "lab", "middle", dy=4)
    v.text(39.5, 31.5, f"in a {fr(m('beam').y[0]-8)} bay — 1\" slack", "labs", "middle", dy=4)
    v.text(92, 27, "landing area", "lab", "middle", dy=4); v.text(92, 31.5, f"30 × {fr(m('beam').y[0]-8)}", "labs", "middle", dy=4)
    v.text(50, 54.5, "doubled 2×10 upstand beam + ¾ poplar wrap — 107, no posts", "labs", "middle", dy=4)
    v.text(104.6, 30, "half-wall below", "labs", "middle", rot=-90)
    v.text(119, 12, "LANDING", "lab", "middle", dy=4); v.text(119, 17, f"24 × {fr(ST.landing)} @ {fr(LAND)}", "labs", "middle", dy=4)
    v.text(119, 50, f"{ST.n_treads} treads @ {fr(ST.run)}", "labs", "middle", dy=4)
    v.text(12, 60.5, "desk 24 × 55", "labs", "middle", dy=4)
    v.text(123, 126, "dresser 16 × 48", "labs", "middle", rot=-90)
    v.text(cx, cy, f"ceiling fan — blades {fr(fan.z[0])}", "labs", "middle", dy=4)
    v.text(2.2, (float(win["y"][0]) + float(win["y"][1])) / 2, "window", "labs", "middle", rot=-90)
    v.text(RX / 2, RY + 3, "closet wall", "labs", "middle", dy=4)
    v.text(2.2, 75, "window wall", "labs", "middle", rot=-90); v.text(RX - 2.2, 88, "right wall", "labs", "middle", rot=-90)
    # dims
    v.dim_h(0, RX, -5.6, fr(RX)); v.dim_h(0, 107, -2.4, "107 deck"); v.dim_h(107, RX, -2.4, "24")
    v.dim_v(-4.5, 0, m("beam_wrap_face").y[1], fr(m("beam_wrap_face").y[1]))
    yb = ST.y_bottom; dg = m("dresser").y
    v.dim_v(RX + 2.6, 0, yb, f"{fr(yb)} stair", left=False); v.dim_v(RX + 2.6, yb, dg[0], f"{fr(dg[0]-yb)} gap", left=False)
    v.dim_v(RX + 2.6, dg[0], dg[1], f"{fr(dg[1]-dg[0])} dresser", left=False); v.dim_v(RX + 2.6, float(door["y"][0]), hy, f"{fr(w)} door", left=False)
    v.dim_v(RX + 2.6, hy, RY, fr(RY - hy), left=False); v.dim_v(-6.2, 0, RY, fr(RY))
    chain = DER["room_depth_chain"]
    v.text(RX / 2, RY + 4.8, f"{fr(yb)} + {fr(dg[0]-yb)} + {fr(dg[1]-dg[0])} + {fr(w)} + {fr(float(door['to_corner']))} = {fr(chain)}  ·  room {fr(RY)} — {fr(RY-chain)} unplaced (field)", "labs", "middle", dy=13)
    return v.svg("Room floor plan, bed wall at the top, window wall to the left")

# =========================================================================== D2 front elevation
def d2():
    v = View(-6, RX + 6, 0, CEILING + 2, 4.4, ml=70, mr=150, mt=30, mb=44)
    v.rect(-6, 0, 0, CEILING, "wall"); v.rect(RX, RX + 6, 0, CEILING, "wall"); v.line(-6, CEILING, RX + 6, CEILING, "floor"); v.line(-6, 0, RX + 6, 0, "floor")
    # stair, in front of the landing: riser faces
    v.rect(107, RX, 0, LAND, "landing")
    for i in range(1, ST.n_risers - 1): v.line(107, ST.riser_z[i], RX, ST.riser_z[i], "dash")
    v.text(119, LAND, f"landing {fr(LAND)}", "labs", "middle", dy=-4); v.text(120, 22, "treads", "labs", "middle")
    # half-wall end, wrap, slats, plate
    ec = m("hw_end_cap"); v.rect(*ec.x, *ec.z, "sheet"); v.text((ec.x[0]+ec.x[1])/2, 8, "half-wall", "labs", "middle", rot=-90)
    wf = m("beam_wrap_face"); v.rect(*wf.x, *wf.z, "fin")
    for k in ids("slat"): R(v, m(k), "x", "z", "lum")
    R(v, m("screen_top_plate"), "x", "z", "lum")
    v.line(0, DECK + MAT["thickness"], 107, DECK + MAT["thickness"], "ghostl"); v.text(108, DECK + MAT["thickness"], "mattress top beyond", "labs", "start", dy=11)
    v.line(0, m("ledge_lid").z[1], 107, m("ledge_lid").z[1], "ghostl"); v.text(108, m("ledge_lid").z[1], "ledge top beyond", "labs", "start", dy=-3)
    dk = m("desk"); v.rect(*dk.x, *dk.z, "dashfill"); v.text(12, 15, "desk", "labs", "middle")
    fan = m("fan"); v.line(fan.x[0], fan.z[0], fan.x[1], fan.z[0], "redline"); v.text((fan.x[0]+fan.x[1])/2, fan.z[0], f"fan blade plane {fr(fan.z[0])} — screen blocks reach", "labb", "middle", dy=-4)
    v.text(53.5, 58, f"doubled 2×10 + ¾ wrap — {fr(m('beam').z[1]-DECK)} above the deck", "lab", "middle", dy=4)
    v.text(53.5, 80, f"{SCR['slat_count']} × 2×2 slats @ {fr(DER['slat_clear'])} clear — end stiles flush both ends", "lab", "middle", dy=4)
    v.text(53.5, m("screen_top_plate").z[0] - 3, "2×4 top plate — into ceiling framing / blocking", "labs", "middle")
    v.text(50, 40, "under-loft space left open — standalone furniture", "labs", "middle")
    v.dim_h(0, m("hw_sheath_loft_a").x[0], 4, f"{fr(DER['clear_below_deck_x'])} clear opening — no posts (deck {fr(107)}; half-wall takes 5)")
    v.dim_v(-3.5, 0, DECK, f"{fr(DECK)} deck"); v.dim_v(RX + 8, m("beam").z[1], CEILING, f"{fr(CEILING - m('beam').z[1])} · slats {fr(m('slat[0]').size('z'))}", left=False)
    v.dim_v(RX + 8, DECK, m("beam").z[1], fr(m("beam").z[1] - DECK), left=False)
    v.text(RX / 2, CEILING, f"ceiling {fr(CEILING)}", "labs", "middle", dy=-4)
    return v.svg("Front elevation looking toward the bed wall, window wall on the left")

# =========================================================================== D3 platform section
def d3():
    xc = 55
    v = View(-4, 62, 0, CEILING + 1, 6, ml=90, mr=110, mt=28, mb=44)
    v.rect(-4, 0, 0, CEILING, "wall"); v.line(-4, CEILING, 60, CEILING, "floor"); v.line(-4, 0, 60, 0, "floor")
    R(v, m("rear_ledger"), "y", "z", "lum", HATCH)
    blk = [k for k in ids("ledger_blocking") if m(k).x[0] <= xc <= m(k).x[1]][0]; R(v, m(blk), "y", "z", "lum", HATCH)
    R(v, m("deck_joist[4]"), "y", "z", "lum2")
    R(v, m("deck_ply"), "y", "z", "sheet", HATCH)
    R(v, m("ledge_front_rail"), "y", "z", "fin", HATCH); R(v, m("ledge_lid"), "y", "z", "fin", HATCH)
    v.rect(8, 8 + MAT["size"][0], DECK, DECK + MAT["thickness"], "matt")
    R(v, m("beam"), "y", "z", "lum", HATCH); R(v, m("beam_wrap_face"), "y", "z", "fin", HATCH); R(v, m("beam_wrap_underside"), "y", "z", "fin", HATCH)
    R(v, m("slat[11]"), "y", "z", "lum2"); R(v, m("screen_top_plate"), "y", "z", "lum", HATCH)
    dk = m("desk"); v.rect(*dk.y, *dk.z, "dashfill")
    fan = m("fan"); v.line(fan.y[0], fan.z[0], 60, fan.z[0], "redline"); v.text(fan.y[0] + 0.5, fan.z[0], f"fan {fr(fan.z[0])}", "labb", "start", dy=-4)
    # labels
    v.text(-1.2, 30, "bed wall", "labs", "middle", rot=-90)
    v.text(4, 71, "boxed ledge", "lab", "start"); v.text(4, 69, f"top {fr(m('ledge_lid').z[1])} — {fr(m('ledge_lid').z[1]-DECK-MAT['thickness'])} proud of the mattress", "labs", "start")
    v.text(4, 67.3, f"well {fr(m('ledge_front_rail').y[0]-m('rear_ledger').y[1])} × {fr(m('ledge_front_rail').z[1]-DECK)}", "labs", "start")
    v.text(2, 52.2, "2×6 ledger, bottom flush with the joists — lags into every stud", "labs", "start")
    v.text(2, 49.8, "2×4 blocking on edge — carries the ply's rear edge", "labs", "start")
    v.text(2, 47.4, f"2×4 joists @ 12 o.c. beyond · {fr(DER['deck_joist_span'])} span · ¾ ply glued & screwed", "labs", "start")
    v.text(27, 61, f"{MAT['size'][0]} mattress in a {fr(m('beam').y[0]-8)} bay", "labs", "middle", dy=4)
    v.text(48.5, 58.4, "doubled 2×10", "lab", "middle", rot=-90); v.text(53.5, 28, "¾ poplar wrap, mitered — underside stops at the half-wall", "labs", "start", rot=-90)
    v.text(56, 66, "2×2 slats beyond, flush with the wrap", "labs", "start", rot=-90)
    v.text(43, 96.5, "2×4 top plate, flat", "labs", "end", dy=-3)
    v.text(27, 15, f"desk {fr(dk.y[1])} deep × {fr(dk.z[1])} high — projects {fr(dk.y[1]-m('beam_wrap_face').y[1])} past the beam", "labs", "middle")
    # dims
    v.dim_h(0, 8, 74, "8"); v.dim_h(8, m("beam").y[0], 74, f"{fr(m('beam').y[0]-8)} bay"); v.dim_h(m("beam").y[0], m("beam_wrap_face").y[1], 74, "3¾")
    v.dim_h(0, m("beam_wrap_face").y[1], 42.5, f"{fr(m('beam_wrap_face').y[1])} platform depth (8 + {fr(m('beam').y[0]-8)} + 3 + ¾)", above=False)
    v.dim_v(-3.3, 0, DECK, f"{fr(DECK)} deck"); v.dim_v(-3.3, DECK, m("ledge_lid").z[1], "8", left=True)
    v.dim_v(20, 0, m("deck_joist[0]").z[0], f"{fr(DER['clear_under_joists'])} clear")
    v.dim_v(50.75, 0, m("beam_wrap_underside").z[0], f"{fr(DER['clear_under_beam'])} under the beam", left=False)
    v.dim_v(44, DECK + MAT["thickness"], CEILING, f"{fr(DER['sitting_headroom'])} sitting headroom")
    return v.svg(f"Section through the platform at x = {xc}, bed wall on the left")

# =========================================================================== D4 stair section
def d4():
    v = View(-4, 76, 0, CEILING + 1, 5.6, ml=130, mr=70, mt=28, mb=44)
    v.rect(-4, 0, 0, CEILING, "wall"); v.line(-4, CEILING, 76, CEILING, "floor"); v.line(-4, 0, 76, 0, "floor")
    for k in ("hw_sheath_stair_a", "hw_sheath_stair_head", "hw_sheath_stair_b"): R(v, m(k), "y", "z", "sheet")
    R(v, m("hw_header"), "y", "z", "dashfill")
    for k in ("hw_trimmer_a", "hw_trimmer_b", "hw_king_a", "hw_king_b"): R(v, m(k), "y", "z", "dashfill")
    if JAMB: v.rect(NOOK_Y[0], NOOK_Y[1], CEIL, HB, "fin")
    v.line(0, DECK, m("beam_wrap_face").y[1], DECK, "dash"); v.text(2, DECK, f"loft deck {fr(DECK)} — beyond the half-wall", "labs", "start", dy=-4)
    v.rect(m("beam").y[0], m("beam_wrap_face").y[1], DECK, m("beam").z[1], "dashfill"); v.text(52, 60.5, "beam end, beyond", "labs", "start")
    R(v, m("lnd_side_member"), "y", "z", "lum2"); R(v, m("lnd_joist[0]"), "y", "z", "dashfill"); R(v, m("lnd_blocking[0]"), "y", "z", "dashfill")
    R(v, m("lnd_ledger_bedwall"), "y", "z", "lum", HATCH); R(v, m("lnd_rim"), "y", "z", "lum", HATCH)
    R(v, m("lnd_ply"), "y", "z", "sheet", HATCH); R(v, m("kicker"), "y", "z", "lum", HATCH)
    v.poly(stringer_pts(), "lum", HATCH); draw_treads(v)
    v.path([(NOOK_Y[0], CEIL), (Y_MEET, CEIL), (NOOK_Y[1], soffit(NOOK_Y[1]))], "soffit")
    v.line(0, 30, 76, 30, "redline"); v.text(48, 30, "30 — guards above this line", "labb", "start", dy=-4)
    # labels
    v.text(-2, 62, "bed wall", "labs", "middle", rot=-90)
    v.text(4, CEIL, f"nook ceiling {fr(CEIL)}", "labs", "start", dy=26)
    v.text(33, soffit(33), "soffit panel on the stringer undersides", "labs", "start", dy=13, rot=-math.degrees(ST.angle))
    v.text(m("lnd_rim").y[0] + 0.75, 45.3, "rim 2×8", "lab", "middle", rot=-90); v.text(8, 43, "side member beyond", "labs", "middle")
    v.text(m("lnd_blocking[0]").y[1] + 0.6, 46.2, "blocking", "labs", "start")
    v.text(8, 47.2, "joists beyond", "labs", "middle")
    v.text(52, 8, f"treads 5/4 · {fr(T)}", "labs", "start"); v.text(69, 3.2, "kicker", "labs", "end")
    for i in range(1, ST.n_risers + 1):
        y = ST.tread_y(i)[1] if i <= ST.n_treads else ST.y_riser_top
        v.text(y + 0.6, ST.riser_z[i] - 0.4, f"{ST.riser_z[i]:.2f}", "labs", "start", dy=3)
    v.text(36, 74, "above about 38\" of tread you're ducking — the top two steps and the landing are a crouch", "labs", "start")
    # dims
    v.dim_v(-2.6, 0, LAND, f"{fr(LAND)} landing"); v.dim_v(8, LAND, CEILING, f"{fr(DER['landing_headroom'])} headroom — stand & turn", left=False)
    v.dim_v(31.5, ST.riser_z[ST.n_treads], CEILING, f"{fr(CEILING - ST.riser_z[ST.n_treads])} over tread {ST.n_treads}", left=False)
    v.dim_h(0, ST.y_top, 52.5, fr(ST.y_top)); v.dim_h(ST.y_top, ST.y_riser_top, 52.5, f"{fr(ST.top_run)} top run"); v.dim_h(ST.y_riser_top, ST.y_bottom, 52.5, f"{fr(ST.y_bottom - ST.y_riser_top)} run · {ST.n_treads} @ {fr(ST.run)}")
    v.dim_h(0, ST.y_bottom, -1.5 + 0, f"{fr(ST.y_bottom)} total — {ST.n_risers} risers @ {ST.R:.3f} · {math.degrees(ST.angle):.1f}°", above=False)
    v.dim_v(m("lnd_rim").y[1] + 0.9, m("lnd_rim").z[0], m("lnd_rim").z[1], "7¼ plumb cut = rim", left=False); v.text(m("lnd_blocking[0]").y[0] + 0.75, 47.2, "", "labs")
    return v.svg("Stair section through stringer B, bed wall on the left, drawn with the bed wall left like every y–z view")

# =========================================================================== D5 nook
def d5a():
    v = View(-2, 52, 0, 64, 7, ml=90, mr=70, mt=30, mb=44)
    v.rect(-2, 0, 0, 64, "wall"); v.line(-2, 0, 52, 0, "floor")
    # through the opening: the nook interior
    v.rect(JAMB_Y[0], JAMB_Y[1], 0, CEIL, "ghost")
    v.path([(JAMB_Y[0], soffit(JAMB_Y[0])), (Y_MEET, CEIL), (JAMB_Y[1], soffit(JAMB_Y[1]))], "soffit")
    v.out.append(f'<ellipse class="light" cx="{v.X(9.5):.1f}" cy="{v.Y(CEIL):.1f}" rx="{3*v.s:.1f}" ry="{0.7*v.s:.1f}"/>')
    # wall: loft-side sheathing, framing dashed, jambs
    for k in ("hw_sheath_loft_a", "hw_sheath_loft_head", "hw_sheath_loft_b"): R(v, m(k), "y", "z", "sheet")
    R(v, m("hw_end_cap"), "y", "z", "sheet")
    for k in ("hw_header", "hw_king_a", "hw_king_b", "hw_trimmer_a", "hw_trimmer_b"): R(v, m(k), "y", "z", "dashfill")
    v.rect(NOOK_Y[0], NOOK_Y[1], CEIL, HB, "fin"); v.rect(NOOK_Y[0], JAMB_Y[0], 0, CEIL, "fin"); v.rect(JAMB_Y[1], NOOK_Y[1], 0, CEIL, "fin")
    for k in ("lnd_side_member", "lnd_rim"): R(v, m(k), "y", "z", "dashfill")
    # above the wall: plates, joists, deck, beam end
    for k in ("hw_top_plate_1", "hw_top_plate_2"): R(v, m(k), "y", "z", "lum")
    R(v, m("deck_joist[8]"), "y", "z", "lum2"); R(v, m("deck_ply"), "y", "z", "sheet")
    v.rect(m("beam").y[0], m("beam").y[1], m("beam").z[0], m("beam").z[1], "lum"); R(v, m("beam_wrap_face"), "y", "z", "fin")
    v.text(-1, 30, "bed wall", "labs", "middle", rot=-90)
    v.text(25, 20, "OPEN NOOK — carpet runs through", "lab", "middle"); v.text(25, 17, f"finished {fr(JAMB_Y[1]-JAMB_Y[0])} wide × {fr(CEIL)} high · 24 deep · rake follows the stringers at {math.degrees(ST.angle):.1f}°", "labs", "middle")
    v.text(25, 36, f"flat ceiling {fr(CEIL)} to y = {fr(Y_MEET)} · one 6\" wafer LED", "labs", "middle")
    v.text(38, 26, "raked panel on the stringers", "labs", "start", rot=-math.degrees(ST.angle))
    v.text(25, CEIL + 0.375, "¾ poplar head jamb — flush with the ceiling", "labs", "middle", dy=3)
    v.text(3.4, 20, "jamb", "labs", "middle", rot=-90); v.text(46.6, 20, "jamb", "labs", "middle", rot=-90)
    v.text(25, 46.6, "header beyond the sheathing · landing framing beyond", "labs", "middle")
    v.text(24, 55.5, "loft deck", "labs", "middle"); v.text(48.9, 58, "beam", "labs", "middle", rot=-90)
    v.dim_h(JAMB_Y[0], JAMB_Y[1], -1.5 + 0, f"{fr(JAMB_Y[1]-JAMB_Y[0])} finished opening", above=False)
    v.dim_h(NOOK_Y[0], NOOK_Y[1], 62, f"{fr(NOOK_Y[1]-NOOK_Y[0])} rough opening")
    v.dim_v(-1.6, 0, CEIL, fr(CEIL)); v.dim_v(50.2, 0, soffit(NOOK_Y[1]), fr(soffit(NOOK_Y[1])), left=False)
    v.dim_h(JAMB_Y[0], Y_MEET, 38.5, f"{fr(Y_MEET - JAMB_Y[0])} flat"); v.dim_h(Y_MEET, JAMB_Y[1], 38.5, f"{fr(JAMB_Y[1] - Y_MEET)} raked")
    return v.svg("Under-stair nook, elevation from the under-loft space, bed wall on the left")

def d5b():
    v = View(100, 133, 0, 50, 8, ml=60, mr=95, mt=30, mb=44, vdown=True)
    v.rect(131, 133, 0, 50, "wall"); v.rect(100, 133, -1, 0, "wall")
    v.rect(m("hw_sheath_loft_a").x[0], m("hw_sheath_stair_a").x[1], 0, m("hw_end_cap").y[1], "sheet")
    v.rect(m("hw_sheath_loft_a").x[0], m("hw_sheath_stair_a").x[1], NOOK_Y[0], NOOK_Y[1], "ghost")
    v.rect(m("hw_sheath_loft_a").x[0], m("hw_sheath_stair_a").x[1], NOOK_Y[0], JAMB_Y[0], "fin"); v.rect(m("hw_sheath_loft_a").x[0], m("hw_sheath_stair_a").x[1], JAMB_Y[1], NOOK_Y[1], "fin")
    v.rect(107, 131, NOOK_Y[0], Y_MEET, "flat"); v.rect(107, 131, Y_MEET, NOOK_Y[1], "rake")
    for k in ("lnd_side_member", "lnd_rim", "lnd_ledger_rightwall", "lnd_ledger_bedwall") + tuple(ids("lnd_joist")) + tuple(ids("lnd_blocking")): R(v, m(k), "x", "y", "dashfill")
    for k in ("stringer_a", "stringer_b", "stringer_c"): v.rect(*m(k).x, ST.y_top, 50, "dashfill")
    v.out.append(f'<circle class="light" cx="{v.X(119):.1f}" cy="{v.Y(13):.1f}" r="{3*v.s:.1f}"/>')
    v.text(119, 6.5, f"flat {fr(CEIL)} · {fr(Y_MEET-JAMB_Y[0])} × 24 from the jamb", "lab", "middle", dy=4); v.text(119, 17.5, "wafer LED", "labs", "middle", dy=4)
    v.text(119, 33, "raked from here", "labs", "middle", dy=4)
    v.text(104.5, 25, "half-wall · jambed opening", "labs", "middle", rot=-90)
    v.text(107.75, 40, "stringer A", "labs", "middle", rot=-90); v.text(119, 40, "B", "labs", "middle"); v.text(130.25, 40, "C", "labs", "middle", rot=-90)
    v.dim_v(132.6, JAMB_Y[0], Y_MEET, f"{fr(Y_MEET-JAMB_Y[0])}", left=False); v.dim_v(132.6, Y_MEET, JAMB_Y[1], f"{fr(JAMB_Y[1]-Y_MEET)}", left=False)
    v.dim_h(107, 131, -0.5 - 1, "24 deep")
    return v.svg("Reflected ceiling plan of the nook, bed wall at the top")

# =========================================================================== D6 platform framing plan
def d6():
    v = View(-3, 110, -3, 57, 5.5, ml=80, mr=60, mt=40, mb=40, vdown=True)
    v.rect(-3, 110, -3, 0, "wall"); v.rect(-3, 0, 0, 53, "wall")
    v.rect(m("hw_bottom_plate").x[0], m("hw_bottom_plate").x[1], 0, m("hw_top_plate_1").y[1], "hid")
    for k in ids("deck_joist"): R(v, m(k), "x", "y", "lum2")
    for k in ids("ledger_blocking") + ["ledger_blocking_last"]: R(v, m(k), "x", "y", "blk")
    for k in ("rear_ledger", "side_ledger", "deck_rim", "beam"): R(v, m(k), "x", "y", "lum")
    R(v, m("beam_wrap_face"), "x", "y", "fin"); v.line(0, 8, 107, 8, "ghostl")
    v.text(50, 0.75, "2×6 rear ledger — lags into every stud", "labs", "middle", dy=4)
    v.text(6, 24, "2×10 side ledger, 48 out", "labs", "middle", rot=-90)
    v.text(50, 24, "2×4 joists @ 12 o.c. · 9 joists · 45½ span", "lab", "middle", dy=4)
    v.text(50, 2.25, "", "labs")
    v.text(50, 48.5, "doubled 2×10 + ¾ wrap — 102 clear span", "lab", "middle", dy=4)
    v.text(105.5, 24, "2×4 rim at 104¾–106¼", "labs", "middle", rot=-90)
    v.text(75, 10.5, "boxed ledge above (8)", "labs", "middle", dy=4)
    v.text(21, 4.5, "2×4 blocking at the ledger — carries the ply's rear edge", "labs", "start", dy=4)
    v.text(54, 55.4, f"¾ ply deck: {fr(DER['deck_ply'][0])} × {fr(DER['deck_ply'][1])} — seams on joist centres, glued & screwed", "labs", "middle", dy=4)
    v.text(0, 52.6, "PARKED: beam end backed by 1\" of the 48\" ledger — see open items", "labb", "start", dy=4)
    v.dim_h(0, 107, -2, "107"); v.dim_h(m("deck_joist[0]").x[0], m("deck_joist[1]").x[0], 40, "12 o.c.")
    v.dim_v(109, 0, m("beam_wrap_face").y[1], fr(m("beam_wrap_face").y[1]), left=False); v.dim_v(-1.6, 0, m("side_ledger").y[1], fr(m("side_ledger").y[1]))
    v.dim_v(80, m("rear_ledger").y[1], m("beam").y[0], f"{fr(DER['deck_joist_span'])} span", left=False)
    return v.svg("Platform framing plan, bed wall at the top")

# =========================================================================== D7 half-wall
def d7a():
    v = View(-1, 52, 97.8, 109.4, 9, ml=70, mr=90, mt=30, mb=30)     # h = y (bed wall left), v = x (stair side up)
    v.rect(-1, 0, 101, 108, "wall")
    for k in ("hw_king_a", "hw_king_b"): R(v, m(k), "y", "x", "lum", HATCH)
    for k in ("hw_trimmer_a", "hw_trimmer_b"): R(v, m(k), "y", "x", "lum2", HATCH)
    for k in ("hw_sheath_loft_a", "hw_sheath_loft_b", "hw_sheath_stair_a", "hw_sheath_stair_b"): R(v, m(k), "y", "x", "sheet")
    R(v, m("hw_end_cap"), "y", "x", "fin")
    v.rect(NOOK_Y[0], JAMB_Y[0], 102, 107, "fin"); v.rect(JAMB_Y[1], NOOK_Y[1], 102, 107, "fin")
    v.rect(m("beam").y[0], m("beam").y[1], m("beam").x[0] and 102.75, m("beam").x[1], "dashfill")
    v.text(25, 104.5, f"{fr(JAMB_Y[1]-JAMB_Y[0])} FINISHED OPENING — wall removed, both faces · ¾ poplar jambs", "lab", "middle", dy=4)
    v.text(25, 103.3, "header above carries the deck rim and the landing rim", "labs", "middle", dy=4)
    v.text(1.5, 107.4, "king + trimmer", "labs", "middle", dy=-3); v.text(48.5, 107.4, "trimmer + king", "labs", "middle", dy=-3); v.text(48.5, 109.0, "beam end above — bears here", "labk", "middle", dy=-3)
    v.text(25, 107.4, "stair side", "labs", "middle", dy=-3); v.text(25, 101.6, "loft side", "labs", "middle", dy=13)
    v.dim_v(51.5, 106.25, 107, "¾", left=False); v.dim_v(51.5, 102.75, 106.25, "3½", left=False); v.dim_v(51.5, 102, 102.75, "¾", left=False); v.dim_v(53.3, 102, 107, "5", left=False)
    v.dim_h(NOOK_Y[0], NOOK_Y[1], 108.4, f"{fr(NOOK_Y[1]-NOOK_Y[0])} rough"); v.dim_h(JAMB_Y[0], JAMB_Y[1], 100.1, f"{fr(JAMB_Y[1]-JAMB_Y[0])} finished", above=False)
    v.dim_h(0, m("hw_end_cap").y[1], 98.7, f"{fr(m('hw_end_cap').y[1])} — full platform depth", above=False)
    return v.svg("Half-wall plan detail, horizontal section at 30 inches, rotated so the bed wall is on the left and the stair side up")

def d7b():
    v = View(-2, 52, 0, 66, 7, ml=120, mr=70, mt=30, mb=44)
    v.rect(-2, 0, 0, 66, "wall"); v.line(-2, 0, 52, 0, "floor")
    half_wall_yz(v)
    R(v, m("hw_end_cap"), "y", "z", "fin")
    R(v, m("deck_rim"), "y", "z", "lum2"); R(v, m("deck_ply"), "y", "z", "sheet", HATCH)
    R(v, m("beam"), "y", "z", "lum", HATCH); R(v, m("beam_wrap_face"), "y", "z", "fin")
    for k in ("lnd_side_member", "lnd_rim", "lnd_ply"): R(v, m(k), "y", "z", "dashfill")
    v.poly([p for p in stringer_pts() if p[0] <= 27.01], "dashfill")
    for y in (m("hw_king_a").y[1], m("hw_king_b").y[0]): v.out.append(f'<circle class="strap" cx="{v.X(y):.1f}" cy="{v.Y(46):.1f}" r="{1.6*v.s:.1f}"/>')
    v.text(25, 47.4, "2×10 + ½ ply spacer + 2×10 = 3½ · 47 long · bears 1½ each end", "labs", "middle", dy=4)
    v.text(25, 45.4, "sized by connection depth, not load (~140 psi)", "labs", "middle", dy=4)
    v.text(25, 52.2, "double top plate — deck rim bears here", "labs", "middle", dy=4)
    v.text(22, 12, f"{fr(NOOK_Y[1]-NOOK_Y[0])} × {fr(HB)} ROUGH · {fr(JAMB_Y[1]-JAMB_Y[0])} × {fr(CEIL)} FINISHED", "lab", "middle")
    v.text(0.75, 25, "king", "labs", "middle", rot=-90); v.text(2.25, 25, "trimmer", "labs", "middle", rot=-90); v.text(3.4, 25, "jamb", "labs", "middle", rot=-90)
    v.text(5, 39.4, "landing beyond — side member, rim, deck (dashed)", "labs", "start"); v.text(22.5, 37.6, "stringer A beyond", "labs", "start")
    v.text(4, 49.6, "strap both header-to-king joints", "labb", "start")
    v.text(46, 64.3, "beam end — bypasses the opening", "labk", "end")
    v.dim_v(-1.6, 0, m("hw_top_plate_2").z[1], f"{fr(m('hw_top_plate_2').z[1])} to top plate"); v.dim_v(44, 0, CEIL, f"{fr(CEIL)} finished head", left=True)
    v.dim_v(50.5, 0, m("beam").z[1], f"{fr(m('beam').z[1])} beam top", left=False)
    v.dim_h(NOOK_Y[0], NOOK_Y[1], -1.5, fr(NOOK_Y[1]-NOOK_Y[0]), above=False); v.dim_h(m("hw_header").y[0], m("hw_header").y[1], 55.6, f"{fr(m('hw_header').size('y'))} header")
    return v.svg("Half-wall section at x = 104.5, bed wall on the left")

# =========================================================================== D8 stair & landing framing
def d8a():
    v = View(100, 133, -1.5, 34, 9, ml=110, mr=60, mt=40, mb=50, vdown=True)
    v.rect(100, 133, -1.5, 0, "wall"); v.rect(131, 133, 0, 34, "wall")
    for k in ("hw_king_a", "hw_king_b", "hw_header"): R(v, m(k), "x", "y", "lum")
    for k in ids("hw_sheath_loft_a") + ids("hw_sheath_loft_head") + ids("hw_sheath_loft_b") + ids("hw_sheath_stair_a") + ids("hw_sheath_stair_head") + ids("hw_sheath_stair_b"): R(v, m(k), "x", "y", "sheet")
    v.rect(m("hw_header").x[0], m("hw_header").x[1], NOOK_Y[0], NOOK_Y[1], "lum", HATCH)
    for k in ("lnd_ledger_bedwall", "lnd_ledger_rightwall", "lnd_side_member") + tuple(ids("lnd_joist")) + tuple(ids("lnd_blocking")): R(v, m(k), "x", "y", "lum")
    R(v, m("lnd_rim"), "x", "y", "lum", HATCH)
    for k in ("stringer_a", "stringer_b", "stringer_c"): v.rect(*m(k).x, ST.y_top, 34, "lum", HATCH)
    for x0 in (107, 128): v.rect(x0, x0 + 1.5, m("lnd_rim").y[0] - 0.4, m("lnd_rim").y[1] + 0.4, "hanger")
    v.text(104.5, 30, "header", "lab", "middle", rot=-90)
    sm = m("lnd_side_member"); v.text(107.75, (sm.y[0]+sm.y[1])/2, "side member 2×8", "lab", "middle", rot=-90)
    for k in ids("lnd_joist"): v.text((m(k).x[0]+m(k).x[1])/2, 9, "joist 2×4", "labs", "middle", rot=-90)
    rm = m("lnd_rim"); v.text(118.5, rm.y[0] + 0.75, "rim 2×8 · 22½", "lab", "middle", dy=4); v.text(109.2, rm.y[0] - 0.6, "HUC28", "labk", "start", dy=0); v.text(127.3, rm.y[0] - 0.6, "HUC28", "labk", "end", dy=0)
    v.text(130.25, 9, "ledger 2×8, to y 18", "lab", "middle", rot=-90); v.text(118, 0.75, "bed-wall ledger 2×8", "labs", "middle", dy=4)
    for k in ids("lnd_blocking"): v.text((m(k).x[0]+m(k).x[1])/2, 26.25, "2×4 blocking", "labs", "middle", dy=4)
    for x, l in ((107.75, "A"), (119, "B"), (130.25, "C")): v.text(x, 32.6, l, "labk", "middle", dy=4)
    v.text(109.3, 20.6, f"stringers run {fr(ST.top_run)} under the landing", "labk", "start", dy=4)
    v.text(120, 4.5, "nook below", "labs", "middle", dy=4)
    v.dim_h(107, 131, -1.5, "24", above=True); v.dim_v(100.8, 0, ST.landing, f"{fr(ST.landing)} landing"); v.dim_v(102.0, ST.y_top, ST.landing, f"{fr(ST.top_run)} top run")
    v.dim_v(126.4, rm.y[0], rm.y[1], "1½", left=True); v.dim_h(107, 129.5, 28.4, "rim 22½", above=False)
    return v.svg("Landing framing plan at z 47, bed wall at the top")

def d8b():
    y_cut = 20
    v = View(100, 133, 31, 53, 9, ml=120, mr=60, mt=30, mb=40)
    v.rect(131, 133, 31, 53, "wall"); v.rect(100, 102, 31, 53, "ghost")
    R(v, m("hw_trimmer_a"), "x", "z", "lum2"); v.rect(102, 102.75, 31, 53, "sheet"); v.rect(106.25, 107, 31, 53, "sheet")
    v.rect(102.75, 106.25, 50.75, 53, "lum"); v.rect(102.75, 106.25, HB, 50.75, "lum", HATCH)
    v.rect(102, 107, CEIL, HB, "fin"); v.rect(107, 131, CEIL, HB, "fin")
    v.text(119, 36.6, f"flat soffit panel · face {fr(CEIL)} · top {fr(CEIL+PANEL)}", "labs", "middle")
    rm = m("lnd_rim"); R(v, rm, "x", "z", "lum"); v.rect(129.5, 131, rm.z[0], rm.z[1], "lum2")
    for x0 in (107, 128): v.rect(x0, x0 + 1.5, rm.z[0], 48.2, "hanger")
    v.text(109, 39.6, "HUC28 on the header", "labk", "start", dy=4); v.text(109, 38.4, "SD screws through the ¾ facing", "labs", "start", dy=4); v.text(128.6, 39.6, "HUC28 on the ledger", "labk", "end", dy=4)
    v.rect(107, 131, 48.96, 49.71, "sheet", HATCH)
    for k in ("stringer_a", "stringer_b", "stringer_c"): v.rect(*m(k).x, U(y_cut), LAND - ST.deck_t, "lum", HATCH)
    for x, l in ((107.75, "A"), (119, "B"), (130.25, "C")): v.text(x, 44.5, l, "labk", "middle", dy=4)
    v.text(109.5, 47.6, "rim 2×8 beyond", "lab", "start", dy=4)
    v.text(104.5, 46, "header", "lab", "middle", rot=-90); v.text(104.5, 36.5, "trimmer beyond", "labs", "middle", rot=-90)
    v.text(119, 34.4, f"stringers cut at y = {y_cut}", "labs", "middle")
    v.dim_v(101.0, HB, rm.z[1], f"{fr(rm.z[1]-HB)} header ↔ rim"); v.dim_v(125.5, rm.z[0], rm.z[1], "7¼ rim = plumb cut", left=True)
    v.dim_h(107, 131, 50.6, "24 between wall faces", above=True)
    return v.svg("Section at y 20 through the stringers' top runs, looking toward the bed wall")

# =========================================================================== D9 framing overlay
def d9():
    v = View(-2, 52, 0, 66, 7, ml=90, mr=70, mt=34, mb=44)
    v.rect(-2, 0, 0, 66, "wall"); v.line(-2, 0, 52, 0, "floor")
    half_wall_yz(v)
    R(v, m("deck_rim"), "y", "z", "lum2"); R(v, m("deck_ply"), "y", "z", "sheet"); R(v, m("beam"), "y", "z", "lum"); R(v, m("beam_wrap_face"), "y", "z", "fin")
    for k in ("lnd_side_member", "lnd_rim", "lnd_ledger_bedwall"): R(v, m(k), "y", "z", "green")
    for k in ids("lnd_joist"): R(v, m(k), "y", "z", "greend")
    R(v, m("lnd_ply"), "y", "z", "green")
    v.poly([p for p in stringer_pts() if p[0] <= 52], "green")
    # connection callouts
    def co(n, y, z):
        v.out.append(f'<circle class="co" cx="{v.X(y):.1f}" cy="{v.Y(z):.1f}" r="9"/><text class="cot" x="{v.X(y):.1f}" y="{v.Y(z)+4:.1f}" text-anchor="middle">{n}</text>')
    co(1, 9, 45.3); co(2, 17.25, 45.3); co(3, 22.5, 45.3); co(4, 48.5, 20); co(5, 16.5, 41); co(6, 1.5, 47.2)
    v.text(25, 64.6, "SANDWICH HEADER — 2×10 + ½ ply + 2×10 = 3½ · bottom 41½ · 16d @ 12 o.c., two rows", "labs", "middle")
    v.text(0.75, 25, "king", "labs", "middle", rot=-90); v.text(2.25, 25, "trim", "labs", "middle", rot=-90); v.text(47.75, 25, "trim", "labs", "middle", rot=-90); v.text(49.25, 25, "king", "labs", "middle", rot=-90)
    v.text(36, 30, "stringer A", "labk", "start")
    v.dim_h(0, ST.y_top, -1.5, fr(ST.y_top), above=False); v.dim_h(ST.y_top, ST.y_riser_top, -1.5, f"{fr(ST.top_run)}", above=False); v.dim_h(ST.y_riser_top, 52, -1.5, "stair run →", above=False)
    v.dim_h(NOOK_Y[0], NOOK_Y[1], 8, f"{fr(NOOK_Y[1]-NOOK_Y[0])} nook opening")
    return v.svg("Framing overlay: half-wall framing with the landing box and stringer A drawn to one datum, bed wall on the left")

# =========================================================================== schedule tables
def tbl(rows, head):
    out = ["<table><tr>" + "".join(f"<th>{E(h)}</th>" for h in head) + "</tr>"]
    for r in rows:
        out.append("<tr>" + "".join(f'<td class="{"n" if i in (1, 2) else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>")
    return "\n".join(out) + "</table>"

def z_row(name, k, note=""):
    mm = m(k); return (name, fr(mm.z[0]), fr(mm.z[1]), note)

def schedule():
    A = [z_row("Half-wall bottom plate", "hw_bottom_plate"), z_row("Half-wall studs (kings)", "hw_king_a", f"{fr(m('hw_king_a').size('z'))} long · trimmers to {fr(m('hw_trimmer_a').z[1])}"),
         z_row("Nook header (3½ sandwich)", "hw_header", "2×10 + ½ ply + 2×10"),
         ("Nook finished ceiling / head jamb", "—", fr(CEIL), f"header bottom {fr(HB)} less ¾ jamb; panel top {fr(CEIL+PANEL)}"),
         z_row("Landing box — rim, side member, ledgers, all 2×8", "lnd_rim", f"clears the {fr(CEIL+PANEL)} panel top by {fr(m('lnd_rim').z[0]-CEIL-PANEL)}"),
         z_row("Landing joists, 2×4", "lnd_joist[0]"), z_row("Stringer plumb cut (at y 18)", "lnd_rim", "= the rim, full depth"),
         ("Landing finished top", "—", fr(LAND), f"{fr(DECK)} − one riser"),
         z_row("Half-wall double top plate", "hw_top_plate_1", "deck bears here"), z_row("Beam wrap, underside", "beam_wrap_underside", "¾ poplar"),
         z_row("Deck joists, 2×4", "deck_joist[0]"), z_row("Beam, doubled 2×10", "beam", f"{fr(m('beam').z[1]-DECK)} proud of the deck"),
         z_row("Side ledger, 2×10", "side_ledger", "top = beam top"), z_row("Rear ledger, 2×6", "rear_ledger", "top inside the ledge box"),
         z_row("Deck plywood", "deck_ply", f"<b>deck top = {fr(DECK)}</b>"), ("Mattress", fr(DECK), fr(DECK + MAT["thickness"]), f"{fr(MAT['thickness'])} ASSUMED"),
         ("Boxed ledge", fr(DECK), fr(m("ledge_lid").z[1]), f"{fr(m('ledge_lid').z[1]-DECK-MAT['thickness'])} proud of the mattress"),
         z_row("Screen slats", "slat[0]", f"{fr(m('slat[0]').size('z'))} long"), z_row("Screen top plate, 2×4 flat", "screen_top_plate"), ("Ceiling", "—", fr(CEILING), "")]
    A[6] = ("Stringer plumb cut (at y 18)", fr(ST.plumb_cut()[0]), fr(ST.plumb_cut()[1]), "= the rim, full depth")
    B = "<table><tr><th>Riser</th>" + "".join(f"<th>{i}{' (landing)' if i == ST.n_treads+1 else ' (deck)' if i == ST.n_risers else ''}</th>" for i in range(1, ST.n_risers + 1)) + "</tr><tr><td>Height</td>" + "".join(f'<td class="n">{ST.riser_z[i]:.2f}</td>' for i in range(1, ST.n_risers + 1)) + "</tr></table>"
    def x_row(name, k, note=""):
        mm = m(k); return (name, fr(mm.x[0]), fr(mm.x[1]), note)
    C = [x_row("Desk (existing)", "desk"), ("Mattress", "2", fr(2 + MAT["size"][1]), "2 tuck gap at the window wall"), ("Deck landing area", fr(2 + MAT["size"][1]), "107", ""),
         ("Half-wall", fr(m("hw_sheath_loft_a").x[0]), fr(m("hw_sheath_stair_a").x[1]), f"studs {fr(m('hw_king_a').x[0])}–{fr(m('hw_king_a').x[1])}"),
         x_row("Deck structural rim", "deck_rim", "stair-side panel runs to the deck top"), ("<b>Deck, overall</b>", "0", "107", ""),
         x_row("Landing side member", "lnd_side_member", "on the header's flush face"), ("Stringers A / B / C", " · ".join(f"{fr(m(k).x[0])}–{fr(m(k).x[1])}" for k in ("stringer_a", "stringer_b", "stringer_c")), "", f"{fr(float(d['stair']['stringer_pitch']))} centres"),
         ("Landing joists", " · ".join(f"{fr(m(k).x[0])}–{fr(m(k).x[1])}" for k in ids("lnd_joist")), "", "run with the stringers"),
         x_row("Right-wall ledger", "lnd_ledger_rightwall"), ("<b>Stair &amp; landing</b>", "107", fr(RX), "24")]
    def y_row(name, k, note=""):
        mm = m(k); return (name, fr(mm.y[0]), fr(mm.y[1]), note)
    D = [y_row("Rear ledger", "rear_ledger"), ("Boxed ledge", "0", "8", f"well {fr(m('ledge_front_rail').y[0]-m('rear_ledger').y[1])} wide"),
         ("Nook opening — rough", fr(NOOK_Y[0]), fr(NOOK_Y[1]), fr(NOOK_Y[1]-NOOK_Y[0])), ("Nook opening — finished", fr(JAMB_Y[0]), fr(JAMB_Y[1]), f"{fr(JAMB_Y[1]-JAMB_Y[0])} between ¾ jambs"),
         y_row("Header (kings 0–1½, 48½–50)", "hw_header", f"{fr(m('hw_header').size('y'))} long, 1½ bearing each end"),
         ("Nook flat ceiling", fr(NOOK_Y[0]), fr(Y_MEET), "rake begins where the stringer undersides reach the panel"),
         ("Mattress bay", "8", fr(m("beam").y[0]), f"{fr(m('beam').y[0]-8)} for a {MAT['size'][0]} mattress"),
         y_row("Landing side member", "lnd_side_member"), y_row("Landing rim", "lnd_rim", "2×8"), ("Stringer top runs", fr(ST.y_top), fr(ST.y_riser_top), "under the landing deck"),
         y_row("Blocking between stringers", "lnd_blocking[0]", "flush with riser 6"), y_row("Right-wall ledger", "lnd_ledger_rightwall", "stringer C bears on its end"),
         ("Landing", "0", fr(ST.landing), ""), y_row("Beam structure", "beam", "over the end stud pack"), y_row("Beam wrap", "beam_wrap_face"),
         ("<b>Platform, finished</b>", "0", fr(m("beam_wrap_face").y[1]), f"8 + {fr(m('beam').y[0]-8)} + 3 + ¾"), y_row("Desk (existing)", "desk", f"projects {fr(m('desk').y[1]-m('beam_wrap_face').y[1])} past the beam"),
         ("Fan blade edge", "—", fr(m("fan").y[0]), f"blades at {fr(m('fan').z[0])}"), ("Stair, to bottom riser", fr(ST.y_riser_top), fr(ST.y_bottom), f"{ST.n_treads} treads @ {fr(ST.run)}"),
         y_row("Dresser (48 × 16)", "dresser", f"{fr(m('dresser').y[0]-ST.y_bottom)} gap to the stair"), ("Entry door (32)", fr(float(room["door"]["y"][0])), fr(float(room["door"]["y"][1])), f"{fr(float(room['door']['to_corner']))} to the corner")]
    Ed = [("Clear span below the deck", fr(DER["clear_below_deck_x"]), "107 deck − 5 half-wall"), ("Clear height under joists", fr(DER["clear_under_joists"]), "58 − ¾ ply − 3½ joist"),
          ("Clear height under the beam", fr(DER["clear_under_beam"]), "less the ¾ wrap — not uniform with the joists"), ("Deck joist span", fr(DER["deck_joist_span"]), "ledger face → beam face"),
          ("Deck plywood", " × ".join(fr(a) for a in DER["deck_ply"]), "1½→106¼ by 1½→47"), ("Sitting headroom", fr(DER["sitting_headroom"]), f"{fr(CEILING)} − mattress top"),
          ("Riser", f"{ST.R:.3f}", f"{fr(DECK)} ÷ {ST.n_risers} — <b>not 8¼</b>"), ("Stair angle", f"{math.degrees(ST.angle):.2f}°", "atan(rise/run)"), ("Stringer throat", fr(ST.throat), "11¼ − notch depth · 3½ min"),
          ("Stringer plumb cut (y 18)", f"{fr(ST.plumb_cut()[0])} → {fr(ST.plumb_cut()[1])}", "7¼ tall = the 2×8 rim"), ("Stringer underside at y 27 / 47", f"{fr(U(27))} / {fr(U(47))}", "notch corners − throat, dropped 1 for the treads"),
          ("Landing headroom", fr(DER["landing_headroom"]), f"{fr(CEILING)} − {fr(LAND)}"), ("Nook finished opening", f"{fr(JAMB_Y[1]-JAMB_Y[0])} × {fr(CEIL)}", "rough less ¾ jambs"),
          ("Nook flat ceiling depth", fr(Y_MEET - JAMB_Y[0]), f"jamb face to y {fr(Y_MEET)}"), ("Nook far end height", fr(DER["nook_far_end_height"]), "stringer underside at 47 − ¾ panel"),
          ("Light chase over the flat", fr(DER["nook_light_chase"]), "joist bottom − header bottom — wafer LED only"), ("Rim ↔ header engagement", fr(DER["rim_header_overlap"]), "full 2×8"),
          ("Rim ↔ stringer bearing", fr(DER["rim_stringer_bearing"]), "full 2×8"), ("Slat clear opening", fr(DER["slat_clear"]), f"(107 − {SCR['slat_count']} × 1½) ÷ {SCR['slat_count']-1} · 3½ max"),
          ("Stair projection", fr(DER["stair_projection"]), f"{fr(ST.landing)} landing + {fr(ST.y_bottom-ST.y_riser_top)} run"), ("Fan clearance", fr(DER["fan_clearance"]), f"{fr(m('fan').y[0])} − {fr(m('beam_wrap_face').y[1])}"),
          ("Room depth chain", fr(DER["room_depth_chain"]), f"{fr(RY - DER['room_depth_chain'])} unplaced in {fr(RY)} — field")]
    return (f'<h2 style="margin-top:4px">A · Vertical datums</h2>{tbl(A, ["Member", "Bottom", "Top", "Note"])}'
            f'<h2 style="margin-top:18px">B · Stair heights</h2>{B}'
            f'<div class="note" style="border-left-color:#b07d1a;background:#fdf7ec"><b style="color:#b07d1a">Riser is {ST.R:.3f}, not 8¼.</b> Step the stringer off by dividing {fr(DECK)} into {ST.n_risers}, or set the square to {ST.R:.3f} / {fr(ST.run)}. Marking 8¼ seven times lands ¼ short. Drop each stringer {fr(T)} for the tread thickness.</div>'
            f'<h2 style="margin-top:18px">C · Plan — x, from the window wall</h2>{tbl(C, ["Element", "From", "To", "Note"])}'
            f'<h2 style="margin-top:18px">D · Plan — y, out from the bed wall</h2>{tbl(D, ["Element", "From", "To", "Note"])}'
            f'<h2 style="margin-top:18px">E · Derived — do not measure these independently</h2>{tbl([(a, b, c) for a, b, c in Ed], ["Quantity", "Value", "Falls out of"])}')

# =========================================================================== page
def revisions():
    rows = json.load(open("archive/revisions-T.json"))
    return "".join(f'<tr><td class="n"><b>{E(r)}</b></td><td>{t}</td></tr>' for r, t in rows)

def page():
    figs = {"d1": d1(), "d2": d2(), "d3": d3(), "d4": d4(), "d5a": d5a(), "d5b": d5b(), "d6": d6(), "d7a": d7a(), "d7b": d7b(), "d8a": d8a(), "d8b": d8b(), "d9": d9()}
    cards = [("Deck height", fr(DECK), "top of plywood, AFF"), ("Platform", f"107 × {fr(m('beam_wrap_face').y[1])}", "finished, incl. ¾ wrap"),
             ("Clear underneath", fr(DER["clear_under_joists"]), f"at joists; {fr(DER['clear_under_beam'])} under the wrapped beam"), ("Sitting headroom", fr(DER["sitting_headroom"]), "mattress top to ceiling"),
             ("Boxed ledge", "8w × 8h", f"well {fr(m('ledge_front_rail').y[0]-1.5)} × {fr(m('ledge_front_rail').z[1]-DECK)}"), ("Mattress bay", f"{fr(m('beam').y[0]-8)} × {fr(107-2-24)}", "1 slack + 2 tuck at the window wall"),
             ("Stair", f"{ST.n_risers} @ {ST.R:.3f}", f"{fr(ST.run)} run · {math.degrees(ST.angle):.1f}° · 24 wide · 5/4 treads"), ("Stair landing", f"24 × {fr(ST.landing)}", f"at {fr(LAND)} — one riser below deck"),
             ("Half-wall", "5 thick", "¾ ply + 3½ studs + ¾ ply"), ("Clear below deck", fr(DER["clear_below_deck_x"]), "107 deck less the 5 wall"),
             ("Under-stair nook", f"{fr(JAMB_Y[1]-JAMB_Y[0])} × {fr(CEIL)}", f"finished, jambed · {fr(DER['nook_far_end_height'])} at the far end")]
    cards_html = "".join(f'<div class="spec"><dt>{E(a)}</dt><dd>{E(b)}<span>{E(c)}</span></dd></div>' for a, b, c in cards)
    today = datetime.date.today().isoformat()
    out = [f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lofted Bed — Working Drawings · Rev {E(REV)}</title>
<style>{CSS}</style></head><body><div class="wrap">
<header><h1>Lofted Bed — Working Drawings</h1>
<div class="meta"><span class="rev">REV {E(REV)}</span><span>Twin loft · {fr(RX)} × {fr(RY)} room · {fr(CEILING)} ceiling</span><span>Deck {fr(DECK)} AFF · post-free 107 span · stairs locked</span><span>generated {today} from {E(YAML)} by drawings.py</span></div></header>

<div class="card"><h2>Conventions</h2><ul>
<li><b>Every drawing is generated from <code>dimensions.yaml</code>.</b> Nothing here was placed by hand. If a drawing looks wrong, the data is wrong — fix the yaml, run <code>python3 verify.py</code>, then <code>python3 drawings.py</code>.</li>
<li><b>Orientation.</b> Plans: bed wall at the top, window wall to the left. x–z views look toward the bed wall (window wall left). y–z views keep the <b>bed wall on the left</b> — sections cut at an x position are drawn mirrored where needed so that stays true.</li>
<li><b>Hatched</b> = cut by the view. <b>Pale</b> = beyond the cut. <b>Dashed</b> = hidden. <b>Blue</b> = hardware. <b>Red</b> = a limit or an open finding.</li>
<li><b>Framing vs finished.</b> Member extents are framing (actual lumber). Platform 50¾ finished / 50 framed. Half-wall 5 / 3½. Deck 107 / 106¼ rim. Nook {fr(NOOK_Y[1]-NOOK_Y[0])} × {fr(HB)} rough / {fr(JAMB_Y[1]-JAMB_Y[0])} × {fr(CEIL)} finished. Cut lists use the framing numbers.</li></ul></div>

<div class="card"><h2>Locked dimensions</h2><dl class="specs">{cards_html}</dl></div>

<div class="card"><h2>Dimension schedule — the controlling reference</h2>
<p class="cap" style="margin:0 0 14px">Every number below is computed by <code>verify.py</code> from the member extents, never typed. All heights are above finished floor; plan positions are from the <b>window wall</b> (x) and the <b>bed wall</b> (y) to finished wall faces.</p>
{schedule()}
<div class="note"><b>Framing vs finished.</b> The platform is 50¾ finished but 50 of framing — the last ¾ is the beam wrap. The half-wall is 5 finished, 3½ of studs. The deck is 107 to the finished wall face but its structural rim stops at 106¼. The nook is {fr(NOOK_Y[1]-NOOK_Y[0])} × {fr(HB)} rough and {fr(JAMB_Y[1]-JAMB_Y[0])} × {fr(CEIL)} finished. Cut lists must use the framing numbers; layout marks use the finished ones.</div></div>
"""]
    for n, title, key, cap in DRAWINGS:
        body = "".join(f'<figure>{figs[k]}</figure>' for k in key)
        out.append(f'<div class="card"><h2>{n} — {E(title)}</h2>{body}<p class="cap">{cap}</p></div>')
    out.append(f'<div class="card"><h2>Structure &amp; load path</h2>{tbl(STRUCTURE, ["Member", "Spec", "Check"])}<div class="note">{CEILING_NOTE}</div></div>')
    out.append(f'<div class="card"><h2>Open items</h2><ul>{"".join(f"<li>{x}</li>" for x in OPEN)}</ul></div>')
    out.append(f'<div class="card"><h2>Revisions</h2><p class="cap" style="margin:0 0 10px">Drawing numbers in entries below refer to the numbering in force at the time.</p><table><tr><th>Rev</th><th>Change</th></tr><tr><td class="n"><b>{E(REV)}</b></td><td>{REV_NOTE}</td></tr>{revisions()}</table></div>')
    out.append("</div></body></html>")
    return "\n".join(out)

CSS = """
:root{color-scheme:light;--ink:#23231f;--ink2:#5f5d56;--ink3:#8a877e;--bg:#fbfaf7;--card:#fff;--line:#e0ddd4;
--lum:#e8d6ae;--lum2:#f1e6cc;--lumline:#7a6238;--sheet:#cfc4ac;--fin:#b98d57;--wall:#3b352c;--ghost:#eee9dd;
--blue:#5b8fc7;--blue2:#dce7f3;--blueink:#2b4a6b;--pencil:#1f4e9c;--red:#c0392b;--green:#4a7c4e;--green2:#cfe0cf;--amber:#b07d1a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;font-size:14px;line-height:1.55}
.wrap{max-width:1040px;margin:0 auto;padding:28px 22px 72px}header{border-bottom:2px solid var(--ink);padding-bottom:14px;margin-bottom:22px}
h1{font-size:22px;margin:0 0 4px}.meta{color:var(--ink2);font-size:12.5px;display:flex;gap:16px;flex-wrap:wrap;align-items:center}
.rev{background:var(--ink);color:#fff;padding:2px 9px;border-radius:99px;font-weight:700;font-size:11.5px;letter-spacing:.04em}
h2{font-size:12px;text-transform:uppercase;letter-spacing:.09em;color:var(--ink2);margin:0 0 12px;font-weight:700}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin-bottom:20px}
.specs{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:8px;overflow:hidden;margin:0}
.spec{background:var(--card);padding:11px 13px}.spec dt{font-size:11px;color:var(--ink3);text-transform:uppercase;letter-spacing:.05em;margin-bottom:3px}
.spec dd{margin:0;font-size:16px;font-weight:650;font-variant-numeric:tabular-nums}.spec dd span{font-size:11.5px;font-weight:400;color:var(--ink2);display:block;margin-top:1px}
figure{margin:0 0 12px;overflow-x:auto}figure svg{display:block;width:100%;height:auto}.cap{color:var(--ink2);font-size:12.5px;margin:10px 2px 0}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--ink3);font-weight:700}td.n{font-variant-numeric:tabular-nums;white-space:nowrap}tr:last-child td{border-bottom:none}
ul{margin:0;padding-left:19px}li{margin-bottom:7px}code{font-size:12.5px;background:#f1efe9;padding:1px 4px;border-radius:3px}
.note{border-left:3px solid var(--red);background:#fdf4f2;padding:11px 14px;border-radius:0 6px 6px 0;font-size:13px;margin-top:14px}.note b{color:var(--red)}
.tag{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.05em;padding:1.5px 7px;border-radius:4px;vertical-align:1px}.t-open{background:#fdf1e3;color:var(--amber)}.t-lock{background:#e8f0e9;color:var(--green)}.t-chk{background:#fbe9e7;color:var(--red)}
svg text{font-family:ui-sans-serif,system-ui,sans-serif;font-size:11.5px;fill:var(--ink)}
.lab{font-weight:650;font-size:12px}.labs{font-size:10.5px;fill:var(--ink2)}.labk{font-weight:650;font-size:11.5px;fill:var(--pencil)}.labb{font-weight:650;font-size:11px;fill:var(--red)}
.lum{fill:var(--lum);stroke:var(--lumline);stroke-width:1}.lum2{fill:var(--lum2);stroke:var(--lumline);stroke-width:.8}.blk{fill:#e6d9bd;stroke:var(--red);stroke-width:1}
.sheet{fill:var(--sheet);stroke:var(--lumline);stroke-width:.6}.fin{fill:var(--fin);stroke:var(--lumline);stroke-width:.8}.wall{fill:var(--wall);stroke:none}.ghost{fill:var(--ghost);stroke:none}
.room{fill:#fff;stroke:var(--ink);stroke-width:4}.deck{fill:var(--blue2);stroke:var(--blue);stroke-width:1.4}.ledge{fill:#eef3f9;stroke:var(--blue);stroke-width:1}.matt{fill:#c8daed;stroke:var(--blue);stroke-width:1}
.beamplan{fill:var(--lum);stroke:var(--lumline);stroke-width:1.2}.landing{fill:var(--green2);stroke:var(--green);stroke-width:1.6}.tread{fill:#efeee8;stroke:var(--ink);stroke-width:1.2}.exist{fill:#efeee8;stroke:var(--ink);stroke-width:1.4}
.hid{fill:none;stroke:var(--ink2);stroke-width:1.4;stroke-dasharray:8 5}.dashfill{fill:none;stroke:var(--ink2);stroke-width:1;stroke-dasharray:5 3}.door{stroke:var(--ink);stroke-width:3}.window{stroke:var(--blue);stroke-width:5}
.green{fill:var(--green2);fill-opacity:.85;stroke:#2c4a2e;stroke-width:1.5}.greend{fill:none;stroke:#2c4a2e;stroke-width:1.2;stroke-dasharray:5 3}.flat{fill:#fdf6e3;stroke:var(--fin);stroke-width:1.2}.rake{fill:#f6f2e6;stroke:var(--fin);stroke-width:.8;stroke-dasharray:4 3}
.hanger{fill:none;stroke:var(--pencil);stroke-width:2.2}.strap{fill:none;stroke:var(--red);stroke-width:2}.light{fill:none;stroke:var(--red);stroke-width:2}.co{fill:var(--red)}.cot{fill:#fff;font-weight:700;font-size:11.5px}
.hatchline{stroke:var(--lumline);stroke-width:.6}.badline{stroke:var(--red);stroke-width:1}.bad{fill:url(#bad);stroke:var(--red);stroke-width:1}
.ink{stroke:var(--ink);stroke-width:1}.dash{stroke:var(--ink2);stroke-width:1;stroke-dasharray:6 4}.ghostl{stroke:var(--ink2);stroke-width:.9;stroke-dasharray:3 3;fill:none}.floor{stroke:var(--wall);stroke-width:3}.redline{stroke:var(--red);stroke-width:1.6;stroke-dasharray:7 4}
.soffit{fill:none;stroke:var(--fin);stroke-width:3}polyline.hanger{fill:none}
.dim line{stroke:var(--pencil);stroke-width:.9}.dim text{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10.5px;fill:var(--pencil)}marker path{fill:var(--pencil)}
"""

# =========================================================================== NOTES — the only hand-written content
DRAWINGS = [
    ("1", "Floor plan", ["d1"], "Facing the bed wall, the window and desk are on your left; the stairs, dresser and entry door on your right. Door swing never reaches below the 150 line. The room-depth chain is ½ short of 186 — one of the field measurements still owed."),
    ("2", "Front elevation", ["d2"], f"Looking toward the bed wall. The wrapped beam stands {fr(m('beam').z[1]-DECK)} above the deck; the slat screen runs from the beam top to a 2×4 flat plate at the ceiling. The stair is seen face-on to the right of the half-wall."),
    ("3", "Section through the platform edge", ["d3"], "Cut at x = 55, between joists, so the joist reads pale (beyond) and the blocking, ply, ledger, beam and top plate are hatched (cut). The deck ply is the floor of the ledge well. The rear ledger's bottom is flush with the joists so the underside is one plane at 53¾; the beam wrap brings its own underside to 53."),
    ("4", "Stair section", ["d4"], f"Cut through stringer B. Each stringer runs {fr(ST.top_run)} under the landing: its top plumb cut, at y {fr(ST.y_top)}, is {fr(ST.plumb_cut()[1]-ST.plumb_cut()[0])} tall — exactly the 2×8 rim it bears on. Stringers are dropped {fr(T)} for the 5/4 treads. All seven risers are {ST.R:.3f}; the last is the sideways step from the landing onto the deck. Handrail on the right wall for the full run."),
    ("5", "Under-stair nook", ["d5a", "d5b"], f"The opening through the half-wall is finished with ¾ poplar jambs; the head jamb and the flat soffit panel share one plane at {fr(CEIL)}, so the ceiling runs straight through the opening. The panel's top at {fr(CEIL+PANEL)} clears every 2×8 in the landing box by {fr(m('lnd_rim').z[0]-CEIL-PANEL)}. Where the stringer undersides come down to that line (y ≈ {fr(Y_MEET)}) the panel simply continues on the stringers to {fr(DER['nook_far_end_height'])} at the far end. No gussets. Power for the wafer light must be in the half-wall before it is sheathed."),
    ("6", "Platform framing plan", ["d6"], "Joists hang off the rear ledger and off the beam's inside face (LUS24 hangers, both ends — they cannot 'land on' a beam that shares their bottom). Nothing bears in the field; the platform is carried by the two walls and the half-wall. Lay the joists out so plywood seams land on centres. <b>Parked finding:</b> the side ledger stops at 48 while the beam occupies 47→50 — 1 of 3 backed; recommended fix is a 50¾ ledger and a double-2×10 hanger."),
    ("7", "Half-wall detail", ["d7a", "d7b"], "Plan detail is a horizontal section at 30, rotated so the bed wall is on the left and the stair side up. The opening removes both faces: what remains is two posts and a sandwich header — a portal frame, not a shear wall. The beam's reaction bypasses it (lands on the far stud pack); the landing box ties the top plate across to the right wall. Glue the deck ply and strap both header-to-king joints."),
    ("8", "Stair & landing framing", ["d8a", "d8b"], "Section at y 20 cuts the three top runs: A is fixed by SDS into the header through the facing, B by SDS from inside the box through the rim, C bears on the ledger end and screws to the right-wall studs. The landing box is four 2×8s at one elevation (41.71→48.96) — rim, side member, bed-wall ledger, right-wall ledger — with two 2×4 joists running with the stringers and 2×4 blocking flush with riser 6. The rim hangs on concealed-flange HUC28s: into the header (SD screws through the ¾ facing) and into the right-wall ledger. <b>Framing order:</b> ledgers → side member (6 × ¼×6 SDS through the facing) → HUC28s and rim → 2 × A35 at the side-member/rim corner → LUS24s and joists → stringer A (4 × ¼×4½ SDS into the header over its top run, 2 toe-screws to the rim), stringer C (4 × ¼×4½ SDS into right-wall studs, 2 toe-screws to the ledger end), then stringer B (3 × ¼×3½ SDS from inside the box through the rim) → kicker → blocking → deck ply, treads, risers."),
    ("9", "Framing overlay · half-wall + landing", ["d9"], "Half-wall framing and the landing/stair framing drawn to one datum. Connection points: ➊ side member → header, 6 × ¼×6 SDS through the facing · ➋ rim → header, HUC28 · ➌ stringer A → header, 4 × ¼×4½ SDS through the facing over y 18→27 · ➍ stringer A → end stud at 47→50, 2 × ¼×4½ SDS · ➎ side member → rim, 2 × A35 · ➏ bed-wall ledger, lags into studs. Not in this view: rim → right-wall ledger HUC28, joists on LUS24s. Every one of these is a rule in dimensions.yaml and passes verify.py."),
]

STRUCTURE = [
    ("Front beam", "Doubled 2×10, 102 clear span", "~240 psi vs ~900 allowable · deflection ≈ L/2500 · lamination to specify"),
    ("Joists", "2×4 @ 12 o.c., 45½ span, LUS24 both ends", "~352 psi · joists hang from the beam's face, they do not bear on it"),
    ("Deck", "¾ ply, glued + screwed", "Required — the diaphragm in place of posts · front-edge blocking at the beam to add"),
    ("Rear ledger", "2×6, 104¾, bottom flush w/ joists", "~110 lb per stud · lags into every stud"),
    ("Side ledger", "2×10, 48 out, bottom at 53¾", "<b>PARKED:</b> beam end backed by 1 of 3 — extend to 50¾ + double hanger"),
    ("Half-wall", "5 total — ¾ ply + 3½ studs + ¾ ply · two stud packs, no field studs · top plate 53¾", "Deck and beam end bear on top · portal frame with a sandwich header"),
    ("Nook header", "2×10 + ½ ply + 2×10 = 3½, over a 44 × 41½ rough opening", "~700 lb → ~140 psi · sized by connection depth: every landing hanger is fully backed by it"),
    ("Header lamination", "16d @ 12 o.c., two rows, through the spacer", "Hangers on the stair face reach the far ply only through this nailing — 4½ screws minimum through the ¾ facing"),
    ("Landing box", "2×8 rim, side member, both ledgers at 41.71→48.96", "Rim on HUC28s, header side with SD screws through the facing · side member 6 × ¼×6 SDS · 2 × A35 at the corner"),
    ("Landing joists", "2 × 2×4 running with the stringers, LUS24s", "Five support lines under the ¾ deck at ≤ 7"),
    ("Stringers", "3 × 2×12, 8.286 rise / 9 run, 9 top run under the landing", f"Throat {fr(ST.throat)} vs 3½ min · plumb cut 7¼ = full rim depth · one 8' board each"),
    ("Stringer fixing", "A: 4 SDS into the header + 2 toe-screws · B: 3 SDS from inside the box · C: on the ledger end + 4 SDS into studs", "≈170 lb per stringer at the top"),
    ("Treads", "5/4 hardwood, 10½ on a 9 run (1½ nosing)", "Stringers dropped 1 · closed risers"),
    ("Nook finish", "¾ poplar jambs; ¾ soffit panel flat to y ≈ 18¼ then on the stringers", f"Finished {fr(JAMB_Y[1]-JAMB_Y[0])} × {fr(CEIL)} · far end {fr(DER['nook_far_end_height'])} · wafer LED only (chase {fr(DER['nook_light_chase'])})"),
    ("Screen", "23 × 2×2 poplar slats @ 3.30 clear, 2×4 flat top plate", "Guard for a 58 deck: top plate into ceiling framing · slat base joints to specify"),
    ("Whole assembly", "≈850 lb loaded", "~17 psf average — but delivered on two lines (half-wall plate, kicker); floor joists below to be located"),
]
CEILING_NOTE = "<b>Ceiling joists run parallel to the bed wall</b> — the top plate can't cross them. Measure the joist line nearest 50¾ out; the plate spans 47¼–50¾ (text) or 46½–50 with a ¾ band (Drawing 3 of Rev T) — <b>decide the plate position first</b>, then measure. If the joist falls outside the band, adjust the ledge (6–10 all work). Don't skip it: unattached, a 200 lb lean at the top of the screen overloads the slat bases."
OPEN = [
    '<span class="tag t-chk">PARKED</span> <b>Beam left end.</b> Side ledger stops at 48; beam is 47→50 — 1 of 3 backed. Fix: ledger to 50¾ + LUS210-2/HUS210-2 (also gives slat 0 a seat). Builder\'s call.',
    '<span class="tag t-chk">FIELD</span> <b>Studs</b> in the bed wall, window wall and right wall — every ledger and stringer C depend on them. <b>Ceiling joist</b> nearest 50¾ out. <b>Mattress</b> thickness (6 assumed). <b>Room depth</b> — ½ unplaced in the chain. <b>Floor joists</b> under the half-wall plate and the kicker.',
    '<span class="tag t-chk">SPECIFY</span> Beam lamination · deck-ply front-edge blocking at the beam · header-to-king straps (member) · kicker anchorage · half-wall bottom-plate anchorage · slat-to-beam and slat-to-plate joints · screen top-plate position (47¼→50¾ vs 46½→50 + band).',
    '<span class="tag t-chk">SEQUENCE</span> Nook power into the half-wall before sheathing; switch on the half-wall face, desk side. Stringer B\'s screws go in before the landing deck.',
    '<span class="tag t-chk">VERIFY</span> Lay out and cut one stringer, measure the actual throat and plumb cut, then cut the other two.',
    '<span class="tag t-lock">LOCKED</span> Deck 58 · platform 107 × 50¾ · 8 boxed ledge · 39 bay · doubled 2×10 upstand beam with ¾ wrap · post-free · half-wall at the stair end · full-height slat screen · 7 @ 8.286 / 9 run · 27 landing at 49.71 · 5/4 treads · stringers 9 under the landing · landing box all 2×8 · nook jambed, ceiling 40¾ flush.',
]
REV_NOTE = ("<b>Model-first.</b> This set is generated by <code>drawings.py</code> from <code>dimensions.yaml</code>, checked by <code>verify.py</code>. "
            "<b>Stringer geometry corrected:</b> the top plumb cut against a rim at y 27 is 7.0 tall, not 11¼ — Rev M/S/T counted wood above the tread-5 cut that doesn't exist, and Drawing 8's path drew it as a zero-width spike. "
            "<b>Landing reframed:</b> stringers extend 9 under the landing so the plumb cut is 41.71→48.96, the depth of a 2×8; rim, side member and both ledgers are 2×8 on that line; rim on HUC28s fully backed by the header; joists run with the stringers; blocking flush with riser 6; rake gussets deleted. "
            "<b>Treads</b> 5/4, stringers dropped 1. <b>Nook</b> jambed in ¾ poplar, finished 42½ × 40¾, soffit flush through the opening (Rev T's 41½ 'finished' ceiling left no room for the panel under the side member). "
            "<b>Cut-list corrections:</b> rear ledger 104¾ not 107; beam 104¾; wrap underside 102; ledge parts start at 1½. Slats drawn at 31½ (Rev T's Drawing 2 still had 29⅝). "
            "<b>Parked:</b> beam left end on the side ledger (1 of 3 backed) and slat 0. See audits/.")

if __name__ == "__main__":
    open(OUT, "w").write(page())
    print(f"{OUT}: rev {REV} from {YAML}")
