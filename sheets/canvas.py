"""sheets.canvas — the drawing surface every v2 sheet draws through.

Two things it enforces, because both used to be per-sheet decisions that drifted:

  THE ROOM SHELL.  A canvas knows which model axis is across the page and which
  is up it, so it knows where the walls, the floor and the ceiling are. `shell()`
  draws them, the same weight and the same poché, on every sheet — and it draws
  them wherever the canvas runs past a room boundary, so a sheet cannot forget one.

  THE DIMENSION GUTTERS.  Dimensions are placed by SIDE and LEVEL, not by a
  coordinate: `dim_h(a, b, "bottom", 0, "107")` is the innermost run under the
  drawing, level 1 the next one out. They land outside the drawing box by
  construction, which is the rule d8a and d8b broke in the old set. Margins are
  computed from the levels actually used, so nothing is clipped and no sheet
  carries hand-tuned margin numbers.

Geometry, dimensions and labels go into separate buckets and come out as separate
<g> layers, which is what the toggles switch.
"""
from __future__ import annotations

import html

from drawings.model import CEILING, RX, RY, fr

ROOM = {"x": (0.0, RX), "y": (0.0, RY), "z": (0.0, CEILING)}
WALL_NAME = {("x", 0): "window wall", ("x", 1): "right wall",
             ("y", 0): "bed wall", ("y", 1): "closet wall",
             ("z", 0): "floor", ("z", 1): "ceiling"}

GUT_BASE, GUT_PITCH = 15.0, 24.0     # px to the first dim run, then per level
# Every figure on a page is a separate <svg> in ONE document, so their <defs> ids
# share a namespace: `url(#box)` resolves to the FIRST clipPath in the document,
# whatever svg it belongs to. That silently clipped seven figures to another
# figure's frame. Ids are numbered per canvas instead. Deterministic, because the
# build renders figures in a fixed order.
_UID = [0]
CHAR = 6.1                            # dim text width estimate, monospace 10.5px
MIN_LABEL_GAP = 13.0                  # px between two labels in the same column
E = html.escape


class Canvas:
    def __init__(self, haxis, vaxis, h0, h1, v0, v1, scale, vdown=False,
                 hflip=False, proj=None):
        self.haxis, self.vaxis = haxis, vaxis
        self.proj = proj                     # (x, y, z) → (h, v), for 3D helpers
        self.h0, self.h1, self.v0, self.v1 = h0, h1, v0, v1
        self.s, self.vdown, self.hflip = scale, vdown, hflip
        _UID[0] += 1
        self.uid = _UID[0]
        self.hatch = f"url(#hatch{self.uid})"     # render.py fills with this
        self.geom, self.dims, self.labels, self.over = [], [], [], []
        self._gut = {"left": 0, "right": 0, "top": 0, "bottom": 0}
        self._wide = {"left": 0.0, "right": 0.0}
        self._res = {"left": 0.0, "right": 0.0, "top": 0.0, "bottom": 0.0}
        self._vtext = []                     # (side, y, label) — placed in svg()

    def reserve(self, **px):
        """Keep clear space outside the drawing box for labels that sit there —
        a sheet with no dimension runs has no gutter of its own to borrow."""
        for k, v in px.items():
            self._res[k] = max(self._res[k], float(v))

    # ------------------------------------------------------------- mapping
    def X(self, h):
        return ((self.h1 - h) if self.hflip else (h - self.h0)) * self.s

    def Y(self, v):
        return ((v - self.v0) if self.vdown else (self.v1 - v)) * self.s

    @property
    def BW(self):
        return (self.h1 - self.h0) * self.s

    @property
    def BH(self):
        return (self.v1 - self.v0) * self.s

    def pt(self, h, v):
        return f"{self.X(h):.2f},{self.Y(v):.2f}"

    # ------------------------------------------------------- 3D helpers
    # Only for the things that are not solids — a floor plane under an isometric,
    # a door swing, a light symbol, a leader that must start on a real member.
    def p3(self, x, y, z):
        return self.proj(x, y, z)

    def poly3(self, pts3, cls, extra="", bucket=None):
        self.poly([self.p3(*p) for p in pts3], cls, extra, bucket)

    def line3(self, a, b, cls, bucket=None):
        (h0, v0), (h1, v1) = self.p3(*a), self.p3(*b)
        self.line(h0, v0, h1, v1, cls, bucket)

    def tag(self, at, s, dh=0.0, dv=0.0, cls="", anchor="middle"):
        """Label a real 3D point, with the text parked (dh, dv) inches away from it
        and a leader back to it. Offsets are in view inches, so a label sits the
        same distance off the drawing whatever the sheet's scale."""
        h, v = self.p3(*at)
        self.labels.append(f'<polyline class="lead" points="{self.pt(h, v)} '
                           f'{self.pt(h + dh, v + dv)}"/>')
        self.text(h + dh, v + dv, s, cls, anchor, dy=3.5)

    def text3(self, at, s, cls="", anchor="middle", dx=0, dy=0, to=None):
        h, v = self.p3(*at)
        if to:
            th, tv = self.p3(*to)
            self.labels.append(f'<polyline class="lead" points="{self.pt(th, tv)} '
                               f'{self.pt(h, v)}"/>')
        self.text(h, v, s, cls, anchor, dx=dx, dy=dy)

    # -------------------------------------------------------------- output
    def add(self, s, bucket=None):
        (bucket if bucket is not None else self.geom).append(s)

    def poly(self, pts, cls, extra="", bucket=None):
        self.add(f'<polygon class="{cls}" points="' +
                 " ".join(self.pt(h, v) for h, v in pts) + f'" {extra}/>', bucket)

    def line(self, h0, v0, h1, v1, cls, bucket=None):
        self.add(f'<line class="{cls}" x1="{self.X(h0):.2f}" y1="{self.Y(v0):.2f}"'
                 f' x2="{self.X(h1):.2f}" y2="{self.Y(v1):.2f}"/>', bucket)

    def rect(self, h0, h1, v0, v1, cls, extra="", bucket=None):
        self.poly([(h0, v0), (h1, v0), (h1, v1), (h0, v1)], cls, extra, bucket)

    def circle(self, h, v, r, cls, bucket=None):
        self.add(f'<circle class="{cls}" cx="{self.X(h):.2f}" cy="{self.Y(v):.2f}"'
                 f' r="{r * self.s:.2f}"/>', bucket)

    # --------------------------------------------------------- room shell
    def shell(self, names=True, ceiling=True):
        """Poché every wall the canvas runs past, plus the floor and ceiling."""
        for axis, lo, hi, is_h in ((self.haxis, self.h0, self.h1, True),
                                   (self.vaxis, self.v0, self.v1, False)):
            r0, r1 = ROOM[axis]
            for end, (a, b) in ((0, (lo, r0)), (1, (r1, hi))):
                if b - a <= 1e-9:
                    continue
                if axis == "z" and end == 1 and not ceiling:
                    continue
                if is_h:
                    self.rect(a, b, self.v0, self.v1, "wall")
                    self.line(r0 if end == 0 else r1, self.v0,
                              r0 if end == 0 else r1, self.v1, "walledge")
                else:
                    self.rect(self.h0, self.h1, a, b, "wall")
                    z = r0 if end == 0 else r1
                    cls = "floorline" if (axis == "z" and end == 0) else "walledge"
                    self.line(self.h0, z, self.h1, z, cls)
                if names:
                    self._wall_name(axis, end, is_h, a, b)

    def _wall_name(self, axis, end, is_h, a, b):
        mid = (a + b) / 2
        if is_h:
            self.add(f'<text class="wallname" x="{self.X(mid):.1f}" '
                     f'y="{self.BH / 2:.1f}" text-anchor="middle" '
                     f'transform="rotate(-90 {self.X(mid):.1f} {self.BH / 2:.1f})">'
                     f'{E(WALL_NAME[(axis, end)])}</text>', self.labels)
        else:
            self.add(f'<text class="wallname" x="{self.BW / 2:.1f}" '
                     f'y="{self.Y(mid) + 3.5:.1f}" text-anchor="middle">'
                     f'{E(WALL_NAME[(axis, end)])}</text>', self.labels)

    # --------------------------------------------------------- dimensions
    def _off(self, side, level):
        self._gut[side] = max(self._gut[side], level + 1)
        d = GUT_BASE + level * GUT_PITCH
        return {"top": -d, "bottom": self.BH + d, "left": -d, "right": self.BW + d}[side]

    def dim_h(self, a, b, side, level, label=None, tick=True):
        """A run measured across the page, parked in the top or bottom gutter."""
        y = self._off(side, level)
        x0, x1 = sorted((self.X(a), self.X(b)))
        t = label if label is not None else fr(abs(b - a))
        ty = y - 4 if side == "top" else y - 4
        self.dims.append(
            f'<g><line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}"'
            f' marker-start="url(#da{self.uid})" marker-end="url(#db{self.uid})"/>'
            + (f'<line x1="{x0:.1f}" y1="{y - 4:.1f}" x2="{x0:.1f}" y2="{y + 4:.1f}"/>'
               f'<line x1="{x1:.1f}" y1="{y - 4:.1f}" x2="{x1:.1f}" y2="{y + 4:.1f}"/>' if tick else "")
            + f'<text x="{(x0 + x1) / 2:.1f}" y="{ty:.1f}" text-anchor="middle">{E(t)}</text></g>')

    def dim_v(self, a, b, side, level, label=None, tick=True):
        """A run measured up the page, parked in the left or right gutter.

        The line goes at this run's own level; the TEXT is held back and placed in
        svg(), in one column beyond the outermost level used on that side. A label
        on an inner run would otherwise be written straight across the outer runs'
        lines — which is what happens on any drawing that stacks two runs whose
        midpoints are close, as the front elevation's ceiling-to-deck and
        ceiling-to-landing are."""
        x = self._off(side, level)
        y0, y1 = sorted((self.Y(a), self.Y(b)))
        t = label if label is not None else fr(abs(b - a))
        self.dims.append(
            f'<g><line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1:.1f}"'
            f' marker-start="url(#da{self.uid})" marker-end="url(#db{self.uid})"/>'
            + (f'<line x1="{x - 4:.1f}" y1="{y0:.1f}" x2="{x + 4:.1f}" y2="{y0:.1f}"/>'
               f'<line x1="{x - 4:.1f}" y1="{y1:.1f}" x2="{x + 4:.1f}" y2="{y1:.1f}"/>' if tick else "")
            + "</g>")
        self._vtext.append((side, (y0 + y1) / 2, t, x))

    def dim_chain(self, stops, side, level, labels=None):
        """Consecutive runs on one line — the way a layout is actually marked out."""
        for i, (a, b) in enumerate(zip(stops, stops[1:])):
            if abs(b - a) < 1e-6:            # two stops on the same line: no run
                continue
            lab = labels[i] if labels else None
            (self.dim_h if side in ("top", "bottom") else self.dim_v)(a, b, side, level, lab)

    # ------------------------------------------------------------- labels
    def text(self, h, v, s, cls="", anchor="middle", dx=0, dy=0, rot=None):
        x, y = self.X(h) + dx, self.Y(v) + dy
        t = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ""
        self.labels.append(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}"'
                           f' text-anchor="{anchor}"{t}>{E(s)}</text>')

    def note(self, h, v, s, to=None, cls="sm", anchor="middle", dy=0):
        """A label with an optional leader to the thing it names."""
        if to:
            self.labels.append(f'<polyline class="lead" points="{self.pt(*to)} '
                               f'{self.pt(h, v)}"/>')
        self.text(h, v, s, cls, anchor, dy=dy)

    # --------------------------------------------------------------- svg
    def _place_vtext(self):
        """Vertical dim labels, in one column clear of every run on that side.

        Built fresh on each call and never appended to self.dims, so a sheet may
        call svg() twice — compose() does, then the sheet adds its own runs and
        calls it again — and the labels are placed once, against the final gutter
        width."""
        out = []
        for side in ("left", "right"):
            rows = [(y, t, xl) for s, y, t, xl in self._vtext if s == side]
            if not rows:
                continue
            off = GUT_BASE + max(0, self._gut[side] - 1) * GUT_PITCH
            x = (-off - 6) if side == "left" else (self.BW + off + 6)
            anchor = "end" if side == "left" else "start"
            self._wide[side] = max(self._wide[side],
                                   off + 6 + max(len(t) for _y, t, _x in rows) * CHAR + 4)
            # two runs with close midpoints would stack their labels on top of
            # each other, so push them apart in the column and let the leader
            # slope back to where the run actually is
            placed, last = [], None
            for y, t, xl in sorted(rows):
                ty = y if last is None else max(y, last + MIN_LABEL_GAP)
                placed.append((y, ty, t, xl))
                last = ty
            for y, ty, t, xl in placed:
                if abs(xl - x) > 1:
                    tip = x + (3 if side == "left" else -3)
                    out.append(f'<polyline class="dimlead" points="{xl:.1f},{y:.1f} '
                               f'{tip:.1f},{ty:.1f}"/>')
                out.append(f'<text x="{x:.1f}" y="{ty:.1f}" text-anchor="{anchor}"'
                           f' dominant-baseline="middle">{E(t)}</text>')
        return out

    def svg(self, aria, extra_defs=""):
        vtext = self._place_vtext()
        ml = max(GUT_BASE + max(0, self._gut["left"] - 1) * GUT_PITCH, self._wide["left"], 12) if self._gut["left"] else 12
        mr = max(GUT_BASE + max(0, self._gut["right"] - 1) * GUT_PITCH, self._wide["right"], 12) if self._gut["right"] else 12
        mt = (GUT_BASE + max(0, self._gut["top"] - 1) * GUT_PITCH + 14) if self._gut["top"] else 14
        mb = (GUT_BASE + max(0, self._gut["bottom"] - 1) * GUT_PITCH + 14) if self._gut["bottom"] else 14
        ml, mr = max(ml, self._res["left"]), max(mr, self._res["right"])
        mt, mb = max(mt, self._res["top"]), max(mb, self._res["bottom"])
        W, H = self.BW + ml + mr, self.BH + mt + mb
        u = self.uid
        defs = ('<defs>'
                f'<marker id="da{u}" markerWidth="7" markerHeight="7" refX="1" refY="3.5" orient="auto">'
                '<path d="M7,0 L0,3.5 L7,7 z"/></marker>'
                f'<marker id="db{u}" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">'
                '<path d="M0,0 L7,3.5 L0,7 z"/></marker>'
                f'<pattern id="hatch{u}" width="6" height="6" patternUnits="userSpaceOnUse" '
                'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="hatchline"/></pattern>'
                f'<clipPath id="box{u}"><rect x="0" y="0" width="{self.BW:.0f}" height="{self.BH:.0f}"/></clipPath>'
                f'{extra_defs}</defs>')
        g = (f'<g transform="translate({ml:.1f},{mt:.1f})">'
             f'<g clip-path="url(#box{u})">{"".join(self.geom)}</g>'
             f'<g class="lay-labels">{"".join(self.labels)}</g>'
             f'<g class="lay-dims">{"".join(self.dims)}{"".join(vtext)}</g>'
             f'{"".join(self.over)}</g>')
        return (f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" '
                f'aria-label="{E(aria)}" preserveAspectRatio="xMidYMid meet">'
                f'{defs}{g}</svg>')
