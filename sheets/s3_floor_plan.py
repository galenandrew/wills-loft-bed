"""Sheet 3 — Floor plan. Bed wall up, window wall left, seen from above."""
from drawings.model import (DER, MAT, MAT_Y0, MAT_Y1, RX, RY, Y_FIN, fr, m, ST, d)
from .canvas import Canvas
from .geometry import ViewSpec, view
from .sheet import compose

NUMBER, TITLE, PAGE = "3", "Floor plan", "overview"

SPEC = ViewSpec("plan", direction=(0, 0, -1), up=(0, 1, 0), mirror=True)

MODES = {"fan": "outline"}


def plan():
    recs = view(SPEC)
    cv = Canvas("x", "y", -6, RX + 6, -6, RY + 6, 4.3, vdown=True)
    cv.shell()
    fig = compose(cv, recs, MODES, "plan",
                  "Floor plan seen from above, bed wall at the top, window wall at the left",
                  title="Floor plan")
    # --- room and the depth chain down the right-hand side
    cv.dim_h(0, RX, "top", 1, f"{fr(RX)} room")
    cv.dim_h(0, 107, "top", 0, "107 deck")
    cv.dim_h(107, RX, "top", 0, "24 stair")
    cv.dim_v(0, RY, "left", 1, f"{fr(RY)} room")
    dr, door = m("dresser").y, d["room"]["door"]
    cv.dim_chain([0, Y_FIN, float(dr[0]), float(dr[1]), float(door["y"][0]), float(door["y"][1]), RY],
                 "right", 0,
                 ["stair", "gap", "dresser", None, f"{fr(float(door['width']))} door", None])
    cv.dim_v(0, float(m("beam_wrap_face").y[1]), "left", 0, fr(float(m("beam_wrap_face").y[1])))
    # --- labels
    cv.text(52, 26, "LOFT DECK over", "")
    cv.text(52, 31, f"twin mattress {MAT['size'][0]} × {MAT['size'][1]}", "sm")
    cv.text(52, 4, "boxed ledge", "sm")
    cv.text(119, 10, "LANDING", "")
    cv.text(119, 15, f"{fr(LAND_W)} × {fr(float(m('lnd_ply').y[1]))}", "sm")
    cv.text(119, 50, f"{ST.n_treads} treads @ {fr(ST.run)}", "sm")
    cv.text(104.6, 30, "half wall", "sm", rot=-90)
    cv.text(12, 60, "desk", "sm")
    cv.text(123, 158, "dresser", "sm", rot=-90)
    fig.svg = cv.svg("Floor plan, bed wall at the top, window wall at the left")
    return fig


LAND_W = 24.0

FIGURES = [("plan", plan)]
CAPTION = ("Facing the bed wall: window and desk on your left, stairs and the door on your "
           f"right. The stair's finished nosing reaches {fr(Y_FIN)} from the bed wall, leaving "
           f"{fr(float(m('dresser').y[0]) - Y_FIN)} to the dresser. Switch <b>Finish</b> off to drop the deck "
           "and landing plywood and read the framing underneath.")
