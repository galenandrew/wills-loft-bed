"""Drawing 3 — Section through the platform edge. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "3", "Section through the platform edge"

def d3():
    xc = 55
    v = View(-4, 62, 0, CEILING + 1, 6, ml=90, mr=110, mt=28, mb=44)
    v.rect(-4, 0, 0, CEILING, "wall"); v.line(-4, CEILING, 60, CEILING, "floor"); v.line(-4, 0, 60, 0, "floor")
    R(v, m("rear_ledger"), "y", "z", "lum", HATCH)
    R(v, m("deck_joist[4]"), "y", "z", "lum2")
    R(v, m("deck_blocking[4]"), "y", "z", "lum", HATCH)   # x 51→61½ contains the cut
    R(v, m("deck_seam_blocking[4]"), "y", "z", "lum", HATCH)  # same bay, so also cut
    _sy = (m("deck_seam_blocking[4]").y[0] + m("deck_seam_blocking[4]").y[1]) / 2
    v.line(_sy, DECK - T, _sy, DECK, "ink")   # the ply seam this block backs
    R(v, m("deck_ply"), "y", "z", "sheet", HATCH)
    R(v, m("loft_ceiling"), "y", "z", "fin", HATCH)
    for k in ("ledge_cleat", "ledge_cleat_rail"): R(v, m(k), "y", "z", "lum", HATCH)
    R(v, m("ledge_strut[1]"), "y", "z", "lum2")
    R(v, m("ledge_rail_splice"), "y", "z", "sheet", HATCH)  # x 48⅛–58⅛ contains the cut
    R(v, m("ledge_front_rail"), "y", "z", "fin", HATCH); R(v, m("ledge_lid"), "y", "z", "fin", HATCH)
    v.rect(8, 8 + MAT["size"][0], DECK, DECK + MAT["thickness"], "matt")
    R(v, m("beam"), "y", "z", "lum", HATCH)
    for w in ("beam_wrap_face", "beam_wrap_inner", "beam_wrap_top"): R(v, m(w), "y", "z", "fin", HATCH)
    R(v, m("slat[11]"), "y", "z", "lum2"); R(v, m("screen_top_plate"), "y", "z", "lum", HATCH)
    dk = m("desk"); v.rect(*dk.y, *dk.z, "dashfill")
    fan = m("fan"); v.line(fan.y[0], fan.z[0], 60, fan.z[0], "redline"); v.text(fan.y[0] + 0.5, fan.z[0], f"fan {fr(fan.z[0])}", "labb", "start", dy=-4)
    # labels
    v.text(-1.2, 30, "bed wall", "labs", "middle", rot=-90)
    v.text(4, 71, "boxed ledge", "lab", "start"); v.text(4, 69, f"top {fr(m('ledge_lid').z[1])} — {fr(m('ledge_lid').z[1]-DECK-MAT['thickness'])} proud of the mattress", "labs", "start")
    v.text(4, 67.3, f"well {fr(m('ledge_front_rail').y[0]-m('rear_ledger').y[1])} × {fr(m('ledge_front_rail').z[1]-DECK)} — {fr(m('ledge_rail_splice').y[0]-m('rear_ledger').y[1])} at this station, the rail splice is behind the cut", "labs", "start")
    v.text(2, 52.2, "2×4 ledger, top flush with the joists — lags into every stud", "labs", "start")
    v.text(4, 65.6, "2×2 cleat — the lid's back bearing", "labs", "start")
    v.text(4, 63.9, "2×2 cleat on the deck — the rail's foot", "labs", "start")
    v.text(4, 62.2, "3 × 2×2 struts under the lid (one shown, beyond) — hold the rail on 7¼", "labs", "start")
    v.text(2, 47.4, f"2×4 joists @ 12 o.c. beyond · {fr(DER['deck_joist_span'])} span · ¾ ply glued & screwed", "labs", "start")
    v.text(46.5, 50, "2×4 blocking — ON EDGE at the beam, FLAT under the seam", "labs", "end")
    v.text(2, 44.8, f"{fr(m('loft_ceiling').size('z'))} finished ceiling below, x 0→{fr(m('loft_ceiling').x[1])} — screwed up into the joists, ledgers and beam", "labs", "start")
    v.text(27, 61, f"{MAT['size'][0]} mattress in a {fr(BAY)} bay, finished", "labs", "middle", dy=4)
    v.text(49.1, 60, BEAMSTOCK, "lab", "middle", rot=-90); v.text(53.5, 28, "¾ paint-grade ply wrap, filled butt joint", "labs", "start", rot=-90)
    v.text(56, 66, f"2×2 slats beyond, centred on the beam — {fr(m('beam_wrap_face').y[1]-m('slat[0]').y[1])} back from each face", "labs", "start", rot=-90)
    v.text(43, 96.5, "paint-grade 2×4 top plate, flat", "labs", "end", dy=-3)
    v.text(27, 15, f"desk {fr(dk.y[1])} deep × {fr(dk.z[1])} high — projects {fr(dk.y[1]-m('beam_wrap_face').y[1])} past the beam", "labs", "middle")
    # dims
    v.dim_h(0, 8, 74, "8"); v.dim_h(8, m("beam_wrap_inner").y[0], 74, f"{fr(BAY)} bay"); v.dim_h(m("beam_wrap_inner").y[0], m("beam_wrap_face").y[1], 74, f"{fr(m('beam_wrap_face').y[1]-m('beam_wrap_inner').y[0])} beam")
    v.dim_h(0, m("beam_wrap_face").y[1], 42.5, f"{fr(m('beam_wrap_face').y[1])} platform depth ({fr(m('ledge_front_rail').y[1])} + {fr(BAY)} + {fr(m('beam_wrap_inner').size('y'))} + {fr(m('beam').size('y'))} + {fr(m('beam_wrap_face').size('y'))})", above=False)
    v.dim_v(-5, 0, DECK, f"{fr(DECK)} deck"); v.dim_v(-5, DECK, m("ledge_lid").z[1], fr(m("ledge_lid").z[1] - DECK), left=True)
    v.dim_v(20, 0, m("loft_ceiling").z[0], f"{fr(DER['clear_under_joists'])} clear")
    v.dim_v(50.75, 0, m("loft_ceiling").z[0], f"{fr(DER['clear_under_beam'])} under the beam", left=False)
    v.dim_v(44, DECK + MAT["thickness"], CEILING, f"{fr(DER['sitting_headroom'])} sitting headroom")
    return v.svg(f"Section through the platform at x = {xc}, bed wall on the left")

FIGURES = [("d3", d3)]
CAPTION = f"Cut at x = 55, between joists, so the joist reads pale (beyond) and the ply, ledger, beam and top plate are hatched (cut). The deck ply is the floor of the ledge well. The rear ledger is the same depth as the joists — top and bottom both flush, top at {fr(DECK)} so the ply runs straight over it to the bed wall, framing bottom 53¾, same plane as the beam's own underside. <b>Rev AP:</b> a {fr(m('loft_ceiling').size('z'))} finished ceiling now closes that plane from below, {fr(m('loft_ceiling').z[0])} finished — the same {fr(DER['clear_under_joists'])} clear height under the joists and the beam, from the bed wall out to {fr(m('beam_wrap_face').y[1])}. <b>Rev AG:</b> the beam is a single {BEAMSTOCK} wrapped on three sides — face, bed side and a cap the slats stand on — and its finished top at {fr(BEAM_FIN_TOP)} stands {fr(BEAM_FIN_TOP-DECK-float(MAT['thickness']))} proud of the {fr(float(MAT['thickness']))} mattress, so it retains it rather than sitting below it the way Rev T's 63 beam did. The boxed ledge tracks it: a {fr(m('ledge_front_rail').size('z'))} rail keeps the lid {fr(m('ledge_lid').z[1]-DECK-float(MAT['thickness']))} proud of the mattress, the curb Rev L chose. Sitting headroom is {fr(DER['sitting_headroom'])} over a measured 8 mattress. <b>Rev AU/AX:</b> the cut at x = 55 falls in the bay between joists 4 and 5, so it passes through <b>two different blocks</b>, both hatched. <b>On edge at the beam face</b> ({len(ids("deck_blocking")) + 1} of them, one per bay) is the diaphragm's fixing to the beam. <b>Flat at y 24</b> ({len(ids("deck_seam_blocking"))} of them, only where the ply is seamed) backs the deck's cross-joist seam — the ply really is two panels butting on it at this station, which is why the joint line is drawn. <code>ledge_rail_splice</code> is cut here too. The joists <i>hang</i> off the beam, so without them the deck ply's front edge lands at the LVL with nothing under it and nothing fastening it: the diaphragm that stands in for posts had no connection to the beam at all. <b>Rev AN:</b> the slats are centred on the beam rather than flush with its face — a grille {fr(m('beam_wrap_face').y[1]-m('slat[0]').y[1])} back on both sides, not one plane with the wrap."
