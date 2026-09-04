# Rev T — inline design review

Date: 2026-09-04 · Reviewer: Claude (Fable 5.1), inline with the full drawing set in context.
Method: read all nine drawings, encoded every member's framing extents into `dimensions.yaml` as drawn, wrote `verify.py`, and checked each claimed connection for three-axis overlap. Every finding below has arithmetic; none is from memory.

Two independent subagent audits (`drawing-auditor`, `connection-checker`) were run afterwards without being told these findings — see the sibling files in this directory.

---

## A. Structural findings — need a decision before anything is cut

### A1. The beam's left end has nothing to land on
**Where:** Drawing 6, structure table ("2×10 side ledger, 48" out — carries the beam's left end").
**Arithmetic:** side ledger y 0→48. Beam y 47→50. Both at z 53¾→63 (same elevation, so neither can bear on the other). Overlap in y = 48 − 47 = **1" of a 3"-wide beam**.
**Consequence:** the beam's ~400 lb end reaction (half the platform plus self-weight) is carried by 1" of end-grain-to-face contact with no fastener specified.
**Fix (recommended):** extend the side ledger to y = 50¾ (matches the platform edge; the ¾" wrap turns the corner onto it) and hang the beam's end on a double-2×10 face-mount hanger (Simpson LUS210-2 / HUS210-2 class) nailed into the ledger, which is lagged into window-wall studs. Ledger cut length becomes 50¾". Alternative: a 2×4 cleat floor-to-53¾ under the beam end at the window wall — behind the desk, invisible, but it's a post.
**Side effect:** also fixes A6.

### A2. Landing rim right end — "on the wall ledger" is not a connection
**Where:** Drawing 8 plan and caption; structure table ("right end on the wall ledger").
**Arithmetic:** rim 2×12, z 37.71→48.96. Right-wall ledger 2×4, z 45.46→48.96. Engagement 3½" of 11¼" (**31%**). Fastener unspecified. A 2×4 cannot carry a 2×12's end.
**Fix (recommended):** make the right-wall landing ledger a **2×8** (z 41.71→48.96, bottom just above the 41½" nook ceiling — same logic as the side member on the other side). Hang the rim's right end on it with an LUS212 (7¼" engaged, nails into solid 1½"). Landing joists hang on the same ledger. Symmetric with the half-wall side, one hanger type for both rim ends.

### A3. Stringer C does not reach the rim
**Where:** Drawing 8 ("treads 24" long, bearing on all three [stringers]"; rim "full 24" wall to wall").
**Arithmetic:** rim as drawn x 107→129½ (it butts the right-wall ledger at 129½). Stringer C x 129½→131. Overlap = **0**. The text says the rim is 24" long; the drawing shows 22½".
**Fix:** decide which. With A2's 2×8 ledger, the rim stays 22½" and stringer C's plumb cut bears on the ledger's end face (7¼" of it) *plus* its full-length screw fixing to the right-wall studs — that is adequate and is what the caption already implies ("stringer C fastens to the right wall"). Update the text: rim is 22½", not "full 24"".

### A4. Rim-to-header hanger: fastener spec is missing and matters
**Where:** Drawing 8/9, connection ➋ ("hangered to the flush header · 7½" engaged").
**Arithmetic:** the hanger nails pass through the ¾" ply facing first. A standard 10d × 1½ hanger nail then penetrates **¾"** of the header. Engagement is 7.46" of the rim's 11¼" (66%); every flange nail hole below z 41½ has air behind it (the nook opening).
**Rim left-end reaction (rough):** stringer A ≈ 170 lb + half of stringer B ≈ 85 + quarter of landing live+dead ≈ 100 → **≈ 350 lb**. Small, but the connection must be a real one.
**Fix:** specify the hanger (LUS212 or HU212) **with SD-series structural screws or 16d nails**, not 10d×1½ — Simpson publishes loads for SD screws in LUS hangers. State on the drawing that only the nail holes above 41½" are live and that the top ones must all be filled. Same note applies to the side member's ¼"×5" screws: 5" through 1½ + ¾ + 1½ + ½ reaches ¾" into the far ply — barely "both plies". Use 6".

### A5. Nook flat ceiling cannot be built as drawn
**Where:** Drawing 5, schedule A ("Nook flat ceiling 41½ — set by header bottom"; "Landing side member 2×8 41.71 — clears the 41½ ceiling by ¼"").
**Arithmetic:** the finished ceiling face at 41½ with a panel of thickness *t* puts the panel top at 41½ + *t*. The side member's bottom is 41.71. So *t* ≤ 0.21". The raked portion is implicitly ¾" (Rev T's rake line sits exactly ¾" below the stringer underside — verify.py confirms 0.75 at y = 27, 36, 47). A ¾" flat panel would sit **0.54" into the side member**.
**Fix (recommended):** treat the nook opening as a *jambed* opening: ¾" poplar jambs on the trimmers and header (matching the wrap). Finished head then = 41½ − ¾ = **40¾"**; finished width 44 − 1½ = **42½"**. Flat soffit panel ¾", face at 40¾, top at 41½ — clears the side member by 0.21". Rake line then starts where the existing rake reaches 40¾: y ≈ 19¼ instead of 18½. Far-end height at y = 47 is unchanged (15¼, still on the stringers). Update Locked Dimensions (which currently present 44 × 41½ as if finished) and the schedule.
**Also:** the flat panel needs nailers along the right wall and at the flat/rake break — none are drawn.

### A6. The first screen slat has nothing under it
**Arithmetic:** slat[0] x 0→1½ sits over the side ledger (x 0→1½) — but the ledger is y 0→48 and the slat is y 49¼→50¾. Beam starts at x 1½. Nothing at z 63 under the first slat.
**Fix:** A1's ledger extension to 50¾ fixes this for free. Also: the last slat (x 105½→107) bears ¾" on the beam and ¾" on the wrap only. Fine for a stile, but say so.

### A7. Slat-to-beam and slat-to-top-plate joints are unspecified
The screen is the guard for a 58" deck and must take the 200 lb top-rail load (which the drawings themselves invoke). Twenty-three slats "sit on" the beam and "under" the top plate with no joint stated — toe-screws? dowels? dadoes? Choose one and put it on Drawing 3. Recommend: ½" deep dadoes in the beam-top cap and top plate, glued, plus one 3" screw per end from behind.

---

## B. Drawing/text contradictions (cut-list consequences)

| # | Item | Rev T says | Reality | Cut-list effect |
|---|---|---|---|---|
| B1 | Rear ledger length | 107" | side ledger occupies x 0–1½; stair-side sheathing (floor→58) occupies 106¼–107 | **104¾"** |
| B2 | Beam length | "107", no posts" | must stop at the side ledger (1½) and the stair-side sheathing (106¼) | **104¾"** |
| B3 | Beam wrap, underside | drawn 0→107 | beam bears on the half-wall top plate past x 102 | **102"** |
| B4 | Side ledger length | 48" | see A1 | **50¾"** |
| B5 | Landing side member | table: 25½" · Drawing 8: 1½→25½ (24") · Drawing 9: 0→25½ | the bed-wall ledger occupies y 0–1½ | **24"** (or shorten the ledger) |
| B6 | Landing rim | "full 24" wall to wall" | drawn 107→129½ | **22½"** (see A3) |
| B7 | Ledger blocking | Drawing 6: 3½" wide in plan; Drawing 3: 3½" tall | a 2×4 is 1½ × 3½ | on edge, y 1½→3, top flush with joists |
| B8 | Boxed ledge parts | drawn from x 0 | side ledger occupies x 0–1½ to z 63 | start at 1½ |
| B9 | Stringer bearing on rim | 11¼" — "full rim depth" | stringer top = landing − tread thickness → 11.0 with 1" treads | note only |
| B10 | Stringer underside at y=27 | 34½ | exact 34.42 | note only |
| B11 | "Wall panel runs floor-to-58 uncut" (schedule C) | — | there is a 44 × 41½ hole in it now | stale note, delete |
| B12 | "Studs @ 16" o.c." (structure table) | — | the wall has four studs total: two kings, two trimmers | stale, delete |

## C. Unspecified — the builder will guess on site

- Tread stock and thickness (sets the stringer drop and the plumb-cut height). Model assumes 1".
- Kicker size and position.
- Half-wall bottom plate anchorage to the floor.
- Joist hanger models (deck joists → ledger, deck joists → beam, landing joists).
- Side ledger lag schedule.
- Nook light: a standard 6" can is 7½" deep; the chase is 3.96". Specify a **wafer/canless LED**.
- What closes the half-wall's end at y 50→50¾ below the wrap.
- Riser material for the closed risers.

## D. What I did *not* find wrong

- Beam: doubled 2×10 over 102" clear — ~240 psi bending, deflection ≈ L/2500. Generous; leave it.
- Header: ~180 psi. Sized by connection depth, correctly so.
- Stair: 7 × 8.286 = 58 ✓; 42.63° ✓; throat 5.15 ✓; landing at riser 6 = 49.71 ✓; headroom 46.29 at landing, 38 at deck ✓.
- Room chain 72 + 30 + 48 + 32 + 3½ = 185½ ✓.
- Screen: 23 slats, 3.30" clear ✓ (< 4" sphere).
- Rim hides above the rake soffit by 2.65"–4.04" ✓.
- Half-wall load path with the portal frame + deck diaphragm — sound for these loads.

## E. Process finding

Every error above is the same species: a number stated in prose or hand-placed in an SVG that was never checked against the member extents. Rev T's schedule helped; it was still hand-maintained. The fix is structural: `dimensions.yaml` is now the model, `verify.py` checks it on every edit, and the HTML should become a rendering of it rather than a parallel source. Recommend generating the framing drawings from the yaml once the decisions above are made.
