"""Sheet 5 — Stair, landing and nook framing plan, seen from above."""
from drawings.model import ST, Y_FIN, NOOK_Y, RX, fr, m
from .canvas import Canvas
from .geometry import ViewSpec, projector, view
from .sheet import compose

NUMBER, TITLE, PAGE = "5", "Stair · landing · nook — framing plan", "stairs"

SPEC = ViewSpec("plan", direction=(0, 0, -1), up=(0, 1, 0), mirror=True)

MODES = {"fan": "off", "dresser": "off", "desk": "off", "mattress": "off"}


def framing():
    recs = view(SPEC)
    cv = Canvas("x", "y", 98, RX + 6, -5, 78, 9.0, vdown=True, proj=projector(SPEC))
    cv.shell()
    fig = compose(cv, recs, MODES, "stair_frame",
                  "Stair and landing framing seen from above, bed wall at the top",
                  title="Stair · landing · nook framing plan",
                  start_off=("off-l-finish",), spec=SPEC,
                  electrical=["nk_light"])
    # --- dims
    cv.dim_h(float(m("hw_sheath_loft_a").x[0]), float(m("hw_sheath_stair").x[1]),
             "top", 0, f"{fr(float(m('hw_sheath_stair').x[1]) - float(m('hw_sheath_loft_a').x[0]))} wall")
    cv.dim_h(float(m("hw_sheath_stair").x[1]), RX, "top", 0,
             f"{fr(RX - float(m('hw_sheath_stair').x[1]))} stair")
    cv.dim_v(0, float(m("lnd_rim").y[1]), "left", 0, f"{fr(float(m('lnd_rim').y[1]))} landing box")
    cv.dim_v(float(m("lnd_rim").y[1]), ST.y_bottom, "left", 0, f"{fr(ST.y_bottom - float(m('lnd_rim').y[1]))} stringers")
    cv.dim_v(0, Y_FIN, "right", 0, f"{fr(Y_FIN)} finished")
    cv.dim_v(*NOOK_Y, "right", 1, f"{fr(NOOK_Y[1] - NOOK_Y[0])} rough opening")
    # --- labels
    cv.text(119, 8, "LANDING BOX", "")
    cv.text(119, 12, "2×8 rim · ledgers · 2×4 joists", "sm")
    cv.text(107.8, 45, "stringer A", "sm", rot=-90)
    cv.text(119.4, 45, "stringer B", "sm", rot=-90)
    cv.text(130.4, 45, "stringer C", "sm", rot=-90)
    cv.text(119, ST.y_bottom + 2.6, "kicker", "sm")
    cv.text(104.5, 60, "half wall", "sm", rot=-90)
    fig.svg = cv.svg("Stair and landing framing plan, bed wall at the top")
    return fig


FIGURES = [("stair_frame", framing)]
CAPTION = ("Framing only — the treads, risers and landing deck start switched off; put "
           "<b>Finish</b> back on to see the boards that land on it. The landing box is four "
           "2×8s at one elevation with two 2×4 joists running with the stringers. Stringer A "
           f"lands on the half-wall framing at x {fr(float(m('stringer_a').x[0]))}, stringer C on the right-wall studs. "
           "The nook's studs sit under stringers A, B and C.")
