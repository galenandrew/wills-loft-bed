"""sheets.electrical — the devices, drawn as symbols on whatever view is in hand.

Electrical is the one layer that is not solids: a receptacle is a point on a face
and a box behind it, not a piece of lumber. So it does not come through
`sheets.geometry` — it is projected here, straight from `verify.electrical_devices`
(the same adapter verify.py checks against, so a symbol cannot end up somewhere the
checker never looked).

Each symbol is a `.pc` group carrying the same `data-c` / `data-l` attributes as a
solid, so it switches with its component and with the Electrical layer, and needs
no special case anywhere in the site.

Sizes follow the drafting convention: a fixture whose face is parallel to the page
is drawn at its TRUE diameter, because where the hole goes is a real dimension;
every glyph on top of it (the cross, the S, the receptacle's blades) is drawn at a
constant size in PAGE pixels, because a symbol is a symbol at any scale.
"""
from __future__ import annotations

from verify import FACE, electrical_devices

from . import taxonomy as tx
from .canvas import E
from drawings.model import M, d

DEVICES = electrical_devices(d, M)
BY_ID = {dev["id"]: dev for dev in DEVICES}

GLYPH = 8.0          # symbol radius, page pixels
LEAD = 13.0          # leader from a surface-mounted device out to its label


def _axis_of(direction):
    """The axis a view looks down, or None if it is an axonometric."""
    for i, a in enumerate("xyz"):
        if abs(direction[i]) > 0.99:
            return a
    return None


def draw(cv, spec, ids=None, labels=True, bucket=None):
    """Draw every device that lands inside the canvas. Returns the (component,
    layer) pairs added, so the figure's switch board picks them up.

    `ids` names the devices this sheet wants; without it, everything in frame is
    drawn — which is right for a plan and wrong for a section that would otherwise
    show a switch standing behind the reader."""
    out = bucket if bucket is not None else cv.geom
    view_axis = _axis_of(spec.direction)
    added = set()
    # An elevation flattens one axis, so two devices can land on the same point —
    # the two desk lights share an x and stack exactly in the front elevation.
    # Draw one symbol there and let the label say how many, rather than printing
    # the same word twice in the same place.
    groups = {}
    for dev in DEVICES:
        if ids is not None and dev["id"] not in ids:
            continue
        h, v = cv.p3(*dev["at"])
        if not (cv.h0 - 1e-6 <= h <= cv.h1 + 1e-6 and cv.v0 - 1e-6 <= v <= cv.v1 + 1e-6):
            continue
        groups.setdefault((round(h, 3), round(v, 3)), []).append(dev)
    for (h, v), devs in groups.items():
        dev = devs[0]
        face_axis = FACE[dev["face"]][0]
        face_on = view_axis is not None and view_axis == face_axis
        for d in devs:
            added.add((tx.component_of_member(d["host"]), "electrical"))
        out.append(_symbol(cv, dev, h, v, face_on))
        if labels:
            _label(cv, dev, h, v, len(devs))
    return added


def _open(dev, comp):
    return (f'<g class="pc" data-c="{comp}" data-l="electrical" '
            f'data-id="{dev["id"]}">')


def _symbol(cv, dev, h, v, face_on):
    comp = tx.component_of_member(dev["host"])
    x, y = cv.X(h), cv.Y(v)
    body = {"light": _light, "outlet": _outlet, "switch": _switch}[dev["kind"]]
    return _open(dev, comp) + body(cv, dev, x, y, face_on) + "</g>"


def _light(cv, dev, x, y, face_on):
    # true size when you are looking at the ceiling it is set into; a glyph when
    # you are looking at that ceiling edge-on and its diameter is not on the page
    r = (float(dev["box"][0]) / 2) * cv.s if face_on else GLYPH
    g = f'<circle class="elecf" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>'
    k = min(r * 0.72, GLYPH)
    return (g + f'<line class="elec" x1="{x - k:.1f}" y1="{y:.1f}" x2="{x + k:.1f}" y2="{y:.1f}"/>'
            + f'<line class="elec" x1="{x:.1f}" y1="{y - k:.1f}" x2="{x:.1f}" y2="{y + k:.1f}"/>')


def _outlet(cv, dev, x, y, face_on):
    r = GLYPH
    return (f'<circle class="elecf" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>'
            f'<line class="elec" x1="{x - 3:.1f}" y1="{y - 3.5:.1f}" x2="{x - 3:.1f}" y2="{y + 3.5:.1f}"/>'
            f'<line class="elec" x1="{x + 3:.1f}" y1="{y - 3.5:.1f}" x2="{x + 3:.1f}" y2="{y + 3.5:.1f}"/>')


def _switch(cv, dev, x, y, face_on):
    return (f'<circle class="elecf" cx="{x:.1f}" cy="{y:.1f}" r="{GLYPH:.1f}"/>'
            f'<text class="elecs" x="{x:.1f}" y="{y + 3.4:.1f}" text-anchor="middle">S</text>')


SHORT = {"light": "light", "outlet": "outlet", "switch": "switch"}


def _label(cv, dev, h, v, count=1):
    """One short name, offset off the symbol. Anything longer belongs in the caption."""
    name = dev.get("label") or SHORT[dev["kind"]]
    if count > 1:
        name = f"{count} × {name}"
    cv.labels.append(
        f'<text class="sm elect" x="{cv.X(h):.1f}" y="{cv.Y(v) - GLYPH - 4:.1f}" '
        f'text-anchor="middle">{E(name)}</text>')
