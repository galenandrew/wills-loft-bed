"""Sheet 8 — Loft cross section, cut between joists."""
from drawings.model import (BAY, BEAM_FIN_TOP, BEAMSTOCK, CEILING, DECK, DER, MAT,
                            MAT_Y0, MAT_Y1, SCR, fr, m)
from .canvas import Canvas
from .geometry import ViewSpec, projector, view
from .sheet import compose

NUMBER, TITLE, PAGE = "8", "Loft — cross section", "loft"

# Between joists 4 and 5, looking back toward the window wall. Mirrored so the bed
# wall stays on the left, the way every y–z view on this set is read.
CUT_X = 55.0
SPEC = ViewSpec("loft_sec", direction=(-1, 0, 0), cut=("x", CUT_X), near=True,
                mirror=True)

MODES = {"stair": "off", "half_wall": "off", "nook": "off", "dresser": "off",
         "fan": "outline", "desk": "outline", "mattress": "flat"}


def section():
    recs = view(SPEC)
    cv = Canvas("y", "z", -5, 62, -4, CEILING + 4, 7.4, proj=projector(SPEC))
    cv.shell()
    fig = compose(cv, recs, MODES, "loft_sec",
                  "Loft cross section cut between joists, bed wall on the left",
                  title=f"Cross section at x {fr(CUT_X)}, between joists", spec=SPEC,
                  electrical=["ledge_outlet_window", "loft_walkway_light"])
    lid, rail = m("ledge_lid"), m("ledge_front_rail")
    # --- dims
    cv.dim_v(0, DECK, "left", 0, f"{fr(DECK)} deck")
    cv.dim_v(DECK, BEAM_FIN_TOP, "left", 1, f"{fr(BEAM_FIN_TOP - DECK)} beam over deck")
    cv.dim_v(DECK, DECK + float(MAT["thickness"]), "right", 0, f"{fr(float(MAT['thickness']))} mattress")
    cv.dim_v(DECK + float(MAT["thickness"]), CEILING, "right", 1,
             f"{fr(DER['sitting_headroom'])} sitting headroom")
    cv.dim_h(MAT_Y0, MAT_Y1, "top", 0, f"{fr(float(MAT['size'][0]))} mattress")
    cv.dim_h(float(rail.y[1]), float(m("beam_wrap_inner").y[0]), "top", 1, f"{fr(BAY)} bay")
    cv.dim_h(0, float(lid.y[1]), "bottom", 0, f"{fr(float(lid.y[1]))} ledge")
    cv.dim_h(0, float(m("beam_wrap_face").y[1]), "bottom", 1,
             f"{fr(float(m('beam_wrap_face').y[1]))} platform")
    # --- labels
    cv.text(30, DECK - 5.4, f"2×4 joists @ 12 o.c. · {fr(DER['deck_joist_span'])} span", "sm")
    cv.text(26, float(m("loft_ceiling").z[0]) - 3.4, "½ finished ceiling under", "sm")
    cv.text(44, BEAM_FIN_TOP + 3, f"{BEAMSTOCK} + wrap", "sm", anchor="end")
    cv.text(44, 84, f"{SCR['slat_count']} slats, all on this plane", "sm", anchor="end")
    cv.text(9.5, float(lid.z[1]) + 3, "boxed ledge", "sm", anchor="start")
    cv.text(26, 26, "open below — the floor stays clear for standalone furniture", "sm")
    fig.svg = cv.svg("Loft cross section between joists, bed wall on the left")
    return fig


FIGURES = [("loft_sec", section)]
CAPTION = (f"Cut at x {fr(CUT_X)}, in the bay between joists, so the ply, ledger, beam and blocking are "
           f"hatched and the joist beside them reads pale. The wrapped beam's top is {fr(BEAM_FIN_TOP - DECK - float(MAT['thickness']))} proud of "
           f"the mattress, so it retains it rather than sitting under it, and the boxed ledge's lid "
           f"tracks it at {fr(float(m('ledge_lid').z[1]) - DECK - float(MAT['thickness']))} proud — the curb on the bed-wall side. Sitting headroom is "
           f"{fr(DER['sitting_headroom'])} over the mattress.")
