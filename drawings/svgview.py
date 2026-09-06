import html
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
        # display at most ~1.3× the drawn size so small views don't blow their text up
        style = f' style="max-width:{min(1000, self.W * 1.3):.0f}px;margin:0 auto"'
        return f'<svg viewBox="0 0 {self.W:.0f} {self.H:.0f}" role="img" aria-label="{html.escape(aria)}"{style}>{defs}' + "".join(self.out) + '</svg>'

