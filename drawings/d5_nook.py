"""Drawing 5 — Under-stair nook. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "5", "Under-stair nook"

def d5a():
    v = View(-2, 52, 0, 64, 7, ml=90, mr=70, mt=30, mb=44)
    v.rect(-2, 0, 0, 64, "wall"); v.line(-2, 0, 52, 0, "floor")
    # through the opening: the nook interior
    v.rect(JAMB_Y[0], JAMB_Y[1], 0, CEIL, "ghost")
    v.path([(JAMB_Y[0], soffit(JAMB_Y[0])), (Y_MEET, CEIL), (JAMB_Y[1], soffit(JAMB_Y[1]))], "soffit")
    v.out.append(f'<ellipse class="light" cx="{v.X(9.5):.1f}" cy="{v.Y(CEIL):.1f}" rx="{3*v.s:.1f}" ry="{0.7*v.s:.1f}"/>')
    # wall: loft-side sheathing, framing dashed, jambs
    for k in ("hw_sheath_loft_a", "hw_sheath_loft_head", "hw_sheath_loft_b"): R(v, m(k), "y", "z", "sheet")
    R(v, m("hw_end_cap"), "y", "z", "sheet")
    for k in ("hw_header", "hw_king_a", "hw_king_b", "hw_trimmer_a", "hw_trimmer_b"): R(v, m(k), "y", "z", "dashfill")
    v.rect(NOOK_Y[0], NOOK_Y[1], CEIL, HB, "fin"); v.rect(NOOK_Y[0], JAMB_Y[0], 0, CEIL, "fin"); v.rect(JAMB_Y[1], NOOK_Y[1], 0, CEIL, "fin")
    for k in ("lnd_side_member", "lnd_rim"): R(v, m(k), "y", "z", "dashfill")
    # above the wall: plates, joists, deck, beam end
    for k in ("hw_top_plate_1", "hw_top_plate_2"): R(v, m(k), "y", "z", "lum")
    R(v, m("deck_joist[8]"), "y", "z", "lum2"); R(v, m("deck_ply"), "y", "z", "sheet")
    v.rect(m("beam").y[0], m("beam").y[1], m("beam").z[0], m("beam").z[1], "lum"); R(v, m("beam_wrap_face"), "y", "z", "fin")
    v.text(-1, 30, "bed wall", "labs", "middle", rot=-90)
    v.text(25, 20, "OPEN NOOK — carpet runs through", "lab", "middle"); v.text(25, 17, f"finished {fr(JAMB_Y[1]-JAMB_Y[0])} wide × {fr(CEIL)} high · 24 deep · rake follows the stringers at {math.degrees(ST.angle):.1f}°", "labs", "middle")
    v.text(25, 36, f"flat ceiling {fr(CEIL)} to y = {fr(Y_MEET)} · one 6\" wafer LED", "labs", "middle")
    v.text(38, 26, "raked panel on the stringers", "labs", "start", rot=-math.degrees(ST.angle))
    v.text(25, CEIL + 0.375, "¾ poplar head jamb — flush with the ceiling", "labs", "middle", dy=3)
    v.text(3.4, 20, "jamb", "labs", "middle", rot=-90); v.text(46.6, 20, "jamb", "labs", "middle", rot=-90)
    v.text(25, 46.6, "header beyond the sheathing · landing framing beyond", "labs", "middle")
    v.text(24, 55.5, "loft deck", "labs", "middle"); v.text(48.9, 58, "beam", "labs", "middle", rot=-90)
    v.dim_h(JAMB_Y[0], JAMB_Y[1], -1.5 + 0, f"{fr(JAMB_Y[1]-JAMB_Y[0])} finished opening", above=False)
    v.dim_h(NOOK_Y[0], NOOK_Y[1], 62, f"{fr(NOOK_Y[1]-NOOK_Y[0])} rough opening")
    v.dim_v(-1.6, 0, CEIL, fr(CEIL)); v.dim_v(50.2, 0, soffit(NOOK_Y[1]), fr(soffit(NOOK_Y[1])), left=False)
    v.dim_h(JAMB_Y[0], Y_MEET, 38.5, f"{fr(Y_MEET - JAMB_Y[0])} flat"); v.dim_h(Y_MEET, JAMB_Y[1], 38.5, f"{fr(JAMB_Y[1] - Y_MEET)} raked")
    return v.svg("Under-stair nook, elevation from the under-loft space, bed wall on the left")

def d5b():
    v = View(100, 133, 0, 50, 8, ml=60, mr=95, mt=30, mb=44, vdown=True)
    v.rect(131, 133, 0, 50, "wall"); v.rect(100, 133, -1, 0, "wall")
    v.rect(m("hw_sheath_loft_a").x[0], m("hw_sheath_stair_a").x[1], 0, m("hw_end_cap").y[1], "sheet")
    v.rect(m("hw_sheath_loft_a").x[0], m("hw_sheath_stair_a").x[1], NOOK_Y[0], NOOK_Y[1], "ghost")
    v.rect(m("hw_sheath_loft_a").x[0], m("hw_sheath_stair_a").x[1], NOOK_Y[0], JAMB_Y[0], "fin"); v.rect(m("hw_sheath_loft_a").x[0], m("hw_sheath_stair_a").x[1], JAMB_Y[1], NOOK_Y[1], "fin")
    v.rect(107, 131, NOOK_Y[0], Y_MEET, "flat"); v.rect(107, 131, Y_MEET, NOOK_Y[1], "rake")
    for k in ("lnd_side_member", "lnd_rim", "lnd_ledger_rightwall", "lnd_ledger_bedwall") + tuple(ids("lnd_joist")) + tuple(ids("lnd_blocking")): R(v, m(k), "x", "y", "dashfill")
    for k in ("stringer_a", "stringer_b", "stringer_c"): v.rect(*m(k).x, ST.y_top, 50, "dashfill")
    v.out.append(f'<circle class="light" cx="{v.X(119):.1f}" cy="{v.Y(13):.1f}" r="{3*v.s:.1f}"/>')
    v.text(119, 6.5, f"flat {fr(CEIL)} · {fr(Y_MEET-JAMB_Y[0])} × 24 from the jamb", "lab", "middle", dy=4); v.text(119, 17.5, "wafer LED", "labs", "middle", dy=4)
    v.text(119, 33, "raked from here", "labs", "middle", dy=4)
    v.text(104.5, 25, "half-wall · jambed opening", "labs", "middle", rot=-90)
    v.text(107.75, 40, "stringer A", "labs", "middle", rot=-90); v.text(119, 40, "B", "labs", "middle"); v.text(130.25, 40, "C", "labs", "middle", rot=-90)
    v.dim_v(132.6, JAMB_Y[0], Y_MEET, f"{fr(Y_MEET-JAMB_Y[0])}", left=False); v.dim_v(132.6, Y_MEET, JAMB_Y[1], f"{fr(JAMB_Y[1]-Y_MEET)}", left=False)
    v.dim_h(107, 131, -0.5 - 1, "24 deep")
    return v.svg("Reflected ceiling plan of the nook, bed wall at the top")

FIGURES = [("d5a", d5a), ("d5b", d5b)]
CAPTION = f"The opening through the half-wall is finished with ¾ poplar jambs; the head jamb and the flat soffit panel share one plane at {fr(CEIL)}, so the ceiling runs straight through the opening. The panel's top at {fr(CEIL+PANEL)} clears every 2×8 in the landing box by {fr(m('lnd_rim').z[0]-CEIL-PANEL)}. Where the stringer undersides come down to that line (y ≈ {fr(Y_MEET)}) the panel simply continues on the stringers to {fr(DER['nook_far_end_height'])} at the far end. No gussets. Power for the wafer light must be in the half-wall before it is sheathed."
