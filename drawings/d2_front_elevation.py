"""Drawing 2 — Front elevation. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "2", "Front elevation"

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

FIGURES = [("d2", d2)]
CAPTION = f"Looking toward the bed wall. The wrapped beam stands {fr(m('beam').z[1]-DECK)} above the deck; the slat screen runs from the beam top to a 2×4 flat plate at the ceiling. The stair is seen face-on to the right of the half-wall."
