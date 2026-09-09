"""takeoff — the materials takeoff: every piece that gets cut, packed and nested.

Split out of tools/materials.py at Rev BD so the workbook and the v2 site read the
SAME takeoff instead of two copies of the nest. tools/materials.py writes it to
xlsx; sheets/cutlist.py draws it. Nothing here imports openpyxl, so the site build
does not depend on a spreadsheet library.

Why the kernel and not just the yaml: the yaml carries framing extents for the
members it declares, but the stair treads, the risers, and the header's three
laminations are NOT members — cad/model.py derives them, and cad's NOTCHED table
fuses several yaml rows into the one board they actually are (the beam and its
tongue, deck_joist[0] and its tail, the two half-wall faces). `build()` returns
exactly the list of solids that get cut, so it is the honest source for a takeoff.

`takeoff()` is cached on disk exactly the way sheets/geometry.py caches its views —
keyed by a hash of every input that can change the answer — because the edit hook
rebuilds the site on every Write and the kernel costs ~3 s to import. Touch a
label and it hits; touch the model and it misses and the kernel runs.
LOFT_KERNEL_NOCACHE=1 forces a real run.
"""
import glob
import hashlib
import json
import math
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from drawings.model import M, ST, d as YAML, fr, m as _m

CACHE = os.path.join(ROOT, ".kernel-cache")
INPUTS = ([os.environ.get("LOFT_YAML") or os.path.join(ROOT, "dimensions.yaml"),
           os.path.join(ROOT, "verify.py"),
           os.path.join(ROOT, "drawings", "model.py")]
          + sorted(glob.glob(os.path.join(ROOT, "cad", "*.py")))
          + [os.path.abspath(__file__)])

def _joist_c(i):
    """Centre of deck_joist[i] in x — the only lines a seam may land on."""
    return sum(_m(f"deck_joist[{i}]").x) / 2


# The deck's layout is DERIVED, not typed. n seam blocks fill the bays between joists
# 0…n, so the long seam is joist n's centre; the rows split at the blocking's own y
# centre; the unseamed landing panel is what is left. Same invariant drawings/model.py
# uses for deck_seam_x / deck_panel_w, so the cut list and the prose cannot disagree —
# before this they were joined by nothing but discipline, and the seam had already moved
# twice in three revs.
_NB = len([k for k in M if k.startswith("deck_seam_blocking[")])
_SEAM_X = _joist_c(_NB)
_SEAM_Y = sum(_m("deck_seam_blocking[0]").y) / 2
_DECK_D = float(_m("deck_ply").y[1]) - float(_m("deck_ply").y[0])
_DECK_L = float(_m("deck_ply").x[1]) - float(_m("deck_ply").x[0])
_CEIL_D = _m("loft_ceiling").size("y")
_CEIL_L = _m("loft_ceiling").size("x")


def _sz(mid, axis):
    return _m(mid).size(axis)

# Actual section for every nominal stock key, straight off the yaml's lumber table.
SECTION = {k: v for k, v in YAML["lumber"].items()}

# Stock lengths the user can get without a special trip: 8 ft and 10 ft (2026-09-06).
# Anything needing 12 or 16 is called out on the Buy list so it can be checked.
STOCK_LENGTHS = (96.0, 120.0)
KERF = 0.125

SHEET_W, SHEET_L = 48.0, 96.0

# Pieces whose AXIS is inclined, so the bounding box overstates nothing but
# understates the board: the real length is the slope diagonal in y-z. A raked
# PANEL (the nook face's head, the stringer skin) is not in here — it lies in a
# plane, so its bbox in that plane already is the rough panel and the rake is
# just a cut edge.
SLOPED_AXIS = {"stringer_a", "stringer_b", "stringer_c", "hw_rake_nailer", "nk_soffit_rake"}

# Panels bigger than one 48 x 96 sheet, split into the pieces they get cut as.
# Each entry: (long-axis pieces, the fixed cross dimension, why the joints land there).
# The deck and the loft ceiling are the awkward ones: both are OVER 48 in y
# (48 1/4 and 50), so the 4 ft sheet width cannot take the full depth and that
# dimension has to run along the sheet's 8 ft length — which caps every piece at
# 48 in x and means one deck piece per sheet, not two.
PANEL_SPLITS = {
    # deck: 106 1/4 x 48 1/4 — a quarter inch over a sheet's 48 width in y, so that
    # dimension always has to run along the 96 length.
    #
    # Rev AW, at the builder's direction: THREE pieces, chosen for joinery over yield.
    # Two long rows run x 0 to 62 1/4 with the cross-joist seam between them at y 24,
    # and one full-depth 44 x 48 1/4 panel covers x 62 1/4 to the landing end with NO seam in
    # it — that is the stretch you step onto off the stairs, the only part of the deck
    # walked on rather than slept on. Both seams end up under the mattress (x 2 to 77):
    # the long one lands on joist 5's centre at 62 1/4 and needs no blocking at all, and
    # the cross seam is shortened from the full 106 1/4 to 62 1/4, dropping the seam
    # blocks from nine to five. 62 1/4 is the furthest in the seam can go: one more joist
    # would need a 56 wide panel and 48 is the sheet width. It costs one sheet against the four-piece version.
    "deck_ply": ([(_SEAM_X, _SEAM_Y), (_SEAM_X, _DECK_D - _SEAM_Y),
                  (_DECK_L - _SEAM_X, _DECK_D)],
                 f"two rows to x {fr(_SEAM_X)} either side of the y-{fr(_SEAM_Y)} seam, then "
                 f"one full-depth {fr(_DECK_L - _SEAM_X)} x {fr(_DECK_D)} panel over the "
                 f"landing end; seam on joist {_NB}'s centre — all derived from the blocking"),
    # ceiling: 102 x 50. EVERY seam runs along a joist, at the builder's direction —
    # three pieces, two seams, both on joist centres (38 1/4 and 74 1/4) and so fully
    # backed. That rules out a cross-joist seam and with it the butt joint hanging
    # between joists that a painted 3/4 ceiling can telegraph through. Since 50 is over
    # the 48 sheet width, each piece's 50 must run along the 96 and only one ceiling
    # piece fits per sheet: this costs a sheet against the two-row version, and the
    # offcuts are large and go back into the pool. Both seams clear all three downlights
    # (rough-in holes at x 9 7/8-14 1/8 and 59 7/8-66 1/8).
    "loft_ceiling": ([(_joist_c(3), _CEIL_D), (_joist_c(6) - _joist_c(3), _CEIL_D),
                      (_CEIL_L - _joist_c(6), _CEIL_D)],
                     f"three pieces, seams on the joist centres at {fr(_joist_c(3))} and "
                     f"{fr(_joist_c(6))} — every ceiling seam is backed by a joist; clear of "
                     f"all downlights. Rev AZ: 1/2 ply, and {fr(_CEIL_L)} long not 102 — the "
                     "half-wall's loft face went to 1/2 with it, so the last piece grew 1/4"),
    # Rev AZ: the three beam-wrap panels are 1/2 ply now, and two of the three changed size
    # with it (the face lost 1/4 of height to the thinner ceiling, the cap lost 1/2 of width
    # to the two thinner faces). Their cross dimensions are read off the members so a future
    # thickness change cannot leave a typed number behind.
    "beam_wrap_face":   ([(53.5, _sz("beam_wrap_face", "z"))] * 2, "joint on x 53 1/2, over deck_joist[4]"),
    "beam_wrap_inner":  ([(53.125, _sz("beam_wrap_inner", "z"))] * 2, "joint on x 53 1/8, the ledge's joint line"),
    "beam_wrap_top":    ([(53.5, _sz("beam_wrap_top", "y"))] * 2, "joint on x 53 1/2, with the face wrap"),
    "ledge_front_rail": ([(53.125, 10.25), (53.125, 10.25)],
                         "joint on x 53 1/8 = centre of ledge_strut[1], backed by ledge_rail_splice"),
    "ledge_lid":        ([(53.125, 8.0), (53.875, 8.0)],
                         "joint on x 53 1/8, over ledge_strut[1]; no splice needed"),
}

HANGERS = ("LUS24", "HUC28", "A35")

# ---------------------------------------------------------------- ply grade groups
# Pieces of different grades cannot share a sheet, so the nest has to run per group,
# not on "3/4 ply" as one pool. Grade is a purchasing decision, not a geometric one,
# so the split lives here rather than in the model. `role:` in the yaml does not carry
# it — role is sheet/finish/structural, which mixes "is it a panel" with "is it seen".
#
# The striking result: almost every 3/4 piece is a SEEN, painted face. Only the deck
# and the rail splice are hidden. See the TBD tab for the deck-surface question that
# hangs off this.
# DECIDED 2026-09-07: the deck IS the finished walking surface, so it is paint-grade
# like everything else and the set is empty. Kept rather than deleted because the
# distinction is real and would come back the moment anything hidden gets added.
#
# Rev AZ: 1/2 ply is ONE pool, deliberately. It now holds both the paint-grade faces that
# moved down from 3/4 and the two structural flitches (hw_jamb_ply_a/b, and the header's
# middle ply, which is a lamination of the header rather than a panel) — at the builder's
# direction, so the jambs come out of the same sheet as the faces instead of being the only
# reason to buy a board. Paint-grade is the better of the two grades, so nothing is
# under-specified by mixing them; if that ever reverses, split it here the way HIDDEN does.
HIDDEN: set[str] = set()


def grade_group(pid, stock):
    if stock != "ply-3/4":
        return stock
    base = pid.split("[")[0].split("#")[0].split(" ")[0]
    return "ply-3/4 structural" if base in HIDDEN else "ply-3/4 paint-grade"


# ------------------------------------------------------------------------- nesting
# Guillotine first-fit-decreasing over a free-rectangle list. Not an optimiser — it
# is deterministic and it never overlaps, which is what a buy count needs. Rotation
# is allowed everywhere: at 12 in joist spacing and an 11-5/8 stringer pitch, 3/4 ply
# is far inside its span rating in EITHER direction, so face-grain direction is not
# structurally binding anywhere in this build. The layout tab reports which pieces
# came out rotated so an appearance call can override one.
def nest(pieces, sheet=(SHEET_W, SHEET_L), kerf=KERF):
    """pieces: [(w, h, label)]. Returns [[(x, y, w, h, label, rotated), ...], ...]."""
    SW, SL = sheet
    sheets = []
    for w, h, label in sorted(pieces, key=lambda p: (-max(p[0], p[1]), -p[0] * p[1])):
        for sh in sheets:
            if _place(sh, w, h, label, kerf):
                break
        else:
            sh = dict(free=[(0.0, 0.0, SW, SL)], placed=[])
            if not _place(sh, w, h, label, kerf):
                sh["placed"].append((0.0, 0.0, w, h, label, False, True))  # oversize
            sheets.append(sh)
    _assert_sane(sheets, sheet)
    return sheets


def _assert_sane(sheets, sheet):
    """No two pieces may overlap and none may hang off the sheet. This is cheap and
    it is the one property a cutting diagram absolutely has to have."""
    SW, SL = sheet
    for n, sh in enumerate(sheets):
        ps = [p for p in sh["placed"] if not p[6]]
        for x, y, w, h, label, _, _ in ps:
            assert x >= -1e-9 and y >= -1e-9 and x + w <= SW + 1e-9 and y + h <= SL + 1e-9, \
                f"sheet {n}: {label} runs off the sheet"
        for i in range(len(ps)):
            ax, ay, aw, ah = ps[i][:4]
            for j in range(i + 1, len(ps)):
                bx, by, bw, bh = ps[j][:4]
                if ax < bx + bw - 1e-9 and bx < ax + aw - 1e-9 and \
                   ay < by + bh - 1e-9 and by < ay + ah - 1e-9:
                    raise AssertionError(f"sheet {n}: {ps[i][4]} overlaps {ps[j][4]}")


def _place(sh, w, h, label, kerf):
    best = None
    for i, (fx, fy, fw, fh) in enumerate(sh["free"]):
        for pw, ph, rot in ((w, h, False), (h, w, True)):
            if pw + kerf <= fw + 1e-9 and ph + kerf <= fh + 1e-9:
                waste = fw * fh - pw * ph
                if best is None or waste < best[0]:
                    best = (waste, i, pw, ph, rot)
    if best is None:
        return False
    _, i, pw, ph, rot = best
    fx, fy, fw, fh = sh["free"].pop(i)
    sh["placed"].append((fx, fy, pw, ph, label, rot, False))
    # guillotine: split the remainder along the shorter leftover axis
    right = (fx + pw + kerf, fy, fw - pw - kerf, fh)
    top = (fx, fy + ph + kerf, pw + kerf, fh - ph - kerf)
    if fw - pw < fh - ph:
        right = (fx + pw + kerf, fy, fw - pw - kerf, ph + kerf)
        top = (fx, fy + ph + kerf, fw, fh - ph - kerf)
    for r in (right, top):
        if r[2] > 0.5 and r[3] > 0.5:
            sh["free"].append(r)
    return True


def layout_svg(nests, path):
    """One page of sheet diagrams. Drawn at 3 px/in with the pieces labelled.

    `nests` is takeoff()["nests"]: [(grade, [[placed…], …])]."""
    S, PAD, COLS = 3.0, 18, 4
    W, H = SHEET_W * S, SHEET_L * S
    cells = [(g, i, sh) for g, shs in nests for i, sh in enumerate(shs)]
    rows = (len(cells) + COLS - 1) // COLS
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{COLS*(W+PAD)+PAD:.0f}" '
           f'height="{rows*(H+PAD+26)+PAD:.0f}" font-family="system-ui,sans-serif">',
           '<rect width="100%" height="100%" fill="#fff"/>']
    for n, (g, i, sh) in enumerate(cells):
        ox = PAD + (n % COLS) * (W + PAD)
        oy = PAD + (n // COLS) * (H + PAD + 26) + 20
        out.append(f'<text x="{ox}" y="{oy-7}" font-size="11" font-weight="600">'
                   f'{g} — sheet {i+1}</text>')
        out.append(f'<rect x="{ox}" y="{oy}" width="{W}" height="{H}" fill="#fafafa" '
                   f'stroke="#333" stroke-width="1.2"/>')
        for (x, y, w, h, label, rot, over) in sh:
            px, py, pw, ph = ox + x * S, oy + y * S, w * S, h * S
            out.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" '
                       f'fill="{"#fde2e0" if over else "#dce9f5"}" stroke="#33506b" stroke-width="0.8"/>')
            if pw > 26 and ph > 21:
                out.append(f'<text x="{px+3:.1f}" y="{py+11:.1f}" font-size="7.5">'
                           f'{label[:26]}{"  ⟳" if rot else ""}</text>')
                out.append(f'<text x="{px+3:.1f}" y="{py+20:.1f}" font-size="7" fill="#555">'
                           f'{fr(w)} × {fr(h)}</text>')
            elif pw > 20 and ph > 7:
                out.append(f'<text x="{px+2:.1f}" y="{py+ph/2+2.2:.1f}" font-size="6">'
                           f'{label[:22]} {fr(w)}×{fr(h)}</text>')
            elif ph > 20 and pw > 7:   # tall and narrow: run the label up the piece
                out.append(f'<text x="{px+pw/2+2.2:.1f}" y="{py+ph-3:.1f}" font-size="6" '
                           f'transform="rotate(-90 {px+pw/2+2.2:.1f} {py+ph-3:.1f})">'
                           f'{label[:22]} {fr(w)}×{fr(h)}</text>')
    out.append("</svg>")
    open(path, "w").write("\n".join(out))


# Nominal board widths, for naming poplar and any other board bought by the 1xN.
BOARD_NOMINAL = [(3.5, "1x4"), (5.5, "1x6"), (7.25, "1x8"), (9.25, "1x10"), (11.25, "1x12")]


def real_stock(pid, stock):
    """The stock you can actually buy. A lamination Piece inherits its parent's
    stock — "header-2x10-sandwich" is a lay-up, not a product — but its id carries
    the ply after a '#', so hw_header#2x10-stair is really a 2x10."""
    if "#" not in pid:
        return stock
    ply = pid.split("#", 1)[1]
    return "2x10" if ply.startswith("2x10") else ply

def sixteenths(v):
    """The nearest sixteenth as a shop-readable string; fr() is the house format."""
    return fr(v)


def slope_len(bb):
    (_, _), (y0, y1), (z0, z1) = bb
    return math.hypot(y1 - y0, z1 - z0)


def piece_rows():
    """Every solid that gets cut, with its rough stock size."""
    # Imported here, not at module scope: build123d costs ~3 s to import and a
    # cached takeoff never needs it.
    from cad.model import build
    rows = []
    for p in build():
        if p.stock is None:
            continue
        bb = p.bbox
        dims = sorted([bb[0][1] - bb[0][0], bb[1][1] - bb[1][0], bb[2][1] - bb[2][0]],
                      reverse=True)
        stock = real_stock(p.id, p.stock)
        if p.id.split("[")[0] in SLOPED_AXIS or p.id in SLOPED_AXIS:
            # the board runs up the rake: length is the slope, and the section comes
            # from the stock (or, for an inclined PANEL, from its one square axis).
            length = slope_len(bb)
            sec = SECTION.get(stock)
            if sec and sec[1]:
                t, w = float(sec[0]), float(sec[1])
            else:
                t, w = float(sec[0]) if sec else dims[2], bb[0][1] - bb[0][0]
            dims = [length, w, t]
            note = (p.note + "; " if p.note else "") + \
                   f"INCLINED: {sixteenths(length)} up the rake, and the bbox is not the board"
        else:
            length = dims[0]
            note = p.note
        rows.append(dict(id=p.id, assembly=p.assembly, stock=stock, parent=p.parent,
                         derived=p.derived, length=length, w=dims[1], t=dims[2], note=note))
    return sorted(rows, key=lambda r: (r["stock"], -r["length"], r["id"]))


def pack(lengths):
    """First-fit-decreasing into the shortest allowed board that holds each piece.
    Returns [(board_length, [piece lengths]), ...] plus anything that will not fit."""
    boards, oversize = [], []
    for L in sorted(lengths, reverse=True):
        if L > max(STOCK_LENGTHS):
            oversize.append(L)
            continue
        for b in boards:
            if b["used"] + KERF + L <= b["len"]:
                b["used"] += KERF + L
                b["cuts"].append(L)
                break
        else:
            size = next(s for s in STOCK_LENGTHS if s >= L)
            boards.append(dict(len=size, used=L, cuts=[L]))
    return boards, oversize


def resolve_count(key, exc=()):
    """How many members a connection key covers, less any the row excepts. verify.py
    honours `except:` and so must this — otherwise the hardware tally buys a hanger for
    a joint the model says is not there."""
    if "[*]" not in key:
        return 1
    stem = key.split("[")[0]
    return sum(1 for mid in M if mid.split("[")[0] == stem and mid not in exc)


def hardware_rows():
    rows, tally = [], defaultdict(int)
    for c in YAML["connections"]:
        a, b = str(c.get("a", "")), str(c.get("b", ""))
        fast = c.get("fastener")
        exc = set(c.get("except") or ())
        n = max(resolve_count(a, exc), resolve_count(b, exc))
        if fast is None:
            text = "NO FASTENER KEY — silent in verify.py, which only reports the rows that say UNSPECIFIED"
        elif fast == "UNSPECIFIED":
            text = "UNSPECIFIED — declared open"
        else:
            text = str(fast)
        rows.append(dict(a=a, b=b, type=c.get("type", ""), n=n, fastener=text))
        for h in HANGERS:
            if fast and h in str(fast):
                # "2 x A35 at the inside corner" is two hangers on one connection;
                # a bare "LUS24" is one per member the wildcard resolves to.
                mult = re.search(rf"(\d+)\s*[x×]\s*{h}", str(fast))
                tally[h] += n * (int(mult.group(1)) if mult else 1)
    return rows, tally




# ------------------------------------------------------------------ the takeoff
def _rows():
    """Everything derived from the model, in one pass. Returned as plain lists so
    the whole thing round-trips through the JSON cache unchanged."""
    rows = piece_rows()
    lumber = [r for r in rows if not r["stock"].startswith("ply")]
    panels = [r for r in rows if r["stock"].startswith("ply")]
    hw_rows, tally = hardware_rows()
    silent = [f"{c['a']} -> {c.get('b','')}" for c in YAML["connections"]
              if c.get("fastener") is None]

    # ---------------------------------------------------------------- buy list
    buy = []
    by_stock = defaultdict(list)
    for r in lumber:
        by_stock[r["stock"]].append(r)
    for stock, rs in sorted(by_stock.items()):
        if stock.startswith("lvl"):
            continue
        boards, over = pack([r["length"] for r in rs])
        counts = defaultdict(int)
        for b in boards:
            counts[b["len"]] += 1
        for size, n in sorted(counts.items()):
            longest = max(r["length"] for r in rs)
            note = (f"{len(rs)} pieces total, longest {sixteenths(longest)}"
                    + ("  ·  LONGEST PIECE NEEDS A 10 FT BOARD" if longest > 96 else ""))
            if stock.startswith("poplar"):
                widest = max(r["w"] for r in rs)
                # BOARD_NOMINAL names 1xN boards, which are 3/4 — it says nothing useful about
                # a 2x-section board. Rev BA: poplar-2x4 is one member, screen_top_plate, at a
                # section no 1xN comes in, and it is 107 long with no joint allowed, so the
                # board LENGTH is the binding constraint rather than the yield.
                if SECTION[stock][0] > 1.0:
                    note += (f"  ·  buy as poplar 8/4 S4S dressed to "
                             f"{sixteenths(SECTION[stock][0])} x {sixteenths(widest)}, or "
                             f"clear/select pine at that section — ONE board, no splice")
                else:
                    nominal = next((n for w, n in BOARD_NOMINAL if widest <= w), "wider than 1x12")
                    note += f"  ·  buy as {nominal} S4S ({sixteenths(widest)} wide needed)"
            if stock == "2x2" and size > 96:
                note += ("  ·  these two are ledge_cleat and ledge_cleat_rail; per the user "
                         "they can be RIPPED from one 10 ft 2x4 instead")
            buy.append([stock, "TBD", f"{int(size/12)} ft", n, "board",
                        note if size == max(counts) else f"{len(rs)} pieces total"])
        for L in over:
            buy.append([stock, "TBD", "SPECIAL ORDER", 1, "board",
                        f"a {sixteenths(L)} piece exceeds a 10 ft board — check 12/16 ft"])

    # sheet goods, after splitting the oversize panels
    flat = []
    for r in panels:
        key = r["id"]
        if key in PANEL_SPLITS:
            parts, why = PANEL_SPLITS[key]
            for i, (L, W) in enumerate(parts):
                flat.append((L, W, f"{key} pc{i+1}", r["stock"], why))
        else:
            flat.append((r["length"], r["w"], key, r["stock"], r["note"]))
    by_grade = defaultdict(list)
    for L, W, lab, st, _ in flat:
        by_grade[grade_group(lab, st)].append((L, W, lab))
    nests = []
    for grade in sorted(by_grade):
        sheets = nest(by_grade[grade])
        nests.append((grade, sheets))
        over = sum(1 for sh in sheets for pl in sh["placed"] if pl[6])
        used = sum(w * h for sh in sheets for (_, _, w, h, _, _, o) in sh["placed"] if not o)
        total = len(sheets) * SHEET_W * SHEET_L
        buy.append([grade, "TBD", "4 x 8 sheet", len(sheets), "sheet",
                    f"{len(by_grade[grade])} pieces nested at {used/total:.0%} of sheet area; "
                    f"{fr((total - used) / 144)} sq ft offcut"
                    + ("  ·  SOME PIECES DO NOT FIT A SHEET" if over else "")
                    + ("  ·  low yield on a single sheet: the longest piece is "
                       f"{fr(max(max(L, W) for L, W, _ in by_grade[grade]))}, so a 4 x 4 "
                       "half sheet covers it if the yard cuts one"
                       if len(sheets) == 1 and used / total < 0.25 else "")
                    + "  ·  see the sheet nest — the Cut layout tab here, the Cut list page on the site"])
    buy.append(["lvl-2x14", "LVL (1 3/4 x 14)", "10 ft preferred", 1, "board",
                "the beam is ONE 106 1/4 notched board. Home Depot stocks 14 ft "
                "(LPLVL14-14) which works with 62 in of waste; a yard 10 ft is the "
                "clean buy. Do NOT cut it to two pieces."])

    # ---------------------------------------------------------------- cut list
    groups = {}
    for r in rows:
        src = "yaml member"
        if r["derived"]:
            src = "DERIVED in cad/model.py — not a yaml member"
        elif r["parent"]:
            src = f"lamination of {r['parent']}"
        note = "" if r["note"] == src else r["note"]
        if r["id"] in PANEL_SPLITS:
            parts, why = PANEL_SPLITS[r["id"]]
            note = (f"CUT AS {len(parts)} PIECES: "
                    + " + ".join(f"{sixteenths(L)}×{sixteenths(W)}" for L, W in parts)
                    + f" — {why}" + (f". {note}" if note else ""))
        key = (r["stock"], round(r["length"], 4), round(r["w"], 4), round(r["t"], 4),
               r["assembly"], src, note)
        groups.setdefault(key, []).append(r["id"])
    cl = []
    for (stock, L, w, t, asm, src, note), ids in sorted(
            groups.items(), key=lambda kv: (kv[0][0], -kv[0][1])):
        stem = ids[0].split("[")[0]
        label = (f"{stem}[0..{len(ids)-1}]" if len(ids) > 3 and
                 all(i.split("[")[0] == stem for i in ids) else ", ".join(ids))
        cl.append([label, len(ids), asm, stock,
                   sixteenths(L), sixteenths(w), sixteenths(t), src, note])

    # ------------------------------------------------------------- sheet goods
    sg = []
    for L, W, lab, stock, why in sorted(flat, key=lambda f: (f[3], -max(f[0], f[1]))):
        sg.append([lab, stock, sixteenths(max(L, W)), sixteenths(min(L, W)),
                   "YES" if lab.endswith(tuple(f"pc{i}" for i in range(1, 6))) else "",
                   why])

    # -------------------------------------------------------------- cut layout
    lay = []
    for grade, sheets in nests:
        for i, sh in enumerate(sheets, 1):
            for (x, y, w, h, label, rot, over) in sorted(sh["placed"], key=lambda p: (p[1], p[0])):
                lay.append([grade, i, label, sixteenths(w), sixteenths(h),
                            sixteenths(x), sixteenths(y),
                            "rotated" if rot else "", "DOES NOT FIT" if over else ""])

    # ---------------------------------------------------------------- hardware
    hw = [[h, tally[h], "Simpson", ""] for h in HANGERS if tally[h]]
    hw.append(["", "", "", ""])
    for r in hw_rows:
        hw.append([f"{r['a']} -> {r['b']}", r["n"], r["type"], r["fastener"]])

    return dict(rev=YAML["rev"], pieces=len(rows), buy=buy, cut=cl, sheet_goods=sg,
                layout=lay, hardware=hw, silent=silent,
                nests=[(g, [sh["placed"] for sh in shs]) for g, shs in nests])


def _key():
    h = hashlib.sha256()
    for f in INPUTS:
        h.update(open(f, "rb").read())
    return h.hexdigest()[:16]


def takeoff():
    """The whole takeoff as plain data: buy / cut / sheet_goods / layout / hardware
    rows ready to tabulate, plus `nests` — [(grade, [[placed…], …])] — where each
    placed piece is (x, y, w, h, label, rotated, oversize) in inches from a sheet's
    bottom-left corner."""
    path = os.path.join(CACHE, f"takeoff-{_key()}.json")
    if not os.environ.get("LOFT_KERNEL_NOCACHE") and os.path.exists(path):
        return json.load(open(path))
    data = _rows()
    os.makedirs(CACHE, exist_ok=True)
    json.dump(data, open(path, "w"), separators=(",", ":"))
    return data
