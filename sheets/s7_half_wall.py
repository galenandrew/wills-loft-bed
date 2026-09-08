"""Sheet 7 — Half wall framing, with the loft edge cut and the stair beyond."""
from drawings.model import CEILING, DECK, DER, NOOK_Y, ST, CEIL, fr, m
from .canvas import Canvas
from .geometry import ViewSpec, view
from .sheet import compose

NUMBER, TITLE, PAGE = "7", "Half wall — framing elevation", "halfwall"

# Cut in the stud cavity, behind the loft-face sheathing: the studs, header and
# plates read as framing rather than being hidden behind a full-height panel, and
# the loft's own edge members — beam, rim, ledgers, deck — are cut with them.
CUT_X = 103.0
SPEC = ViewSpec("hw_frame", direction=(1, 0, 0), cut=("x", CUT_X), near=True)

MODES = {"stair": "outline", "mattress": "off", "desk": "off", "dresser": "off",
         "fan": "off"}


def elevation():
    recs = view(SPEC)
    cv = Canvas("y", "z", -5, 78, -4, CEILING + 4, 6.2)
    cv.shell()
    fig = compose(cv, recs, MODES, "hw_frame",
                  "Half-wall framing elevation, bed wall on the left, stair beyond",
                  title="Half-wall framing, with the loft edge cut")
    hd, tp = m("hw_header"), m("hw_top_plate_2")
    # --- dims
    cv.dim_h(*NOOK_Y, "bottom", 0, f"{fr(NOOK_Y[1] - NOOK_Y[0])} rough opening")
    cv.dim_h(0, float(m("hw_top_plate_1").y[1]), "bottom", 1,
             f"{fr(float(m('hw_top_plate_1').y[1]))} wall")
    cv.dim_v(0, float(hd.z[0]), "left", 0, f"{fr(float(hd.z[0]))} to header")
    cv.dim_v(*hd.z, "left", 1, f"{fr(hd.size('z'))} header")
    cv.dim_v(float(tp.z[1]), DECK, "right", 0, f"{fr(DECK - float(tp.z[1]))} to deck")
    cv.dim_v(0, float(tp.z[1]), "right", 1, f"{fr(float(tp.z[1]))} top plate")
    # --- labels
    cv.text(25, float(hd.z[0]) + 4.6, "2×10 sandwich header", "sm")
    cv.text(25, float(tp.z[1]) + 2.4, "two 2×4 top plates", "sm")
    cv.text(25, CEIL - 4, "NOOK OPENING", "")
    cv.text(60, 24, "stair beyond (dashed)", "sm")
    cv.text(2.5, DECK + 12, "loft edge, cut on this plane", "sm", anchor="start")
    fig.svg = cv.svg("Half-wall framing elevation with the loft edge cut")
    return fig


FIGURES = [("hw_frame", elevation)]
CAPTION = (f"Cut at x {fr(CUT_X)} — inside the stud cavity, so the loft face sheathing is in front of "
           "the plane and draws dashed, and the framing reads. The opening removes both faces: "
           "what is left is two posts and a sandwich header — a portal frame, not a shear wall. "
           "The beam's reaction bypasses it onto the far stud pack, and the landing box ties the "
           "top plate across to the right wall. The loft's own edge — beam, rim, ledger, deck — is "
           "cut on the same plane at the top left. The stair beyond is dashed; switch it off if it "
           "is in the way.")
