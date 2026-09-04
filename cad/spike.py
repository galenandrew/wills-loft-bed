"""cad.spike — run the whole spike:  python3 -m cad.spike

Writes spike/: model.step, model.stl, d4-kernel.svg, d8b-kernel.svg,
d4-overlay.svg, clash.txt, fasteners.txt, section.txt — and prints a verdict
against the four criteria in cad/BRIEF.md.

Nothing here writes to dimensions.yaml, verify.py, drawings/, content/ or site/.
"""
from __future__ import annotations

import math
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "tools")]

import drawings.model as dm                      # noqa: E402
from svgview import View                          # noqa: E402

from . import check, export, model, section       # noqa: E402

OUT = os.path.join(ROOT, "spike")
ST, M = dm.ST, dm.M
TOL = 0.011          # verify.py's coincidence tolerance — a 64th


def w(name, text):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w") as f:
        f.write(text)
    return os.path.join(OUT, name)


# ============================================================ 1 · section fidelity
D4_VIEW = dict(h0=-4, h1=76, v0=0, v1=dm.CEILING + 1, s=5.6, ml=130, mr=70, mt=28, mb=44)
D8B_VIEW = dict(h0=100, h1=133, v0=31, v1=53, s=9, ml=120, mr=60, mt=30, mb=40)


def d4_view():
    p = D4_VIEW
    return View(p["h0"], p["h1"], p["v0"], p["v1"], p["s"],
                ml=p["ml"], mr=p["mr"], mt=p["mt"], mb=p["mb"])


def d8b_view():
    p = D8B_VIEW
    return View(p["h0"], p["h1"], p["v0"], p["v1"], p["s"],
                ml=p["ml"], mr=p["mr"], mt=p["mt"], mb=p["mb"])


def parse_sheet(path, p):
    """Pull the drawn shapes out of a generated figure and put them back into
    inches, by inverting the same View transform that wrote them."""
    svg = open(path).read()

    def h_of(X):
        return p["h0"] + (float(X) - p["ml"]) / p["s"]

    def v_of(Y):
        return p["v1"] - (float(Y) - p["mt"]) / p["s"]

    shapes = []
    for mo in re.finditer(r'<rect class="([^"]+)" x="([-\d.]+)" y="([-\d.]+)" '
                          r'width="([-\d.]+)" height="([-\d.]+)"([^/]*)/>', svg):
        cls, X, Y, W, H, rest = mo.groups()
        h0, h1 = h_of(X), h_of(float(X) + float(W))
        v1, v0 = v_of(Y), v_of(float(Y) + float(H))
        shapes.append((cls + ("+hatch" if "hatch" in rest else ""),
                       [(h0, v0), (h1, v0), (h1, v1), (h0, v1)]))
    for mo in re.finditer(r'<polygon class="([^"]+)" points="([^"]+)"([^/]*)/>', svg):
        cls, pts, rest = mo.groups()
        loop = [(h_of(a), v_of(b)) for a, b in (q.split(",") for q in pts.split())]
        shapes.append((cls + ("+hatch" if "hatch" in rest else ""), loop))
    return shapes


def _centroid(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def _pt_seg(p, a, b):
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return math.dist(p, (ax + t * dx, ay + t * dy))


def _to_boundary(pts, loop):
    return max(min(_pt_seg(p, loop[i], loop[(i + 1) % len(loop)]) for i in range(len(loop)))
               for p in pts)


def hausdorff(a, b):
    """Symmetric max distance between two closed polygons, in inches."""
    return max(_to_boundary(a, b), _to_boundary(b, a))


def compare_section(loops, shapes):
    """Match each kernel cut face to the nearest hand-drawn shape and measure."""
    rows = []
    for pid, pts in loops:
        c = _centroid(pts)
        best, bd = None, 1e9
        for cls, loop in shapes:
            d = math.dist(c, _centroid(loop))
            if d < bd:
                best, bd = (cls, loop), d
        if best is None or bd > 6.0:
            rows.append((pid, None, None, bd))
            continue
        rows.append((pid, best[0], hausdorff(pts, best[1]), bd))
    return rows


# ============================================================ 3 · fasteners
FASTENERS = [
    # stringer A into the nook header, through the 3/4 facing (yaml: 4 × 1/4 × 4-1/2
    # SDS through the facing, over y 18-27). Driven from the stringer's outer face.
    *[check.Fastener(f"stringer_a→hw_header #{i+1}", (108.5, y, z), (-1, 0, 0), 4.5,
                     "1/4 x 4-1/2 SDS")
      for i, (y, z) in enumerate([(20.0, 43.0), (20.0, 47.5), (25.0, 43.0), (25.0, 47.5)])],
    # stringer B off the rim (yaml: 3 × 1/4 × 3-1/2 SDS from inside the box through
    # the rim, before the deck goes on). Driven from the rim's inside face.
    *[check.Fastener(f"stringer_b→lnd_rim #{i+1}", (119.0, 16.5, z), (0, 1, 0), 3.5,
                     "1/4 x 3-1/2 SDS")
      for i, z in enumerate([43.0, 45.3, 47.5])],
    # and the side member, whose 5" screws are the longest in the box
    check.Fastener("lnd_side_member→hw_header #1", (108.5, 9.0, 45.0), (-1, 0, 0), 5.0,
                   "1/4 x 5 structural screw"),
]


def yaml_through(a_id, b_id):
    for c in dm.d["connections"]:
        if c["a"] == a_id and c["b"] == b_id:
            return c.get("through", []), c.get("fastener", "")
    return None, ""


# ============================================================ main
def main():
    t_all = time.time()
    log = []

    def say(s=""):
        print(s)
        log.append(s)

    import importlib.metadata as md
    say(f"cad spike · build123d {md.version('build123d')} · "
        f"OCP {md.version('cadquery-ocp-novtk')} · python {sys.version.split()[0]}")
    say(f"dimensions.yaml rev {dm.REV} · stair: {ST.n_risers} risers @ {ST.R:.4f}, "
        f"run {ST.run}, throat {ST.throat:.3f}")
    say()

    t = time.time()
    pieces = model.build(riser_scheme="standard")       # Rev W joinery
    alt = model.build(riser_scheme="as-drawn")           # what Rev V drew, for contrast
    t_build = time.time() - t
    say(f"[build] {len(pieces)} solids in {t_build:.2f}s "
        f"({sum(1 for p in pieces if p.derived)} derived, not yaml members)")

    # ---------------------------------------------------------------- criterion 2
    t = time.time()
    clashes = check.interference(pieces)
    clashes_alt = check.interference(alt)
    t_clash = time.time() - t

    def split(cl):
        real, rounding = [], []
        for c in cl:
            pen = min(hi - lo for lo, hi in c.box)
            (rounding if pen <= TOL else real).append((c, pen))
        return real, rounding

    real, rounding = split(clashes)
    real_alt, rounding_alt = split(clashes_alt)
    lines = [f"kernel interference check · {len(pieces)} solids · {t_clash:.2f}s",
             f"verify.py reports 0 volume clashes (it skips every `kind: stringer` member "
             f"and knows nothing about treads/risers, which are not members).", ""]
    lines.append(f"REAL INTERFERENCE — Rev W joinery, riser scheme 'standard': {len(real)}")
    for c, pen in sorted(real, key=lambda r: -r[0].volume):
        lines.append(f"  {c}   min penetration {pen:.3f}\"")
    lines.append("")
    lines.append(f"for contrast — riser scheme 'as-drawn', what Rev V drew: {len(real_alt)}")
    for c, pen in sorted(real_alt, key=lambda r: -r[0].volume):
        lines.append(f"  {c}   min penetration {pen:.3f}\"")
    lines.append("")
    lines.append(f"COINCIDENT FACES (penetration ≤ verify.py's TOL {TOL}\") — not findings: {len(rounding)}")
    for c, pen in rounding:
        lines.append(f"  {c}   {pen:.4f}\"")

    # soffit clearance, kernel vs verify.py
    P = model.by_id(pieces)
    panel = P["soffit_panel"]
    # only where a stringer exists: the stringers start at y_top, the nook opening at y=3
    ys = [round(y, 2) for y in [ST.y_top, dm.Y_MEET, 20.0, 27.0, 35.0, 40.0, dm.NOOK_Y[1]]]
    lines += ["", "SOFFIT PANEL → STRINGER UNDERSIDE  (kernel ray cast vs verify.py's Stair.underside)"]
    worst = 0.0
    for sid in ("stringer_a", "stringer_b", "stringer_c"):
        scan = check.underside_scan(P[sid], ys)
        top = {y: _top_of(panel, P[sid], y) for y in ys}
        lines.append(f"  {sid}")
        for y in ys:
            kz, pz = scan[y], top[y]
            vz = ST.underside(y)
            if kz is None:
                lines.append(f"    y={y:6.2f}  no stringer material on this ray")
                continue
            d = abs(kz - vz)
            worst = max(worst, d)
            gap_k = (kz - pz) if pz is not None else None
            gap_v = (vz - (dm.CEIL + dm.PANEL)) if y <= dm.Y_MEET else 0.0
            lines.append(f"    y={y:6.2f}  underside kernel {kz:7.3f}  verify {vz:7.3f}  Δ {d:.5f}"
                         f"   panel top {pz if pz is None else round(pz,3)}"
                         f"   gap kernel {'—' if gap_k is None else f'{gap_k:6.3f}'}"
                         f"  verify {gap_v:6.3f}")
    d_pan, pa, pb = check.clearance(panel.solid, P["lnd_side_member"].solid)
    lines.append(f"  soffit panel → lnd_side_member: kernel {d_pan:.4f}\"  "
                 f"(verify.py: {M['lnd_side_member'].z[0] - (dm.CEIL + dm.PANEL):.4f}\")")
    w("clash.txt", "\n".join(lines) + "\n")
    say(f"[clash] {len(real)} real interferences, {len(rounding)} coincident faces "
        f"({t_clash:.2f}s) → spike/clash.txt")
    say(f"        underside ray cast vs Stair.underside(): worst Δ {worst:.5f}\"")
    for c, pen in sorted(real, key=lambda r: -r[0].volume)[:6]:
        say(f"        · {c}")

    # ---------------------------------------------------------------- criterion 3
    t = time.time()
    flines = ["fastener ray casts · a screw is a segment from a start point along a direction", ""]
    for f in FASTENERS:
        hits = check.ray_cast(f, pieces)
        flines.append(f"{f.id}  [{f.spec}]  start {f.start} dir {f.direction} len {f.length}")
        run = 0.0
        for h in hits:
            flines.append(f"    {h.entry:5.3f} → {h.exit:5.3f}   {h.piece:26s} {h.depth:5.3f}\"")
            run += h.depth
        flines.append(f"    material crossed {run:.3f}\" of {f.length}\"; "
                      f"{f.length - run:.3f}\" in air/void")
        flines.append("")
    a_thru, a_spec = yaml_through("stringer_a", "hw_header")
    b_thru, b_spec = yaml_through("stringer_b", "lnd_rim")
    flines += ["yaml `through:` for stringer_a → hw_header: "
               f"{a_thru}  ({sum(M[t].size('x') for t in a_thru):.2f}\" total) — {a_spec}",
               "yaml `through:` for stringer_b → lnd_rim: "
               f"{b_thru or 'none'} — {b_spec}"]
    w("fasteners.txt", "\n".join(flines) + "\n")
    t_fast = time.time() - t
    say(f"[fasteners] {len(FASTENERS)} rays in {t_fast:.2f}s → spike/fasteners.txt")

    # ---------------------------------------------------------------- criterion 1
    t = time.time()
    L4 = section.section(pieces, "x", 119.0, look_positive=True)
    v4 = d4_view()
    w("d4-kernel.svg", section.to_svg(L4, v4, pieces,
                                      "Drawing 4 — kernel section at x = 119 (stringer B)"))
    L8 = section.section(pieces, "y", 20.0, look_positive=False)
    v8 = d8b_view()
    w("d8b-kernel.svg", section.to_svg(L8, v8, pieces,
                                       "Drawing 8b — kernel section at y = 20"))
    t_sec = time.time() - t

    shapes = parse_sheet(os.path.join(ROOT, "site", "figs", "d4.svg"), D4_VIEW)
    rows = compare_section(L4.cut, shapes)
    slines = [f"section fidelity · kernel cut at x=119 vs site/figs/d4.svg "
              f"({len(shapes)} drawn shapes parsed back into inches)", ""]
    worst_row = None
    for pid, cls, dev, cd in sorted(rows, key=lambda r: -(r[2] or 0)):
        if dev is None:
            slines.append(f"  {pid:22s} NO MATCH within 6\" of any drawn shape "
                          f"(nearest centroid {cd:.2f}\") — not drawn on Drawing 4")
            continue
        flag = "  ←" if dev > 1 / 16 else ""
        slines.append(f"  {pid:22s} vs <{cls}>  max deviation {dev:.4f}\"{flag}")
        if worst_row is None or dev > worst_row[1]:
            worst_row = (pid, dev, cls)
    slines += ["", "overlay written to spike/d4-overlay.svg "
               "(hand-drawn shapes grey, kernel cut faces red)"]
    w("section.txt", "\n".join(slines) + "\n")
    w("d4-overlay.svg", overlay_svg(v4, shapes, L4.cut))
    say(f"[section] cut+HLR in {t_sec:.2f}s → spike/d4-kernel.svg, spike/d8b-kernel.svg")
    say(f"          worst cut-edge deviation vs d4.svg: "
        f"{worst_row[1]:.4f}\" on {worst_row[0]} (1/16\" = 0.0625)")

    # ---------------------------------------------------------------- criterion 4
    t = time.time()
    export.step(pieces, os.path.join(OUT, "model.step"))
    export.stl(pieces, os.path.join(OUT, "model.stl"))
    t_exp = time.time() - t
    say(f"[export] model.step {os.path.getsize(os.path.join(OUT,'model.step'))/1024:.0f} kB, "
        f"model.stl {os.path.getsize(os.path.join(OUT,'model.stl'))/1024:.0f} kB in {t_exp:.2f}s")
    # no GUI here, so read the STEP back and check it survived the round trip
    from build123d import import_step
    back = import_step(os.path.join(OUT, "model.step"))
    v_out = sum(p.volume for p in pieces)
    v_in = sum(s.volume for s in back.solids())
    say(f"         re-imported: {len(back.solids())} solids "
        f"(wrote {sum(len(p.solid.solids()) for p in pieces)}), "
        f"volume {v_in:.2f} vs {v_out:.2f} cu in, Δ {abs(v_in - v_out):.4f}")

    total = time.time() - t_all
    say()
    say(f"TOTAL {total:.2f}s  (build {t_build:.2f} · clash {t_clash:.2f} · "
        f"fasteners {t_fast:.2f} · section {t_sec:.2f} · export {t_exp:.2f})")
    w("REPORT.md", "# spike run log\n\nRegenerate with `python3 -m cad.spike` from the repo root.\n"
                   "Full write-up: `audits/V-kernel-spike.md`.\n\n```\n" + "\n".join(log) + "\n```\n")
    return 0


def _top_of(panel, stringer, y):
    """z of the soffit panel's top face directly under the stringer at plan y."""
    (x0, x1), _, _ = stringer.bbox
    xm = (x0 + x1) / 2
    ts = check._hits(panel.solid, (xm, y, 100.0), (0, 0, -1), 200.0)
    return 100.0 - ts[0] if ts else None


def overlay_svg(view, shapes, loops):
    out = ['<rect width="%.0f" height="%.0f" fill="#fff"/>' % (view.W, view.H)]
    for _cls, loop in shapes:
        pt = " ".join(f"{view.X(h):.2f},{view.Y(v):.2f}" for h, v in loop)
        out.append(f'<polygon points="{pt}" fill="#00000010" stroke="#999" stroke-width="2.4"/>')
    for _pid, pts in loops:
        pt = " ".join(f"{view.X(h):.2f},{view.Y(v):.2f}" for h, v in pts)
        out.append(f'<polygon points="{pt}" fill="none" stroke="#d02020" stroke-width="0.9"/>')
    return (f'<svg viewBox="0 0 {view.W:.0f} {view.H:.0f}" xmlns="http://www.w3.org/2000/svg">'
            + "".join(out) +
            '<text x="12" y="16" font-family="sans-serif" font-size="11">'
            'grey = Drawing 4 as drawn · red = kernel cut at x=119</text></svg>')


if __name__ == "__main__":
    sys.exit(main())
