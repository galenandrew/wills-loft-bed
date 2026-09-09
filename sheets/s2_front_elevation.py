"""Sheet 2 — Front elevation. Looking at the bed wall, window wall on the left."""
from drawings.model import (BEAMSTOCK, BEAM_FIN_TOP, CEILING, DECK, DER, LAND, M,
                            MAT, RX, SCR, ST, fr, m)
from .canvas import Canvas
from .geometry import ViewSpec, projector, view
from .sheet import compose

NUMBER, TITLE, PAGE = "2", "Front elevation", "overview"

SPEC = ViewSpec("front", direction=(0, -1, 0), up=(0, 0, 1))

MODES = {"dresser": "off", "desk": "outline", "fan": "outline", "mattress": "flat"}


def front():
    recs = view(SPEC)
    cv = Canvas("x", "z", -6, RX + 6, -5, CEILING + 5, 6.4, proj=projector(SPEC))
    cv.shell()
    fig = compose(cv, recs, MODES, "front",
                  "Front elevation, looking toward the bed wall with the window wall on the left",
                  title="Front elevation", spec=SPEC)
    # --- dimensions, in the gutters
    cv.dim_h(0, RX, "bottom", 1, f"{fr(RX)} room")
    cv.dim_h(0, m("hw_sheath_loft_a").x[0], "bottom", 0,
             f"{fr(DER['clear_below_deck_x'])} clear — no posts")
    cv.dim_h(m("hw_sheath_loft_a").x[0], RX, "bottom", 0, f"{fr(RX - float(m('hw_sheath_loft_a').x[0]))} wall + stair")
    # Left: the wall section, floor to ceiling in three runs that close on the
    # room height — what the screen, the beam and the space under it each take.
    beam_soffit = float(m("beam").z[0])
    cv.dim_v(BEAM_FIN_TOP, CEILING, "left", 0, f"{fr(CEILING - BEAM_FIN_TOP)} screen")
    cv.dim_v(beam_soffit, BEAM_FIN_TOP, "left", 0, f"{fr(BEAM_FIN_TOP - beam_soffit)} beam")
    cv.dim_v(0, beam_soffit, "left", 0, f"{fr(beam_soffit)} under beam")
    cv.dim_v(0, CEILING, "left", 1, f"{fr(CEILING)} ceiling")
    # Right: the two levels you stand on, both measured down from the ceiling, and
    # the landing's own height — so ceiling-to-landing and landing-to-floor also
    # close on the room height.
    cv.dim_v(DECK, CEILING, "right", 0, f"{fr(CEILING - DECK)} ceiling to deck")
    cv.dim_v(LAND, CEILING, "right", 1, f"{fr(CEILING - LAND)} ceiling to landing")
    cv.dim_v(0, LAND, "right", 1, f"{fr(LAND)} landing")
    # --- labels
    cv.text(53, BEAM_FIN_TOP - 4, f"{BEAMSTOCK} beam + wrap", "", dy=-4)
    cv.text(53, (BEAM_FIN_TOP + CEILING) / 2, f"{SCR['slat_count']} slats @ {fr(DER['slat_clear'])} clear", "sm")
    cv.text(53, float(m("loft_ceiling").z[0]) - 6, f"loft ceiling {fr(float(m('loft_ceiling').z[0]))}", "sm")
    cv.text(119, 12, "stair beyond", "sm")
    cv.text(104.6, 20, "half wall", "sm", rot=-90)
    fig.svg = cv.svg("Front elevation, looking toward the bed wall")
    return fig


FIGURES = [("front", front)]
CAPTION = ("Looking toward the bed wall. The wrapped beam is the bed rail — it stands "
           f"{fr(BEAM_FIN_TOP - DECK - float(MAT['thickness']))} proud of the mattress top — and the slat screen runs from its "
           "cap to a flat 2×4 plate at the ceiling. The stair is face-on to the right of the half wall.")
