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
    # wall: the two-piece face (its head panel is raked with the opening), framing dashed.
    # Rev AD: the lining is NOT drawn here. It stops at x 102.75, so in this elevation all
    # three sheets project inside the face panels that now lap them — see d7a for the lap.
    # The seam between the two face pieces falls on y 4.25 and draws itself, as the edge
    # between hw_sheath_loft_a and hw_sheath_loft_head.
    for k in ("hw_sheath_loft_a", "hw_sheath_loft_head", "hw_sheath_loft_b"): R(v, m(k), "y", "z", "sheet")
    R(v, m("hw_end_cap"), "y", "z", "sheet")
    for k in ("hw_header", "hw_king_a", "hw_king_b", "hw_trimmer_a", "hw_trimmer_b",
              "hw_jamb_ply_a", "hw_jamb_ply_b", "hw_rake_nailer"): R(v, m(k), "y", "z", "dashfill")
    for k in ("lnd_side_member", "lnd_rim"): R(v, m(k), "y", "z", "dashfill")
    # above the wall: plates, joists, deck, beam end
    for k in ("hw_top_plate_1", "hw_top_plate_2"): R(v, m(k), "y", "z", "lum")
    R(v, m("deck_joist[8]"), "y", "z", "lum2"); R(v, m("deck_ply"), "y", "z", "sheet")
    v.rect(m("beam").y[0], m("beam").y[1], m("beam").z[0], m("beam").z[1], "lum"); R(v, m("beam_wrap_face"), "y", "z", "fin")
    v.text(-1, 30, "bed wall", "labs", "middle", rot=-90)
    v.text(24, 16, "OPEN NOOK — carpet runs through", "lab", "middle")
    v.text(24, 13, f"finished {fr(JAMB_Y[1]-JAMB_Y[0])} wide × {fr(CEIL)} at the head · {fr(RX - m('nk_soffit_flat').x[0])} of lining deep", "labs", "middle")
    v.text(22, 10, f"head raked at {math.degrees(ST.angle):.1f}° — the ply wrap turns the corner", "labs", "middle")
    v.text(10, 31, f"flat ceiling {fr(CEIL)} to y {fr(Y_MEET)}", "labs", "middle")
    v.text(10, 28, "one 6\" wafer LED", "labs", "middle")
    v.text(2.1, 20, f"{fr(m('hw_sheath_loft_a').size('x'))} face laps the wrap", "labs", "middle", rot=-90); v.text(47.9, 8, "laps the wrap", "labs", "middle", rot=-90)
    v.text(5.5, 42.5, "the one seam — on the jamb line", "labk", "start")
    v.text(25, 46.6, "header beyond the sheathing · landing framing beyond", "labs", "middle")
    v.text(24, 55.5, "loft deck", "labs", "middle"); v.text(48.9, 58, "beam", "labs", "middle", rot=-90)
    v.dim_h(JAMB_Y[0], JAMB_Y[1], -1.5 + 0, f"{fr(JAMB_Y[1]-JAMB_Y[0])} finished opening", above=False)
    v.dim_h(NOOK_Y[0], NOOK_Y[1], 62, f"{fr(NOOK_Y[1]-NOOK_Y[0])} rough opening")
    v.dim_v(-3, 0, CEIL, fr(CEIL)); v.dim_v(50.2, 0, soffit(NOOK_Y[1]), fr(soffit(NOOK_Y[1])), left=False)
    v.dim_h(JAMB_Y[0], Y_MEET, 36, f"{fr(Y_MEET - JAMB_Y[0])} flat"); v.dim_h(Y_MEET, JAMB_Y[1], 36, f"{fr(JAMB_Y[1] - Y_MEET)} raked")
    return v.svg("Under-stair nook, elevation from the under-loft space, bed wall on the left")

def d5b():
    v = View(100, 133, 0, 50, 8, ml=60, mr=95, mt=30, mb=44, vdown=True)
    v.rect(131, 133, 0, 50, "wall"); v.rect(100, 133, -1, 0, "wall")
    v.rect(m("hw_sheath_loft_a").x[0], SKIRT.x[1], 0, m("hw_end_cap").y[1], "sheet")
    v.rect(m("hw_sheath_loft_a").x[0], SKIRT.x[1], NOOK_Y[0], NOOK_Y[1], "ghost")
    # Rev X: the ceiling runs the whole way out through the wall, so the flat and raked
    # zones start in the half-wall, not at 107 — that is the point of the rake nailer.
    # Rev AD: they start at 102.75 now, the back of the one-piece nook face.
    XW = m("nk_soffit_flat").x
    v.rect(*XW, JAMB_Y[0], Y_MEET, "flat"); v.rect(*XW, Y_MEET, JAMB_Y[1], "rake")
    # the nailer walls that carry the wrap on the two sides
    for k in ("hw_bottom_plate_a", "hw_bottom_plate_b"): R(v, m(k), "x", "y", "lum")
    for k in ids("nk_bedwall_stud") + ids("nk_shortwall_strut"): R(v, m(k), "x", "y", "lum2")
    for k in ("nk_wrap_bedwall", "nk_wrap_shortwall"): R(v, m(k), "x", "y", "fin")
    R(v, m("hw_rake_nailer"), "x", "y", "lum2")
    for k in ("lnd_side_member", "lnd_rim", "lnd_ledger_rightwall", "lnd_ledger_bedwall") + tuple(ids("lnd_joist")) + tuple(ids("lnd_blocking")): R(v, m(k), "x", "y", "dashfill")
    for k in ("stringer_a", "stringer_b", "stringer_c"): v.rect(*m(k).x, ST.y_top, 50, "dashfill")
    v.out.append(f'<circle class="light" cx="{v.X(119):.1f}" cy="{v.Y(13):.1f}" r="{3*v.s:.1f}"/>')
    v.text(119, 10.5, f"flat {fr(CEIL)}", "lab", "middle", dy=4); v.text(119, 18.5, "wafer LED", "labs", "middle", dy=4)
    v.text(119, 33, "raked from here", "labs", "middle", dy=4)
    v.text(104.4, 30, "rake nailer in the wall", "labs", "middle", rot=-90)
    v.text(118, 4.4, "2×4 studs on edge · the plate runs through the half wall", "labs", "middle", dy=4)
    v.text(117, 44.6, "struts to the stringers", "labs", "middle", dy=4)
    v.text(107, 40, "stringer A", "labs", "middle", rot=-90); v.text(118.6, 40, "B", "labs", "middle"); v.text(130.25, 40, "C", "labs", "middle", rot=-90)
    v.dim_v(134, JAMB_Y[0], Y_MEET, f"{fr(Y_MEET-JAMB_Y[0])}", left=False); v.dim_v(134, Y_MEET, JAMB_Y[1], f"{fr(JAMB_Y[1]-Y_MEET)}", left=False)
    v.dim_h(XW[0], XW[1], -0.5 - 1, f"{fr(XW[1]-XW[0])} — back of the nook face to the right wall")
    return v.svg("Reflected ceiling plan of the nook, bed wall at the top")

FIGURES = [("d5a", d5a), ("d5b", d5b)]
CAPTION = f"Rev AE. <b>The face is one piece and the tube is behind it.</b> The nook face — everything you see at x {fr(m('hw_sheath_loft_a').x[0])}, floor to deck — was three ply panels with the ends of all three lining sheets showing between them: six edges to fill. It is now <b>two boards</b>: a {fr(m('hw_sheath_loft_a').size('y'))} stile in the bed-wall corner, and one {fr(m('hw_sheath_loft_b').y[1] - m('hw_sheath_loft_head').y[0])} × {fr(m('hw_sheath_loft_a').size('z'))} board with the opening sawn out of it, running unbroken round the head and out to the corner you walk past. One seam, and it falls on y {fr(JAMB_Y[0])} — the same line as the opening jamb below it. It is two and not one only because the face is {fr(m('hw_sheath_loft_b').y[1])} × {fr(m('hw_sheath_loft_a').size('z'))} and neither dimension fits a 48 sheet; a 5×5 panel would make it one. <b>The lining is recessed behind it</b> — <code>nk_wrap_bedwall</code>, <code>nk_wrap_shortwall</code> and the soffit panels all stop at x {fr(m('nk_soffit_flat').x[0])} instead of running out to the face, so the face laps their ends and no end grain shows on it. The finished opening is {fr(JAMB_Y[1]-JAMB_Y[0])} × {fr(CEIL)}; the face panel's own edge is the first {fr(m('hw_sheath_loft_a').size('x'))} of each jamb and the lining takes over behind it. <b>Rev AZ:</b> the tube is no longer one thickness — the bed-wall jamb stays {fr(m('nk_wrap_bedwall').size('y'))} and the short-wall jamb and both soffit boards go to {fr(m('nk_wrap_shortwall').size('y'))}, so the opening is {fr(JAMB_Y[1]-JAMB_Y[0])} rather than the symmetric {fr(NOOK_Y[1]-NOOK_Y[0]-2*m('nk_wrap_bedwall').size('y'))}, its two jamb returns differ by {fr(m('nk_wrap_bedwall').size('y')-m('nk_wrap_shortwall').size('y'))}, and the ceiling rises the same amount to {fr(CEIL)}. It runs from x {fr(m('nk_soffit_flat').x[0])} straight through to the right wall — no jambs, no separate head trim. Its ceiling is flat at {fr(CEIL)} to y = {fr(Y_MEET)}, where the stringer undersides come down to that line, then rides them to {fr(DER['nook_far_end_height'])} at the far end. <b>Rev AE:</b> that ceiling is <b>two boards</b>, not one — <code>nk_soffit_flat</code> and <code>nk_soffit_rake</code>. It was drawn and encoded as a single sheet with a {math.degrees(ST.angle):.1f}° kink along it, which is not a thing you can cut; the two now butt on a plumb joint at y {fr(Y_MEET)}, where both faces are on {fr(CEIL)}, so the joint is flush and full-thickness and the ceiling still reads as one plane turning a corner. the framing plane above it is {fr(CEIL+PANEL)}, the bottom of both the nook header and the landing ledgers, so the panel screws straight to them with nothing to fur. Inside the wall the raked run is carried by <code>hw_rake_nailer</code>, a 2×4 laid flat with its underside on the stringer line, bevelled where it dies into the header. The two sides are ordinary 2×4 nailer walls — studs on edge, 1½ × 3½, on a 2×4 laid flat and run right up to the bed wall. They are a full 3½ deep because Rev Z added a ½ ply flitch inside each jamb pack (king + ½ ply + trimmer = 3½, the same lay-up as the header), so the trimmer faces and the nook stud faces are one plane and each wrap crosses its reveal without a step. On the short wall the three struts land at x {" and ".join([", ".join(fr(m(k).x[0]) for k in ids("nk_shortwall_strut")[:-1]), fr(m(ids("nk_shortwall_strut")[-1]).x[0])])} — directly under stringers A, B and C. <b>Rev AE:</b> both plates now run through the half wall — <code>hw_bottom_plate_a</code> and <code>hw_bottom_plate_b</code> are each one 28¼ board carrying the half-wall's jamb pack and then the nook's studs, because the ¾ sheathing that used to separate them at x 106¼→107 is gone. No bottom plate crosses the opening — the floor runs through. Power for the wafer light must be in the half-wall before it is sheathed."
