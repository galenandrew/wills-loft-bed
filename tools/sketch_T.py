"""Render the Rev T landing-rim decision as inline SVG.

Historical: defaults to the frozen `archive/dimensions-T.yaml`. HB/JAMB/CEIL below
and the figure functions' literals are pinned to that decision; passing the live
dimensions.yaml as the second argument mixes current geometry with Rev T numbers
rather than reproducing anything real."""
import sys, html, json
sys.path.insert(0, ".")
import yaml
from verify import expand, Stair

d = yaml.safe_load(open(sys.argv[2] if len(sys.argv) > 2 else "archive/dimensions-T.yaml"))
M = expand(d["members"]); d["stair"]["_stringer_depth"] = 11.25
ST = Stair(d["stair"], 58); T = ST.t
HB = 41.5; JAMB = 0.75; CEIL = HB - JAMB          # jambed nook head, decided
def U(y): return ST.underside(y)
Y_BREAK = 27 - (HB - U(27)) / ST.tan               # where the stringer-underside soffit line reaches the flat ceiling

class View:
    def __init__(self, h0, h1, v0, v1, s, ml=120, mr=24, mt=30, mb=44, vdown=False):
        self.h0, self.h1, self.v0, self.v1, self.s, self.vdown = h0, h1, v0, v1, s, vdown
        self.ml, self.mr, self.mt, self.mb = ml, mr, mt, mb
        self.W = ml + (h1 - h0) * s + mr; self.H = mt + (v1 - v0) * s + mb; self.out = []
    def X(self, h): return self.ml + (h - self.h0) * self.s
    def Y(self, v): return self.mt + ((v - self.v0) if self.vdown else (self.v1 - v)) * self.s
    def rect(self, h0, h1, v0, v1, cls="lum", extra=""):
        h0, h1 = max(h0, self.h0), min(h1, self.h1); v0, v1 = max(v0, self.v0), min(v1, self.v1)
        if h1 <= h0 or v1 <= v0: return
        top = self.Y(v0) if self.vdown else self.Y(v1)
        self.out.append(f'<rect class="{cls}" x="{self.X(h0):.1f}" y="{top:.1f}" width="{(h1-h0)*self.s:.1f}" height="{(v1-v0)*self.s:.1f}" {extra}/>')
    def poly(self, pts, cls, extra=""):
        self.out.append(f'<polygon class="{cls}" points="' + " ".join(f"{self.X(h):.1f},{self.Y(v):.1f}" for h, v in pts) + f'" {extra}/>')
    def path(self, pts, cls):
        self.out.append(f'<polyline class="{cls}" points="' + " ".join(f"{self.X(h):.1f},{self.Y(v):.1f}" for h, v in pts) + '"/>')
    def line(self, h0, v0, h1, v1, cls="ink"):
        self.out.append(f'<line class="{cls}" x1="{self.X(h0):.1f}" y1="{self.Y(v0):.1f}" x2="{self.X(h1):.1f}" y2="{self.Y(v1):.1f}"/>')
    def text(self, h, v, s, cls="lab", anchor="start", dx=0, dy=0, rot=None):
        x, y = self.X(h) + dx, self.Y(v) + dy
        t = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ""
        self.out.append(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}"{t}>{html.escape(s)}</text>')
    def dim_h(self, h0, h1, v, label, above=True):
        y = self.Y(v); x0, x1 = self.X(h0), self.X(h1)
        self.out.append(f'<g class="dim"><line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" marker-start="url(#da)" marker-end="url(#db)"/>'
                        f'<line x1="{x0:.1f}" y1="{y-5:.1f}" x2="{x0:.1f}" y2="{y+5:.1f}"/><line x1="{x1:.1f}" y1="{y-5:.1f}" x2="{x1:.1f}" y2="{y+5:.1f}"/>'
                        f'<text x="{(x0+x1)/2:.1f}" y="{y + (-5 if above else 13):.1f}" text-anchor="middle">{html.escape(label)}</text></g>')
    def dim_v(self, h, v0, v1, label, left=True, cls=""):
        x = self.X(h); y0, y1 = sorted((self.Y(v1), self.Y(v0))); tx = x - 6 if left else x + 6
        self.out.append(f'<g class="dim {cls}"><line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1:.1f}" marker-start="url(#da)" marker-end="url(#db)"/>'
                        f'<line x1="{x-5:.1f}" y1="{y0:.1f}" x2="{x+5:.1f}" y2="{y0:.1f}"/><line x1="{x-5:.1f}" y1="{y1:.1f}" x2="{x+5:.1f}" y2="{y1:.1f}"/>'
                        f'<text x="{tx:.1f}" y="{(y0+y1)/2:.1f}" text-anchor="{"end" if left else "start"}" dominant-baseline="middle">{html.escape(label)}</text></g>')
    def svg(self, aria):
        defs = ('<defs><marker id="da" markerWidth="7" markerHeight="7" refX="1" refY="3.5" orient="auto"><path d="M7,0 L0,3.5 L7,7 z"/></marker>'
                '<marker id="db" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 z"/></marker>'
                '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="hatchline"/></pattern>'
                '<pattern id="bad" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><line x1="0" y1="0" x2="0" y2="5" class="badline"/></pattern></defs>')
        return f'<svg viewBox="0 0 {self.W:.0f} {self.H:.0f}" role="img" aria-label="{html.escape(aria)}">{defs}' + "".join(self.out) + '</svg>'

PC = ST.plumb_cut()                                   # [33.42, 40.43]
RIM = M["lnd_rim"]

# ============================================================ FIG 1 · plan, cut at z 47
def fig_plan():
    v = View(100, 133, -1.5, 34, 20, ml=130, mr=22, mt=34, mb=46, vdown=True)
    v.rect(100, 133, -1.5, 0, "wall"); v.rect(131, 133, 0, 34, "wall")
    for k in ("hw_king_a", "hw_king_b", "hw_header"): v.rect(*M[k].x, *M[k].y, "lum")
    for k in ("hw_sheath_loft_a", "hw_sheath_loft_head", "hw_sheath_loft_b", "hw_sheath_stair_a", "hw_sheath_stair_head", "hw_sheath_stair_b"):
        v.rect(*M[k].x, *M[k].y, "sheet")
    v.rect(102.75, 106.25, 3, 47, "lum", 'fill="url(#hatch)"')
    for k in ("lnd_ledger_bedwall", "lnd_ledger_rightwall", "lnd_side_member", "lnd_joist[0]", "lnd_joist[1]"): v.rect(*M[k].x, *M[k].y, "lum")
    v.rect(*RIM.x, *RIM.y, "lum", 'fill="url(#hatch)"')
    for k in ("stringer_a", "stringer_b", "stringer_c"): v.rect(*M[k].x, 27, 34, "lum2")
    v.text(104.5, 30, "header", "lab", "middle", rot=-90)
    v.text(107.75, 13, "side member 2×8", "lab", "middle", rot=-90)
    v.text(119, 8.75, "joist", "labs", "middle", dy=4); v.text(119, 17.75, "joist", "labs", "middle", dy=4)
    v.text(118, 26.25, "rim 2×12", "lab", "middle", dy=4)
    v.text(130.25, 13, "right-wall ledger 2×4", "lab", "middle", rot=-90)
    v.text(118, 0.75, "bed-wall ledger 2×4", "labs", "middle", dy=4)
    for x, l in ((107.75, "A"), (119, "B"), (130.25, "C")): v.text(x, 30.5, l, "labk", "middle", dy=4)
    v.text(112, 33.2, "stringers — plumb cuts against the rim face", "labs", "start")
    v.text(120, 4.5, "nook below this framing", "labs", "middle", dy=4)
    v.text(106.6, 22, "¾ facing", "labs", "end", dy=4)
    v.dim_h(107, 131, -1.5, "24", above=True); v.dim_h(107, 129.5, 28.4, "rim 22½ as drawn", above=False)
    v.dim_v(100.8, 0, 27, "27 landing"); v.dim_v(128.6, 25.5, 27, "1½", left=True)
    return v.svg("Plan of the landing framing cut at 47 inches, bed wall at the top as in Drawing 1")

# ============================================================ FIG 2 · side section at x = 119, through stringer B
def fig_side():
    v = View(-2, 74, 0, 60, 9, ml=118, mr=26, mt=34, mb=44)
    v.rect(-2, 0, 0, 60, "wall")
    v.line(-2, 0, 74, 0, "floor")
    # beyond the cut: the half-wall's stair face, header behind it, side member, deck line
    for k in ("hw_sheath_stair_a", "hw_sheath_stair_head", "hw_sheath_stair_b"): v.rect(*M[k].y, *M[k].z, "sheet")
    v.rect(*M["hw_header"].y, *M["hw_header"].z, "dashfill")
    for k in ("hw_trimmer_a", "hw_trimmer_b", "hw_king_a", "hw_king_b"): v.rect(*M[k].y, *M[k].z, "dashfill")
    v.rect(3, 47, CEIL, HB, "fin")                                   # head jamb, beyond
    sm = M["lnd_side_member"]; v.rect(*sm.y, *sm.z, "lum2")
    v.line(0, 58, 50.75, 58, "dash"); v.text(25, 58, "loft deck 58 — beyond the half-wall", "labs", "middle", dy=-4)
    # cut members
    for k in ("lnd_ledger_bedwall", "lnd_joist[0]", "lnd_joist[1]"): v.rect(*M[k].y, *M[k].z, "lum", 'fill="url(#hatch)"')
    v.rect(*RIM.y, *RIM.z, "lum", 'fill="url(#hatch)"')
    v.rect(0, 27, 48.96, 49.71, "sheet")
    v.rect(*M["kicker"].y, *M["kicker"].z, "lum", 'fill="url(#hatch)"')
    # stringer B profile (dropped by the tread thickness)
    pts = [(27, U(27)), (27, PC[1])]
    for i in range(ST.n_treads, 0, -1):
        y0, y1 = ST.tread_y(i); pts += [(y1, ST.riser_z[i] - T), (y1, ST.riser_z[i - 1] - T if i > 1 else 0)]
    y_floor = 27 + U(27) / ST.tan
    pts += [(y_floor, 0)]
    v.poly(pts, "lum", 'fill="url(#hatch)"')
    # treads and risers
    for i in range(1, ST.n_treads + 1):
        y0, y1 = ST.tread_y(i); v.rect(y0, y0 + 10.5, ST.riser_z[i] - T, ST.riser_z[i], "fin")
        yr = y1; zlo = ST.riser_z[i - 1] if i > 1 else 0
        v.rect(yr - 0.75, yr, zlo, ST.riser_z[i] - T, "fin")
    v.rect(27, 27.75, ST.riser_z[5], 49.71, "fin")                     # riser 6 on the rim face
    # soffit: flat at CEIL to the break, then on the stringer undersides
    v.path([(3, CEIL), (Y_BREAK, CEIL), (47, U(47) - 0.75)], "soffit")
    v.text(4, CEIL, "nook ceiling 40¾ (jambed)", "labs", "start", dy=26)
    v.text(33, U(33) - 0.75, "soffit panel on the stringer undersides", "labs", "start", dy=13, rot=-42.6)
    # LSC connector at the stringer top
    v.path([(27, PC[1] + 5.5), (27, PC[1]), (31.5, PC[1] - 4.1)], "hanger")
    v.text(27.6, PC[1] + 5.3, "LSC", "labk", "start", dy=4)
    # Rev T's phantom
    v.rect(27, 27.4, PC[1] + 1, 49.71, "bad")
    v.text(28.6, 44.3, "Rev T draws the stringer to 49.7 — no wood above the tread-5 cut", "labb", "start", dy=4)
    # labels
    v.text(0.75, 47.2, "ledger", "labs", "middle", rot=-90)
    v.text(8.75, 47.2, "joist", "labs", "middle", rot=-90); v.text(17.75, 47.2, "joist", "labs", "middle", rot=-90)
    v.text(13.5, 43.0, "side member 2×8 beyond", "labs", "middle")
    v.text(26.25, 45.6, "rim 2×12", "lab", "middle", rot=-90)
    v.text(25, 53.5, "header + facing beyond (dashed)", "labs", "middle")
    v.text(48.5, 36, "half-wall stair face beyond", "labs", "start", rot=-90)
    v.text(52, 8, "treads 5/4 · 1\"", "labs", "start"); v.text(69, 3.2, "kicker", "labs", "end")
    v.text(46, 0, "floor", "labs", "start", dy=-4)
    # dims
    v.dim_v(-1.0, PC[0], PC[1], "7.0 plumb cut")
    v.dim_v(23.6, RIM.z[0], PC[1], "2.72 overlap", left=True)
    v.dim_v(72.6, 0, 49.71, "49.71 landing", left=False)
    v.dim_h(0, 27, 51.6, "27 landing"); v.dim_h(27, 72, 51.6, "45 run · 5 @ 9")
    v.dim_v(51.6, HB, RIM.z[1], "7.46 header ↔ rim", left=False)
    return v.svg("Side section through stringer B at x = 119, bed wall at left, showing the stringer's 7 inch plumb cut against the 2×12 rim")

# ============================================================ FIG 3 · elevation from the stair, Rev T vs Option E
def fig_rim(opt):
    v = View(100, 133, 31, 53, 20, ml=130, mr=26, mt=30, mb=40)
    v.rect(131, 133, 31, 53, "wall"); v.rect(100, 102, 31, 53, "ghost")
    # beyond the header, below it: trimmer A and the sheathing strips at y 0–3
    v.rect(*M["hw_trimmer_a"].x, 31, HB, "lum2")
    v.rect(102, 102.75, 31, 53, "sheet"); v.rect(106.25, 107, 31, 53, "sheet")
    v.rect(102.75, 106.25, 50.75, 53, "lum")
    v.rect(102.75, 106.25, HB, 50.75, "lum", 'fill="url(#hatch)"')
    v.rect(102, 107, CEIL, HB, "fin")
    v.line(107, CEIL, 131, CEIL, "dash"); v.text(119, CEIL, "nook ceiling 40¾", "labs", "middle", dy=13)
    v.rect(107, 131, 48.96, 49.71, "sheet")
    v.rect(*RIM.x, *RIM.z, "lum")
    v.text(124.5, 45.2, "rim 2×12 · 22½", "lab", "middle", dy=4)
    if opt == "T":
        v.rect(129.5, 131, 45.46, 48.96, "lum", 'fill="url(#hatch)"')
        v.rect(107, 108.5, RIM.z[0], 47.5, "hanger"); v.rect(107, 108.5, RIM.z[0], HB, "bad")
        v.text(109, 39.4, "hanger seat 3.79 below the header — flange nails hit air", "labb", "start", dy=4)
        v.text(128.9, 43.6, "2×12 end into a 2×4 face — 31% engaged", "labb", "end", dy=4)
        v.text(130.25, 36.2, "C: nothing behind", "labb", "middle", rot=-90)
        v.text(116, 47.7, "'11¼ bearing face for the stringers'", "labb", "middle", dy=-4)
        v.text(130.25, 47.2, "2×4", "labs", "middle", rot=-90)
    else:
        v.rect(129.5, 131, 41.71, 48.96, "lum", 'fill="url(#hatch)"')
        v.text(130.25, 45.3, "2×8 ledger", "labs", "middle", rot=-90)
        for x0 in (107, 128):
            v.rect(x0, x0 + 1.5, 42.2, 48.4, "tie")
        v.text(109, 43.3, "A35 ×2 to the side member, behind", "labk", "start", dy=4)
        v.text(127.4, 43.3, "A35 ×2 to the ledger", "labk", "end", dy=4)
        for z in (43.5, 45.5, 47.5): v.out.append(f'<circle class="dot" cx="{v.X(107.75):.1f}" cy="{v.Y(z):.1f}" r="3"/>')
        v.text(109, 41.6, "3 × ¼×4½ SDS toe-screwed into the header through the facing", "labs", "start", dy=4)
        for k in ("stringer_a", "stringer_b", "stringer_c"):
            m = M[k]; v.rect(m.x[0] - 0.4, m.x[1] + 0.4, PC[1], PC[1] + 5.5, "hanger")
        v.text(113.5, 47.4, "LSC at each stringer", "labk", "middle", dy=4)
    for k in ("stringer_a", "stringer_b", "stringer_c"): v.rect(*M[k].x, PC[0], PC[1], "front")
    for x, l in ((107.75, "A"), (119, "B"), (130.25, "C")): v.text(x, 32.3, l, "labk", "middle", dy=4)
    v.text(104.5, 46, "header", "lab", "middle", rot=-90); v.text(104.5, 36.5, "trimmer beyond", "labs", "middle", rot=-90)
    v.dim_v(101.0, HB, 48.96, "7.46 header ↔ rim")
    v.dim_v(112.5, PC[0], PC[1], "7.0 plumb cuts", left=True)
    v.dim_h(107, 131, 50.6, "24 between wall faces", above=True)
    return v.svg(f"Elevation of the landing rim from the stair, {'as drawn in Rev T' if opt == 'T' else 'Option E'}")

# ============================================================ FIG 4 · nook head with jambs (decided)
def fig_nook():
    v = View(100, 133, 36.5, 52, 20, ml=130, mr=26, mt=30, mb=40)
    v.rect(131, 133, 36.5, 52, "wall"); v.rect(100, 102, 36.5, 52, "ghost")
    v.rect(102.75, 106.25, 36.5, HB, "lum2")
    v.rect(102, 102.75, 36.5, 52, "sheet"); v.rect(106.25, 107, 36.5, 52, "sheet")
    v.rect(102.75, 106.25, HB, 50.75, "lum", 'fill="url(#hatch)"'); v.rect(102.75, 106.25, 50.75, 52, "lum")
    sm = M["lnd_side_member"]; v.rect(*sm.x, *sm.z, "lum", 'fill="url(#hatch)"')
    j = M["lnd_joist[0]"]; v.rect(*j.x, *j.z, "lum2")
    v.rect(107, 131, 48.96, 49.71, "sheet")
    v.rect(129.5, 131, 41.71, 48.96, "lum", 'fill="url(#hatch)"')
    v.rect(102, 107, CEIL, HB, "fin"); v.rect(107, 131, CEIL, HB, "fin")
    v.text(104.5, CEIL + 0.375, "head jamb ¾", "labs", "middle", dy=3)
    v.text(119, CEIL + 0.375, "¾ soffit panel · face at 40¾, flush with the jamb", "labs", "middle", dy=3)
    v.text(109.1, 42.6, "0.21 clear under the side member", "labk", "start", dy=4)
    v.text(119, 38.2, "finished opening 42½ × 40¾", "labk", "middle")
    v.text(104.5, 46, "header", "lab", "middle", rot=-90); v.text(104.5, 39, "trimmer beyond", "labs", "middle", rot=-90)
    v.text(107.75, 45.3, "side member", "lab", "middle", rot=-90)
    v.text(119, 47.2, "landing joist beyond", "labs", "middle", dy=4)
    v.text(130.25, 45.3, "2×8 ledger", "labs", "middle", rot=-90)
    v.text(119, 50.5, "landing deck 49.71", "labs", "middle")
    v.dim_v(101.2, CEIL, 50.75, "header + jamb")
    v.dim_h(107, 131, 37.2, "24 nook depth", above=False)
    return v.svg("Section through the nook head at y = 12 with the jambed finish")

figs = dict(plan=fig_plan(), side=fig_side(), rimT=fig_rim("T"), rimE=fig_rim("E"), nook=fig_nook())
json.dump(figs, open(sys.argv[1], "w"))
print(f"plumb cut {PC[0]:.2f}→{PC[1]:.2f} · overlap with rim {RIM.z[0]:.2f}→{PC[1]:.2f} = {PC[1]-RIM.z[0]:.2f} · soffit break y={Y_BREAK:.2f} · far end {U(47)-0.75:.2f}")
