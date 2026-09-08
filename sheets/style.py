"""sheets.style — one palette, stated once, used by the CSS and by the shader.

Face shading on an axonometric multiplies the fill, so the colours have to exist
in Python as well as in CSS; everything else reads them from the variables here.
"""

PALETTE = {
    # layer fills: framing is warm, finish is cool. Two glances, two layers.
    # Fills carry to the printed page and to a phone in a dusty room, so they are
    # a shade stronger than they look on screen, and every outline is a real line.
    "framing":   ("#e7d8b8", "#6f5930"),
    "finish":    ("#ccd8de", "#4f6874"),
    "context":   ("#efedea", "#9d988e"),
    "wall":      ("#3b352c", "#3b352c"),
    "electric":  ("#fdeceb", "#c0392b"),
}
INK, INK2, INK3 = "#23231f", "#5f5d56", "#8a877e"
DIM = "#1f4e9c"          # dimension blue — the pencil colour the old set used
GHOST = "#b06a3b"        # what stands in front of a cut, or under a plan
BG, CARD, LINE = "#fbfaf7", "#ffffff", "#e0ddd4"


def shade(hexcolor, k):
    """Multiply a fill toward white/black by k (1 = unchanged). Used only where a
    view shows more than one face of the same solid — an axonometric."""
    k = max(0.0, min(1.4, k))
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    f = lambda c: max(0, min(255, int(round(c * k))))
    return f"#{f(r):02x}{f(g):02x}{f(b):02x}"


def svg_css():
    fr_f, fr_s = PALETTE["framing"]
    fi_f, fi_s = PALETTE["finish"]
    cx_f, cx_s = PALETTE["context"]
    return f"""
.dwg svg{{display:block;width:100%;height:auto;font-family:ui-sans-serif,system-ui,sans-serif}}
.pc{{stroke-linejoin:round}}
.pc polygon,.pc path{{vector-effect:non-scaling-stroke}}
[data-l="framing"] .fill{{fill:{fr_f};stroke:{fr_s};stroke-width:1}}
[data-l="finish"] .fill{{fill:{fi_f};stroke:{fi_s};stroke-width:1}}
[data-l="context"] .fill{{fill:{cx_f};stroke:{cx_s};stroke-width:.9;stroke-dasharray:4 3}}
.pc .sil{{fill:none;stroke:{INK};stroke-width:1.2}}
[data-l="context"] .sil{{stroke:{cx_s};stroke-width:.9;stroke-dasharray:4 3}}
.pc .cut{{stroke:{INK};stroke-width:1.6;fill:{fr_f}}}
[data-l="finish"] .cut{{fill:{fi_f}}}[data-l="context"] .cut{{fill:{cx_f}}}
.pc .hatch{{fill:url(#hatch);stroke:none;pointer-events:none}}
.pc .ghost{{fill:none;stroke:{GHOST};stroke-width:.9;stroke-dasharray:5 3}}
.mode-ghost .fill,.mode-ghost .sil,.mode-ghost .hatch{{display:none}}
.mode-outline .fill,.mode-outline .hatch{{display:none}}
.mode-outline .sil{{stroke:{INK2};stroke-width:.9;stroke-dasharray:6 4}}
.mode-flat .hatch{{display:none}}
.wall{{fill:{PALETTE["wall"][0]};stroke:none}}
.walledge{{stroke:{PALETTE["wall"][0]};stroke-width:2;fill:none}}
.floorline{{stroke:{PALETTE["wall"][0]};stroke-width:2.5;fill:none}}
.ceilline{{stroke:{INK2};stroke-width:1.2;fill:none;stroke-dasharray:none}}
.gridline{{stroke:{LINE};stroke-width:.7;fill:none}}
.elec{{fill:none;stroke:{PALETTE["electric"][1]};stroke-width:1.6}}
.elecf{{fill:{PALETTE["electric"][0]};stroke:{PALETTE["electric"][1]};stroke-width:1.4}}
.lay-dims line{{stroke:{DIM};stroke-width:.9}}
.lay-dims text{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10.5px;fill:{DIM}}}
.lay-dims marker path{{fill:{DIM}}}
.lay-labels text{{font-size:11px;fill:{INK}}}
.lay-labels .sm{{font-size:10px;fill:{INK2}}}
.lay-labels .lead{{stroke:{INK3};stroke-width:.8;fill:none}}
.lay-labels .wallname{{font-size:10px;fill:#cfc9bd;letter-spacing:.06em}}
.hatchline{{stroke:{PALETTE["framing"][1]};stroke-width:.55}}
"""
