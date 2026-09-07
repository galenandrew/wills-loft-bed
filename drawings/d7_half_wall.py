"""Drawing 7 — Half-wall detail. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "7", "Half-wall detail"

# Rev Y.1: this plan used to cut at z 30, which since Rev X is ABOVE the raked head —
# the plane crossed both head sheathing panels and the rake nailer (undrawn), and the
# rough / finished dims were only true lower down. Cut at 12 instead: below the rake
# everywhere (the underside reaches z 12 at y 50.4, past the opening's far edge), so the
# opening really is full width here, and the short-wall wrap shows.
CUT_Z = 12.0

def d7a():
    v = View(-1, 52, 97.8, 109.4, 9, ml=70, mr=90, mt=30, mb=30)     # h = y (bed wall left), v = x (stair side up)
    v.rect(-1, 0, 101, 108, "wall")
    for k in ("hw_king_a", "hw_king_b"): R(v, m(k), "y", "x", "lum", HATCH)
    for k in ("hw_trimmer_a", "hw_trimmer_b"): R(v, m(k), "y", "x", "lum2", HATCH)
    for k in ("hw_jamb_ply_a", "hw_jamb_ply_b"): R(v, m(k), "y", "x", "sheet")
    for k in ("hw_sheath_loft_a", "hw_sheath_loft_b"): R(v, m(k), "y", "x", "sheet")
    # Rev AE: nothing on the stair side at this height. The face there is a skirt above the
    # stringers (its lowest edge is z 24 at the wall's end), so at z 12 the wall is the
    # loft sheathing plus 3½ of framing — and stringer A itself is the next thing outboard
    # of it. Rev AZ: that sheathing is ½, so this height is 4, not 4¼.
    R(v, m("hw_end_cap_foot"), "y", "x", "fin")
    y_str = ST.y_riser_top + (ST.underside(ST.y_riser_top) - CUT_Z) / ST.tan       # 50.4
    v.rect(y_str, 52, *m("stringer_a").x, "lum2", HATCH)
    R(v, m("stringer_a_skin"), "y", "x", "fin")
    # the ply wrap on both reveals — clipped to the wall, since both sheets run on
    # into the nook to x 131. Both exist at this height; the short wall's tops out on the
    # stringer underside. Rev AZ: the two are no longer the same thickness — ¾ on the bed
    # wall, ½ on the short wall — so the two jamb returns differ and JAMB_Y reads each face.
    # Rev AD: drawn from the member's own start (102.75), so this section shows the lap —
    # the face panel in front of the wrap's end, not butted to it.
    for k in ("nk_wrap_bedwall", "nk_wrap_shortwall"): v.rect(*m(k).y, m(k).x[0], 107, "fin")
    v.rect(m("beam").y[0], m("beam").y[1], m("beam").x[0] and 102.75, m("beam").x[1], "dashfill")
    v.text(25, 104.5, f"{fr(JAMB_Y[1]-JAMB_Y[0])} FINISHED OPENING — wall removed, both faces · {fr(m('nk_wrap_bedwall').size('y'))} wrap this jamb, {fr(m('nk_wrap_shortwall').size('y'))} the other", "lab", "middle", dy=4)
    v.text(25, 103.3, "header above carries the deck rim and the landing rim", "labs", "middle", dy=4)
    v.text(25, 105.84, f"nook face laps the wrap · no sheathing on the stair side here — the {VALS['hw_fin_w']} is above the skirt only", "labs", "middle", dy=4)
    v.text(1.75, 107.4, "king + ½ ply + trimmer", "labs", "middle", dy=-3); v.text(48.25, 107.4, "trimmer + ½ ply + king", "labs", "middle", dy=-3); v.text(48.5, 109.0, "beam end above — bears here", "labk", "middle", dy=-3)
    v.text(25, 106.9, "stair side — bare framing below the skirt", "labs", "middle", dy=-3)
    v.text(51.8, 100.9, "stringer A + its skin enter the cut here", "labk", "end", dy=-3); v.text(25, 101.6, "loft side", "labs", "middle", dy=13)
    _sh = m("hw_sheath_loft_a")
    v.dim_v(51.5, 102.75, 106.25, fr(m("hw_king_a").size("x")), left=False)
    v.dim_v(51.5, _sh.x[0], _sh.x[1], fr(_sh.size("x")), left=False)
    v.dim_v(53.3, _sh.x[0], 106.25, f"{fr(106.25 - float(_sh.x[0]))} here", left=False)
    v.dim_h(NOOK_Y[0], NOOK_Y[1], 108.4, f"{fr(NOOK_Y[1]-NOOK_Y[0])} rough"); v.dim_h(JAMB_Y[0], JAMB_Y[1], 100.1, f"{fr(JAMB_Y[1]-JAMB_Y[0])} finished", above=False)
    v.dim_h(0, m("hw_end_cap").y[1], 98.7, f"{fr(m('hw_end_cap').y[1])} — full platform depth", above=False)
    return v.svg(f"Half-wall plan detail, horizontal section at {fr(CUT_Z)} inches, rotated so the bed wall is on the left and the stair side up")

def d7b():
    TOP = m("beam_wrap_top").z[1] + 1.5      # Rev AG: the beam tops out at 68½ finished
    v = View(-2, 52, 0, TOP, 7, ml=120, mr=70, mt=30, mb=44)
    v.rect(-2, 0, 0, TOP, "wall"); v.line(-2, 0, 52, 0, "floor")
    half_wall_yz(v)
    R(v, m("hw_end_cap"), "y", "z", "fin")
    R(v, m("deck_rim"), "y", "z", "lum2"); R(v, m("deck_ply"), "y", "z", "sheet", HATCH)
    R(v, m("beam"), "y", "z", "lum", HATCH)
    for k in ("beam_wrap_face", "beam_wrap_inner", "beam_wrap_top"): R(v, m(k), "y", "z", "fin")
    for k in ("lnd_side_member", "lnd_rim", "lnd_ply"): R(v, m(k), "y", "z", "dashfill")
    v.poly([p for p in stringer_pts() if p[0] <= 27.01], "dashfill")
    # Rev BA.1: the two red strap markers at the header-to-king joints are GONE. Rev AS
    # scrapped the straps — the joint is closed by sheathing on both faces plus the two
    # continuous top plates — and Open Items has said so since, while this sheet went on
    # drawing them and telling the builder to fit them. Found by connection-checker at BA.
    v.text(25, 47.4, f"2×10 + ½ ply + 2×10 = 3½ wide × {fr(m('hw_header').size('z'))} deep, full stock · {fr(m('hw_header').size('y'))} long · bears {fr(m('hw_trimmer_a').y[1] - m('hw_header').y[0])} each end", "labs", "middle", dy=4)
    v.text(25, 45.4, "sized by connection depth, not load (~140 psi)", "labs", "middle", dy=4)
    v.text(25, 55.4, "double top plate — deck rim bears here", "labs", "middle", dy=4)
    v.text(24, 9, f"{fr(NOOK_Y[1]-NOOK_Y[0])} × {fr(HB)} ROUGH", "lab", "middle")
    v.text(24, 6, f"{fr(JAMB_Y[1]-JAMB_Y[0])} × {fr(CEIL)} finished at the head, raked past y {fr(Y_MEET)}", "labs", "middle")
    v.text(31, 26, "rake nailer — dies straight onto stringer A", "labs", "middle")
    v.text(0.75, 25, "king", "labs", "middle", rot=-90); v.text(2.75, 25, "½ ply + trimmer", "labs", "middle", rot=-90); v.text(3.9, 25, "ply wrap", "labs", "middle", rot=-90)
    v.text(5, 39.4, "landing beyond — side member, rim, deck (dashed)", "labs", "start"); v.text(27, 34.5, "stringer A beyond", "labs", "start")
    v.text(4, 49.6, "header-to-king: no straps — sheathed both faces + 2 top plates over", "labs", "start")
    v.text(46, m("beam_wrap_top").z[1] - 3.7, "beam end — bypasses the opening", "labk", "end")
    v.dim_v(-3, 0, m("hw_top_plate_2").z[1], f"{fr(m('hw_top_plate_2').z[1])} to top plate"); v.dim_v(20, 0, CEIL, f"{fr(CEIL)} finished head", left=True)
    v.dim_v(52.5, 0, m("beam_wrap_top").z[1], f"{fr(m('beam_wrap_top').z[1])} beam top, finished", left=False)
    v.dim_h(NOOK_Y[0], NOOK_Y[1], -1.5, fr(NOOK_Y[1]-NOOK_Y[0]), above=False); v.dim_h(m("hw_header").y[0], m("hw_header").y[1], 52, f"{fr(m('hw_header').size('y'))} header")
    return v.svg("Half-wall section at x = 104.5, bed wall on the left")

FIGURES = [("d7a", d7a), ("d7b", d7b)]
CAPTION = f"Plan detail is a horizontal section at {fr(CUT_Z)} — deliberately low, because the opening head is raked and only below {fr(DER['nook_far_end_height'])} is the opening its full {fr(NOOK_Y[1]-NOOK_Y[0])} rough width across the whole span. Rotated so the bed wall is on the left and the stair side up. The opening removes both faces: what remains is two posts and a sandwich header — a portal frame, not a shear wall. The beam's reaction bypasses it (lands on the far stud pack); the landing box ties the top plate across to the right wall. Glue the deck ply. <b>The header-to-king joints are NOT strapped</b> (Rev AS): the wall is sheathed across both of them &#8212; <code>hw_sheath_stair</code> on the stair face and the one-piece nook face on the loft face &#8212; and the two continuous top plates bear over the header and both kings. Rev AZ took the loft face to &#189; and the builder accepted it: the joint carries gravity into the trimmers, whose bearing is checked, so the sheathing is a racking and continuity gusset rather than a tension tie. <b>Rev AE:</b> the stair side of the wall is not sheathed below the stair. Stringer A lands on the framing at x {fr(m('stringer_a').x[0])}, the landing box with it, and both bottom plates run on through into the nook as single boards; what is left of the stair face is <code>hw_sheath_stair</code>, a skirt above the stringers&#8217; top line. At this cut the wall is therefore {fr(m('hw_king_a').x[1] - m('hw_sheath_loft_a').x[0])} thick, not 5."
