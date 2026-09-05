"""Drawing 5 — Under-stair nook. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "5", "Under-stair nook"

def d5a():
    v = View(-2, 52, 0, 64, 7, ml=90, mr=70, mt=30, mb=44)
    v.rect(-2, 0, 0, 64, "wall"); v.line(-2, 0, 52, 0, "floor")
    # through the opening: the nook interior. Rev X — the head follows the rake, so
    # the void is a five-sided profile, not a rectangle with a soffit line across it.
    v.poly([(JAMB_Y[0], 0), (JAMB_Y[0], CEIL), (Y_MEET, CEIL),
            (JAMB_Y[1], soffit(JAMB_Y[1])), (JAMB_Y[1], 0)], "ghost")
    v.out.append(f'<ellipse class="light" cx="{v.X(9.5):.1f}" cy="{v.Y(CEIL):.1f}" rx="{3*v.s:.1f}" ry="{0.7*v.s:.1f}"/>')
    # wall: loft-side sheathing (its head panel is raked with the opening), framing dashed
    for k in ("hw_sheath_loft_a", "hw_sheath_loft_head", "hw_sheath_loft_b"): R(v, m(k), "y", "z", "sheet")
    R(v, m("hw_end_cap"), "y", "z", "sheet")
    for k in ("hw_header", "hw_king_a", "hw_king_b", "hw_trimmer_a", "hw_trimmer_b",
              "hw_rake_nailer"): R(v, m(k), "y", "z", "dashfill")
    # the ply wrap — real members now, so the reveal is drawn, not typed
    for k in ("nk_wrap_bedwall", "nk_wrap_shortwall", "nk_soffit_panel"): R(v, m(k), "y", "z", "fin")
    for k in ("lnd_side_member", "lnd_rim"): R(v, m(k), "y", "z", "dashfill")
    # above the wall: plates, joists, deck, beam end
    for k in ("hw_top_plate_1", "hw_top_plate_2"): R(v, m(k), "y", "z", "lum")
    R(v, m("deck_joist[8]"), "y", "z", "lum2"); R(v, m("deck_ply"), "y", "z", "sheet")
    v.rect(m("beam").y[0], m("beam").y[1], m("beam").z[0], m("beam").z[1], "lum"); R(v, m("beam_wrap_face"), "y", "z", "fin")
    v.text(-1, 30, "bed wall", "labs", "middle", rot=-90)
    v.text(24, 16, "OPEN NOOK — carpet runs through", "lab", "middle")
    v.text(24, 13, f"finished {fr(JAMB_Y[1]-JAMB_Y[0])} wide × {fr(CEIL)} at the head · 24 deep", "labs", "middle")
    v.text(22, 10, f"head raked at {math.degrees(ST.angle):.1f}° — the ply wrap turns the corner", "labs", "middle")
    v.text(10, 31, f"flat ceiling {fr(CEIL)} to y {fr(Y_MEET)}", "labs", "middle")
    v.text(10, 28, "one 6\" wafer LED", "labs", "middle")
    v.text(1.9, 20, "wrap", "labs", "middle", rot=-90); v.text(48.1, 8, "wrap", "labs", "middle", rot=-90)
    v.text(25, 46.6, "header beyond the sheathing · landing framing beyond", "labs", "middle")
    v.text(24, 55.5, "loft deck", "labs", "middle"); v.text(48.9, 58, "beam", "labs", "middle", rot=-90)
    v.dim_h(JAMB_Y[0], JAMB_Y[1], -1.5 + 0, f"{fr(JAMB_Y[1]-JAMB_Y[0])} finished opening", above=False)
    v.dim_h(NOOK_Y[0], NOOK_Y[1], 62, f"{fr(NOOK_Y[1]-NOOK_Y[0])} rough opening")
    v.dim_v(-1.6, 0, CEIL, fr(CEIL)); v.dim_v(50.2, 0, soffit(NOOK_Y[1]), fr(soffit(NOOK_Y[1])), left=False)
    v.dim_h(JAMB_Y[0], Y_MEET, 36, f"{fr(Y_MEET - JAMB_Y[0])} flat"); v.dim_h(Y_MEET, JAMB_Y[1], 36, f"{fr(JAMB_Y[1] - Y_MEET)} raked")
    return v.svg("Under-stair nook, elevation from the under-loft space, bed wall on the left")

def d5b():
    v = View(100, 133, 0, 50, 8, ml=60, mr=95, mt=30, mb=44, vdown=True)
    v.rect(131, 133, 0, 50, "wall"); v.rect(100, 133, -1, 0, "wall")
    v.rect(m("hw_sheath_loft_a").x[0], m("hw_sheath_stair_a").x[1], 0, m("hw_end_cap").y[1], "sheet")
    v.rect(m("hw_sheath_loft_a").x[0], m("hw_sheath_stair_a").x[1], NOOK_Y[0], NOOK_Y[1], "ghost")
    # Rev X: the ceiling runs the whole way out to the wall's outer face, so the flat
    # and raked zones start at x 102, not 107 — that is the point of the rake nailer.
    XW = m("nk_soffit_panel").x
    v.rect(*XW, JAMB_Y[0], Y_MEET, "flat"); v.rect(*XW, Y_MEET, JAMB_Y[1], "rake")
    # the nailer walls that carry the wrap on the two sides
    for k in ("nk_bedwall_plate", "nk_shortwall_plate"): R(v, m(k), "x", "y", "lum")
    for k in ids("nk_bedwall_stud") + ids("nk_shortwall_strut"): R(v, m(k), "x", "y", "lum2")
    for k in ("nk_wrap_bedwall", "nk_wrap_shortwall"): R(v, m(k), "x", "y", "fin")
    R(v, m("hw_rake_nailer"), "x", "y", "lum2")
    for k in ("lnd_side_member", "lnd_rim", "lnd_ledger_rightwall", "lnd_ledger_bedwall") + tuple(ids("lnd_joist")) + tuple(ids("lnd_blocking")): R(v, m(k), "x", "y", "dashfill")
    for k in ("stringer_a", "stringer_b", "stringer_c"): v.rect(*m(k).x, ST.y_top, 50, "dashfill")
    v.out.append(f'<circle class="light" cx="{v.X(119):.1f}" cy="{v.Y(13):.1f}" r="{3*v.s:.1f}"/>')
    v.text(119, 10.5, f"flat {fr(CEIL)}", "lab", "middle", dy=4); v.text(119, 18.5, "wafer LED", "labs", "middle", dy=4)
    v.text(119, 33, "raked from here", "labs", "middle", dy=4)
    v.text(104.4, 30, "rake nailer in the wall", "labs", "middle", rot=-90)
    v.text(118, 4.4, "2×4-flat nailer wall, 2×2 sill", "labs", "middle", dy=4)
    v.text(117, 44.6, "struts to the stringers", "labs", "middle", dy=4)
    v.text(107.75, 40, "stringer A", "labs", "middle", rot=-90); v.text(119, 40, "B", "labs", "middle"); v.text(130.25, 40, "C", "labs", "middle", rot=-90)
    v.dim_v(132.6, JAMB_Y[0], Y_MEET, f"{fr(Y_MEET-JAMB_Y[0])}", left=False); v.dim_v(132.6, Y_MEET, JAMB_Y[1], f"{fr(JAMB_Y[1]-Y_MEET)}", left=False)
    v.dim_h(XW[0], XW[1], -0.5 - 1, f"{fr(XW[1]-XW[0])} — outer face of the half-wall to the right wall")
    return v.svg("Reflected ceiling plan of the nook, bed wall at the top")

FIGURES = [("d5a", d5a), ("d5b", d5b)]
CAPTION = f"Rev X. The nook is one ¾-plywood-wrapped tube running from the half-wall's outer face at x {fr(m('nk_soffit_panel').x[0])} straight through to the right wall — no jambs, no separate head trim. Its ceiling is flat at {fr(CEIL)} to y = {fr(Y_MEET)}, where the stringer undersides come down to that line, then rides them to {fr(DER['nook_far_end_height'])} at the far end; the framing plane above it is {fr(CEIL+PANEL)}, the bottom of both the nook header and the landing ledgers, so the panel screws straight to them with nothing to fur. Inside the wall the raked run is carried by <code>hw_rake_nailer</code>, a 2×4 laid flat with its underside on the stringer line, bevelled where it dies into the header. The two sides are nailer walls: 2×4 studs on the flat into 2×2 plates, in line with the trimmers, so the reveal and the nook faces are one plane. No bottom plate crosses the opening — the floor runs through. Power for the wafer light must be in the half-wall before it is sheathed."
