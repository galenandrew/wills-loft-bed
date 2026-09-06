"""cad.__main__ — run the whole kernel model:  python3 -m cad

Writes cad-out/: model.step, model.stl, d4-kernel.svg, d8b-kernel.svg,
d4-overlay.svg, clash.txt, fasteners.txt, section.txt — and prints a verdict
against the four criteria the kernel was adopted on (archive/CAD-BRIEF.md).

Nothing here writes to dimensions.yaml, verify.py, drawings/, content/ or site/.
"""
from __future__ import annotations

import math
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT]

import drawings.model as dm                      # noqa: E402
from drawings.svgview import View                # noqa: E402

from . import check, export, model, section       # noqa: E402

OUT = os.path.join(ROOT, "cad-out")
# " in 0.17s", " (0.64s)" and the whole TOTAL line — the only run-to-run variation
# in the tracked outputs. Stripped from REPORT.md; still printed.
TIMINGS = re.compile(r" in \d+\.\d+s|\s*\(\d+\.\d+s\)|^TOTAL .*$\n?", re.M)
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


def compare_section(loops, shapes, skip=()):
    """Match each kernel cut face to the nearest hand-drawn shape and measure.
    `skip` is the sheet's own skip list — a member the sheet deliberately leaves
    out has nothing to compare against and is not a fidelity finding."""
    rows = []
    for pid, pts in loops:
        if any(pid.startswith(p) for p in skip):
            continue
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
    # stringer A into the nook header (yaml: 4 × 1/4 × 3-1/2 SDS over y 18-27). Driven
    # from the stringer's outer face — Rev AE: the face is at 107.75 and there is no
    # facing in the path any more, so 3-1/2 goes as deep as 4-1/2 used to.
    *[check.Fastener(f"stringer_a→hw_header #{i+1}",
                     (float(dm.m("stringer_a").x[1]), y, z), (-1, 0, 0), 3.5,
                     "1/4 x 3-1/2 SDS")
      for i, (y, z) in enumerate([(20.0, 43.0), (20.0, 47.5), (25.0, 43.0), (25.0, 47.5)])],
    # stringer B off the rim (yaml: 3 × 1/4 × 3-1/2 SDS from inside the box through
    # the rim, before the deck goes on). Driven from the rim's inside face.
    *[check.Fastener(f"stringer_b→lnd_rim #{i+1}",
                     (float(sum(dm.m("stringer_b").x)) / 2, 16.5, z), (0, 1, 0), 3.5,
                     "1/4 x 3-1/2 SDS")
      for i, z in enumerate([43.0, 45.3, 47.5])],
    # and the side member, the longest screws in the box
    check.Fastener("lnd_side_member→hw_header #1",
                   (float(dm.m("lnd_side_member").x[1]), 9.0, 45.0), (-1, 0, 0), 4.0,
                   "1/4 x 4 structural screw"),
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
    say(f"cad kernel · build123d {md.version('build123d')} · "
        f"OCP {md.version('cadquery-ocp-novtk')} · python {sys.version.split()[0]}")
    say(f"dimensions.yaml rev {dm.REV} · stair: {ST.n_treads + 1} risers @ {ST.R:.4f} + {ST.R_top:.4f}, "
        f"run {ST.run}, throat {ST.throat:.3f}")
    say()

    t = time.time()
    pieces = model.build(riser_scheme="standard", context=True)   # Rev W joinery
    alt = model.build(riser_scheme="as-drawn")           # what Rev V drew, for contrast
    t_build = time.time() - t
    say(f"[build] {len(pieces)} solids in {t_build:.2f}s "
        f"({sum(1 for p in pieces if p.derived)} derived, not yaml members)")
    for a in list(model.SCOPE) + ["context"]:
        n = [p for p in pieces if p.assembly == a]
        say(f"        {a:10s} {len(n):3d} solids  {sum(p.volume for p in n)/1728:7.2f} cu ft")
    for mid, parts in model.NOTCHED.items():
        p = model.by_id(pieces)[mid]
        say(f"        {mid} is ONE notched solid ({p.volume:.3f} cu in, "
            f"x {p.bbox[0][0]:g}\u2192{p.bbox[0][1]:g}); yaml rows fused: {', '.join(parts)}")

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
    lines = [f"kernel interference check · {len(pieces)} solids",
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
    panel = P["nk_soffit_rake"]      # Rev AE: the soffit is two boards; the rake is the one
                                     # that rides the stringers
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
        f"({t_clash:.2f}s) → cad-out/clash.txt")
    say(f"        underside ray cast vs Stair.underside(): worst Δ {worst:.5f}\"")
    for c, pen in sorted(real, key=lambda r: -r[0].volume)[:6]:
        say(f"        · {c}")

    # ------------------------------------------------------- the loft (Rev Y port)
    t = time.time()
    llines, findings = loft_report(pieces)
    w("loft.txt", "\n".join(llines) + "\n")
    say(f"[loft] bearing areas, slat gaps and clearances in {time.time()-t:.2f}s → cad-out/loft.txt")
    for f in findings:
        say(f"       · {f}")

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
    say(f"[fasteners] {len(FASTENERS)} rays in {t_fast:.2f}s → cad-out/fasteners.txt")

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
    rows = compare_section(L4.cut, shapes, skip=("nk_",))   # Drawing 4 leaves the nook to Drawing 5
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
    slines += ["", "overlay written to cad-out/d4-overlay.svg "
               "(hand-drawn shapes grey, kernel cut faces red)"]
    w("section.txt", "\n".join(slines) + "\n")
    w("d4-overlay.svg", overlay_svg(v4, shapes, L4.cut))
    say(f"[section] cut+HLR in {t_sec:.2f}s → cad-out/d4-kernel.svg, cad-out/d8b-kernel.svg")
    say(f"          worst cut-edge deviation vs d4.svg: "
        f"{worst_row[1]:.4f}\" on {worst_row[0]} (1/16\" = 0.0625)")

    # ---------------------------------------------------------------- criterion 4
    t = time.time()
    build_only = [p for p in pieces if p.assembly != "context"]
    export.step(build_only, os.path.join(OUT, "model.step"), name="loft-bed")
    export.step(pieces, os.path.join(OUT, "room.step"), name="loft-bed-in-room")
    export.stl(build_only, os.path.join(OUT, "model.stl"))
    t_exp = time.time() - t
    say(f"[export] model.step {os.path.getsize(os.path.join(OUT,'model.step'))/1024:.0f} kB, "
        f"model.stl {os.path.getsize(os.path.join(OUT,'model.stl'))/1024:.0f} kB in {t_exp:.2f}s")
    # no GUI here, so read the STEP back and check it survived the round trip
    from build123d import import_step
    back = import_step(os.path.join(OUT, "model.step"))
    v_out = sum(p.volume for p in build_only)
    v_in = sum(s.volume for s in back.solids())
    say(f"         re-imported: {len(back.solids())} solids "
        f"(wrote {sum(len(p.solid.solids()) for p in build_only)}), "
        f"volume {v_in:.2f} vs {v_out:.2f} cu in, Δ {abs(v_in - v_out):.4f}")

    total = time.time() - t_all
    say()
    say(f"TOTAL {total:.2f}s  (build {t_build:.2f} · clash {t_clash:.2f} · "
        f"fasteners {t_fast:.2f} · section {t_sec:.2f} · export {t_exp:.2f})")
    # REPORT.md is tracked, so it must change only when the MODEL does. Timings are
    # real output but pure noise in a diff — they stay on stdout and are scrubbed here,
    # so a dirty cad-out/ in `git status` means the kernel genuinely disagrees with the
    # last committed run, not that the machine was busy.
    body = TIMINGS.sub("", "\n".join(log)).rstrip()
    w("REPORT.md", "# cad-out run log\n\nRegenerate with `python3 -m cad` from the repo root.\n"
                   "Timings are printed, not recorded — this file changes only when the model does.\n"
                   "Full write-up: `audits/V-kernel-spike.md`.\n\n```\n" + body + "\n```\n")
    return 0


# ---------------------------------------------------------------------- loft
# What the boxes could not answer about the loft: how much face two members that
# "bear" actually share, and what the real gaps are. Every number here is measured
# off the solids; the `expected:` values it is compared with come from the yaml.
BEARINGS = [
    # (a, b, axis, what the yaml claims)
    # Rev AG: the beam is one notched LVL, and its window end BEARS on the ledger and
    # the sistered joist instead of butting the ledger's end face.
    ("beam", "side_ledger", "z", "bearing — the notch sits on the ledger top at 57.25"),
    ("beam", "deck_joist[0]", "z", "bearing — and on joist 0, sistered to the ledger"),
    ("beam", "hw_top_plate_2", "z", "bearing"),
    ("deck_rim", "hw_top_plate_2", "z", "bearing"),
    ("deck_joist[0]", "rear_ledger", "y", "hanger LUS24"),
    ("deck_joist[0]", "side_ledger", "x", "face-screw — the sister that carries half the beam reaction"),
    ("deck_joist[1]", "beam", "y", "hanger LUS24, 10dx1-1/2 into 1-3/4 of LVL"),
    ("deck_joist[8]", "beam", "y", "same"),
    ("deck_ply", "side_ledger", "z", "bearing — glued and screwed, the anti-roll diaphragm"),
    ("beam_wrap_top", "beam", "z", "the cap the slats stand on"),
    ("rear_ledger", "side_ledger", "x", "not a listed connection"),
    ("screen_top_plate", "slat[0]", "z", "bearing — UNSPECIFIED"),
]


def loft_report(pieces):
    """cad-out/loft.txt — and a short list of things that want the builder's eye."""
    P = model.by_id(pieces)
    exp = dm.d["expected"]
    out = ["loft + screen · what the kernel can answer that a box cannot", ""]
    found = []

    out.append("BEARING AREA — how much face two members that 'bear' actually share")
    for a, b, ax, claim in BEARINGS:
        area = check.bearing_area(P[a].solid, P[b].solid, ax)
        out.append(f"  {a:16s} on {b:16s} [{ax}]  {area:8.2f} sq in   ({claim})")
        if area <= 1e-6:
            found.append(f"{a} → {b}: NO shared face at all ({claim})")
    out.append("")

    out.append("SLAT SEATING — every slat's footprint on what is under it")
    seats = ("beam_wrap_top", "beam", "beam_wrap_face", "side_ledger", "hw_top_plate_2")
    n_slats = int(dm.SCR["slat_count"])
    for i in range(n_slats):
        s_ = P[f"slat[{i}]"]
        got = {b: check.bearing_area(s_.solid, P[b].solid, "z") for b in seats}
        got = {b: v for b, v in got.items() if v > 1e-6}
        txt = ", ".join(f"{b} {v:.2f}" for b, v in got.items()) or "NOTHING"
        out.append(f"  slat[{i:2d}] x {float(M[f'slat[{i}]'].x[0]):7.3f}→{float(M[f'slat[{i}]'].x[1]):7.3f}   {txt}")
    # Rev AG: every slat stands on beam_wrap_top and screws THROUGH it into the LVL, so
    # "seated" is no longer a shared face with the beam — it is whether the screw reaches
    # wood. Cast it: down the slat's centre from just above the cap, and require it to
    # cross the cap and then the beam. That is the same question Rev Z asked of slat[0]
    # (which sat on 3/4 of poplar and nothing else), asked of a detail with a cap in it.
    cap_t = float(M["beam_wrap_top"].size("z"))
    # the beam's extents come from the FUSED solid, not the yaml body row — the notched
    # end (beam_tongue, x 0->3) is part of the same board and carries slat 0.
    bx = list(P["beam"].bbox[0])
    missing, part, off = [], [], []
    for i in range(n_slats):
        sm = M[f"slat[{i}]"]
        sx = [float(v) for v in sm.x]
        lo, hi = max(sx[0], bx[0]), min(sx[1], bx[1])       # the slat's width over the LVL
        if hi - lo <= 1e-6:
            missing.append(i)
            continue
        if hi - lo < float(sm.size("x")) - 0.011:
            part.append((i, hi - lo))
        cx = (lo + hi) / 2                                  # centre the screw on the wood
        if abs(cx - (sx[0] + sx[1]) / 2) > 1e-6:
            off.append(i)
        # in y the slat is half on the LVL and half on the wrap face's top edge (its
        # outer face is flush with the wrap at 50.75), so the screw goes in the inboard
        # half — the centre of the slat/beam overlap, not the centre of the slat.
        sy, by = [float(v) for v in sm.y], list(P["beam"].bbox[1])
        cy = (max(sy[0], by[0]) + min(sy[1], by[1])) / 2
        hit = check.ray_cast(check.Fastener(f"slat[{i}] screw", (cx, cy, float(sm.z[0]) + 0.01),
                                            (0, 0, -1), 3.0), pieces)
        if sum(h.depth for h in hit if h.piece == "beam") < 3.0 - cap_t - 0.011:
            missing.append(i)
    if missing:
        found.append(f"slat{missing}: a screw through the cap never reaches the beam")
    for i, w in part:
        found.append(f"slat[{i}]: only {w:.2f} of its 1.50 width is over the LVL "
                     f"(it overhangs the beam's end onto the stair face) — offset its screw inboard")
    out.append(f"  seated on {cap_t:.2f} of cap over the LVL; "
               f"{n_slats - len(missing)} of {n_slats} take a screw into the beam"
               + (f", {len(off)} of them offset from the slat's own centre" if off else ""))
    out.append("")

    out.append("SLAT GAPS — kernel minimum distance, vs expected slat_clear "
               f"{exp['slat_clear']} and screen.max_clear {dm.SCR['max_clear']}")
    gaps = []
    for i in range(1, n_slats):
        d_, _, _ = check.clearance(P[f"slat[{i-1}]"].solid, P[f"slat[{i}]"].solid)
        gaps.append(d_)
    out.append(f"  {len(gaps)} gaps, min {min(gaps):.4f}\" max {max(gaps):.4f}\"")
    if max(gaps) > float(dm.SCR["max_clear"]):
        found.append(f"slat gap {max(gaps):.4f}\" exceeds max_clear {dm.SCR['max_clear']}\"")
    out.append("")

    out.append("CLEARANCES — true minimum distance between solids")
    # fan_clearance is a HORIZONTAL reach distance — the y gap from the platform's
    # finished front face to the fan disc (verify.py: fan.y0 - platform_finished[1]).
    # Measure that, not a 3D slat distance: until Rev AN the slats' outer face sat on
    # 50.75 as well, so the two agreed by coincidence, and the row has read "differs
    # from expected" ever since the slats moved inboard to centre on the beam.
    guard = max(P[i].bbox[1][1] for i in ("beam_wrap_face", "beam_wrap_top", "screen_top_plate"))
    rows = [("fan → platform face (horizontal)", P["fan"].bbox[1][0] - guard,
             float(exp["fan_clearance"])),
            ("mattress top → ceiling", dm.CEILING - P["mattress"].bbox[2][1],
             float(exp["sitting_headroom"])),
            ("deck top → ceiling", dm.CEILING - P["deck_ply"].bbox[2][1],
             float(exp["deck_headroom"])),
            ("floor → loft ceiling underside", P["loft_ceiling"].bbox[2][0],
             float(exp["clear_under_joists"])),
            ("floor → loft ceiling underside (beam)", P["loft_ceiling"].bbox[2][0],
             float(exp["clear_under_beam"]))]
    for name, got, want in rows:
        flag = "" if abs(got - want) <= 0.011 else "   ← differs from expected:"
        out.append(f"  {name:34s} kernel {got:8.4f}   expected {want:8.4f}{flag}")
        if flag:
            found.append(f"{name}: kernel {got:.4f}\", yaml expects {want}")
    # What the screen itself keeps between a child and the blades — the kernel's own
    # answer, in 3D, with no yaml expectation to compare against. Since Rev AN the
    # slats sit inboard of the platform face, so this is the LARGER of the two.
    fan_3d = min(check.clearance(P["fan"].solid, P[f"slat[{i}]"].solid)[0]
                 for i in range(n_slats))
    out.append(f"  {'fan → nearest slat (true 3D)':38s} kernel {fan_3d:8.4f}")
    # the bay is between the ledge rail and the beam's INNER face; the poplar wrap is
    # on the far side of the beam and is not what the mattress meets.
    d_, _, _ = check.clearance(P["mattress"].solid, P["beam_wrap_inner"].solid)
    out.append(f"  {'mattress → beam inner face (bay slack)':38s} kernel {d_:8.4f}")
    out.append("")
    out.append("UNSPECIFIED fasteners the kernel cannot ray-cast until they are chosen:")
    for c in dm.d["connections"]:
        f_ = str(c.get("fastener") or "")
        if "UNSPECIFIED" in f_ and any(k in c["a"] + c["b"]
                                       for k in ("beam", "slat", "screen", "ledger", "deck", "ledge")):
            out.append(f"  {c['a']} → {c['b']}: {f_}")
    return out, found


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
