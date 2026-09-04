"""Drawing 4 — Stair section. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "4", "Stair section"

def d4():
    v = View(-4, 76, 0, CEILING + 1, 5.6, ml=130, mr=70, mt=28, mb=44)
    v.rect(-2, 0, 0, CEILING, "wall"); v.line(-2, CEILING, 76, CEILING, "floor"); v.line(-2, 0, 76, 0, "floor")
    v.line(0, DECK, m("beam_wrap_face").y[1], DECK, "dash"); v.text(2, DECK, f"loft deck {fr(DECK)} — beyond the half-wall", "labs", "start", dy=-4)
    v.rect(m("beam").y[0], m("beam_wrap_face").y[1], DECK, m("beam").z[1], "dashfill"); v.text(52, 60.5, "beam end, beyond", "labs", "start")
    R(v, m("lnd_side_member"), "y", "z", "lum2"); R(v, m("lnd_joist[0]"), "y", "z", "dashfill"); R(v, m("lnd_blocking[0]"), "y", "z", "dashfill")
    R(v, m("lnd_ledger_bedwall"), "y", "z", "lum", HATCH); R(v, m("lnd_rim"), "y", "z", "lum", HATCH)
    R(v, m("lnd_ply"), "y", "z", "fin")  # the member now carries its own 1/8 nose over riser 6 (Rev W)
    R(v, m("kicker"), "y", "z", "lum", HATCH)
    v.poly(stringer_pts(), "lum", HATCH); draw_treads(v)
    # half-wall framing, in front of the section cut from this angle — shown as a transparent outline so it doesn't hide the stair
    for k in ("hw_sheath_stair_a", "hw_sheath_stair_head", "hw_sheath_stair_b", "hw_header", "hw_trimmer_a", "hw_trimmer_b", "hw_king_a", "hw_king_b"):
        R(v, m(k), "y", "z", "dashfill")
    # labels
    v.text(-1, 62, "bed wall", "labw", "middle", rot=-90)
    v.text(52, 8, f"treads {fr(T)} ply · 1/8 overhang, taped edge, painted", "labs", "start"); v.text(69, 3.2, "kicker", "labs", "end")
    for i in range(1, ST.n_risers + 1):
        y = ST.tread_y(i)[1] if i <= ST.n_treads else ST.y_riser_top
        v.text(y + 0.6, ST.riser_z[i] - 0.4, f"{ST.riser_z[i]:.2f}", "labs", "start", dy=3)
    v.text(36, 74, "above about 38\" of tread you're ducking — the top two steps and the landing are a crouch", "labs", "start")
    # dims
    v.dim_v(-3.3, 0, LAND, f"{fr(LAND)} landing"); v.dim_v(8, LAND, CEILING, f"{fr(DER['landing_headroom'])} headroom — stand & turn", left=False)
    v.dim_v(31.5, ST.riser_z[ST.n_treads], CEILING, f"{fr(CEILING - ST.riser_z[ST.n_treads])} over tread {ST.n_treads}", left=False)
    v.dim_h(0, ST.y_top, 52.5, fr(ST.y_top)); v.dim_h(ST.y_top, ST.y_riser_top, 52.5, f"{fr(ST.top_run)} top run"); v.dim_h(ST.y_riser_top, ST.y_bottom, 52.5, f"{fr(ST.y_bottom - ST.y_riser_top)} run · {ST.n_treads} @ {fr(ST.run)}")
    v.dim_h(0, ST.y_bottom, -1.5 + 0, f"{fr(ST.y_bottom)} framing · {fr(Y_FIN)} to the bottom nosing — {ST.n_risers} risers @ {ST.R:.3f} · {math.degrees(ST.angle):.1f}°", above=False)
    v.dim_v(m("lnd_rim").y[1] + 0.9, m("lnd_rim").z[0], m("lnd_rim").z[1], f"{fr(DER['rim_stringer_bearing'])} plumb cut = rim", left=False)
    return v.svg("Stair section through stringer B, bed wall on the left, drawn with the bed wall left like every y–z view")

FIGURES = [("d4", d4)]
CAPTION = f"Cut through stringer B. Each stringer runs {fr(ST.top_run)} under the landing: its top plumb cut, at y {fr(ST.y_top)}, is {fr(ST.plumb_cut()[1]-ST.plumb_cut()[0])} tall — close to the 2×8 rim it bears on. Stringers are dropped {fr(T)} for the ¾ plywood treads — no nosing, just a 1/8 overhang with a tape-sealed edge, painted. <b>Tread/riser joint:</b> the riser board goes on the front of each plumb cut, its bottom edge on the stringer&#8217;s horizontal cut for the tread below; that tread starts where the riser ends and butts its face. Simple butt joint, riser behind the tread, nothing notched — every board is a full {fr(24)} wide and the nosing-to-nosing going is exactly {fr(ST.run)}. At the foot the stringers are notched {fr(1.5)} × {fr(3.5)} over the kicker. All seven risers are {ST.R:.3f}; the last is the sideways step from the landing onto the deck. Half-wall framing (dashed) sits in front of this section from this angle. Handrail on the right wall for the full run."
