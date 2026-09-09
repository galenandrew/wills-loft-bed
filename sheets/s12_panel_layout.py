"""Sheet 12 — The half wall's loft face: two boards, one seam, one sawn opening."""
from drawings.model import CEILING, JAMB_Y, CEIL, fr, m
from .canvas import Canvas
from .geometry import ViewSpec, projector, view
from .render import only
from .sheet import compose

NUMBER, TITLE, PAGE = "12", "Half wall — loft face panel layout", "halfwall"

# Cut just behind the face, looking at it: only what is beyond x survives, so the
# loft never gets drawn over the panel it hides.
CUT_X = 102.24
SPEC = ViewSpec("hw_face", direction=(1, 0, 0), cut=("x", CUT_X))

MODES = {"framing": "outline", "stair": "off", "loft": "off"}


def face():
    recs = only(view(SPEC), components=("half_wall", "nook"))
    cv = Canvas("y", "z", -4, 56, -4, 58, 9.4, proj=projector(SPEC))
    cv.shell(ceiling=False)
    fig = compose(cv, recs, MODES, "hw_face",
                  "The half wall's loft face seen square on",
                  title="Loft face — panel layout", spec=SPEC,
                  electrical=["sw_half_wall", "nk_light"])
    a, b = m("hw_sheath_loft_a"), m("hw_sheath_loft_b")
    hd = m("hw_sheath_loft_head")
    cv.dim_h(*a.y, "bottom", 0, f"{fr(a.size('y'))} stile")
    cv.dim_h(float(hd.y[0]), float(b.y[1]), "bottom", 0,
             f"{fr(float(b.y[1]) - float(hd.y[0]))} one board, opening sawn out")
    cv.dim_h(*JAMB_Y, "top", 0, f"{fr(JAMB_Y[1] - JAMB_Y[0])} finished opening")
    cv.dim_v(0, float(a.z[1]), "left", 0, f"{fr(a.size('z'))} tall")
    cv.dim_v(0, CEIL, "right", 0, f"{fr(CEIL)} opening")
    cv.text(2.1, 30, "stile", "sm", rot=-90)
    cv.text(30, 48, "head runs unbroken round the opening", "sm")
    cv.text(25, 20, "NOOK OPENING", "")
    fig.svg = cv.svg("The half wall's loft face, seen square on")
    return fig


FIGURES = [("hw_face", face)]
CAPTION = ("The face a person walks past, and the one panel layout worth drawing. It is "
           f"<b>two boards</b>: a {fr(m('hw_sheath_loft_a').size('y'))} stile in the bed-wall corner, then one board with the opening "
           "sawn out of it, running unbroken round the head and out to the corner. One seam, on "
           f"y {fr(JAMB_Y[0])} — the same line as the jamb below it. Two boards and not one only because "
           "neither dimension fits a 48 sheet; a 5×5 panel would make it one. The lining behind "
           "is recessed, so the face laps its ends and no end grain shows. The switch box lands "
           "in this board, not in a stud — behind the head panel there is open cavity, so it is "
           "an old-work box clamped to the ½.")
