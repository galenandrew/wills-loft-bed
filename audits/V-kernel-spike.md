# Rev V — CAD kernel spike

Date: 2026-09-04 · Time-boxed spike per `cad/BRIEF.md`. Inline (no subagents).
**Amended twice, same day** — see the two sections at the end. The edge-attribution blocker
this report first named as the main obstacle to porting the drawings does not
exist. `cad/section.py` now carries the fix and the recommendation is unchanged in
verdict but weaker in its reasons.
Nothing in `dimensions.yaml`, `verify.py`, `drawings/`, `content/` or `site/` was
changed. Reproduce with `python3 -m cad.spike` from the repo root.

## Versions

| | |
|---|---|
| Python | 3.13.12 (pyenv) |
| build123d | 0.11.1 |
| OCCT bindings | `cadquery-ocp-novtk` 7.9.3.1.1 (+ `cadquery-ocp-proxy`) — OCCT 7.9.3 |
| Pulled in | `ocpsvg` 0.6.0, `ezdxf` 1.4.4, `svgpathtools`, `trianglesolver`, numpy 2.5.2, scipy 1.18.1 |
| On-disk cost | `OCP` 220 MB, `build123d` 3 MB |

`python3 -m pip install build123d` resolved first try on this machine's 3.13.

## What was built

```
cad/__init__.py
cad/model.py     yaml → 38 solids. Boxes from framing extents; the three stringers
                 extruded from drawings.stringer_pts() through their own thickness.
                 Stair geometry is imported, never re-derived: verify.Stair and
                 drawings.model.stringer_pts are the only sources.
cad/section.py   plane ∩ solids (cut faces) + HLR projection of the far and near
                 sides, emitted in the *inch* (h,v) coordinates tools/svgview.View
                 takes, so a kernel figure drops onto the sheet at the sheet's own
                 scale and margins.
cad/check.py     solid–solid interference (real booleans, bbox-prefiltered),
                 BRepExtrema minimum distance, and a fastener ray cast that returns
                 the bodies crossed in order with entry/exit and depth in each.
cad/export.py    STEP and STL of the whole model or one assembly.
cad/spike.py     python3 -m cad.spike — runs all of it, writes spike/.
```

Scope, per the brief: stringers A/B/C, kicker, the whole landing box, landing ply,
the half-wall as context, plus **12 solids the yaml does not contain** — 5 treads,
6 risers and the soffit panel, all flagged `derived=True` — and `hw_header` carried
as its three laminations instead of one 3½" box.

Run: **0.88 s total** (build 0.05 · interference 0.30 · fasteners 0.01 · sections
0.34 · export 0.09), plus 2.7 s to import build123d.

## Criteria

### 1 · Section fidelity — PASS, with one real drift found

Kernel cut at x = 119 (stringer B), rendered through the identical
`View(-4, 76, 0, 97, 5.6, ml=130, mr=70, mt=28, mb=44)` as Drawing 4. The published
`site/figs/d4.svg` was parsed back into inches by inverting that same transform (29
shapes), and each of the 17 kernel cut faces was matched to the nearest drawn shape
and compared by symmetric Hausdorff distance on the outlines — not by vertex count,
because OCCT merges the collinear points `stringer_pts()` emits (20 points in, 15 out;
same polygon).

| kernel cut face | max deviation |
|---|---|
| `stringer_b` (15-vertex notched profile), `lnd_rim`, `lnd_ledger_bedwall` | **0.0043"** |
| `kicker`, all 5 treads, all 6 risers | **0.0000"** |
| `lnd_ply` | **0.1251"** ← |
| `soffit_panel` | no counterpart — Drawing 4 does not draw it |

The floor for this comparison is the sheet itself: `svgview.View` writes coordinates
at one decimal place, so at 5.6 px/in every drawn edge carries up to ±0.0089" of
quantisation. Everything except the landing ply is at that floor. **Largest real
deviation: 0.1251" on `lnd_ply`, at its stair-side edge.**

That is not a kernel error. `drawings/d4_stair_section.py:13` draws the landing ply
as `m("lnd_ply").y[1] + 0.125` — a ⅛" nose typed into the sheet. The yaml member
stops at y 27. So **the landing ply's cut depth is 27⅛, not 27, and the model does
not know it.** Note the inconsistency: the treads' ⅛" overhang *is* in the yaml
(`stair.tread_board_width: 9.125`), which is why all five treads land at 0.0000".
Fixing it means `lnd_ply.y: [0, 27.125]` **and** dropping the `+ 0.125` from d4 in
the same edit — a `drawings/` change, which this spike is not allowed to make.

`spike/d4-kernel.svg` (cut + far-side HLR + near-side ghost), `spike/d4-overlay.svg`
(drawn shapes grey, kernel cut red), `spike/d8b-kernel.svg` (the y = 20 section,
where the header's three laminations show as three separate cut faces).

### 2 · Stringer clashes — the agreement half passes exactly; the "no interference" half fails, because there is interference

**Agreement with `verify.py`, where both can answer:**

| quantity | kernel | verify.py | Δ |
|---|---|---|---|
| stringer underside, ray-cast at y = 18, 18.5, 20, 27, 35, 40, 47, all three stringers | see `spike/clash.txt` | `Stair.underside(y)` | **0.00000"** at all 21 points |
| soffit panel top → stringer underside, raked zone | 0.000 | 0.000 | 0 |
| soffit panel top → stringer underside at y = 18 (still flat there) | 0.458 | 0.458 | 0 |
| soffit panel → `lnd_side_member` | **0.2100"** | **0.2100"** | 0 |

Well inside the 0.01" the brief asked for. The kernel and the profile maths are the
same geometry, which is the point: the kernel adds nothing here and contradicts
nothing.

**Interference: `verify.py` reports 0 volume clashes. The kernel finds three
distinct real conflicts** (24 pairs, because the risers repeat). It can, because
`verify.py:check_clashes` skips every `kind: stringer` member by construction, and
because treads and risers are not members at all.

**A · The stringers pass through the kicker.** 7.87 cu in each, 1½" of penetration
over 3½" of run, all three (x 107–108½, 118¼–119¾, 129½–131; y 68½–72; z 0–1½).
The profile's bottom is flat on the floor from y 63.57 to 72 (that is the seat
cut); the kicker is a 2×4 flat on the floor at y 68½–72. They want the same space.
`verify.py` passes this: its `bearing` rule for a stringer checks *plan* overlap
only — "seat over 1½ × 3½" — which is exactly what it prints today.
The stringer is 7.54" deep there (top edge at riser 1 − tread = 7.536), so a
1½ × 3½ notch over the kicker leaves 6.04" — no throat problem. But it is a cut on
the stringer that `stringer_pts()` does not model and no drawing shows, and the
kicker's own note already says its position is ASSUMED. **Decide before the
stringers are cut.**

**B · The riser boards land inside the stringers.** As `draw_treads()` places them
(y₁−¾ → y₁, dropping to the notch corner) each riser occupies ¾" of solid stringer
at each of the three stringers — 9.32 cu in at a time for risers 2–6, 8.48 for riser 1,
18 pairs — and riser 1 additionally drives 27.00 cu in through the kicker.

Rebuilt with the Rev V note read literally — *"risers butt on top of the tread
below"*, i.e. on the **front** of the plumb cut, y₁ → y₁+¾, standing on the tread
below and stopping under the tread above — the count drops from 24 pairs to 8:
**all 15 stringer∩riser pairs for risers 1–5 go away, and so does the kicker one**,
and each riser becomes a single full-width 24" board. What is left is findings A and
C. The as-drawn placement instead needs each riser cut into two 9¾" pieces to fit the
bays between stringers (108½–118¼ and 119¾–129½): 10 pieces instead of 5.

Both readings are buildable; only one is one board per step, and it is the one Rev V's
own note describes. Consequence of the on-tread reading: riser 1 moves to y 72 → 72¾,
so the stair's footprint becomes 72¾ where `expected.stair_projection` says 72 — and
it then clears the kicker.

**C · The landing face, the blocking and the stringers' top runs all want y 26¼–27.**
`lnd_blocking` is encoded y 25½–27 (note: *"front face flush with riser 6"*). The
landing-face board has to sit at y 26¼–27 for its face to be flush at the landing
edge — which is 25.59 cu in into each blocking piece, and 9.32 cu in into each
stringer's top run. The stringers themselves already form that face at y = 27 between
the bays, so the board is really two 9¾" fillers in the bays, and the blocking behind
it belongs at **y 24¾–26¼**, not 25½–27. Nothing in `verify.py` can see this: riser 6
is not a member.

**Not findings** (4 pairs, listed separately in `spike/clash.txt`): the stringer tops
and the landing ply overlap by 0.0043", because `lnd_ply.z[0]` is written 48.96 where
the exact landing-minus-deck is 48.9643. Inside `verify.py`'s TOL (0.011"). Rounding,
not material.

### 3 · Fastener ray cast — PASS

A screw is a segment: start point, direction, length. The ray reports every body it
crosses, in order, with entry/exit and depth.

`stringer_a → hw_header`, 4 × ¼ × 4½ SDS driven from the stringer's outer face
(x 108½) in −x, at (y, z) = (20, 43), (20, 47½), (25, 43), (25, 47½) — all four
identical:

```
0.000 → 1.500   stringer_a               1.500"
1.500 → 2.250   hw_sheath_stair_head     0.750"   ← the ¾ facing, exactly the yaml's `through:`
2.250 → 3.750   hw_header#2x10-stair     1.500"
3.750 → 4.250   hw_header#ply-1/2        0.500"
4.250 → 4.500   hw_header#2x10-loft      0.250"
```

Matches the hand-typed `through: [hw_sheath_stair_head]` (0.75") exactly, and then
says something the yaml cannot: **a 4½" screw reaches 2¼" into a 3½" header — through
the stair-side 2×10, through the ½" ply flitch, and only ¼" into the far 2×10.** Worth
a look before ordering; a 5" screw would put ¾" into the far ply. (The 1.5/0.5/1.5
lay-up is ASSUMED — it is the only split that makes the lumber table's 3½", but no
drawing states the order.)

`stringer_b → lnd_rim`, 3 × ¼ × 3½ SDS from inside the box at x 119, y 16½, z 43 /
45.3 / 47½: rim 1.500", then stringer_b 2.000" — full length in material, 2" of bite
into the stringer's plumb cut. The yaml declares this connection with no `through:`
because `a` and `b` are the reverse of the driving direction; the ray gets the order
right without being told.

Bonus: `lnd_side_member → hw_header`, ¼ × 5: 1.5 side member + 0.75 facing + 1.5 +
0.5 + 0.75 — the 5" screw is the one that fully crosses the sandwich.

### 4 · Export + timing — PASS

`spike/model.step` 751 kB, `spike/model.stl` 29 kB. No GUI viewer on this machine, so
"opens in a viewer" was evidenced by a round trip instead: re-importing the STEP gives
**38 solids for 38 written, total volume 10828.61 cu in vs 10828.61, Δ 0.0000**.
Whole run **0.88 s**, against the brief's 10 s budget.

## What the kernel found that verify.py missed — and vice versa

Kernel → verify: findings A, B and C above, plus the ⅛" landing-ply nose from
criterion 1, plus the header's real per-ply embedment. All four are things boxes
cannot represent (a notched profile, a member that is not a member, a laminated
member, a hand-typed literal in a sheet).

Verify → kernel: everything else. `verify.py`'s two parked FAILs (beam left end,
slat 0) and its `room chain` WARN are all outside this scope and the kernel has
nothing to say about them. More importantly, `verify.py` checks things the kernel
does not: hanger engagement percentages, "is a's full width backed by b", stock
sections against the lumber table, room bounds, and the `expected:` audit trail.
**The kernel is not a replacement for any of that.** Where both can answer, they
agreed to 5 decimal places at every one of 21 sample points.

Nothing the kernel says contradicts `verify.py`. Every conflict it found is in a
place `verify.py` deliberately declines to look.

## What it would take to go further

**(a) Feed `drawings/` from kernel sections, with a layer model on top.** The
geometry half already works — `cad/section.py` emits into `View`'s own inch
coordinates and the cut faces land on the current sheet to 0.004". Three things are
missing:

1. ~~**Edge attribution.**~~ **Solved — see the Correction below.** `HLRBRep_Algo`
   takes each piece as a separate added shape and `HLRBRep_HLRToShape.VCompound(S)` /
   `HCompound(S)` read back that piece's own visible and hidden edges with occlusion
   computed across the whole assembly. `cad/section.py:project()` now does this;
   every projected edge carries its member id, so `lum` / `lum2` / `sheet` / `fin`
   styling keys on it directly.
2. **A per-sheet visibility declaration.** Drawing 4 ghosts *only* the half-wall;
   the kernel's `near` layer honestly returns everything on the near side, which is
   mostly lines coincident with the cut. Each sheet needs about one line saying what
   is cut, what is shown beyond, and what is ghosted.
3. **The derived solids need a home.** Treads, risers, the soffit panel and the
   header laminations are invented in `cad/model.py`. If sheets are generated from
   the kernel they have to come from the yaml (or from one shared derived-members
   module) or the drawings lose material they draw today.

Labels, dimensions and captions stay hand-placed in `drawings/d<N>_*.py`; none of
that changes. Cost per sheet is ~0.34 s of section work on top of a 2.7 s import,
against a `build.py` that currently finishes in under a second — so the hook would
get noticeably slower.

**(b) Run `check.py` inside `build.py`.** The checks themselves are cheap (0.30 s
interference + 0.01 s fasteners on 38 solids). The import is not, and the hook fires
on every Write/Edit. Better shape: leave the fast box checks in the hook exactly as
they are, and run the kernel checks on demand and before cutting — the way
`drawing-auditor` and `connection-checker` are already used.

## Recommendation

**Adopt for checks. Do not port the drawings yet.**

The kernel earned its keep in one afternoon: three real conflicts in the stair and
landing that the box model is structurally unable to see, one of them (the stringers
through the kicker) a cut on a member that has not been made yet, and one (the riser
scheme) that turns 10 pocket-cut riser pieces into 5 full-width boards. It agreed
with `verify.py` everywhere both could answer, to 5 decimals. That is exactly the
result that justifies keeping it as a second opinion and not as a replacement.

Against porting the drawings now, after the correction below, exactly one argument
survives: **220 MB of OCCT and a 2.7 s import in front of a build that currently
finishes in under a second, on a hook that fires on every Write/Edit** — for sheets
that already land within 0.004" of the kernel. The drift the kernel found in the
sheets was one hand-typed ⅛", not a systematic problem. That is a cost question, not
an engineering one, and it is the builder's call.

Suggested next steps, in order:

1. **Decide the three conflicts** (kicker vs seat cut; riser scheme; blocking at
   y 24¾–26¼) — all three are stair/landing cuts and all three are now-or-never.
2. **Land the ⅛" landing-ply nose** in the yaml and drop the literal from d4, in one
   edit, with a rev bump.
3. Keep `python3 -m cad.spike` as a pre-cut gate alongside `drawing-auditor` and
   `connection-checker`. Extend `SCOPE` in `cad/model.py` to the platform and screen
   when those are next touched.
4. Revisit the drawings port only if a second kind of drift shows up in a sheet, or
   if a rendered 3D view is wanted for its own sake — the STEP is already there.

## Outputs

`spike/` (gitignored except `REPORT.md`): `model.step`, `model.stl`, `d4-kernel.svg`,
`d8b-kernel.svg`, `d4-overlay.svg`, `clash.txt`, `fasteners.txt`, `section.txt`,
`REPORT.md` (the run log).

---

## Correction (same day, after the report was first written)

This report claimed edge attribution was the one real engineering item standing
between `drawings/` and kernel-generated geometry, and costed it at half a day. That
was wrong, and it was the load-bearing reason for "don't port yet". The facts:

`HLRBRep_Algo.Add()` accepts each solid as a separate added shape, and
`HLRBRep_HLRToShape` has a per-shape overload — `VCompound(S)`, `HCompound(S)`,
`OutLineVCompound(S)`, and so on — that returns *that shape's* visible and hidden
edges with occlusion still computed across everything added. build123d's
`project_to_viewport()` only wraps the no-argument form, which is why the first pass
came back anonymous.

Measured on the spike's 38 solids, Drawing 4's camera angle:

| | |
|---|---|
| per-shape edge sets vs one whole-assembly query | **108 visible / 284 hidden, both ways** — an exact partition, nothing lost or doubled |
| cross-shape occlusion | real: `stringer_b` and `stringer_c` return **0 visible / 30 hidden** each (entirely behind stringer A), as do `lnd_rim`, `lnd_ledger_bedwall`, `lnd_ply`, `hw_header#ply-1/2` |
| cost | **0.01 s** for all 38 solids — cheaper than the three separate compound projections it replaced |
| code | ~30 lines dropping to OCP |

`cad/section.py:project()` now does this. `Layers` carries `(piece id, geometry)`
throughout, so a sheet can style one member differently from its neighbour, and the
per-sheet visibility declaration (item 2 above) reduces to a filter on member id —
e.g. Drawing 4's "ghost the half-wall" is `pid.startswith("hw_")`. Total spike
runtime is unchanged at 0.87 s.

The verdict — adopt for checks, port deliberately rather than now — stands. Its
reasons are narrower: the remaining objection is the dependency and import cost in
the hook, not the drawing engine.

---

## Outcome (same day) — Rev W

All four findings were put to the builder and resolved. Two of my three
"conflicts" turned out to rest on my own mis-modelling of the tread/riser joint,
which the builder corrected:

**The riser detail.** I probed the stringer solid rather than reasoning about it:
at every plumb notch, material is on the **uphill** side and air on the downhill
side, so the exposed riser face is downhill. A riser applied to it sits at
y₁ → y₁+¾ with its bottom edge on the stringer's horizontal cut for the tread
below, and the tread below starts at y₁+¾ and butts its face. That is the
builder's stated detail — riser behind the tread, simple butt joint, nothing
notched — and neither of the two schemes I modelled. Modelled correctly:

| scheme | real interferences |
|---|---|
| `as-drawn` (what `draw_treads()` drew) | 24 |
| `on-tread` (Rev V's note read literally) | 4 |
| **`standard`** (the builder's detail) | **3** — all of them the stringer∩kicker |

Every board is full 24" width, tread boards stay 9⅛, and the nosing-to-nosing
going comes out **exactly 9.000 at all five steps**.

**Two of my findings were wrong, and one number was wrong:**

- **Finding C (move `lnd_blocking`) was an artifact.** With the riser proud at
  y 27→27.75, the blocking's front face at y 27 *is* its backing. The yaml note
  was right; the blocking stays at 25½→27.
- **The ⅛" nose number was wrong.** The ply noses ⅛ past the *riser face* at
  27.75, not past the framing line at 27 — so `lnd_ply.y` is **[0, 27.875]**, not
  27.125 as this report first said.
- **It was the treads, not only the risers, that were misplaced** — they were
  drawn starting at the stringer's notch corner instead of ¾ downhill of it.

**Finding A (stringers through the kicker) stood** and is fixed: `stringer_pts()`
now cuts a 1½ × 3½ notch at the floor seat, and the kicker's position is no longer
`ASSUMED`.

Landed as **Rev W** — `dimensions.yaml` (rev, `lnd_ply`, kicker note, decisions
block), `drawings/model.py` (`stringer_pts`, `draw_treads`, `tread_y_board`,
`riser_y`), `drawings/d4_stair_section.py` (dropped the literal nose, caption), and
`content/revisions.json`. `verify.py` still reports only its two parked FAILs.

**Kernel re-check after the change: 0 real interferences in the stair and landing,
and every Drawing 4 cut face within 0.0043" of the kernel section** — the sheet's
own coordinate-rounding floor. Framing is unchanged; the finished nosings sit ⅞
downhill of the framing lines, so the stair's finished projection is 72⅞ (framing
still 72) and the landing 27⅞ (framing still 27), which the builder accepted rather
than shifting the whole landing box for ⅞".

The spike's own worth is now measurable: it caught a joint that was drawn three
different ways in three places, and a stringer cut that had not been made yet.

---

## Port (same day) — Drawing 4

Ported, with a measurement that corrects this report twice over.

**Fidelity.** `d4()`'s six hand-enumerated cut calls (`R()` × 4, `v.poly(stringer_pts())`,
`draw_treads()`) collapse to one line — `kernel_cut(v, "x", CUT_X, skip=("soffit_panel",))`
— and the plane decides what is cut. Compared shape by shape against the committed
hand-drawn sheet, in inches:

| | |
|---|---|
| shapes before / after | **29 / 29** |
| worst deviation, all matched shapes | **0.0000"** |
| missing or added | **none** |

The SVG differs structurally (13 rects + 16 polygons where there were 28 + 1, since
cut faces come back as loops) but not geometrically. The 15 labels, 6 dimensions and
the caption are untouched — the whole point of porting rather than starting fresh.

**Cost — my baseline was wrong.** This report said "a build that currently finishes
in under a second". Measured, `python3 build.py` is **0.06 s**. So the kernel's ~3 s
import is a 35× hit on a hook that fires on every Write/Edit, not the 3.5 s I
projected. That is bad enough to have killed the port on its own.

**Fixed by caching**, which was the mitigation this report proposed:

| | |
|---|---|
| cold (cache miss, kernel runs) | **3.20 s** |
| warm (cache hit, build123d never imported) | **0.06 s** |
| cached output vs a live kernel run | **byte-identical** (verified) |

The key is a SHA-256 over every input that can change a cut — `dimensions.yaml`,
`verify.py` (`Stair`), `drawings/model.py` (`stringer_pts` and the tread/riser
layout) and all of `cad/*.py` — plus the call's own axis, position and skip list.
Nudging the kicker ½" missed the cache, rebuilt in 2.04 s and moved the notch;
restoring it returned the identical file. `LOFT_KERNEL_NOCACHE=1` forces a real run
and `cad.spike` never reads the cache, so nothing is ever *verified* against a
cached value.

**Scope held deliberately.** Only the cut layer is kernel-generated. Drawing 4's
"beyond" and "ghosted" members are axis-aligned boxes whose projection is already
exact, so `R()` keeps drawing them; swapping them for HLR linework would be a style
change, not a fidelity one. Every other sheet is untouched.

**Revised recommendation.** Adopt for checks (unchanged), and port the remaining
section sheets — d5, d8b, d3, d7 — as they are next touched. With the cache the
objection this report ended on is gone: the hook stays at 0.06 s, and the 3 s is
paid only when the geometry actually moved, which is exactly when you wanted to look
at the figure anyway. The plans (d1, d6, d8a, d9) should stay on box projection —
the kernel would add cost and nothing else.

---

## Handedness (same day) — the exported solid was mirrored

The builder opened `spike/model.stl` and found the half-wall on the wrong side of
the stair. It was, and the cause is worth recording because it nearly sent me
"fixing" a drawing set that was correct all along.

**The yaml's axes are left-handed as they map onto the room.** Facing the closet
wall (+y), the window wall (x = 0) is on your *right*, so yaml +x runs to your left
and `x × y = −z`. The labelling is not wrong — facing the **bed** wall, +x really is
on your right, which is the vantage the sheets are read from — it is just a
left-handed pairing.

In 2D that is harmless. Every figure maps two yaml axes onto the page, and once the
frame is read correctly all twelve check out: the plans are true from-above plans,
Drawing 4's half-wall genuinely is in front of the cut at x 119, and Drawing 8b
genuinely does look toward the bed wall. My first pass computed the viewpoints
assuming a right-handed frame and concluded the plans were drawn from below and the
captions contradicted themselves. **That was wrong**, and it is recorded here
because acting on it would have mirrored a correct drawing set.

For a solid it is not harmless. A CAD kernel's space is right-handed, so feeding
these coordinates in builds the mirror image of the room. Fixed in
`cad/export.py:to_room_frame()`, which mirrors x for STEP and STL only:

    X = room.x − x    from the stair/door wall toward the window wall
    Y = y             unchanged
    Z = z             unchanged

`X × Y = Z`, so the export now opens the same way round as the room — stair at
X 0→24 with stringer C against the door wall, the ¾ facing at 24→24.75, the
half-wall framing at 24.75→28.25, the loft beyond. Volume is preserved exactly
(10820.74 cu in before and after) and all 38 labelled children survive; `mirror()`
had to be applied per piece because it flattens a Compound and drops its labels.

Everything upstream stays in yaml coordinates, where it agrees with the drawings to
0.0000" — checks, ray casts, sections and the Drawing 4 port are all unaffected.

**The general lesson for this repo:** a coordinate convention that is merely a
labelling choice in 2D becomes a real geometric error the moment a solid kernel is
involved. Any future 3D view, render or fabrication output must go through
`to_room_frame()`.

---

## Up-axis (2026-09-05)

The builder previewed `model.step` and found the bed wall reading as the bottom
plane, the ceiling as the front, and the door/window walls as left/right. Not a
handedness problem — left/right were correct, so `to_room_frame()` is doing its job.
It is the up-axis: the room frame is **Z-up**, the CAD convention, while Quick Look
and most web/STL previewers assume **Y-up** and so show a Z-up model lying on its
back.

`export.to_preview_frame()` rotates −90° about X, `(X, Y, Z) → (X, Z, −Y)`. A
rotation, so handedness is preserved and the frame stays right-handed. Floor → Y 0,
ceiling → +Y, bed wall → Z 0 with the closet running to −Z, so a previewer's default
front view looks at the bed wall — the same vantage the sheets are read from.

`cad.spike` now writes both, and neither is authoritative over the other:

| file | up-axis | for |
|---|---|---|
| `model.step`, `model.stl` | Z-up | FreeCAD, Fusion, SolidWorks, anything mechanical |
| `model-yup.step`, `model-yup.stl` | Y-up | Quick Look, Preview, web previewers |

Volume is identical across all four (10820.74 cu in).
