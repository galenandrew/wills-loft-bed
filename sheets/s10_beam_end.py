"""Sheet 10 — The beam's end bearing at the window wall, at large scale.

The joint the whole post-free span rests on, and the one the kernel caught failing
twice: the beam's outer ply once had 0.00 sq in on the side ledger, and slat 0 once
sat on ¾ poplar with no beam under it. Both are fixed; this is what fixed them.
"""
from drawings.model import BEAM_FIN_TOP, DECK, VALS, fr, m
from .canvas import Canvas
from .geometry import ViewSpec, view
from .sheet import compose

NUMBER, TITLE, PAGE = "10", "Beam end — bearing detail", "loft"

CUT_Z = 56.0      # in the notch: below the beam's tongue, through ledger and joist
CUT_Y = 49.0      # through the beam, looking toward the bed wall

# Both are SLAB views: a couple of inches beyond the plane and no further, or the
# whole loft stacks up behind the joint and hides it.
PLAN = ViewSpec("beam_end_plan", direction=(0, 0, -1), up=(0, 1, 0), mirror=True,
                cut=("z", CUT_Z), depth=2.0)
SECT = ViewSpec("beam_end_sec", direction=(0, -1, 0), cut=("y", CUT_Y), depth=1.0)

MODES = {"stair": "off", "half_wall": "off", "nook": "off", "screen": "off",
         "mattress": "off", "desk": "off", "dresser": "off", "fan": "off"}


def plan():
    recs = view(PLAN)
    cv = Canvas("x", "y", -4, 16, 41, 53, 26.0, vdown=True)
    cv.shell()
    cv.reserve(right=110)
    fig = compose(cv, recs, MODES, "beam_end_plan",
                  f"Plan cut at z {fr(CUT_Z)}, in the beam's notch",
                  title=f"Plan cut at z {fr(CUT_Z)} — inside the notch", electrical=False)
    sl, j0, bm = m("side_ledger"), m("deck_joist[0]"), m("beam")
    cv.dim_h(*sl.x, "top", 0, f"{fr(sl.size('x'))} ledger")
    cv.dim_h(float(sl.x[0]), float(bm.x[0]), "top", 1,
             f"{fr(float(bm.x[0]) - float(sl.x[0]))} notch — ledger + joist 0")
    cv.dim_v(float(bm.y[0]), float(bm.y[1]), "right", 0,
             f"{fr(bm.size('y'))} beam over joist 0's tail")
    cv.text(9, 42.4, "beam ends here — the notch is beyond this plane", "sm", of="beam")
    cv.text(0.85, 44, "side ledger", "sm", rot=-90, of="side_ledger")
    cv.text(2.35, 44, "joist 0", "sm", rot=-90, of="deck_joist[0]")
    fig.svg = cv.svg(f"Plan cut at z {fr(CUT_Z)} through the beam's notch")
    return fig


def sect():
    recs = view(SECT)
    cv = Canvas("x", "z", -4, 20, 50, 72, 15.0)
    cv.shell(ceiling=False)
    cv.reserve(right=90)
    fig = compose(cv, recs, MODES, "beam_end_sec",
                  f"Section at y {fr(CUT_Y)}, looking toward the bed wall",
                  title=f"Section at y {fr(CUT_Y)} — the seat", electrical=False)
    sl, bm, tg = m("side_ledger"), m("beam"), m("beam_tongue")
    cv.dim_v(*sl.z, "left", 0, f"{fr(sl.size('z'))} seat")
    cv.dim_v(float(bm.z[0]), BEAM_FIN_TOP, "left", 1, f"{fr(BEAM_FIN_TOP - float(bm.z[0]))} beam + cap")
    cv.dim_h(float(tg.x[0]), float(tg.x[1]), "bottom", 0, f"{fr(tg.size('x'))} bearing")
    cv.dim_v(float(bm.z[0]), DECK, "right", 0, f"deck {fr(DECK)}")
    cv.text(11, float(sl.z[1]) + 4, "beam tongue over the seat", "sm", of="beam")
    cv.text(0.75, 55.5, "ledger", "sm", rot=-90, of="side_ledger")
    cv.text(2.25, 55.5, "joist 0", "sm", rot=-90, of="deck_joist[0]")
    fig.svg = cv.svg(f"Section at y {fr(CUT_Y)} through the beam's seat")
    return fig


FIGURES = [("beam_end_plan", plan), ("beam_end_sec", sect)]
NOTCH_X = float(m("beam").x[0]) - float(m("side_ledger").x[0])   # 3, along the beam
NOTCH_Z = float(m("beam_tongue").z[0]) - float(m("beam").z[0])   # 3½, up its end

CAPTION = (f"The beam is one {VALS['beam_stock']} notched {fr(NOTCH_X)} × {fr(NOTCH_Z)} out of its bottom left corner, so its "
           f"end sits on the 2×4 side ledger <i>and</i> on joist 0 sistered beside it — "
           f"{VALS['beam_seat_area']} sq in of seat, about 115 psi against 425 allowable. A 2×4 ledger cannot "
           "back the beam's end on its own, which is why the joint is a notch and a sistered "
           "joist rather than a butt into a hanger. <b>Field item:</b> the window wall wants a stud "
           "(or added blocking) within about 6 of y {} — the reaction lands 1½–3 off the wall face "
           "and a 3½-deep ledger has a short couple to resist it.").format(fr(float(m("deck_joist_tail").y[1])))
