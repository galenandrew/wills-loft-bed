"""Materials list + cut list, generated from dimensions.yaml and the CAD kernel.

Why the kernel and not just the yaml: the yaml carries framing extents for the
members it declares, but the stair treads, the risers, and the header's three
laminations are NOT members — cad/model.py derives them, and cad's NOTCHED table
fuses several yaml rows into the one board they actually are (the beam and its
tongue, deck_joist[0] and its tail, the two half-wall faces). `build()` returns
exactly the list of solids that get cut, so it is the honest source for a takeoff.

Development harness, like everything else in tools/: nothing here is imported by
the build, and the workbook is a deliverable, not a source of truth. Run it again
after any change to the model.

    python3 tools/materials.py            -> materials/materials-list.xlsx
"""
import math
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from cad.model import build
from drawings.model import M, ST, d as YAML, fr

# Actual section for every nominal stock key, straight off the yaml's lumber table.
SECTION = {k: v for k, v in YAML["lumber"].items()}

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "materials", "materials-list.xlsx")

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
    "deck_ply":     ([38.25, 36.0, 32.0], 48.25,
                     "joints on deck_joist centres x 38 1/4 and 74 1/4"),
    "loft_ceiling": ([38.25, 36.0, 27.75], 50.0,
                     "joints on deck_joist centres x 38 1/4 and 74 1/4"),
    "beam_wrap_face":  ([53.5, 53.5], 14.75, "joint on x 53 1/2, over deck_joist[4]"),
    "beam_wrap_inner": ([53.125, 53.125], 9.75, "joint on x 53 1/8, the ledge's joint line"),
    "beam_wrap_top":   ([53.5, 53.5], 3.25, "joint on x 53 1/2, with the face wrap"),
    "ledge_front_rail": ([53.125, 53.125], 10.25,
                         "joint on x 53 1/8 = centre of ledge_strut[1], backed by ledge_rail_splice"),
    "ledge_lid":        ([53.125, 53.875], 8.0,
                         "joint on x 53 1/8, over ledge_strut[1]; no splice needed"),
}

HANGERS = ("LUS24", "HUC28", "A35")

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

THIN = Side(style="thin", color="FFBFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD = PatternFill("solid", fgColor="FF1F3864")
BAND = PatternFill("solid", fgColor="FFF2F2F2")
FLAG = PatternFill("solid", fgColor="FFFFF2CC")


def sixteenths(v):
    """The nearest sixteenth as a shop-readable string; fr() is the house format."""
    return fr(v)


def slope_len(bb):
    (_, _), (y0, y1), (z0, z1) = bb
    return math.hypot(y1 - y0, z1 - z0)


def piece_rows():
    """Every solid that gets cut, with its rough stock size."""
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


def shelf_sheets(panels):
    """Indicative sheet count by shelf packing: sort by long edge, lay each panel
    on a shelf across the sheet's 48 width. Not a nesting optimiser — it exists so
    the buy list has a defensible number, and the Sheet goods tab says so."""
    sheets = []
    for L, W, label in sorted(panels, key=lambda p: -max(p[0], p[1])):
        long_, short = max(L, W), min(L, W)
        if long_ > SHEET_L or short > SHEET_W:
            sheets.append(dict(shelves=[dict(depth=short, run=long_, items=[label])],
                               over=True))
            continue
        for s in sheets:
            if s.get("over"):
                continue
            for sh in s["shelves"]:
                if short <= sh["depth"] and sh["run"] + long_ <= SHEET_L:
                    sh["run"] += long_
                    sh["items"].append(label)
                    break
            else:
                if sum(sh["depth"] for sh in s["shelves"]) + short <= SHEET_W:
                    s["shelves"].append(dict(depth=short, run=long_, items=[label]))
                else:
                    continue
            break
        else:
            sheets.append(dict(shelves=[dict(depth=short, run=long_, items=[label])]))
    return sheets


def resolve_count(key):
    """How many members a connection key covers — 'slat[*]' is 23 of them."""
    if "[*]" not in key:
        return 1
    stem = key.split("[")[0]
    return sum(1 for mid in M if mid.split("[")[0] == stem)


def hardware_rows():
    rows, tally = [], defaultdict(int)
    for c in YAML["connections"]:
        a, b = str(c.get("a", "")), str(c.get("b", ""))
        fast = c.get("fastener")
        n = max(resolve_count(a), resolve_count(b))
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


# ------------------------------------------------------------------ workbook
def style_header(ws, ncols, row=1):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = Font(bold=True, color="FFFFFFFF", size=11)
        cell.fill = HEAD
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 30
    ws.freeze_panes = f"A{row + 1}"


def widths(ws, spec):
    for i, w in enumerate(spec, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def write(ws, rows, header, wide):
    ws.append(header)
    style_header(ws, len(header))
    for i, r in enumerate(rows):
        ws.append(r)
        if i % 2:
            for c in range(1, len(header) + 1):
                ws.cell(row=ws.max_row, column=c).fill = BAND
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=len(header)):
        for cell in row:
            cell.border = BORDER
            if cell.row > 1:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
    widths(ws, wide)
    ws.auto_filter.ref = f"A1:{get_column_letter(len(header))}{ws.max_row}"


def main():
    rows = piece_rows()
    lumber = [r for r in rows if not r["stock"].startswith("ply")]
    panels = [r for r in rows if r["stock"].startswith("ply")]
    hw_rows, tally = hardware_rows()
    silent = [f"{c['a']} -> {c.get('b','')}" for c in YAML["connections"]
              if c.get("fastener") is None]
    wb = Workbook()

    # ---------------------------------------------------------- Buy list
    ws = wb.active
    ws.title = "Buy list"
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
            if stock == "poplar-3/4":
                widest = max(r["w"] for r in rs)
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
            lens, cross, why = PANEL_SPLITS[key]
            for i, L in enumerate(lens):
                flat.append((L, cross, f"{key} pc{i+1}", r["stock"], why))
        else:
            flat.append((r["length"], r["w"], key, r["stock"], r["note"]))
    for stock in sorted({f[3] for f in flat}):
        mine = [(L, W, lab) for L, W, lab, s, _ in flat if s == stock]
        sheets = shelf_sheets(mine)
        buy.append([stock, "TBD", "4 x 8 sheet", len(sheets), "sheet",
                    f"{len(mine)} pieces; indicative shelf packing, see the Sheet goods tab"])
    buy.append(["lvl-2x14", "LVL (1 3/4 x 14)", "10 ft preferred", 1, "board",
                "the beam is ONE 106 1/4 notched board. Home Depot stocks 14 ft "
                "(LPLVL14-14) which works with 62 in of waste; a yard 10 ft is the "
                "clean buy. Do NOT cut it to two pieces."])
    write(ws, buy,
          ["Stock", "Species / grade", "Length", "Qty", "Unit", "Notes"],
          [20, 22, 18, 8, 10, 72])

    # ---------------------------------------------------------- Cut list
    ws = wb.create_sheet("Cut list")
    groups = {}
    for r in rows:
        src = "yaml member"
        if r["derived"]:
            src = "DERIVED in cad/model.py — not a yaml member"
        elif r["parent"]:
            src = f"lamination of {r['parent']}"
        note = "" if r["note"] == src else r["note"]
        if r["id"] in PANEL_SPLITS:
            lens, cross, why = PANEL_SPLITS[r["id"]]
            note = (f"CUT AS {len(lens)} PIECES: "
                    + " + ".join(sixteenths(L) for L in lens)
                    + f", each {sixteenths(cross)} — {why}"
                    + (f". {note}" if note else ""))
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
    write(ws, cl,
          ["Part", "Qty", "Assembly", "Stock", "Length", "Width", "Thick", "Source", "Notes"],
          [26, 6, 12, 18, 10, 10, 8, 30, 78])

    # ---------------------------------------------------------- Sheet goods
    ws = wb.create_sheet("Sheet goods")
    sg = []
    for L, W, lab, stock, why in sorted(flat, key=lambda f: (f[3], -max(f[0], f[1]))):
        sg.append([lab, stock, sixteenths(max(L, W)), sixteenths(min(L, W)),
                   "YES" if lab.endswith(tuple(f"pc{i}" for i in range(1, 6))) else "",
                   why])
    write(ws, sg,
          ["Panel", "Stock", "Long", "Short", "From a split?", "Notes / joint"],
          [26, 14, 10, 10, 14, 90])

    # ---------------------------------------------------------- Hardware
    ws = wb.create_sheet("Hardware")
    hw = [[h, tally[h], "Simpson", ""] for h in HANGERS if tally[h]]
    hw.append(["", "", "", ""])
    for r in hw_rows:
        hw.append([f"{r['a']} -> {r['b']}", r["n"], r["type"], r["fastener"]])
    write(ws, hw, ["Connection / item", "Qty", "Type", "Fastener spec"],
          [46, 8, 14, 110])

    # ---------------------------------------------------------- TBD
    ws = wb.create_sheet("TBD and assumptions")
    tbd = [
        ["GRADE", "Every species/grade cell says TBD",
         "Pending price and availability. Three ply grades are needed and they are "
         "not interchangeable: structural (deck_ply, the half-wall sheathing), "
         "paint-grade show faces (beam wrap, ledge rail and lid, treads, risers, "
         "nook lining), and 1/2 flitches (jamb packs, the header's middle ply)."],
        ["MEMBER", "Deck-ply front-edge blocking at the beam — NOT in this takeoff",
         "Recommended and still open. The joists hang off the beam's face on LUS24s, "
         "so the deck ply's front edge lands at the LVL over eight 10 1/2 gaps and the "
         "deck — the anti-roll diaphragm — has no fastening to the beam at all. "
         "Eight 2x4 blocks on edge: one 8 ft board, 16 screws."],
        ["CLOSED", "The beam notch needs no separate ply cheek (Rev AT)",
         "It is beam_wrap_face, which already spans the corner on the clear outboard "
         "face: adhesive + #8 x 2 at 6 in o.c. over x 0-27, into the tongue above z 57 1/4 "
         "and into the ledger and joist-tail end faces below it. Nothing extra to buy — but "
         "the wrap's fixing over that first 27 in is STRUCTURAL, not finish, and its screws "
         "must stay 1 in clear of the corner and out of the notch void below z 57 1/4."],
        ["FIELD", "Stud locations: bed wall, window wall, right wall",
         "Every ledger fixing count on the Hardware tab assumes 16 in o.c. The window "
         "wall needs a stud (or added blocking) within ~6 in of y 50 for the beam's end "
         "reaction."],
        ["FIELD", "Ceiling joist nearest 50 3/4 from the bed wall",
         "No longer gates the design (Rev AS: the plate is fixed at 47 1/4-50 3/4 and "
         "blocking can be added from the attic), but it decides whether you screw to a "
         "joist or block first."],
        ["FIELD", "Floor joists under the half-wall plate and the kicker", ""],
        ["SPECIFY", "hw_bottom_plate_a / _b to floor", "Left TBD by the user 2026-09-06."],
        ["CHECKER", f"{len(silent)} connections carry NO fastener key at all",
         "Filter the Hardware tab for 'NO FASTENER KEY'. verify.py only reports a row "
         "that literally says UNSPECIFIED, so these pass silently: "
         + "; ".join(silent) + ". Most are ordinary nailing, but the kicker is already an "
         "open anchorage item. Worth making verify.py WARN on a missing key — it would "
         "change the 0 WARN baseline, so it is your call. (Counted from the model, not "
         "typed: an earlier hand count said 8.)"],
        ["SPECIFY", "kicker anchorage", ""],
        ["METHOD", "Sheet counts are shelf-packed, not nested",
         "The Sheet goods tab lists every panel with its real size. Buy the counts as a "
         "floor, not a ceiling, and lay out the deck and the loft ceiling on paper first: "
         "both are OVER 48 in y (48 1/4 and 50), so that dimension has to run along the "
         "sheet's 8 ft length and each takes one sheet per piece."],
        ["METHOD", "Cut lengths are FRAMING extents",
         "Finished faces are their own parts. No waste allowance is added anywhere; "
         "the board counts include a 1/8 kerf per cut and nothing else."],
    ]
    tbd.insert(0, ["SOURCE", f"Generated from dimensions.yaml rev {YAML['rev']}",
                   "tools/materials.py, off the same model verify.py and the CAD kernel "
                   "read. Regenerate after ANY model change — nothing here updates itself, "
                   "and a stale workbook looks exactly like a current one."])
    write(ws, tbd, ["Kind", "Item", "Detail"], [12, 52, 100])
    wb.properties.title = f"Loft bed materials and cut list — rev {YAML['rev']}"
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=1):
        row[0].fill = FLAG

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wb.save(OUT)
    print(f"{OUT}: {len(rows)} pieces, {len(buy)} buy lines, rev {YAML['rev']}")


if __name__ == "__main__":
    main()
