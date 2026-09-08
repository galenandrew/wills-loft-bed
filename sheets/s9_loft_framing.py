"""Sheet 9 — Loft framing plan, seen from above."""
from drawings.model import DER, ids, fr, m, VALS, BEAMSTOCK
from .canvas import Canvas
from .geometry import ViewSpec, view
from .sheet import compose

NUMBER, TITLE, PAGE = "9", "Loft — framing plan", "loft"

SPEC = ViewSpec("plan", direction=(0, 0, -1), up=(0, 1, 0), mirror=True)

MODES = {"stair": "off", "nook": "off", "mattress": "off", "desk": "off",
         "dresser": "off", "fan": "off", "screen": "off"}


def framing():
    recs = view(SPEC)
    cv = Canvas("x", "y", -6, 112, -5, 58, 7.6, vdown=True)
    cv.shell()
    fig = compose(cv, recs, MODES, "loft_frame",
                  "Loft framing plan, bed wall at the top, window wall at the left",
                  title="Loft framing plan",
                  start_off=("off-l-finish",))
    j0, j1 = m("deck_joist[0]"), m("deck_joist[1]")
    # --- dims
    cv.dim_h(0, 107, "top", 1, "107")
    cv.dim_h(float(j0.x[0]), float(j1.x[0]), "top", 0, "12 o.c.")
    cv.dim_v(0, float(m("beam_wrap_face").y[1]), "right", 0,
             fr(float(m("beam_wrap_face").y[1])))
    cv.dim_v(float(m("rear_ledger").y[1]), float(m("beam").y[0]), "left", 0,
             f"{fr(DER['deck_joist_span'])} span")
    cv.dim_v(0, float(m("side_ledger").y[1]), "left", 1, fr(float(m("side_ledger").y[1])))
    # --- labels
    cv.text(52, 0.8, "2×4 rear ledger — lags into every stud", "sm")
    cv.text(52, 20, f"2×4 joists @ 12 o.c. · {len(ids('deck_joist'))} joists", "sm")
    cv.text(52, 49.2, f"{BEAMSTOCK} upstand beam — {VALS['beam_span']} c/c bearings", "sm")
    cv.text(52, 44, "2×4 blocking on edge at the beam", "sm")
    cv.text(6, 26, "2×4 side ledger", "sm", rot=-90)
    cv.text(105.6, 26, "2×4 rim", "sm", rot=-90)
    cv.text(52, 4.4, "boxed ledge over", "sm")
    fig.svg = cv.svg("Loft framing plan, bed wall at the top")
    return fig


FIGURES = [("loft_frame", framing)]
CAPTION = ("Joists hang off the rear ledger and off the beam's inside face — LUS24s both ends; "
           "they cannot land on a beam that shares their bottom. Nothing bears in the field. "
           "<b>Joist 0 runs on past the beam face to y 50</b>, sistered to the ledger, and the beam "
           "is notched over the pair; sheet 10 is that joint. Two things follow: the ledger wants a "
           "stud within 6 of y 50, and the deck ply must be glued and screwed onto the ledger, "
           "because that diaphragm is what stops it rolling. Switch <b>Finish</b> on to lay the deck "
           "ply back down.")
