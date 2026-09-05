"""Candidate F — stringers extended 9 in under the landing; all landing members 2x8."""
import sys, json
sys.path.insert(0, ".")
import yaml
from verify import expand, Stair
from svgview import View

d = yaml.safe_load(open(sys.argv[1]))
M = expand(d["members"]); d["stair"]["_stringer_depth"] = 11.25
ST = Stair(d["stair"], 58); T = ST.t
HB = 41.5; CEIL = HB - float(d["nook"].get("wrap", 0.75)); PANEL = 0.75
def U(y): return ST.underside(y)
Y_MEET = 27 - (CEIL + PANEL - U(27)) / ST.tan
PC = ST.plumb_cut(); RIM = M["lnd_rim"]; YT = ST.y_top
def soffit(y): return CEIL if y <= Y_MEET else U(y) - PANEL

def fig_plan():
    v = View(100, 133, -1.5, 34, 20, ml=130, mr=22, mt=34, mb=46, vdown=True)
    v.rect(100, 133, -1.5, 0, "wall"); v.rect(131, 133, 0, 34, "wall")
    for k in ("hw_king_a", "hw_king_b", "hw_header"): v.rect(*M[k].x, *M[k].y, "lum")
    for k in [k for k in M if k.startswith("hw_sheath")]: v.rect(*M[k].x, *M[k].y, "sheet")
    v.rect(102.75, 106.25, 3, 47, "lum", 'fill="url(#hatch)"')
    for k in ("lnd_ledger_bedwall", "lnd_ledger_rightwall", "lnd_side_member", "lnd_joist[0]", "lnd_joist[1]", "lnd_blocking[0]", "lnd_blocking[1]"): v.rect(*M[k].x, *M[k].y, "lum")
    v.rect(*RIM.x, *RIM.y, "lum", 'fill="url(#hatch)"')
    for k in ("stringer_a", "stringer_b", "stringer_c"): v.rect(*M[k].x, YT, 34, "lum", 'fill="url(#hatch)"')
    v.text(104.5, 30, "header", "lab", "middle", rot=-90)
    v.text(107.75, 9, "side member 2×8", "lab", "middle", rot=-90)
    v.text(115.5, 9, "joist 2×4", "labs", "middle", rot=-90); v.text(122.5, 9, "joist 2×4", "labs", "middle", rot=-90)
    v.text(119, 17.25, "rim 2×8 · 22½", "lab", "middle", dy=4)
    v.text(130.25, 9, "ledger 2×8, to y 18", "lab", "middle", rot=-90)
    v.text(118, 0.75, "bed-wall ledger 2×8", "labs", "middle", dy=4)
    v.text(113.4, 26.25, "2×4 blocking", "labs", "middle", dy=4); v.text(124.6, 26.25, "2×4 blocking", "labs", "middle", dy=4)
    for x, l in ((107.75, "A"), (119, "B"), (130.25, "C")): v.text(x, 30.5, l, "labk", "middle", dy=4)
    v.text(109.3, 20.6, "stringers run 9\" under the landing — top runs carry the deck", "labk", "start", dy=4)
    v.text(120, 4.5, "nook below", "labs", "middle", dy=4)
    v.dim_h(107, 131, -1.5, "24", above=True)
    v.dim_v(100.8, 0, 27, "27 landing"); v.dim_v(102.0, YT, 27, "9 top run"); v.dim_v(128.6, 16.5, 18, "1½", left=True)
    v.dim_h(107, 129.5, 28.4, "rim 22½ · HUC28 on the header and on the ledger", above=False)
    return v.svg("Plan of candidate F landing framing at z 47, bed wall at the top")

def fig_side():
    v = View(-2, 74, 0, 60, 9, ml=118, mr=26, mt=34, mb=44)
    v.rect(-2, 0, 0, 60, "wall"); v.line(-2, 0, 74, 0, "floor")
    for k in [k for k in M if k.startswith("hw_sheath_stair")]: v.rect(*M[k].y, *M[k].z, "sheet")
    v.rect(*M["hw_header"].y, *M["hw_header"].z, "dashfill")
    for k in ("hw_trimmer_a", "hw_trimmer_b", "hw_king_a", "hw_king_b"): v.rect(*M[k].y, *M[k].z, "dashfill")
    v.rect(3, 47, CEIL, HB, "fin")
    sm = M["lnd_side_member"]; v.rect(*sm.y, *sm.z, "lum2")
    for k in ("lnd_blocking[0]", "lnd_blocking[1]"): v.rect(*M[k].y, *M[k].z, "dashfill")
    v.line(0, 58, 50.75, 58, "dash"); v.text(25, 58, "loft deck 58 — beyond the half-wall", "labs", "middle", dy=-4)
    v.rect(*M["lnd_ledger_bedwall"].y, *M["lnd_ledger_bedwall"].z, "lum", 'fill="url(#hatch)"')
    v.rect(*M["lnd_joist[0]"].y, *M["lnd_joist[0]"].z, "dashfill")
    v.rect(*RIM.y, *RIM.z, "lum", 'fill="url(#hatch)"')
    v.rect(0, 27, 48.96, 49.71, "sheet"); v.rect(*M["kicker"].y, *M["kicker"].z, "lum", 'fill="url(#hatch)"')
    # stringer with the top run
    top = ST.riser_z[6] - ST.deck_t                      # 48.96
    y_edge = 27 - (top - (ST.riser_z[6] - T)) / ST.tan   # where the top-run cut meets the nosing line
    pts = [(YT, U(YT)), (YT, top), (y_edge, top), (27, ST.riser_z[6] - T)]
    for i in range(ST.n_treads, 0, -1):
        y0, y1 = ST.tread_y(i); pts += [(y0, ST.riser_z[i] - T), (y1, ST.riser_z[i] - T), (y1, ST.riser_z[i - 1] - T if i > 1 else 0)]
    pts += [(27 + U(27) / ST.tan, 0)]
    v.poly(pts, "lum", 'fill="url(#hatch)"')
    for i in range(1, ST.n_treads + 1):
        y0, y1 = ST.tread_y(i); v.rect(y0, y0 + 10.5, ST.riser_z[i] - T, ST.riser_z[i], "fin")
        v.rect(y1 - 0.75, y1, ST.riser_z[i - 1] if i > 1 else 0, ST.riser_z[i] - T, "fin")
    v.rect(27, 27.75, ST.riser_z[5], 49.71, "fin")
    v.path([(3, CEIL), (Y_MEET, CEIL), (47, soffit(47))], "soffit")
    v.text(4, CEIL, "nook ceiling 40¾", "labs", "start", dy=26)
    v.text(33, soffit(33), "soffit panel on the stringer undersides", "labs", "start", dy=13, rot=-42.6)
    for z in (43.5, 45.5, 47.5): v.out.append(f'<circle class="dot" cx="{v.X(YT - 0.7):.1f}" cy="{v.Y(z):.1f}" r="3"/>')
    v.text(YT - 1.4, 45.5, "B: 3 SDS from inside the box", "labk", "end", dy=4)
    v.text(0.75, 45.3, "ledger 2×8", "labs", "middle", rot=-90); v.text(9, 47.2, "joists beyond (run with the stringers)", "labs", "middle")
    v.text(9, 43.0, "side member 2×8 beyond", "labs", "middle")
    v.text(17.25, 45.3, "rim 2×8", "lab", "middle", rot=-90)
    v.text(26.25, 47.2, "blocking", "labs", "middle", rot=-90)
    v.text(25, 53.5, "header + facing beyond (dashed)", "labs", "middle")
    v.text(48.5, 36, "half-wall stair face beyond", "labs", "start", rot=-90)
    v.text(52, 8, "treads 5/4 · 1\"", "labs", "start"); v.text(69, 3.2, "kicker", "labs", "end")
    v.dim_v(-1.0, PC[0], PC[1], "7¼ plumb cut = rim")
    v.dim_v(72.6, 0, 49.71, "49.71 landing", left=False)
    v.dim_h(0, YT, 51.6, "18"); v.dim_h(YT, 27, 51.6, "9 top run"); v.dim_h(27, 72, 51.6, "45 run · 5 @ 9")
    v.dim_v(51.6, HB, RIM.z[1], "7.46 header ↔ rim", left=False)
    v.text(Y_MEET, CEIL, f"break y={Y_MEET:.1f}", "labk", "middle", dy=-6)
    return v.svg("Side section through stringer B for candidate F: the stringer runs 9 inches under the landing and bears full depth on a 2x8 rim")

def fig_sect20():
    y_cut = 20
    v = View(100, 133, 31, 53, 20, ml=130, mr=26, mt=30, mb=40)
    v.rect(131, 133, 31, 53, "wall"); v.rect(100, 102, 31, 53, "ghost")
    v.rect(*M["hw_trimmer_a"].x, 31, HB, "lum2")
    v.rect(102, 102.75, 31, 53, "sheet"); v.rect(106.25, 107, 31, 53, "sheet")
    v.rect(102.75, 106.25, 50.75, 53, "lum"); v.rect(102.75, 106.25, HB, 50.75, "lum", 'fill="url(#hatch)"')
    v.rect(102, 107, CEIL, HB, "fin"); v.rect(107, 131, CEIL, HB, "fin")
    v.text(119, CEIL, "flat soffit panel · face 40¾ · top 41½", "labs", "middle", dy=13)
    v.rect(*RIM.x, *RIM.z, "lum")                                        # rim face at y 18, beyond
    v.rect(129.5, 131, 41.71, 48.96, "lum2")                             # ledger end face at y 18
    for x0 in (107, 128): v.rect(x0, x0 + 1.5, RIM.z[0], 48.2, "hanger")
    v.text(110.3, 40.2, "HUC28 on the header (SD screws through the facing)", "labk", "start", dy=4)
    v.text(127.4, 40.2, "HUC28 on the ledger", "labk", "end", dy=4)
    v.rect(107, 131, 48.96, 49.71, "sheet", 'fill="url(#hatch)"')
    zs = [U(y_cut), 48.96]
    for k in ("stringer_a", "stringer_b", "stringer_c"): v.rect(*M[k].x, *zs, "lum", 'fill="url(#hatch)"')
    for x, l in ((107.75, "A"), (119, "B"), (130.25, "C")): v.text(x, 44.5, l, "labk", "middle", dy=4)
    v.text(124.5, 46.2, "rim 2×8, beyond", "lab", "middle", dy=4)
    v.text(113.4, 46.2, "rim 2×8, beyond", "lab", "middle", dy=4)
    v.text(104.5, 46, "header", "lab", "middle", rot=-90); v.text(104.5, 36.5, "trimmer beyond", "labs", "middle", rot=-90)
    v.text(119, 34.5, "stringers cut at y = 20 — A: SDS into the header · B: SDS from inside · C: on the ledger end + wall studs", "labs", "middle")
    v.dim_v(101.0, HB, 48.96, "7.46 header ↔ rim"); v.dim_v(112.5, RIM.z[0], RIM.z[1], "7¼ rim = plumb cut", left=True)
    v.dim_h(107, 131, 50.6, "24 between wall faces", above=True)
    return v.svg("Section at y 20 looking toward the bed wall, candidate F")

figs = dict(planF=fig_plan(), sideF=fig_side(), sect20F=fig_sect20())
json.dump(figs, open(sys.argv[2], "w"))
print(f"F: plumb cut {PC[0]:.2f}→{PC[1]:.2f} at y={YT}; soffit break y={Y_MEET:.2f}; far end {soffit(47):.2f}")
