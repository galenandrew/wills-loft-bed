"""sheets.cutlist — the Cut list page: the sheet nest drawn, and the tables behind it.

Everything here comes from `takeoff()`, the same call tools/materials.py writes the
workbook from, so the page and the spreadsheet cannot disagree about where a seam
lands or how many sheets to buy. Nothing is re-nested for the web.

Every SHEET is its own <svg>, tiled in a CSS grid and clickable into a lightbox that
steps through all of them with the arrow keys. One sheet per figure is what makes that
possible, and it is also why every sheet comes out at the same scale for free: the grid
gives each tile the same width and the viewBox is the sheet at true size, so an inch is
an inch everywhere and a piece in one group is comparable to a piece in another.

The sheet number and its yield are HTML under the tile rather than text inside the SVG,
so they stay at reading size however small the tile gets.
"""
from drawings.model import fr
from takeoff import KERF, SHEET_L, SHEET_W
from .style import CARD, INK, INK2, INK3, LINE, PALETTE

E = lambda s: (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

GAP = 7.0          # inches between sheets on the page
TOP = 6.0          # room above each sheet for its caption
PAD = 2.0

FILL, STROKE = PALETTE["finish"]
OVER_F, OVER_S = PALETTE["electric"]


def _fit(text, inches, fs):
    """Clamp a label to the piece it sits on. Nothing in this figure is placed by
    hand, so a label that does not fit gets cut rather than run over its neighbour;
    the Cut layout table below carries every name in full."""
    n = int(inches / (0.52 * fs))
    return text if len(text) <= n else (text[:max(1, n - 1)] + "\u2026")


def _piece(x, y, w, h, label, rot, over, fs):
    """One placed piece, at true size. The label goes across the piece, up it, or
    nowhere, chosen by which way the piece is long — a 14 x 53 panel labelled across
    is a label lying over its neighbours.

    `fs` is the text height in INCHES of the drawing, and every threshold here is a
    multiple of it, so the enlarged view is not the thumbnail's labels made bigger:
    at a smaller `fs` the same rules put a name on pieces that had no room for one.
    That is the whole point of the lightbox — more detail, not more pixels."""
    f, s = (OVER_F, OVER_S) if over else (FILL, STROKE)
    out = [f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
           f'fill="{f}" stroke="{s}" stroke-width=".35"/>']
    name = E(label) + (" \u27f3" if rot else "")
    size = f"{fr(w)} \u00d7 {fr(h)}"
    pad = 0.48 * fs
    if w > 6 * fs and h > 3.2 * fs:                    # room for two lines across it
        out.append(f'<text x="{x+pad:.3f}" y="{y+1.44*fs:.3f}" font-size="{fs:.2f}">'
                   f'{_fit(name, w - 2*pad, fs)}</text>')
        out.append(f'<text x="{x+pad:.3f}" y="{y+2.76*fs:.3f}" '
                   f'font-size="{fs*0.92:.2f}" fill="{INK2}">'
                   f'{_fit(size, w - 2*pad, fs*0.92)}</text>')
    elif h > w and h > 6 * fs and w > 1.2 * fs:        # tall: run it up the piece
        cx, cy = x + w / 2 + 0.32 * fs, y + h - 0.48 * fs
        out.append(f'<text x="{cx:.3f}" y="{cy:.3f}" font-size="{fs*0.84:.2f}" '
                   f'transform="rotate(-90 {cx:.3f} {cy:.3f})">'
                   f'{_fit(name + " " + size, h - 2*pad, fs*0.84)}</text>')
    elif w > 5.2 * fs and h > 1.2 * fs:                # short and wide: one line
        out.append(f'<text x="{x+0.4*fs:.3f}" y="{y+h/2+0.32*fs:.3f}" '
                   f'font-size="{fs*0.84:.2f}">'
                   f'{_fit(name + " " + size, w - 0.8*fs, fs*0.84)}</text>')
    return out


# Label height in inches for the two renders of every sheet: the tile, which is about
# 190 px wide, and the lightbox, which is roughly five times that. Both land near 11 px
# of text on screen — the enlarged one just has five times as many pieces big enough
# to carry a label.
FS_TILE, FS_BIG = 2.5, 1.3


def sheet_svg(placed, fs):
    """One sheet, at true size. No title inside it — the caption is HTML below."""
    W, H = SHEET_W + 2 * PAD, SHEET_L + 2 * PAD
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}">',
           f'<rect x="{PAD}" y="{PAD}" width="{SHEET_W}" height="{SHEET_L}" '
           f'fill="{CARD}" stroke="{INK}" stroke-width=".5"/>',
           f'<g transform="translate({PAD} {PAD})">']
    for p in sorted(placed, key=lambda p: (p[1], p[0])):
        out += _piece(*p, fs)
    out += ["</g>", "</svg>"]
    return "\n".join(out)


def tile(grade, i, placed):
    """One clickable sheet. A <button>, so it is reachable and operable from the
    keyboard without the lightbox having to invent its own focus handling."""
    used = sum(w * h for _x, _y, w, h, _l, _r, o in placed if not o)
    cap = f"{grade} · sheet {i + 1}"
    return (f'<button class="nestcell" type="button" data-cap="{E(cap)}" '
            f'aria-label="Enlarge {E(cap)}">{sheet_svg(placed, FS_TILE)}'
            f'<span class="nestbig" hidden>{sheet_svg(placed, FS_BIG)}</span>'
            f'<span class="nestcap"><span>Sheet {i + 1}</span>'
            f'<b>{used / (SHEET_W * SHEET_L):.0%} used</b></span></button>')


def lightbox():
    """One per page. The stage is filled by cloning the tile's own detail render, so
    the enlarged view cannot drift from the thumbnail: same data, same code, one
    parameter apart."""
    return ('<div class="lb" id="lb" hidden role="dialog" aria-modal="true" '
            'aria-label="Sheet nest, enlarged">'
            '<div class="lbbar"><span class="lbcap"></span>'
            '<span class="lbn"></span>'
            '<button class="lbbtn lbx" type="button" aria-label="Close">&times;</button></div>'
            '<button class="lbbtn lbnav lbprev" type="button" aria-label="Previous sheet">'
            '&#8592;</button>'
            '<div class="lbstage"></div>'
            '<button class="lbbtn lbnav lbnext" type="button" aria-label="Next sheet">'
            '&#8594;</button></div>')


def tbl(rows, head, num=()):
    """Plain table in the reference-card classes — `num` columns get tabular figures."""
    th = "".join(f"<th>{E(h)}</th>" for h in head)
    body = "".join(
        "<tr>" + "".join(f'<td{" class=\"n\"" if i in num else ""}>{E(c)}</td>'
                         for i, c in enumerate(r)) + "</tr>" for r in rows)
    return (f'<div class="scroll"><table><thead><tr>{th}</tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def cards():
    """The Cut list page: the nest drawn, then the buy list, the cut list and the
    piece offsets that make the diagram markable."""
    from takeoff import takeoff
    t = takeoff()
    figs = "".join(
        f'<h3 class="nesth">{E(g)} · {len(shs)} sheet{"s" if len(shs) != 1 else ""}'
        f'</h3><div class="nestgrid">'
        + "".join(tile(g, i, sh) for i, sh in enumerate(shs)) + "</div>"
        for g, shs in t["nests"])
    over = any(p[6] for _g, shs in t["nests"] for sh in shs for p in sh)

    nest_card = (
        f'<div class="card" id="nest"><h2>Sheet nesting — '
        f'{sum(len(s) for _g, s in t["nests"])} sheets</h2>'
        f'<p class="cap" style="margin:-4px 0 14px">Every panel placed by a guillotine '
        f'first-fit-decreasing nest that reserves <b>{fr(KERF)}</b> on every cut, drawn '
        f'here at true size on 48 × 96 sheets. No two pieces overlap and none runs off '
        f'a sheet — both are asserted when the takeoff is built, so this is a layout '
        f'you can mark out rather than an indicative count. ⟳ marks a piece the nest '
        f'turned; rotation is allowed everywhere because 3/4 ply is inside its span rating '
        f'in either direction at this joist spacing, so an appearance call can override '
        f'one. <b>No factory-edge trim is allowed for:</b> the first piece sits in the '
        f'corner, so two usable edges are assumed. <b>Click any sheet</b> to enlarge it; '
        f'&#8592;/&#8594; step through all {sum(len(s) for _g, s in t["nests"])} of them.</p>'
        f'{figs}{lightbox()}'
        + ('<div class="note"><b>Some pieces do not fit a sheet</b> — shown in red '
           'above.</div>' if over else "")
        + '</div>')

    return [
        nest_card,
        f'<div class="card" id="buy"><h2>Buy list</h2>'
        f'<p class="cap" style="margin:-4px 0 12px">Board counts are a first-fit-decreasing '
        f'pack into 8 ft and 10 ft stock. Species and grade are still open — see Open '
        f'items.</p>'
        f'{tbl(t["buy"], ["Stock", "Species / grade", "Length", "Qty", "Unit", "Notes"], num=(3,))}'
        f'</div>',
        f'<div class="card" id="cutlist"><h2>Cut list — {t["pieces"]} pieces</h2>'
        f'<p class="cap" style="margin:-4px 0 12px">Lengths are <b>framing</b> extents; '
        f'finished faces are their own parts. Identical pieces are collapsed to one row. '
        f'An inclined board’s length is the slope, not its bounding box.</p>'
        f'{tbl(t["cut"], ["Part", "Qty", "Assembly", "Stock", "Length", "Width", "Thick", "Source", "Notes"], num=(1, 4, 5, 6))}'
        f'</div>',
        f'<div class="card" id="layout"><h2>Cut layout — piece offsets</h2>'
        f'<p class="cap" style="margin:-4px 0 12px">Where each piece sits on its sheet, '
        f'measured from the same corner the diagrams above are drawn from — the numbers behind them, and every piece name in full.</p>'
        f'{tbl(t["layout"], ["Grade", "Sheet", "Piece", "W", "H", "From edge X", "From edge Y", "Grain", "Flag"], num=(1, 3, 4, 5, 6))}'
        f'</div>',
    ]
