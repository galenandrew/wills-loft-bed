"""Sheet 2 — Front elevation. Looking at the bed wall, window wall on the left."""
from drawings.model import CEILING, RX, DECK, BEAM_FIN_TOP, DER, M, fr, m, ST, MAT, SCR, BEAMSTOCK
from .canvas import Canvas
from .geometry import ViewSpec, view
from .sheet import compose

NUMBER, TITLE, PAGE = "2", "Front elevation", "overview"

SPEC = ViewSpec("front", direction=(0, -1, 0), up=(0, 0, 1))

MODES = {"dresser": "off", "desk": "outline", "fan": "outline", "mattress": "flat"}


def front():
    recs = view(SPEC)
    cv = Canvas("x", "z", -6, RX + 6, -5, CEILING + 5, 6.4)
    cv.shell()
    fig = compose(cv, recs, MODES, "front",
                  "Front elevation, looking toward the bed wall with the window wall on the left",
                  title="Front elevation")
    # --- dimensions, in the gutters
    cv.dim_h(0, RX, "bottom", 1, f"{fr(RX)} room")
    cv.dim_h(0, m("hw_sheath_loft_a").x[0], "bottom", 0,
             f"{fr(DER['clear_below_deck_x'])} clear — no posts")
    cv.dim_h(m("hw_sheath_loft_a").x[0], RX, "bottom", 0, f"{fr(RX - float(m('hw_sheath_loft_a').x[0]))} wall + stair")
    cv.dim_v(0, DECK, "left", 0, f"{fr(DECK)} deck")
    cv.dim_v(DECK, BEAM_FIN_TOP, "right", 0, fr(BEAM_FIN_TOP - DECK))
    cv.dim_v(BEAM_FIN_TOP, CEILING, "right", 0, fr(CEILING - BEAM_FIN_TOP))
    cv.dim_v(0, CEILING, "right", 1, f"{fr(CEILING)} ceiling")
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
