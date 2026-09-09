"""Sheet 6 — Tread and riser joint, at large scale."""
from drawings.model import NOSE, RISER_T, ST, T, fr, riser_y, tread_y_board
from .canvas import Canvas
from .geometry import ViewSpec, view
from .sheet import compose
from .s4_stair_section import SPEC

NUMBER, TITLE, PAGE = "6", "Tread & riser detail", "stairs"

MODES = {"mattress": "off", "desk": "off", "dresser": "off", "fan": "off",
         "loft": "off", "ledge": "off", "half_wall": "off", "nook": "off"}

STEP = 3          # the step drawn — any of them; they are identical


def detail():
    recs = view(SPEC)
    y0, y1 = tread_y_board(STEP)
    z = ST.riser_z[STEP]
    # framed on the joint, not on the step: the corner where riser, tread and
    # stringer meet is the whole point of the sheet.
    cv = Canvas("y", "z", y0 - 3, y1 + 4, z - ST.R - 4, z + 4, 26.0)
    cv.reserve(right=150, top=26)
    fig = compose(cv, recs, MODES, "tread_detail",
                  f"Tread and riser joint at step {STEP}, drawn large",
                  title=f"Tread & riser joint — step {STEP} of {ST.n_treads}", electrical=False)
    # --- dims
    cv.dim_h(*tread_y_board(STEP), "bottom", 0, f"{fr(y1 - y0)} board")
    cv.dim_h(*ST.tread_y(STEP), "bottom", 1, f"{fr(ST.run)} going")
    cv.dim_v(z - T, z, "left", 0, f"{fr(T)}")
    cv.dim_v(ST.riser_z[STEP - 1], z, "left", 1, f"{fr(ST.R)} rise")
    cv.dim_h(riser_y(STEP)[0], riser_y(STEP)[1], "top", 0, fr(RISER_T))
    # --- labels
    cv.text(y0 + 2.5, z + 1.6, "tread — ¾ ply, taped edge, painted", "sm", anchor="start",
            of="stair")
    cv.text(y1 + 1.2, z - ST.R / 2, "riser, in front of the plumb cut", "sm", of="stair",
            anchor="start")
    cv.text(y0 - 1.4, z - ST.R + 1.4, "stringer", "sm", anchor="start", of="stringer_b")
    cv.text(y1 + 1.2, z - T - 1.2, f"{fr(NOSE)} nose past the riser face", "sm", anchor="start", of="stair")
    fig.svg = cv.svg(f"Tread and riser joint at step {STEP}")
    return fig


FIGURES = [("tread_detail", detail)]
CAPTION = ("The joint everybody builds from memory and gets wrong. The exposed face of "
           "every plumb notch is its <b>downhill</b> side, so the riser board goes in front "
           "of the cut with its bottom edge on the stringer's horizontal cut for the tread "
           "below; the tread above starts where that riser ends and butts its face. A simple "
           f"butt joint, riser behind the tread, nothing notched — and the nosing-to-nosing "
           f"going stays exactly {fr(ST.run)}.")
