"""sheets.render — geometry records → SVG, one group per piece.

Every piece becomes its own <g data-id data-c data-l>, drawn whole and in depth
order. That is what makes the toggles honest: hiding a component removes its
groups and what stood behind it is still complete, because nothing was ever
erased to make room for it. (A hidden-line pass would have to be re-run per
combination; this composites in the browser instead.)

Modes are per sheet, keyed by component or by piece id:

  solid    filled, with a silhouette over it — the default
  flat     filled, but never hatched even where the plane cuts it
  outline  no fill, a dashed silhouette — the "shown for reference" overlay
  ghost    only the part in FRONT of the section plane, dashed — d4's half-wall
  off      not drawn at all
"""
from __future__ import annotations

from .style import PALETTE, shade as _shade

MODES = ("solid", "flat", "outline", "ghost", "off")


def _path(cv, loops):
    return " ".join("M " + " L ".join(cv.pt(h, v) for h, v in loop) + " Z"
                    for loop in loops if len(loop) >= 3)


def mode_of(rec, modes):
    m = modes.get(rec["id"]) or modes.get(rec["id"].split("#")[0]) \
        or modes.get(rec["id"].split("[")[0]) or modes.get(rec["component"]) \
        or modes.get(rec["layer"]) or "solid"
    return m


def draw(cv, recs, modes=None, shade=False, hatch=True, bucket=None):
    """Draw every record onto the canvas, far to near. Returns the ids drawn, so a
    sheet can assert it got what it expected instead of trusting a member list."""
    modes = modes or {}
    out = bucket if bucket is not None else cv.geom
    solids, cuts, ghosts, drawn = [], [], [], []

    for r in recs:
        m = mode_of(r, modes)
        # "off" is a STARTING STATE, not an exclusion: the piece is drawn and the
        # figure starts with its switch down, so the reader can turn it back on.
        # A sheet that genuinely does not want a piece filters the records instead.
        if m == "off":
            m = "solid"
        drawn.append(r["id"])
        depth = max((f["depth"] for f in r["faces"]), default=-1e9)
        if m == "ghost":
            if r["near"]:
                ghosts.append(r)
            continue
        # A piece that lies entirely in FRONT of the cut plane has no far geometry
        # to draw. Ghost it rather than dropping it silently — that is what "the
        # half wall is in front of this section" looks like, and it means a sheet
        # never has to name the pieces its own cut happens to miss.
        if not r["faces"] and not r["outline"] and not r["cut"] and r["near"]:
            ghosts.append(r)
            continue
        if r["faces"] or r["outline"]:
            solids.append((depth, r, m))
        if r["cut"]:
            cuts.append((r, m))

    solids.sort(key=lambda t: -t[0])
    for _d, r, m in solids:
        out.append(_group(cv, r, m, shade))
    for r, m in cuts:
        out.append(_cut_group(cv, r, m, hatch))
    for r in ghosts:
        out.append(f'{_open(r, "ghost")}<path class="ghost" d="{_path(cv, r["near"])}"/></g>')
    return drawn


def _open(r, mode):
    cls = "pc" + ("" if mode == "solid" else f" mode-{mode}")
    return (f'<g class="{cls}" data-c="{r["component"]}" data-l="{r["layer"]}"'
            f' data-id="{r["id"]}">')


def _group(cv, r, mode, shade):
    body = []
    if mode != "outline":
        base = PALETTE.get(r["layer"], PALETTE["framing"])[0]
        for f in sorted(r["faces"], key=lambda f: -f["depth"]):
            fill = f' fill="{_shade(base, f["shade"])}"' if shade else ""
            loops = [f["pts"]] + f["holes"]
            body.append(f'<path class="fill" d="{_path(cv, loops)}"'
                        f' fill-rule="evenodd"{fill}/>')
    if r["outline"]:
        body.append(f'<path class="sil" d="{_path(cv, r["outline"])}"/>')
    return _open(r, mode) + "".join(body) + "</g>"


def _cut_group(cv, r, mode, hatch):
    d = _path(cv, r["cut"])
    body = f'<path class="cut" d="{d}" fill-rule="evenodd"/>'
    # Framing lumber reads hatched where the saw would expose it; sheet goods draw
    # plain, the convention the old set used and the one a builder expects.
    if hatch and mode != "flat" and r["layer"] == "framing":
        body += f'<path class="hatch" d="{d}" fill-rule="evenodd"/>'
    return _open(r, mode) + body + "</g>"


def by_id(recs):
    return {r["id"]: r for r in recs}


def only(recs, *, components=None, layers=None, ids=None, without=()):
    """A filtered copy — for a detail sheet that genuinely wants three members."""
    def keep(r):
        if r["id"].split("#")[0] in without or r["id"].split("[")[0] in without:
            return False
        if components is not None and r["component"] not in components:
            return False
        if layers is not None and r["layer"] not in layers:
            return False
        if ids is not None and r["id"].split("#")[0] not in ids:
            return False
        return True
    return [r for r in recs if keep(r)]
