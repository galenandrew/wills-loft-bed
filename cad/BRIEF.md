# CAD kernel spike — brief

Date: 2026-09-04. Decided after the Rev V commit. Context in `audits/U-decisions.md` and the memory notes.

## Why

`dimensions.yaml` + `verify.py` check axis-aligned boxes exactly, but the model lies in three places: stringers (their bbox is ignored and every clash/connection rule exempts them), fastener paths (`through:` is typed by hand), and section styling (each sheet module decides cut / beyond / hidden by hand, so sheets drift from each other). A CAD kernel closes all three: real notched stringer solids, ray-cast fasteners, true sections with hidden-line removal. It also gives STEP/STL export and cut lengths from solids.

## Goal (time-boxed: one session, about an afternoon)

Prove, on the stair and landing only, that build123d can be a derived layer under the existing yaml. **Do not** replace `verify.py`, `drawings/`, or `site/`. The yaml stays the single source of truth; the kernel model is built *from* it.

## Where to build

```
cad/
  __init__.py
  model.py      yaml → build123d solids. Boxes for every rectangular member; stringers extruded
                from the true profile (reuse `Stair` in verify.py and `stringer_pts()` in
                drawings/model.py — do not re-derive the stair geometry); panels/ply as boxes.
                Each solid carries the member id and, later, an assembly tag.
  section.py    a section through the model on a plane (x=, y=, or z=) → SVG polylines,
                using the kernel's section + hidden-line projection. Must produce the same
                orientation as drawings/svgview.py's View (plans bed-wall-up; y–z views bed-wall-left).
  check.py      (a) solid–solid interference on the real stringers vs blocking, soffit panel,
                rim, ledgers, hangers; (b) fastener ray cast: a screw as a segment from a
                start point and direction, returning the bodies crossed and depth in each.
  export.py     STEP and STL of the whole model or an assembly subset.
  spike.py      `python3 -m cad.spike` — runs everything below and writes outputs.
spike/          outputs only (gitignored except REPORT.md): model.step, model.stl,
                d4-kernel.svg, d8b-kernel.svg, clash.txt, fasteners.txt
audits/V-kernel-spike.md   the report (see below)
```

Scope of members: stringers A/B/C, landing rim, side member, both ledgers, landing joists, blocking, kicker, landing ply, treads, risers (Rev V: ¾ ply treads, risers butt on top of the tread below), and as context the half-wall header, kings, trimmers, and the ¾ facing. Skip the platform, screen, and room fixtures unless they are free.

Install: `python3 -m pip install build123d` (resolves on this machine's Python 3.13; `cadquery-ocp` 7.9.x). Record the exact versions in the report.

## Success criteria — all four, or say which failed and why

1. **Section fidelity.** `spike/d4-kernel.svg`, a y–z section through stringer B, overlays the current Drawing 4 (`site/figs/d4.svg`, same View scale and margins) with every cut edge within 1/16" of the hand-styled version. Report the largest deviation and where.
2. **Stringer clashes.** `check.py` finds no interference among the landing/stair solids except any that `verify.py` already reports, and it reports the soffit panel's true clearance to each stringer underside (verify.py computes this from the profile; the kernel should agree within 0.01").
3. **Fastener ray cast.** Stringer A's 4 × ¼×4½ SDS into the header through the ¾ facing: the kernel reports facing ¾, then header ply depths, matching the hand-typed `through:` in the yaml. Also stringer B's 3 × ¼×3½ from inside the box through the rim.
4. **Export + timing.** `model.step` opens in a viewer; the full run takes under 10 s so it can live in `build.py` later (the fast box checks stay in the hook).

## Rules that still apply

- Never assert a geometric relationship from memory; compute it. If the kernel and `verify.py` disagree, find out which is wrong before trusting either — say so in the report.
- Framing extents only; finished faces are separate members. Coordinates: x from the window wall, y from the bed wall, z above floor.
- Do not edit `verify.py`, `drawings/`, `content/`, or `site/`. If a yaml member is mis-encoded, fix the yaml and record it in the report.
- `dimensions.yaml` edits trigger the hook (verify + build); that is expected.
- Push back if a criterion is unreasonable. Scale down the spike, not the honesty of the report.

## Report (`audits/V-kernel-spike.md`)

Versions · what was built · each criterion pass/fail with numbers · anything the kernel found that `verify.py` missed (or vice versa) · what it would take to (a) feed `drawings/` from kernel sections with a layer model on top, and (b) run `check.py` inside `build.py` · a recommendation: adopt, adopt for checks only, or drop.

Then update `CLAUDE.md` (Files section, one paragraph on `cad/`) and the memory note. Do not start the drawings port in the same session.
