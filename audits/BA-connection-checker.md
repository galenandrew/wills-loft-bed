# Connection audit — Rev BA (on top of Rev AZ)

Scope: whole `connections:` block, weighted toward the members whose stock/extents
moved in AZ/BA: `beam_wrap_face`, `beam_wrap_inner`, `beam_wrap_top`, `beam_end_cap`,
`loft_ceiling`, `slat[*]`, `screen_top_plate`, `hw_end_cap`, `hw_end_cap_foot`,
`hw_sheath_loft_a`, `hw_sheath_loft_head`, `hw_sheath_loft_b`, `stringer_a_skin`,
`nk_wrap_shortwall`, `nk_soffit_flat`, `nk_soffit_rake`.

## Runs

- `python3 verify.py` — **0 FAIL, 0 WARN**, clean.
- `python3 -m cad` — clean: 0 real interferences, 3 coincident faces (pre-existing,
  0.0003", not findings), STEP re-import volume matches to 4 decimals, `d4`/`d8b`
  kernel sections agree with the box drawings to 0.0048" (limit 1/16"). One
  pre-existing kernel/verify.py disagreement noted below (not caused by this rev).
- Spot-checked 3 PASS lines against raw yaml extents:
  - `lnd_rim → hw_header`: yaml gives y-overlap `[16.5,18]∩[1.5,48.5]` = 1.5, z-overlap
    `[41.5,48.75]∩[41.5,50.75]` = 7.25 — matches verify's "y 1½, z 7¼" exactly.
  - `deck_joist[0] → rear_ledger`: x-overlap `[1.5,3]∩[1.5,106.25]` = 1.5, z-overlap
    `[53.75,57.25]∩[53.75,57.25]` = 3.5 — matches "x 1½, z 3½".
  - `stringer_a → hw_king_b`: naive bbox z-overlap would read ~47.25 (stringer_a's box
    is `z[0,48.75]`), but verify reports z 11.59 — because stringers are `kind:
    stringer` and the checker correctly uses the true sloped profile, not the bbox,
    per the documented convention. This is the right answer (confirmed against
    `ST.top_edge`/`U()` by hand), not a bug — good evidence the script is honest
    rather than doing bbox arithmetic everywhere.

## Fastener re-derivation (the hand-restated strings)

All of the penetration numbers that were hand-typed for the thinner panels
re-derive correctly:

| Connection | Screw | Panel now | Penetration claimed | Recomputed |
|---|---|---|---|---|
| `beam_wrap_face → beam` | #8×2 | ½ ply | 1½ into 1¾ LVL | 2−0.5=1.5 ✓ |
| `beam_wrap_face → side_ledger` | #8×2½ | ½ ply | "makes it 2" | 2.5−0.5=2.0 ✓ |
| `beam_wrap_face → deck_joist_tail` | #8×2½ | ½ ply | not restated, "same as ledger half" | 2.5−0.5=2.0 ✓ (math is right; note text wasn't updated to say so — see below) |
| `beam_wrap_inner → beam` | #8×2 | ½ ply | (finish only, not restated) | 2−0.5=1.5, into 1¾ LVL, fine |
| `beam_wrap_top → beam` (slat bearing) | #8×3 | ½ cap | 2½ into beam | 3−0.5=2.5 ✓, beam is 14" deep there, no risk of blow-through |
| `slat[22] → beam_wrap_top` | #8×3 offset inboard | ½ cap | (same as above, geometry-driven, not thickness) | slat footprint 105.5–107 vs LVL end 106.25 → 0.75 of 1.5" width over solid LVL, rest over `beam_end_cap` (still ¾ ply, unchanged) — offset is still correctly required |
| `loft_ceiling → deck_joist[*]` | #8×2 | ½ ply | 1½ into 3½ joist | 2−0.5=1.5 ✓ |
| `loft_ceiling → deck_joist_tail` | #8×2 ×2 | ½ ply | "into the tail's 1¾ of bottom edge" | that 1¾ is the tail's own length (its y-extent, 48.25→50), not the embedment — embedment is the same 2−0.5=1.5 as the sibling row, just phrased differently. Not wrong, just worth clarifying so it isn't mistaken for a stated 1¾ embedment. |
| `stringer_a_skin → stringer_a` | 1½" 16ga nail | ½ skin | "1 in penetration" | 1.5−0.5=1.0 ✓ |
| `screen_top_plate → slat[*]` | #8×2½ angled | n/a (end-grain, angled) | not a straight-through calc | plausible (1.5×1.5 slat into a 1.5"-thick plate, entering at an angle) but not machine-checkable — the kernel itself lists this row under "UNSPECIFIED fasteners it cannot ray-cast," because the geometry is angled, not because the spec is missing. Don't conflate the two: it *is* specified in prose. |

**Verdict on the restated fasteners: sound.** Every embedment number that changed
with the ½" panels was recomputed correctly. Two rows (`beam_wrap_face →
deck_joist_tail`, `loft_ceiling → deck_joist_tail`) have arithmetic that still comes
out right but weren't given the same explicit "Rev AZ: now X" annotation their
sibling rows got — a documentation-consistency nit, not a structural error.

## 1. Missing declarations

**The one real finding of this audit.** Every purely decorative/closure sheathing
member in the model has **zero rows in `connections:`** — not even an informal one
in its own `note:`. This is a pre-existing pattern (it is not new to BA/AZ), but
five of the affected members are exactly the ones that changed stock/position this
rev, and two of them now carry a genuine functional claim that depends on the very
fastening this audit can't find:

- `hw_end_cap`, `hw_end_cap_foot` — changed to ½" ply, repositioned (x0 102→102.25,
  y-face 50.75→50.5), notch re-cut (4¾×24 corner, was 5×24). Zero connections. No
  note even says glue-and-nail. It is a finish return, non-load-bearing as drawn, so
  this is a documentation gap rather than a safety one — but there is no record of
  what holds a 53"-tall closure board to the framing behind it.
- `hw_sheath_loft_a`, `hw_sheath_loft_head`, `hw_sheath_loft_b` — all moved to ½"
  ply, jamb cut shifted ¼" on two of three edges (`hw_sheath_loft_head`'s far jamb
  45.75→46, near jamb unchanged at 4.25). Zero connections declared anywhere for
  this whole 50×53¾ face (it is later described in `content/structure.yaml` as
  "seams backed full length," but that claim is never checked against the yaml).
- `hw_sheath_stair`, `beam_end_cap`, `ledge_end_cap` — unchanged this rev, same gap,
  pre-existing.
- `nk_wrap_shortwall`, `nk_soffit_flat`, `nk_soffit_rake` — all moved to ½" ply.
  Zero connections. `nk_soffit_flat`/`nk_soffit_rake` bear on `hw_trimmer_a`'s face
  and the stringer undersides per their own notes, but that bearing is never a
  `connections:` row, so it never gets checked for real overlap the way every other
  bearing joint in the model does.
- `nk_wrap_bedwall` — unchanged in thickness, but **the Rev BA note newly makes a
  load-relevant claim about it**: "¾ ply takes a screw on its own almost anywhere on
  the sheet where ½ does not," used to justify keeping this one wall at ¾ so shelves
  can be hung on it, with a "now-or-never: blocking between the `nk_bedwall_stud`
  bays before this sheet goes on" if shelves will be heavy. But `nk_wrap_bedwall`
  has no `connections:` row to `nk_bedwall_stud` (3 studs @ 11⅝" o.c., starting at
  x 106.25 — the first ~3.5" of the 28¼-long wall, x 102.75–106.25, has no stud in
  the model at all, presumably relying on the half-wall's jamb framing instead, but
  that reliance is never stated). The member the whole justification rests on is
  itself unverified.

**Fix:** add `connections:` rows (even lightweight ones — construction adhesive +
16ga finish nails at some spacing, which is what all of these plainly are) for at
least `nk_wrap_bedwall → nk_bedwall_stud` and `nk_wrap_shortwall → ` whatever framing
backs it, since those two now carry an explicit "holds a screw" claim; the rest are
lower priority but should not stay silently undeclared forever, per the project's
own rule that an un-declared connection is unverified.

**Second finding, also in scope (Drawing 7):** `drawings/d7_half_wall.py` (both
`d7a`'s caption and `d7b`'s figure) still draws strap callouts and says "strap both
header-to-king joints" — but `content/open-items.yaml`'s Rev AS entry explicitly
says **"Header-to-king straps: scrapped"** (the sheathing nailed to both header and
kings is a stiffer tie, so the strap is redundant) and that decision is *why* there
is no `strap` connection row anywhere in `dimensions.yaml`. Drawing 7 is stale and
contradicts the decision on record — a communication defect on exactly the sheet
this audit was asked to check.

**Third finding (small, in scope):** `content/structure.yaml`'s "Screen" row has two
fields that now contradict each other in the same row:
```
spec:  "... 2×4 flat top plate"
check: "... Rev BA: the plate is paint-grade solid stock ... not an SPF 2×4 ..."
```
The `spec` line is a hand-typed literal that Rev BA didn't update; it should read
"poplar 2×4 flat top plate" (or quote `{m:screen_top_plate.stock}`). `python3
tools/literals.py d6 d7 d8 d9` and a manual scan of `content/` turned this up; it's
the only literal actually contradicted by a model change in this rev — everything
else flagged by that tool (joist/stud/hardware call-outs like "2×4 rear ledger",
"2×8 rim") is a real nominal-stock name, which is deliberately literal per the
token-discipline note in CLAUDE.md, not drift.

## 2. The window-end notch reinforcement — both claims checked

The beam's notch (`beam_tongue`, x 0–3, the window-wall end) is claimed to be
reinforced two ways. Both still hold at ½" panel thickness:

- **`beam_wrap_face`, in shear, in the plane of the split.** Glued only to
  `beam_tongue` over x 0–3 (no screws within 1" of the corner), then *structurally*
  screwed to `beam` (the body) starting immediately past the corner, 6" o.c. over x
  0–27, **and** anchored below the corner into the two members `beam_tongue` bears
  on: `side_ledger`'s end face (#8×2½, now 2.0" embedment, was 1.75) and
  `deck_joist_tail`'s end face (same). The panel is continuous across the corner, so
  a split there has to shear the panel to open — the load path (glue on top piece →
  continuous panel → screwed to anchored members below) is unchanged in kind by the
  thinning; only the embedment numbers moved, and they moved the right direction
  (more, not less). **Sound.**
- **`loft_ceiling`, in withdrawal, tying the beam's bottom edge to members that
  can't move.** Screwed at 6" o.c. into `beam`'s bottom edge over x 3–27 (tighter
  than the 8" field spacing elsewhere), and into `side_ledger` and `deck_joist_tail`
  bottom faces on the far side of x 3 (both at x 0–1.5 / 1.5–3, confirmed by
  verify's overlap output). Embedment into the joist/tail actually *increased* ¼"
  with the thinner ceiling panel (2−0.5=1.5 vs 2−0.75=1.25 before). This is
  explicitly the *secondary* restraint (screw withdrawal from an LVL laminated
  edge, weaker than shear), and the model says so. **Sound, and correctly labeled
  secondary.**

Neither restraint's *character* changed — the thinning only moved fastener
penetration numbers, and all of them moved in the direction of more embedment, as
the revision notes claim.

## 3. The screen's 200 lb lateral load, slat top to floor

1. **Top of slat (z 94.5)**, lean applied here per the design note. One angled #8×2½
   screw + adhesive + 2 pins ties the slat top into `screen_top_plate` (bearing,
   `z=94.5` on both members — checked, matches). Sound as a slat-to-plate joint.
2. **`screen_top_plate → ceiling`.** This is where the path currently ends. The
   fastener is **UNSPECIFIED**: `"into ceiling framing / blocking — joist location
   not yet measured"` (a pre-existing field item, `content/open-items.yaml`'s
   `ceiling_note`, unchanged by BA). Until a joist or added blocking is actually
   screwed here, this connection carries nothing.
3. **Base of the same slat, in parallel**: bears on `beam_wrap_top` (1× #8×3, 2.5"
   into the LVL — verified above). This is a straight-down bearing/withdrawal screw,
   not a moment connection; the model's own reasoning (`ceiling_note`: "unattached,
   a 200 lb lean at the top of the screen overloads the slat bases") is consistent
   with what a single vertical screw at 1.5"×1.5" bearing can actually resist.
   Rough numbers: with the top pinned to the ceiling, a lean applied essentially at
   the top support sheds nearly all 200 lb into step 2 directly, leaving only a
   small shear reaction at the base. **Without** step 2 built, the slat behaves as a
   cantilever fixed only at its base screw over a free height of 94.5−68.25 = 26.25",
   i.e. roughly 200 lb × 26.25" ≈ 5,250 in-lb of overturning on a single vertical
   #8 screw and a 1.5"×1.5" bearing footprint — not something that connection is
   sized for, which is exactly why the model calls it out.
4. From `beam_wrap_top` the path continues through verified connections: `beam` →
   `side_ledger`/`deck_joist[0]` (bed-wall end, screwed to window-wall studs — see
   below) and `beam` → `hw_top_plate_2` (half-wall end) → `hw_king_a`/`hw_king_b` →
   `hw_bottom_plate` → floor. All of these rows pass verify with real overlap.

**Verdict: marginal, unchanged by this rev.** The base connection is sound as a
bearing/shear detail; the guard's actual job (resisting a 200 lb push without
letting the top swing) still depends entirely on the one connection in the whole
screen assembly that has no fastener chosen yet. This isn't a new problem — it's
the same open item as before BA/AZ — but since the prompt asked me to trace this
load explicitly, it remains the finding: **do not treat the screen as a finished
guard until `screen_top_plate → ceiling` is specified and built.**

## 4. Load paths, floor to floor (rough reactions)

- **Deck** (~50 psf design load per joist bay) → 9× `deck_joist` (2×4 @ 12" o.c.,
  46¾" span, ~370 psi, defl. L/1350) → `LUS24` hangers into `rear_ledger` (bed wall,
  lags to studs, ~110 lb/stud) and into `beam`'s face (except joist 0). Beam
  reaction ≈ half the deck tributary width per joist, concentrated at its two ends.
- **Beam ends**: bed-wall end → notch bears on `side_ledger` + `deck_joist_tail`
  (3×1¾ = 5.25 sq in, ~115 psi vs 425 allowable) → `side_ledger` screwed to
  **window-wall studs** — still `FIELD`: "confirm a stud lands there or add
  blocking," per CLAUDE.md's still-open field measurement. This is the weakest
  documented link in the beam's load path and remains unresolved at this rev.
  Window-wall end → bears on `hw_top_plate_2` → `hw_king_a`/`hw_king_b` → studs →
  `hw_bottom_plate` → floor (~700 lb region per the header row, unaffected by BA/AZ).
- **Landing**: `lnd_ply`/joists → `lnd_rim` (HUC28 hangers) → `hw_header` (one end)
  and `lnd_ledger_rightwall` (other end, screwed to right-wall studs — also FIELD,
  unmeasured) and `lnd_side_member` (A35 straps) → down through half-wall framing to
  floor, same as above.
- **Each stringer**: A → `hw_header` + `hw_king_b`/`hw_trimmer_b` (SDS, ~2" into
  header/king) + `lnd_rim` (toe-screw) at top, `stringer_a_skin_cleat` → floor (3×
  #10×3 screws into subfloor) at bottom — a real, declared, verified path.
  B and C → `lnd_rim`/`lnd_ledger_rightwall` at top, then **hook over the kicker**
  at the bottom — `kicker → floor` is declared but its own fastener is
  UNSPECIFIED (pre-existing open item, not part of this rev's scope but still the
  single weakest link in the whole stair's horizontal thrust path; worth repeating
  since the prompt asked to follow every load to the floor).
- **Screen's 200 lb lateral**: see §3 above — sound at the base, open at the top.

## Summary table

| Connection | Drawing claim | yaml/script | Fastener & penetration | Verdict | Fix |
|---|---|---|---|---|---|
| `beam_wrap_face`→`beam` | splice reinforcement, shear | PASS, 103¼ of 106¼ width backed | #8×2, 1.5" into 1¾ LVL | sound | — |
| `beam_wrap_face`→`side_ledger` | anchor side of splice | PASS | #8×2½, 2.0" embedment (recomputed) | sound | — |
| `beam_wrap_face`→`deck_joist_tail` | other anchor side | PASS | #8×2½, 2.0" (math right, note not updated) | sound | reword note to state the AZ number like the ledger row does |
| `loft_ceiling`→`beam`/`side_ledger`/`deck_joist_tail` | 2nd notch restraint, withdrawal | PASS | #8×2, 1.5" (gained ¼") | sound | — |
| `loft_ceiling`→`deck_joist_tail` | ditto | PASS | "1¾ of bottom edge" — ambiguous phrasing | sound but confusing | clarify that 1¾ is the tail's length, not embedment |
| `beam_wrap_top`/`slat[*]`→beam | slats' seat, screw | PASS | #8×3, 2.5" into 14" LVL | sound | — |
| `slat[22]`→`beam_wrap_top` | offset screw, LVL end | PASS, exception row | offset inboard, geometry-checked | sound | — |
| `screen_top_plate`→`slat[*]` | top restraint | PASS (bearing) | #8×2½ angled + pins; not kernel-checkable (angled) but not unspecified | sound | — |
| `screen_top_plate`→`ceiling` | guard's top anchorage | PASS (touches plane only) | **UNSPECIFIED** — joist not yet measured | **not done** | measure joist, specify screw/blocking, verify penetration |
| `stringer_a_skin`→`stringer_a` | closes cavity | PASS | 1½" nail, 1.0" into ½" skin | sound | — |
| `hw_end_cap`, `hw_end_cap_foot` | closes wall end | **no connections row at all** | none stated | **unverified** | add a row (adhesive + finish nails is plausible; ~1" penetration through ½" ply with a 1½" 16ga nail) |
| `hw_sheath_loft_a/head/b` | half-wall loft face | **no connections row at all** | none stated | **unverified** | add rows to `hw_king_a/b`, `hw_trimmer_a/b`, header |
| `nk_wrap_bedwall`→`nk_bedwall_stud` | shelf substrate (Rev BA's own justification) | **no connections row at all** | none stated | **unverified** | add a row; this is the member the ¾-vs-½ decision was made to protect |
| `nk_wrap_shortwall`, `nk_soffit_flat/rake` | nook lining/ceiling | **no connections row at all** | none stated | **unverified** | add rows |
| half-wall header-to-king strap (Drawing 7) | "strap both ... joints" | **not in yaml; decision on record is NO strap** | n/a | **drawing contradicts the model** | remove the stale strap callouts/text from `d7_half_wall.py` |
| Screen row, `content/structure.yaml` | "2×4 flat top plate" vs "not an SPF 2×4" in the same row | model correct (`poplar-2x4`) | n/a | **stale literal** | quote `{m:screen_top_plate.stock}` or reword to "poplar 2×4" |
| `side_ledger`→`wall:window` | beam's bed-wall-end reaction | PASS, but `FIELD` | ¼×4 SDS, 2/stud — stud presence unconfirmed | **open**, pre-existing | measure/add blocking within 6" of y 50 |
| `kicker`→`floor` | resists stair thrust | declared, UNSPECIFIED | none | **open**, pre-existing | specify anchorage |

