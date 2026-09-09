"""Sheet 1 — Isometric overview. The one view that says what the thing is."""
from drawings.model import CEILING, DECK, LAND, RX, RY, fr, m, ST
from .canvas import Canvas
from .geometry import ViewSpec, projector, view
from .render import only
from .sheet import compose, frame_from

NUMBER, TITLE, PAGE = "1", "Isometric overview", "overview"

# From the doorway: high on the right wall, looking across the room at the stair,
# the half wall and the bed beyond it. Faces pointing +x, +y and +z are the ones
# you see — the three sides a builder needs to place a member.
SPEC = ViewSpec("iso", direction=(-0.52, -1.0, -0.58), up=(0, 0, 1))

# The fan is left out of this view entirely rather than switched off: it is a 54
# disc floating over the whole drawing, and the clearance question it exists for is
# asked on the front elevation. The furniture starts off and can be switched on.
MODES = {"desk": "outline", "dresser": "outline", "mattress": "flat"}


def iso():
    recs = only(view(SPEC), without=("fan",))
    h0, h1, v0, v1 = frame_from(recs, pad=4)
    cv = Canvas("x", "z", h0, h1, v0, v1, 4.4, proj=projector(SPEC))
    cv.reserve(left=96, right=96, top=30, bottom=20)
    # the floor and the two walls the build stands against, so it is not floating
    cv.poly3([(0, 0, 0), (RX, 0, 0), (RX, RY, 0), (0, RY, 0)], "gridline",
             'fill="#f4f2ed"')
    for a, b in (((0, 0, 0), (0, 0, CEILING)), ((RX, 0, 0), (RX, 0, CEILING)),
                 ((0, 0, CEILING), (RX, 0, CEILING))):
        cv.line3(a, b, "gridline")
    fig = compose(cv, recs, MODES, "iso",
                  "Isometric view of the whole build from the doorway",
                  title="Isometric overview — from the doorway", shade=True, spec=SPEC,
                  start_off=("off-c-desk", "off-c-dresser"))
    # Labels are parked clear of the model and led back to a real point on the
    # member they name — offsets are in view inches, so they hold at any scale.
    cv.tag((16, 49, 84), "SCREEN", -14, 6, anchor="end")
    cv.tag((10, 4, 69), "BOXED LEDGE", -14, -4, anchor="end")
    cv.tag((16, 25, 53.5), "LOFT DECK", -14, -6, anchor="end")
    cv.tag((102.4, 25, 20), "HALF WALL", -16, -16, anchor="end")
    cv.tag((131, 45, 20), "STAIR", 14, -10, anchor="start")
    cv.tag((131, 8, 49.5), "LANDING", 14, 6, anchor="start")
    cv.tag((131, 12, 14), "NOOK", 14, -22, anchor="start")
    fig.svg = cv.svg("Isometric view of the whole build from the doorway")
    return fig


FIGURES = [("iso", iso)]
CAPTION = (f"Everything at once, seen from the door. The deck is at {fr(DECK)}, the landing at "
           f"{fr(LAND)}, and the {ST.n_treads} treads come down toward you along the right wall. "
           "Faces are shaded by which way they point, so a member's orientation reads without a "
           "dimension on it — and there are no dimensions here on purpose, because nothing in an "
           "isometric is to scale along the page. Switch a component off to see what it hides.")
