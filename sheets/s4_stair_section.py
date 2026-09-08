"""Sheet 4 — Stair, landing and nook section, cut through stringer B."""
from drawings.model import (CEILING, DER, LAND, ST, T, Y_FIN, CEIL, JAMB_Y, fr, m,
                            tread_y_board)
from .canvas import Canvas
from .geometry import ViewSpec, view
from .sheet import compose

NUMBER, TITLE, PAGE = "4", "Stair · landing · nook — section", "stairs"

CUT_X = 118.6            # through stringer B (x 117⅞ → 119⅜)
SPEC = ViewSpec("stair_sec", direction=(1, 0, 0), cut=("x", CUT_X), near=True)

# The half wall stands in front of this cut and ghosts itself. The loft is in front
# of it too and is a lot of lines, so it starts switched off.
MODES = {"mattress": "off", "desk": "off", "dresser": "off", "fan": "off"}


def section():
    recs = view(SPEC)
    cv = Canvas("y", "z", -5, 78, -4, CEILING + 4, 6.2)
    cv.shell()
    fig = compose(cv, recs, MODES, "stair_sec",
                  "Section through stringer B, bed wall on the left",
                  title="Section through stringer B",
                  start_off=("off-c-loft",))
    # --- dims
    cv.dim_h(0, ST.y_top, "bottom", 0, fr(ST.y_top))
    cv.dim_h(ST.y_top, ST.y_riser_top, "bottom", 0, f"{fr(ST.top_run)} top run")
    cv.dim_h(ST.y_riser_top, ST.y_bottom, "bottom", 0,
             f"{ST.n_treads} @ {fr(ST.run)}")
    cv.dim_h(0, Y_FIN, "bottom", 1, f"{fr(Y_FIN)} to the bottom nosing")
    cv.dim_v(0, LAND, "left", 0, f"{fr(LAND)} landing")
    cv.dim_v(LAND, CEILING, "left", 1, f"{fr(DER['landing_headroom'])} headroom")
    cv.dim_v(0, CEIL, "right", 0, f"{fr(CEIL)} nook")
    # --- labels
    cv.text(ST.y_top - 4, LAND + 5, "LANDING", "")
    cv.text(14, 62, f"{ST.n_treads + 1} risers @ {fr(ST.R)}, then {fr(ST.R_top)} onto the deck", "sm",
            anchor="start")
    cv.text(11, CEIL / 2, "NOOK", "")
    cv.text(60, 30, "stringer B", "sm", rot=-53)
    cv.text(ST.y_bottom + 3, 3.5, "kicker", "sm", anchor="start")
    fig.svg = cv.svg("Section through stringer B, bed wall on the left")
    return fig


FIGURES = [("stair_sec", section)]
CAPTION = (f"Cut through stringer B. Each stringer runs {fr(ST.top_run)} on under the landing; its top "
           f"plumb cut at y {fr(ST.y_top)} is {fr(ST.plumb_cut()[1] - ST.plumb_cut()[0])} tall, close to the 2×8 rim it bears on. "
           f"Stringers are dropped {fr(T)} for the ¾ plywood treads. The {ST.n_treads + 1} stair risers are {fr(ST.R)}; "
           f"the last step onto the deck is {fr(ST.R_top)}, because it is the framing stack over the nook "
           f"header rather than a stair riser — do not step {fr(ST.R)} off {ST.n_risers} times. "
           "The half wall is in front of this plane and draws dashed. Switch the "
           "<b>Loft</b> on to see where the deck lands relative to the landing.")
