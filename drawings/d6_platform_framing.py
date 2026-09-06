"""Drawing 6 — Platform framing plan. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "6", "Platform framing plan"

def d6():
    v = View(-3, 110, -3, 57, 5.5, ml=80, mr=60, mt=40, mb=40, vdown=True)
    v.rect(-3, 110, -3, 0, "wall"); v.rect(-3, 0, 0, 53, "wall")
    v.rect(m("hw_bottom_plate_a").x[0], m("hw_bottom_plate_a").x[1], 0, m("hw_top_plate_1").y[1], "hid")
    for k in ids("deck_joist"): R(v, m(k), "x", "y", "lum2")
    for k in ids("ledger_blocking") + ["ledger_blocking_last"]: R(v, m(k), "x", "y", "blk")
    for k in ("rear_ledger", "side_ledger", "deck_rim", "beam"): R(v, m(k), "x", "y", "lum")
    R(v, m("beam_wrap_face"), "x", "y", "fin"); v.line(0, 8, 107, 8, "ghostl")
    v.text(50, 0.75, "2×6 rear ledger — lags into every stud", "labs", "middle", dy=4)
    v.text(6, 24, f"2×10 side ledger, {fr(m('side_ledger').y[1])} out", "labs", "middle", rot=-90)
    v.text(50, 24, "2×4 joists @ 12 o.c. · 9 joists · 45½ span", "lab", "middle", dy=4)
    v.text(50, 2.25, "", "labs")
    v.text(50, 48.5, "doubled 2×10 + ¾ wrap — 102 clear span", "lab", "middle", dy=4)
    v.text(105.5, 24, "2×4 rim at 104¾–106¼", "labs", "middle", rot=-90)
    v.text(75, 10.5, "boxed ledge above (8)", "labs", "middle", dy=4)
    v.text(24, 15, "front rail notched 1½ × 5 over this ledger — ledge runs flush to the window wall", "labs", "start", dy=4)
    v.text(21, 4.5, "2×4 blocking at the ledger — carries the ply's rear edge", "labs", "start", dy=4)
    v.text(54, 55.4, f"¾ ply deck: {fr(DER['deck_ply'][0])} × {fr(DER['deck_ply'][1])} — seams on joist centres, glued & screwed", "labs", "middle", dy=4)
    v.dim_h(0, 107, -4, "107"); v.dim_h(m("deck_joist[0]").x[0], m("deck_joist[1]").x[0], 40, "12 o.c.")
    v.dim_v(109, 0, m("beam_wrap_face").y[1], fr(m("beam_wrap_face").y[1]), left=False); v.dim_v(-4, 0, m("side_ledger").y[1], fr(m("side_ledger").y[1]))
    v.dim_v(80, m("rear_ledger").y[1], m("beam").y[0], f"{fr(DER['deck_joist_span'])} span", left=False)
    return v.svg("Platform framing plan, bed wall at the top")

FIGURES = [("d6", d6)]
CAPTION = "Joists hang off the rear ledger and off the beam's inside face (LUS24 hangers, both ends — they cannot 'land on' a beam that shares their bottom). Nothing bears in the field; the platform is carried by the two walls and the half-wall. Lay the joists out so plywood seams land on centres. <b>Rev Z:</b> the side ledger runs 50 out, not 48, so its face backs the beam's full 3 width — 13⅞ sq in of end bearing per 2×10 ply. It stops at 50 rather than the 50¾ once suggested: the ¾ poplar wrap occupies 50→50¾ across the whole 107 and returns over the ledger's end. The hanger there is still to be chosen — a concealed-flange type, since an outer flange would hang past the ledger end with nothing behind it, the same reason the landing rim uses HUC28s. <b>Rev AB:</b> the boxed ledge now runs flush to the window wall. Its front rail is one 107 board notched 1½ (x) × 5 (z) out of its bottom left corner to clear this ledger, whose top is at 63; the 2¼ tongue left above the notch lands on the ledger top and is screwed down. The lid is above 63 and needs no notch — it simply runs to x 0."
