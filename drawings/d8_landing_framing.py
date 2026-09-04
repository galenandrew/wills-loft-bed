"""Drawing 8 — Stair & landing framing. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "8", "Stair & landing framing"

def d8a():
    v = View(100, 133, -1.5, 34, 9, ml=110, mr=60, mt=40, mb=50, vdown=True)
    v.rect(100, 133, -1.5, 0, "wall"); v.rect(131, 133, 0, 34, "wall")
    for k in ("hw_king_a", "hw_king_b", "hw_header"): R(v, m(k), "x", "y", "lum")
    for k in ids("hw_sheath_loft_a") + ids("hw_sheath_loft_head") + ids("hw_sheath_loft_b") + ids("hw_sheath_stair_a") + ids("hw_sheath_stair_head") + ids("hw_sheath_stair_b"): R(v, m(k), "x", "y", "sheet")
    v.rect(m("hw_header").x[0], m("hw_header").x[1], NOOK_Y[0], NOOK_Y[1], "lum", HATCH)
    for k in ("lnd_ledger_bedwall", "lnd_ledger_rightwall", "lnd_side_member") + tuple(ids("lnd_joist")) + tuple(ids("lnd_blocking")): R(v, m(k), "x", "y", "lum")
    R(v, m("lnd_rim"), "x", "y", "lum", HATCH)
    for k in ("stringer_a", "stringer_b", "stringer_c"): v.rect(*m(k).x, ST.y_top, 34, "lum", HATCH)
    for x0 in (107, 128): v.rect(x0, x0 + 1.5, m("lnd_rim").y[0] - 0.4, m("lnd_rim").y[1] + 0.4, "hanger")
    v.text(104.5, 30, "header", "lab", "middle", rot=-90)
    sm = m("lnd_side_member"); v.text(107.75, (sm.y[0]+sm.y[1])/2, "side member 2×8", "lab", "middle", rot=-90)
    for k in ids("lnd_joist"): v.text((m(k).x[0]+m(k).x[1])/2, 9, "joist 2×4", "labs", "middle", rot=-90)
    rm = m("lnd_rim"); v.text(118.5, rm.y[0] + 0.75, "rim 2×8 · 22½", "lab", "middle", dy=4); v.text(109.2, rm.y[0] - 0.6, "HUC28", "labk", "start", dy=0); v.text(127.3, rm.y[0] - 0.6, "HUC28", "labk", "end", dy=0)
    v.text(130.25, 9, "ledger 2×8, to y 18", "lab", "middle", rot=-90); v.text(118, 0.75, "bed-wall ledger 2×8", "labs", "middle", dy=4)
    for k in ids("lnd_blocking"): v.text((m(k).x[0]+m(k).x[1])/2, 26.25, "2×4 blocking", "labs", "middle", dy=4)
    for x, l in ((107.75, "A"), (119, "B"), (130.25, "C")): v.text(x, 32.6, l, "labk", "middle", dy=4)
    v.text(109.3, 20.6, f"stringers run {fr(ST.top_run)} under the landing", "labk", "start", dy=4)
    v.text(120, 4.5, "nook below", "labs", "middle", dy=4)
    v.dim_h(107, 131, -1.5, "24", above=True); v.dim_v(100.8, 0, ST.landing, f"{fr(ST.landing)} landing"); v.dim_v(102.0, ST.y_top, ST.landing, f"{fr(ST.top_run)} top run")
    v.dim_v(126.4, rm.y[0], rm.y[1], "1½", left=True); v.dim_h(107, 129.5, 28.4, "rim 22½", above=False)
    return v.svg("Landing framing plan at z 47, bed wall at the top")

def d8b():
    y_cut = 20
    v = View(100, 133, 31, 53, 9, ml=120, mr=60, mt=30, mb=40)
    v.rect(131, 133, 31, 53, "wall"); v.rect(100, 102, 31, 53, "ghost")
    R(v, m("hw_trimmer_a"), "x", "z", "lum2"); v.rect(102, 102.75, 31, 53, "sheet"); v.rect(106.25, 107, 31, 53, "sheet")
    v.rect(102.75, 106.25, 50.75, 53, "lum"); v.rect(102.75, 106.25, HB, 50.75, "lum", HATCH)
    v.rect(102, 107, CEIL, HB, "fin"); v.rect(107, 131, CEIL, HB, "fin")
    v.text(119, 36.6, f"flat soffit panel · face {fr(CEIL)} · top {fr(CEIL+PANEL)}", "labs", "middle")
    rm = m("lnd_rim"); R(v, rm, "x", "z", "lum"); v.rect(129.5, 131, rm.z[0], rm.z[1], "lum2")
    for x0 in (107, 128): v.rect(x0, x0 + 1.5, rm.z[0], 48.2, "hanger")
    v.text(109, 39.6, "HUC28 on the header", "labk", "start", dy=4); v.text(109, 38.4, "SD screws through the ¾ facing", "labs", "start", dy=4); v.text(128.6, 39.6, "HUC28 on the ledger", "labk", "end", dy=4)
    v.rect(107, 131, 48.96, 49.71, "sheet", HATCH)
    for k in ("stringer_a", "stringer_b", "stringer_c"): v.rect(*m(k).x, U(y_cut), LAND - ST.deck_t, "lum", HATCH)
    for x, l in ((107.75, "A"), (119, "B"), (130.25, "C")): v.text(x, 44.5, l, "labk", "middle", dy=4)
    v.text(109.5, 47.6, "rim 2×8 beyond", "lab", "start", dy=4)
    v.text(104.5, 46, "header", "lab", "middle", rot=-90); v.text(104.5, 36.5, "trimmer beyond", "labs", "middle", rot=-90)
    v.text(119, 34.4, f"stringers cut at y = {y_cut}", "labs", "middle")
    v.dim_v(101.0, HB, rm.z[1], f"{fr(rm.z[1]-HB)} header ↔ rim"); v.dim_v(125.5, rm.z[0], rm.z[1], "7¼ rim = plumb cut", left=True)
    v.dim_h(107, 131, 50.6, "24 between wall faces", above=True)
    return v.svg("Section at y 20 through the stringers' top runs, looking toward the bed wall")

FIGURES = [("d8a", d8a), ("d8b", d8b)]
CAPTION = "Section at y 20 cuts the three top runs: A is fixed by SDS into the header through the facing, B by SDS from inside the box through the rim, C bears on the ledger end and screws to the right-wall studs. The landing box is four 2×8s at one elevation (41.71→48.96) — rim, side member, bed-wall ledger, right-wall ledger — with two 2×4 joists running with the stringers and 2×4 blocking flush with riser 6. The rim hangs on concealed-flange HUC28s: into the header (SD screws through the ¾ facing) and into the right-wall ledger. <b>Framing order:</b> ledgers → side member (6 × ¼×6 SDS through the facing) → HUC28s and rim → 2 × A35 at the side-member/rim corner → LUS24s and joists → stringer A (4 × ¼×4½ SDS into the header over its top run, 2 toe-screws to the rim), stringer C (4 × ¼×4½ SDS into right-wall studs, 2 toe-screws to the ledger end), then stringer B (3 × ¼×3½ SDS from inside the box through the rim) → kicker → blocking → deck ply, treads, risers."
