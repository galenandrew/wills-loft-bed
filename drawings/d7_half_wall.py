"""Drawing 7 — Half-wall detail. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "7", "Half-wall detail"

def d7a():
    v = View(-1, 52, 97.8, 109.4, 9, ml=70, mr=90, mt=30, mb=30)     # h = y (bed wall left), v = x (stair side up)
    v.rect(-1, 0, 101, 108, "wall")
    for k in ("hw_king_a", "hw_king_b"): R(v, m(k), "y", "x", "lum", HATCH)
    for k in ("hw_trimmer_a", "hw_trimmer_b"): R(v, m(k), "y", "x", "lum2", HATCH)
    for k in ("hw_sheath_loft_a", "hw_sheath_loft_b", "hw_sheath_stair_a", "hw_sheath_stair_b"): R(v, m(k), "y", "x", "sheet")
    R(v, m("hw_end_cap"), "y", "x", "fin")
    v.rect(NOOK_Y[0], JAMB_Y[0], 102, 107, "fin"); v.rect(JAMB_Y[1], NOOK_Y[1], 102, 107, "fin")
    v.rect(m("beam").y[0], m("beam").y[1], m("beam").x[0] and 102.75, m("beam").x[1], "dashfill")
    v.text(25, 104.5, f"{fr(JAMB_Y[1]-JAMB_Y[0])} FINISHED OPENING — wall removed, both faces · ¾ poplar jambs", "lab", "middle", dy=4)
    v.text(25, 103.3, "header above carries the deck rim and the landing rim", "labs", "middle", dy=4)
    v.text(1.5, 107.4, "king + trimmer", "labs", "middle", dy=-3); v.text(48.5, 107.4, "trimmer + king", "labs", "middle", dy=-3); v.text(48.5, 109.0, "beam end above — bears here", "labk", "middle", dy=-3)
    v.text(25, 107.4, "stair side", "labs", "middle", dy=-3); v.text(25, 101.6, "loft side", "labs", "middle", dy=13)
    v.dim_v(51.5, 106.25, 107, "¾", left=False); v.dim_v(51.5, 102.75, 106.25, "3½", left=False); v.dim_v(51.5, 102, 102.75, "¾", left=False); v.dim_v(53.3, 102, 107, "5", left=False)
    v.dim_h(NOOK_Y[0], NOOK_Y[1], 108.4, f"{fr(NOOK_Y[1]-NOOK_Y[0])} rough"); v.dim_h(JAMB_Y[0], JAMB_Y[1], 100.1, f"{fr(JAMB_Y[1]-JAMB_Y[0])} finished", above=False)
    v.dim_h(0, m("hw_end_cap").y[1], 98.7, f"{fr(m('hw_end_cap').y[1])} — full platform depth", above=False)
    return v.svg("Half-wall plan detail, horizontal section at 30 inches, rotated so the bed wall is on the left and the stair side up")

def d7b():
    v = View(-2, 52, 0, 66, 7, ml=120, mr=70, mt=30, mb=44)
    v.rect(-2, 0, 0, 66, "wall"); v.line(-2, 0, 52, 0, "floor")
    half_wall_yz(v)
    R(v, m("hw_end_cap"), "y", "z", "fin")
    R(v, m("deck_rim"), "y", "z", "lum2"); R(v, m("deck_ply"), "y", "z", "sheet", HATCH)
    R(v, m("beam"), "y", "z", "lum", HATCH); R(v, m("beam_wrap_face"), "y", "z", "fin")
    for k in ("lnd_side_member", "lnd_rim", "lnd_ply"): R(v, m(k), "y", "z", "dashfill")
    v.poly([p for p in stringer_pts() if p[0] <= 27.01], "dashfill")
    for y in (m("hw_king_a").y[1], m("hw_king_b").y[0]): v.out.append(f'<circle class="strap" cx="{v.X(y):.1f}" cy="{v.Y(46):.1f}" r="{1.6*v.s:.1f}"/>')
    v.text(25, 47.4, "2×10 + ½ ply spacer + 2×10 = 3½ · 47 long · bears 1½ each end", "labs", "middle", dy=4)
    v.text(25, 45.4, "sized by connection depth, not load (~140 psi)", "labs", "middle", dy=4)
    v.text(25, 52.2, "double top plate — deck rim bears here", "labs", "middle", dy=4)
    v.text(22, 12, f"{fr(NOOK_Y[1]-NOOK_Y[0])} × {fr(HB)} ROUGH · {fr(JAMB_Y[1]-JAMB_Y[0])} × {fr(CEIL)} FINISHED", "lab", "middle")
    v.text(0.75, 25, "king", "labs", "middle", rot=-90); v.text(2.25, 25, "trimmer", "labs", "middle", rot=-90); v.text(3.4, 25, "jamb", "labs", "middle", rot=-90)
    v.text(5, 39.4, "landing beyond — side member, rim, deck (dashed)", "labs", "start"); v.text(22.5, 37.6, "stringer A beyond", "labs", "start")
    v.text(4, 49.6, "strap both header-to-king joints", "labb", "start")
    v.text(46, 64.3, "beam end — bypasses the opening", "labk", "end")
    v.dim_v(-1.6, 0, m("hw_top_plate_2").z[1], f"{fr(m('hw_top_plate_2').z[1])} to top plate"); v.dim_v(44, 0, CEIL, f"{fr(CEIL)} finished head", left=True)
    v.dim_v(50.5, 0, m("beam").z[1], f"{fr(m('beam').z[1])} beam top", left=False)
    v.dim_h(NOOK_Y[0], NOOK_Y[1], -1.5, fr(NOOK_Y[1]-NOOK_Y[0]), above=False); v.dim_h(m("hw_header").y[0], m("hw_header").y[1], 55.6, f"{fr(m('hw_header').size('y'))} header")
    return v.svg("Half-wall section at x = 104.5, bed wall on the left")

FIGURES = [("d7a", d7a), ("d7b", d7b)]
CAPTION = "Plan detail is a horizontal section at 30, rotated so the bed wall is on the left and the stair side up. The opening removes both faces: what remains is two posts and a sandwich header — a portal frame, not a shear wall. The beam's reaction bypasses it (lands on the far stud pack); the landing box ties the top plate across to the right wall. Glue the deck ply and strap both header-to-king joints."
