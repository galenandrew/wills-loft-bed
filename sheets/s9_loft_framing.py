"""Sheet 9 — Loft framing plan, seen from above."""
from drawings.model import DER, ids, fr, m, VALS, BEAMSTOCK
from .canvas import Canvas
from .geometry import ViewSpec, projector, view
from .sheet import compose

NUMBER, TITLE, PAGE = "9", "Loft — framing plan", "loft"

SPEC = ViewSpec("plan", direction=(0, 0, -1), up=(0, 1, 0), mirror=True)

MODES = {"stair": "off", "nook": "off", "mattress": "off", "desk": "off",
         "dresser": "off", "fan": "off", "screen": "off"}


def framing():
    recs = view(SPEC)
    cv = Canvas("x", "y", -6, 112, -5, 58, 7.6, vdown=True, proj=projector(SPEC))
    cv.shell()
    fig = compose(cv, recs, MODES, "loft_frame",
                  "Loft framing plan, bed wall at the top, window wall at the left",
                  title="Loft framing plan",
                  start_off=("off-l-finish",), spec=SPEC)
    j0, j1 = m("deck_joist[0]"), m("deck_joist[1]")
    # --- dims
    cv.dim_h(0, float(m("ledge_lid").x[1]), "top", 1, fr(float(m("ledge_lid").x[1])))
    cv.dim_h(float(j0.x[0]), float(j1.x[0]), "top", 0, f"{VALS['joist_oc']} o.c.")
    cv.dim_v(0, float(m("beam_wrap_face").y[1]), "right", 0,
             fr(float(m("beam_wrap_face").y[1])))
    cv.dim_v(float(m("rear_ledger").y[1]), float(m("beam").y[0]), "left", 0,
             f"{fr(DER['deck_joist_span'])} span")
    # --- labels
    cv.text(52, 0.8, "2×4 rear ledger — lags into every stud", "sm", of="rear_ledger")
    cv.text(52, 20, f"2×4 joists @ {VALS['joist_oc']} o.c. · {len(ids('deck_joist'))} joists", "sm",
            of="deck_joist[0]")
    cv.text(52, 49.2, f"{BEAMSTOCK} upstand beam — {VALS['beam_span']} c/c bearings", "sm", of="beam")
    cv.text(52, 44, "2×4 blocking on edge at the beam", "sm", of="deck_blocking[0]")
    cv.text(6, 26, "2×4 side ledger", "sm", rot=-90, of="side_ledger")
    cv.text(105.6, 26, "2×4 rim", "sm", rot=-90, of="deck_rim")
    cv.text(52, 4.4, "boxed ledge over", "sm", of="ledge")
    fig.svg = cv.svg("Loft framing plan, bed wall at the top")
    return fig


FIGURES = [("loft_frame", framing)]
CAPTION = ("Joists hang off the rear ledger and off the beam's inside face — LUS24s both ends; "
           "they cannot land on a beam that shares their bottom. Nothing bears in the field. "
           f"<b>Joist 0 runs on past the beam face to y {fr(float(m('deck_joist_tail').y[1]))}</b>, sistered to the ledger, and the beam "
           "is notched over the pair; sheet 10 is that joint. Two things follow: the ledger wants a "
           f"stud within 6 of y {fr(float(m('deck_joist_tail').y[1]))}, and the deck ply must be glued and screwed onto the ledger, "
           "because that diaphragm is what stops it rolling. Switch <b>Finish</b> on to lay the deck "
           "ply back down.")
