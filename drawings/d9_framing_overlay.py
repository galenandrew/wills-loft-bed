"""Drawing 9 — Framing overlay · half-wall + landing. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "9", "Framing overlay · half-wall + landing"

STRINGER_CUT = 51  # 1" past hw_king_b's far edge (50) — the drawn stub crosses both trimmer and king before breaking

def break_line(y, z0, z1, n=4, amp=0.6):
    """Break-line symbol: a zigzag from (y, z0) to (y, z1) showing a member cut off short of its true end."""
    return [(y + (amp if i % 2 else -amp), z0 + (z1 - z0) * i / n) for i in range(1, n)]

def d9():
    v = View(-2, 52, 0, 66, 7, ml=90, mr=70, mt=34, mb=44)
    v.rect(-2, 0, 0, 66, "wall"); v.line(-2, 0, 52, 0, "floor")
    half_wall_yz(v)
    R(v, m("deck_rim"), "y", "z", "lum2"); R(v, m("deck_ply"), "y", "z", "sheet"); R(v, m("beam"), "y", "z", "lum"); R(v, m("beam_wrap_face"), "y", "z", "fin")
    for k in ("lnd_side_member", "lnd_rim", "lnd_ledger_bedwall"): R(v, m(k), "y", "z", "green")
    for k in ids("lnd_joist"): R(v, m(k), "y", "z", "greend")
    R(v, m("lnd_ply"), "y", "z", "green")
    top_z, bot_z = ST.top_edge(STRINGER_CUT), U(STRINGER_CUT)
    stringer_body = [p for p in stringer_pts() if p[0] <= STRINGER_CUT]
    v.poly(stringer_body + [(STRINGER_CUT, top_z)] + break_line(STRINGER_CUT, top_z, bot_z) + [(STRINGER_CUT, bot_z)], "green")
    # connection callouts
    def co(n, y, z):
        v.out.append(f'<circle class="co" cx="{v.X(y):.1f}" cy="{v.Y(z):.1f}" r="9"/><text class="cot" x="{v.X(y):.1f}" y="{v.Y(z)+4:.1f}" text-anchor="middle">{n}</text>')
    co(1, 9, 45.3); co(2, 17.25, 45.3); co(3, 22.5, 45.3); co(4, 48.5, 20); co(5, 16.5, 41); co(6, 1.5, 47.2)
    v.text(25, 64.6, "SANDWICH HEADER — 2×10 + ½ ply + 2×10 = 3½ · bottom 41½ · 16d @ 12 o.c., two rows", "labs", "middle")
    v.text(0.75, 25, "king", "labs", "middle", rot=-90); v.text(2.25, 25, "trim", "labs", "middle", rot=-90); v.text(47.75, 25, "trim", "labs", "middle", rot=-90); v.text(49.25, 25, "king", "labs", "middle", rot=-90)
    v.text(36, 30, "stringer A", "labk", "start")
    v.dim_h(0, ST.y_top, -1.5, fr(ST.y_top), above=False); v.dim_h(ST.y_top, ST.y_riser_top, -1.5, f"{fr(ST.top_run)}", above=False); v.dim_h(ST.y_riser_top, 52, -1.5, "stair run →", above=False)
    v.dim_h(NOOK_Y[0], NOOK_Y[1], 8, f"{fr(NOOK_Y[1]-NOOK_Y[0])} nook opening")
    return v.svg("Framing overlay: half-wall framing with the landing box and stringer A drawn to one datum, bed wall on the left")

FIGURES = [("d9", d9)]
CAPTION = f"Half-wall framing and the landing/stair framing drawn to one datum. <b>Rev AE:</b> stringer A and the whole landing box land on the half-wall framing at x {fr(m('stringer_a').x[0])} — there is no ¾ facing between them any more, so every screw here is an inch shorter for the same penetration. Connection points: ➊ side member → header, 6 × ¼×4 SDS · ➋ rim → header, HUC28 · ➌ stringer A → header, 4 × ¼×3½ SDS over y 18→27 · ➍ stringer A → far jamb pack at {fr(m('hw_king_b').y[0])}→{fr(m('hw_king_b').y[1])}, 2 × ¼×3½ SDS into the king and 2 into the trimmer · ➎ side member → rim, 2 × A35 · ➏ bed-wall ledger, lags into studs. Not in this view: rim → right-wall ledger HUC28, joists on LUS24s. Every one of these is a rule in dimensions.yaml and passes verify.py."
