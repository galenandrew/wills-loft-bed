"""Drawing 3 — Section through the platform edge. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "3", "Section through the platform edge"

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
    R(v, m("beam"), "y", "z", "lum", HATCH); R(v, m("beam_wrap_face"), "y", "z", "fin", HATCH)
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
    v.text(48.5, 58.4, "doubled 2×10", "lab", "middle", rot=-90); v.text(53.5, 28, "¾ poplar wrap, mitered", "labs", "start", rot=-90)
    v.text(56, 66, "2×2 slats beyond, flush with the wrap", "labs", "start", rot=-90)
    v.text(43, 96.5, "2×4 top plate, flat", "labs", "end", dy=-3)
    v.text(27, 15, f"desk {fr(dk.y[1])} deep × {fr(dk.z[1])} high — projects {fr(dk.y[1]-m('beam_wrap_face').y[1])} past the beam", "labs", "middle")
    # dims
    v.dim_h(0, 8, 74, "8"); v.dim_h(8, m("beam").y[0], 74, f"{fr(m('beam').y[0]-8)} bay"); v.dim_h(m("beam").y[0], m("beam_wrap_face").y[1], 74, "3¾")
    v.dim_h(0, m("beam_wrap_face").y[1], 42.5, f"{fr(m('beam_wrap_face').y[1])} platform depth (8 + {fr(m('beam').y[0]-8)} + 3 + ¾)", above=False)
    v.dim_v(-5, 0, DECK, f"{fr(DECK)} deck"); v.dim_v(-5, DECK, m("ledge_lid").z[1], "8", left=True)
    v.dim_v(20, 0, m("deck_joist[0]").z[0], f"{fr(DER['clear_under_joists'])} clear")
    v.dim_v(50.75, 0, m("beam").z[0], f"{fr(DER['clear_under_beam'])} under the beam", left=False)
    v.dim_v(44, DECK + MAT["thickness"], CEILING, f"{fr(DER['sitting_headroom'])} sitting headroom")
    return v.svg(f"Section through the platform at x = {xc}, bed wall on the left")

FIGURES = [("d3", d3)]
CAPTION = "Cut at x = 55, between joists, so the joist reads pale (beyond) and the blocking, ply, ledger, beam and top plate are hatched (cut). The deck ply is the floor of the ledge well. The rear ledger's bottom is flush with the joists so the underside is one plane at 53¾, same as the beam's own underside."
