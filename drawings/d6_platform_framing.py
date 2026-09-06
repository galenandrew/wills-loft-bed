"""Drawing 6 — Platform framing plan. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "6", "Platform framing plan"

def d6():
    v = View(-3, 110, -3, 57, 5.5, ml=80, mr=60, mt=40, mb=40, vdown=True)
    v.rect(-3, 110, -3, 0, "wall"); v.rect(-3, 0, 0, 53, "wall")
    v.rect(m("hw_bottom_plate_a").x[0], m("hw_bottom_plate_a").x[1], 0, m("hw_top_plate_1").y[1], "hid")
    for k in ids("deck_joist"): R(v, m(k), "x", "y", "lum2")
    for k in ids("ledger_blocking") + ["ledger_blocking_last"]: R(v, m(k), "x", "y", "blk")
    for k in ("rear_ledger", "side_ledger", "deck_rim", "beam", "beam_tongue", "deck_joist_tail"): R(v, m(k), "x", "y", "lum")
    R(v, m("beam_wrap_face"), "x", "y", "fin"); v.line(0, 8, 107, 8, "ghostl")
    v.text(50, 0.75, "2×6 rear ledger — lags into every stud", "labs", "middle", dy=4)
    v.text(6, 24, f"2×4 side ledger, {fr(m('side_ledger').y[1])} out — below the deck", "labs", "middle", rot=-90)
    v.text(50, 24, f"2×4 joists @ 12 o.c. · {len(ids('deck_joist'))} joists · {fr(DER['deck_joist_span'])} span", "lab", "middle", dy=4)
    v.text(50, 2.25, "", "labs")
    v.text(50, 48.5, f"{BEAMSTOCK} + ¾ wrap — {VALS['beam_span']} c/c bearings", "lab", "middle", dy=4)
    v.text(105.5, 24, "2×4 rim at 104¾–106¼", "labs", "middle", rot=-90)
    v.text(75, 10.5, f"boxed ledge above (8 wide × {fr(m('ledge_lid').z[1]-DECK)} high)", "labs", "middle", dy=4)
    v.text(20, 15, "beam notched 3 × 3½ over the ledger and joist 0 — its end bears on both", "labs", "start", dy=4)
    v.text(21, 4.5, "2×4 blocking at the ledger — carries the ply's rear edge", "labs", "start", dy=4)
    v.text(54, 55.4, f"¾ ply deck: {fr(DER['deck_ply'][0])} × {fr(DER['deck_ply'][1])} — seams on joist centres, glued & screwed", "labs", "middle", dy=4)
    v.dim_h(0, 107, -4, "107"); v.dim_h(m("deck_joist[0]").x[0], m("deck_joist[1]").x[0], 40, "12 o.c.")
    v.dim_v(109, 0, m("beam_wrap_face").y[1], fr(m("beam_wrap_face").y[1]), left=False); v.dim_v(-4, 0, m("side_ledger").y[1], fr(m("side_ledger").y[1]))
    v.dim_v(80, m("rear_ledger").y[1], m("beam").y[0], f"{fr(DER['deck_joist_span'])} span", left=False)
    return v.svg("Platform framing plan, bed wall at the top")

FIGURES = [("d6", d6)]
CAPTION = f"Joists hang off the rear ledger and off the beam's inside face (LUS24 hangers, both ends — they cannot 'land on' a beam that shares their bottom). Nothing bears in the field; the platform is carried by the two walls and the half-wall. Lay the joists out so plywood seams land on centres. <b>Rev AG:</b> the window end is a different joint. The side ledger is a <b>2×4 at deck level</b>, so nothing of it shows above the ply and the ledge's front rail needs no notch — but a 2×4 cannot back the beam's end, so the beam does not butt it. <b>Joist 0 runs on past the beam face to y 50</b>, sistered to the ledger over its whole {fr(m('deck_joist_tail').y[1]-m('deck_joist[0]').y[0])}, and the beam is <b>notched 3 × 3½ out of its bottom left corner and bears on the pair</b> — 3 × 1¾ = 5.25 sq in, ~115 psi against 425 allowable, where before it was end grain against a hanger nobody had chosen. The other eight joists stop at the beam face on LUS24s. Two things follow for the builder: the ledger's screws want a <b>stud within 6 of y 50</b> (or blocking added — the reaction lands 1½–3 off the wall face and a 3½-deep ledger has a short couple to resist it), and the <b>deck ply must be glued and screwed down onto the ledger</b>, because that diaphragm is what stops it rolling."
