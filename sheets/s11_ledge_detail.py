"""Sheet 11 — The boxed ledge, at large scale."""
from drawings.model import DECK, MAT, fr, m
from .canvas import Canvas
from .geometry import projector, view
from .sheet import compose
from .s8_loft_section import SPEC

NUMBER, TITLE, PAGE = "11", "Boxed ledge — detail", "loft"

MODES = {"stair": "off", "half_wall": "off", "nook": "off", "screen": "off",
         "dresser": "off", "fan": "off", "desk": "off", "mattress": "flat"}


def detail():
    recs = view(SPEC)
    lid, rail = m("ledge_lid"), m("ledge_front_rail")
    cv = Canvas("y", "z", -3, 16, 50, 74, 17.0, proj=projector(SPEC))
    cv.shell(ceiling=False)
    fig = compose(cv, recs, MODES, "ledge_detail",
                  "Boxed ledge in section, bed wall on the left",
                  title="Boxed ledge — section at the same cut as sheet 8", spec=SPEC,
                  electrical=["ledge_outlet_window"],
                  electrical_labels=False)
    cv.dim_h(0, float(lid.y[1]), "bottom", 0, f"{fr(float(lid.y[1]))} lid")
    cv.dim_h(float(m("rear_ledger").y[1]), float(rail.y[0]), "bottom", 1,
             f"{fr(float(rail.y[0]) - float(m('rear_ledger').y[1]))} well")
    cv.dim_v(DECK, float(lid.z[1]), "left", 0, f"{fr(float(lid.z[1]) - DECK)} high")
    cv.dim_v(DECK, DECK + float(MAT["thickness"]), "right", 0, "mattress")
    cv.text(6.5, float(lid.z[1]) + 1.4, "¾ ply lid", "sm", anchor="start", of="ledge_lid")
    cv.text(8.2, float(m("ledge_cleat_rail").z[0]) - 1.8, "2×2 cleats carry the lid", "sm", of="ledge_cleat",
            anchor="start")
    cv.note(11.5, 66.5, "front rail", to=(7.6, 64), cls="sm", anchor="start",
            of="ledge_front_rail")
    # both outlets are at the same y and z, so this section shows them on top of
    # each other — the plan is where their x positions read
    cv.text(1.2, 72.2, "outlets — one at each end of the lid", "sm", anchor="start",
            of="ledge_lid")
    fig.svg = cv.svg("Boxed ledge section, bed wall on the left")
    return fig


FIGURES = [("ledge_detail", detail)]
CAPTION = (f"The ledge is a box, not a shelf: a ¾ ply lid on 2×2 cleats, a ply front rail, and the "
           f"deck ply as its floor. The lid stands {fr(float(m('ledge_lid').z[1]) - DECK - float(MAT['thickness']))} proud of the mattress — the curb on the "
           "bed-wall side — and runs the full 107, over the stair face at the deck end. The two "
           "outlets are flush in the lid, one at each end; their boxes hang into the well, clear "
           "of both 2×2 cleats and of every strut. <b>Wire them before the lid goes down</b> — "
           "afterwards the well is a closed box.")
