"""sheets.sheet — what a v2 sheet module is, and the two helpers they all use.

A module exposes NUMBER, TITLE, PAGE and FIGURES = [(key, fn)]; each fn returns a
Fig. The toolbar for a figure is built from what the figure ACTUALLY drew, not
from a hand-kept list — add a member to the yaml and its component appears on the
switch board by itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import render, taxonomy as tx
from .geometry import ViewSpec, view


@dataclass
class Fig:
    key: str
    svg: str
    title: str = ""
    components: list = field(default_factory=list)
    layers: list = field(default_factory=list)
    off: list = field(default_factory=list)      # chip classes starting switched off
    note: str = ""


def _has_geometry(r):
    return bool(r["faces"] or r["outline"] or r["cut"] or r["near"])


def _loops(r):
    for f in r["faces"]:
        yield f["pts"]
    for k in ("outline", "cut", "near"):
        for loop in r[k]:
            yield loop


def _in_view(cv, r):
    """Does any of this piece land inside the canvas box? The view is clipped to
    that box, so a piece outside it was never on the page and must not get a
    switch — the dresser is in the stair section's data, but not in its frame."""
    for loop in _loops(r):
        for h, v in loop:
            if cv.h0 - .01 <= h <= cv.h1 + .01 and cv.v0 - .01 <= v <= cv.v1 + .01:
                return True
    return False


def present(recs, drawn, modes, cv=None):
    """The components and layers a figure really contains, in canonical order.

    A component with nothing in this view gets no switch: a detail at the beam's
    end should not offer to toggle a dresser eight feet away that was never on the
    page. What is switchable is what is drawable."""
    ids = set(drawn)
    here = [r for r in recs if r["id"] in ids and _has_geometry(r)
            and (cv is None or _in_view(cv, r))]
    comps = {r["component"] for r in here}
    lays = {r["layer"] for r in here}
    off = {c for c in comps if modes.get(c) == "off"}
    return ([c for c in tx.COMPONENTS if c in comps],
            [l for l in tx.LAYERS if l in lays],
            [f"off-c-{c}" for c in tx.COMPONENTS if c in off])


def compose(cv, recs, modes, key, aria, title="", shade=False, hatch=True,
            note="", extra_defs="", start_off=(), spec=None, electrical=None,
            electrical_labels=True):
    """Draw, then wrap the result up as a Fig with its own switch list.

    `start_off` names chips that begin switched off — "off-l-finish" on a framing
    plan, say. The reader can switch them back on; nothing is missing from the
    file, only from the first look at it.

    `electrical` is a list of device ids, or None for every device that lands in
    frame, or False for none. Symbols go on last, over the geometry, and bring
    their own component and layer chips with them."""
    drawn = render.draw(cv, recs, modes, shade=shade, hatch=hatch)
    comps, lays, off = present(recs, drawn, modes, cv)
    if electrical is not False and spec is not None and cv.proj is not None:
        from . import electrical as elec
        for comp, layer in elec.draw(cv, spec, ids=electrical,
                                     labels=electrical_labels):
            if comp not in comps:
                comps.append(comp)
            if layer not in lays:
                lays.append(layer)
        comps = [c for c in tx.COMPONENTS if c in comps]
        lays = [l for l in tx.LAYERS if l in lays]
    return Fig(key, cv.svg(aria, extra_defs), title, comps, lays,
               sorted(set(off) | set(start_off)), note)


def frame_from(recs, pad=2.0, what=("faces", "cut", "near"), built_only=True):
    """(h0, h1, v0, v1) around everything the view contains, plus a margin — so a
    sheet frames itself off the model instead of off four hand-typed numbers.

    `built_only` frames on what is being BUILT: a dresser eight feet away should
    not pull the whole drawing down to a third of its scale."""
    from .geometry import bounds
    use = [r for r in recs if r["component"] in tx.BUILT] if built_only else recs
    h0, h1, v0, v1 = bounds(use or recs, what)
    return h0 - pad, h1 + pad, v0 - pad, v1 + pad
