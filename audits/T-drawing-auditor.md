# Rev T — drawing-auditor report

Date: 2026-09-04 · Agent: `drawing-auditor` (Fable), run cold. SVG geometry converted to inches with each drawing's own scale (Dwg 1: 4.2 px/in, 2: 4.6, 3: 6.0, 4 & 8-section: 5.0, 5: 7.0, 6: 5.6, 7: 6.0 vertical / 5.5 horizontal, 8-plan & 9: 8.0). verify.py's known failures treated as baseline.

Reviewer's note (inline, after reading): item 18 is a non-finding — the deck runs over the half-wall at z 58, so from treads 4–5 the far side of the wall is the deck surface, not a drop. Everything else was checked and stands.

## Most consequential

1. **Landing rim: "full 24" wall to wall" (text, 5 places) vs 22½" (Drawing 8 plan and the yaml).** Rev S.1 ("rim and ledgers redrawn so they butt") introduced the 22½" rim. Consequence: stringer C has zero overlap with the rim and lands on the end grain of a 2×4 ledger — verify.py's FAIL is faithful to the drawing. Design rationale requires the 24" rim. Cut-list impact: rim 24 not 22½; right-wall ledger 25½ not 27. "On the wall ledger" cannot work (2×4 vs 2×12).

2. **Tread thickness is never stated, and the stair/nook geometry only closes if it is zero.** Every drawn stringer has its tread cuts at the Table B riser heights and its underside at 34.42 at y=27 — no drop. Either treads sit on those cuts (first riser 8.29+t, landing step 8.29−t: a 2" variation with 1" treads against "all seven risers uniform") or the stringer is dropped by t, in which case the underside is 33.42/15.01, the rake soffit set from the header bottom is 1" inside the stringers at y=47, the flat/rake break moves to y≈17.4 and the far-end height to ≈14¼. verify.py bug: `underside()` did not subtract t while `top_edge()`/`plumb_cut()` did. *(Fixed inline the same day.)*

3. **Screen top plate: Drawing 3 vs text disagree by ¾".** Drawing 3 draws the 2×4 at y 46½→50 with a ¾" band at 50→50¾; the structure note, Open Items and the yaml say 47¼→50¾ with no band. The ceiling-joist measurement targets the *framing*, so this must be settled first.

4. **Drawing 2 SVG still shows pre-Rev-T slats: 29.6" long under a 3½" plate.** Table A and the dimension text on the same drawing say 31½" under a 1½" flat plate. Cut-list impact: 31½".

5. **Side member length stated three ways** — 24 (Dwg 8 plan, yaml) vs 25½ (table, Dwg 8 section, Dwg 9). 0→25.5 would occupy the bed-wall ledger's volume. 24" is right.

6. **Rim called a 2×10 in two places** — Drawing 7 section (drawn 9¼" deep, labelled 2×10) and Drawing 8 caption load path. It is a 2×12.

7. **Riser "8¼"" survives in seven places** despite the Rev T note. Drawing 4's riser labels are also rounded inconsistently (16½, 24⅞, 33, 41½).

## Yaml faithfulness

8. **Boxed ledge mis-encoded.** Drawing 3: deck ply is the well floor; front rail 7¼ tall (58→65.25); ¾ lid at 65.25→66. Yaml had an 8" rail, a separate ¾ bottom, no lid. *(Fixed.)*
9. **Window extent**: Drawing 1 draws y 95→150 (55" wide), yaml had 95→136. *(Fixed.)*
10. **Ledger blocking** drawn three different widths (3½ flat in Dwg 6; 2.67 × 3½ in Dwg 3; on edge in the yaml). Orientation is an open choice.
11. **Beam / side ledger / first slat** — the yaml's 1.5→106.25 beam is a reasonable resolution of Drawing 6's 0→107; the two resulting FAILs are one drawing problem: nothing says how the beam's left end is carried.
12. **Half-wall end at y 50→50¾ is closed by nothing in the drawings.** Yaml's `hw_end_cap` is an ASSUMED fill.

## Chains, claims, stale text

13. **Room-depth chain is ½" short.** Door 150→182 + 3½ = 185½ ≠ 186; Drawing 1 draws the gap as 4" under a "3½"" label. verify.py did not compare to `room.y`. *(Fixed — now a WARN.)*
14. **Flat nook ceiling vs side member** — 0.54" interference with a ¾ panel; unresolved anywhere in the set.
15. **Recessed light sits under landing joist 1** (centred y≈10.75; joist y 8→9.5). Only 3.96" of chase; fixture depth unstated. Move to between joists (≈13.25) or use a wafer.
16. **Structure table stale text:** "studs @ 16"" (no field studs); treads "24" span" (Rev S.1 corrected the drawing, not the table); slats "~65 lf" (23 × 31½ = 60.4); "rear ledger 107"" (cut 104¾).
17. **Drawing 6 caption "joists landing on the beam"** — they share a bottom; they hang from its face. Hanger unspecified.
18. ~~Half-wall as guard at treads 4–5~~ — withdrawn, see note above.

## Cosmetic
19. Dwg 8 throat arrow is 7.67" long, labelled 5.15 (number right, arrow wrong). 20. Dwg 5 reflected-ceiling "24"" dim spans 29". 21. Dwg 7 mixes 6 and 5.5 px/in. 22. Dwg 2 "102" clear" dim measures 101.1".

## What checks out
Tables A–E, slat pitch, joist/blocking/rim positions (Dwg 6), half-wall framing (Dwgs 7, 9), stringer positions and the 27/45/72 chain, headroom, fan clearance, desk projection, nook opening, header bearing, ledger/joist/rim elevations, Drawing 3 beam/wrap/slat geometry — all agree with the yaml within rounding. The yaml's three cut-list corrections (rear ledger 104¾, wrap underside 102, beam 1.5→106.25) are right.
