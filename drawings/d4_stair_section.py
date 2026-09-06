"""Drawing 4 — Stair section. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "4", "Stair section"
CUT_X = 118.6        # through stringer B (Rev AE: x 117⅞→119⅜)

def d4():
    v = View(-4, 76, 0, CEILING + 1, 5.6, ml=130, mr=70, mt=28, mb=44)
    v.rect(-2, 0, 0, CEILING, "wall"); v.line(-2, CEILING, 76, CEILING, "floor"); v.line(-2, 0, 76, 0, "floor")
    v.line(0, DECK, m("beam_wrap_face").y[1], DECK, "dash"); v.text(2, DECK, f"loft deck {fr(DECK)} — beyond the half-wall", "labs", "start", dy=-4)
    v.rect(m("beam_wrap_inner").y[0], m("beam_wrap_face").y[1], DECK, m("beam_wrap_top").z[1], "dashfill"); v.text(52, 60.5, "beam end, beyond", "labs", "start")
    # beyond the cut plane — axis-aligned boxes, so a box projection is exact
    R(v, m("lnd_side_member"), "y", "z", "lum2"); R(v, m("lnd_joist[0]"), "y", "z", "dashfill"); R(v, m("lnd_blocking[0]"), "y", "z", "dashfill")
    # ON the cut plane — the kernel decides what stringer B's plane crosses, and gives
    # the real notched profile rather than a hand-kept polygon. The nook's lining and
    # nailer walls are in this cut too; they are Drawing 5's story, so this sheet
    # leaves the whole nk_ family out.
    kernel_cut(v, "x", CUT_X, skip=("nk_*",))
    # half-wall framing, in front of the section cut from this angle — shown as a transparent outline so it doesn't hide the stair
    for k in ("hw_sheath_stair", "hw_header", "hw_trimmer_a", "hw_trimmer_b",
              "hw_jamb_ply_a", "hw_jamb_ply_b", "hw_king_a", "hw_king_b"):
        R(v, m(k), "y", "z", "dashfill")
    # Rev AC: stringer A's ply skin — in front of this cut with the half-wall. Outline
    # only: its stepped top edge lies on the stringer profile already drawn, so a filled
    # polygon would say nothing the vertical edge at its uphill end does not.
    v.poly(skin_pts(), "ghostl")
    # labels
    v.text(-1, 62, "bed wall", "labw", "middle", rot=-90)
    v.text(SKIN_Y0 + 0.8, 28, "¾ skin on stringer A beyond", "labs", "start")
    v.text(74, 4.5, f"treads {fr(T)} ply · 1/8 overhang, taped edge, painted", "labs", "end"); v.text(69, 3.2, "kicker", "labs", "end")
    for i in range(1, ST.n_risers + 1):
        y = ST.tread_y(i)[1] if i <= ST.n_treads else ST.y_riser_top
        v.text(y + 0.6, ST.riser_z[i] - 0.4, f"{ST.riser_z[i]:.2f}", "labs", "start", dy=3)
    v.text(30, 74, f"above tread {ST.n_treads} at {fr(ST.riser_z[ST.n_treads])} you're ducking — the top step and the landing are a crouch", "labs", "middle")
    # dims
    v.dim_v(-3.3, 0, LAND, f"{fr(LAND)} landing"); v.dim_v(8, LAND, CEILING, f"{fr(DER['landing_headroom'])} headroom — stand & turn", left=False)
    v.dim_v(31.5, ST.riser_z[ST.n_treads], CEILING, f"{fr(CEILING - ST.riser_z[ST.n_treads])} over tread {ST.n_treads}", left=False)
    v.dim_h(0, ST.y_top, 52.5, fr(ST.y_top)); v.dim_h(ST.y_top, ST.y_riser_top, 52.5, f"{fr(ST.top_run)} top run"); v.dim_h(ST.y_riser_top, ST.y_bottom, 52.5, f"{fr(ST.y_bottom - ST.y_riser_top)} run · {ST.n_treads} @ {fr(ST.run)}")
    v.dim_h(0, ST.y_bottom, -1.5 + 0, f"{fr(ST.y_bottom)} framing · {fr(Y_FIN)} to the bottom nosing — {ST.n_treads+1} risers @ {fr(ST.R)} then {fr(ST.R_top)} to the deck · {math.degrees(ST.angle):.1f}°", above=False)
    v.dim_v(m("lnd_rim").y[1] + 0.9, m("lnd_rim").z[0], m("lnd_rim").z[1], f"{fr(DER['rim_stringer_bearing'])} plumb cut = rim", left=False)
    return v.svg("Stair section through stringer B, bed wall on the left, drawn with the bed wall left like every y–z view")

FIGURES = [("d4", d4)]
CAPTION = f"Cut through stringer B. Each stringer runs {fr(ST.top_run)} under the landing: its top plumb cut, at y {fr(ST.y_top)}, is {fr(ST.plumb_cut()[1]-ST.plumb_cut()[0])} tall — close to the 2×8 rim it bears on. Stringers are dropped {fr(T)} for the ¾ plywood treads — no nosing, just a 1/8 overhang with a tape-sealed edge, painted. <b>Tread/riser joint:</b> the riser board goes on the front of each plumb cut, its bottom edge on the stringer&#8217;s horizontal cut for the tread below; that tread starts where the riser ends and butts its face. Simple butt joint, riser behind the tread, nothing notched — the nosing-to-nosing going is exactly {fr(ST.run)}. <b>Rev AE:</b> stringer A moved ¾ out onto the half-wall framing at {fr(m('stringer_a').x[0])} — the ¾ ply that used to sit between them, and behind the whole landing box, is gone, and what is left of the half-wall&#8217;s stair face is a SKIRT: <code>hw_sheath_stair</code>, one board cut to the stringers&#8217; own top line and lapping nothing. The treads and risers are trimmed back ¾ to butt it, so the finished stair is still {fr(STAIR_X[1] - STAIR_X[0])} wide and the finished wall face is still at x 107. Boards are {fr(STAIR_X[1] - STAIR_X[0])} uphill of the wall&#8217;s end and {fr(STAIR_X[1] - SKIN_X0)} past it, where they lap the skin on stringer A&#8217;s outer face; board 3 straddles the end cap at y {fr(STEP_Y)} and is notched {fr(STAIR_X[0]-SKIN_X0)} × {fr(STEP_Y - tread_y_board(3)[0])}. At the foot the stringers are notched {fr(1.5)} × {fr(3.5)} over the kicker. The {ST.n_treads+1} stair risers are {fr(ST.R)}; the {ST.n_risers}th — the sideways step from the landing onto the deck — is {fr(ST.R_top)}, because it is the framing stack over the nook header rather than a stair riser. Do not step {fr(ST.R)} off {ST.n_risers} times. Half-wall framing (dashed) sits in front of this section from this angle. Handrail on the right wall for the full run."
