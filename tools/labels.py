#!/usr/bin/env python3
"""tools/labels.py — find labels that sit on top of each other in docs/.

Text placement is the one thing in the v2 set that is still authored by hand, so
it is the one thing that can collide. This reads the built pages, boxes every
<text> element the way the browser lays it out (per-class font size, anchor,
rotation) and reports pairs whose boxes overlap.

    python3 tools/labels.py              every figure
    python3 tools/labels.py loft_sec     just that one
    python3 tools/labels.py --min 30     only overlaps bigger than 30 px²

Estimates, not layout: it will not catch a label sitting on a drawn line, and a
couple of px² of overlap between two short labels is usually fine. Use it to find
the ones worth looking at, then look at them.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# font size and average glyph width per class, from sheets/style.py
FONTS = {
    "sm": (10.0, 0.50), "wallname": (10.0, 0.52), "elecs": (10.0, 0.60),
    "elect": (10.0, 0.50), "dim": (10.5, 0.60), "": (11.0, 0.52),
}
TEXT = re.compile(r'<text([^>]*)>(.*?)</text>', re.S)
ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')
ROT = re.compile(r'rotate\(\s*(-?[\d.]+)')


def boxes(svg, default="") :
    """[(text, x0, y0, x1, y1)] for every label in one fragment.

    `default` is the class to assume when the element carries none — dimension
    text is monospace and set inside <g class="lay-dims">, not on the element."""
    out = []
    for attrs, body in TEXT.findall(svg):
        a = dict(ATTR.findall(attrs))
        txt = re.sub(r"<[^>]+>", "", body).strip()
        if not txt:
            continue
        try:
            x, y = float(a.get("x", 0)), float(a.get("y", 0))
        except ValueError:
            continue
        cls = a.get("class", "").split()
        key = next((c for c in cls if c in FONTS), default)
        size, ratio = FONTS.get(key, FONTS[""])
        w, h = len(txt) * size * ratio, size
        anchor = a.get("text-anchor", "start")
        x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
        y0 = y - h * 0.78
        rot = ROT.search(attrs)
        if rot and abs(float(rot.group(1))) > 45:      # rotated: swap the extents
            out.append((txt, x - h / 2, y - w / 2, x + h / 2, y + w / 2))
        else:
            out.append((txt, x0, y0, x0 + w, y0 + h))
    return out


def overlaps(bs, minimum):
    hits = []
    for i, (t1, a0, b0, a1, b1) in enumerate(bs):
        for t2, c0, d0, c1, d1 in bs[i + 1:]:
            w = min(a1, c1) - max(a0, c0)
            h = min(b1, d1) - max(b0, d0)
            if w > 0 and h > 0 and w * h >= minimum:
                hits.append((round(w * h), t1, t2))
    return sorted(hits, reverse=True)


def figures():
    for path in sorted(glob.glob(os.path.join(ROOT, "docs", "*.html"))):
        page = os.path.basename(path)[:-5]
        html = open(path).read()
        for chunk in html.split('data-fig="')[1:]:
            key = chunk.split('"')[0]
            svg = chunk.split("<svg", 1)[1].split("</svg>")[0] if "<svg" in chunk else ""
            yield page, key, svg


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    minimum = 12.0
    if "--min" in sys.argv:
        minimum = float(sys.argv[sys.argv.index("--min") + 1])
    total = 0
    for page, key, svg in figures():
        if args and key not in args:
            continue
        # labels and dimension text are set in different fonts, so box them apart
        # and then compare the two sets together. The fragments must be DISJOINT:
        # the label group is emitted before the dim group, so partition on the dim
        # marker first, or every dim label gets boxed twice and overlaps itself.
        head, _, dim = svg.partition('<g class="lay-dims">')
        lab = head.partition('<g class="lay-labels">')[2]
        hits = overlaps(boxes(lab, "") + boxes(dim, "dim"), minimum)
        if hits:
            total += len(hits)
            print(f"\n{page}/{key} — {len(hits)} overlapping pair(s)")
            for area, t1, t2 in hits[:10]:
                print(f"   {area:5} px²  {t1[:44]!r}  ×  {t2[:44]!r}")
    print(f"\n{total} overlapping label pairs (threshold {minimum:g} px²)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
