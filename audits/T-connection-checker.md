# Rev T — connection-checker report

Date: 2026-09-04 · Agent: `connection-checker` (Sonnet), run cold against `dimensions.yaml`, `verify.py`, and `loft-bed-drawings.html`, not told the inline findings.

## Headline

Six connections in Rev T do not work as drawn. Two of them — the landing rim's hanger at the nook header, and stringer C's top — are load-path failures, not tolerance drift. Two more (the beam's left end, slat 0) fail on a single axis by exactly the amount one member was cut short.

## 1 · Declared connections — three-axis check

Overlap = `min(a_hi, b_hi) − max(a_lo, b_lo)`. Negative = gap; 0 = butt (correct for hangers/face-screws on the face axis).

| # | Connection | Δx | Δy | Δz | Verdict | Fix |
|---|---|---|---|---|---|---|
| 1 | `beam` → `side_ledger` (hanger, face x) | 0 butt ✓ | **+1.0 of 3.0** | +9.25 ✓ | **Does not exist as detailed — y fails.** The ledger stops at y=48; 2" of the beam's end and any hanger seat hang over air. | Side ledger 50" long (y 0→50). Also fixes #4. Specify a HUS/HGUS-class hanger for the doubled member. |
| 2 | `lnd_rim` → `hw_header` (hanger, face x, through ¾" ply) | 0 after ply ✓ | +1.5 ✓ | **+7.46 of 11.25 (66%)** | **Does not exist for the fastener described.** Rim bottom 37.71, header bottom 41.50: the hanger *seat* sits 3.79" below the supporting member. Nails: 1.5" − 0.75" ply = 0.75" into the near ply. | (a) Notch the rim's left end up to z=41.5 so the seat bears at the header's underside (7.46" of rim remains). (b) ¼"×3½" structural screws, or hold the ply facing clear of the hanger footprint as Rev O required. |
| 3 | `lnd_rim` → `lnd_ledger_rightwall` (hanger, face x) | 0 butt ✓ | +1.5 ✓ | **+3.5 of 11.25 (31%)** | **Does not exist — z fails.** A 2×12 butted into the face of a 2×4. | Right-wall ledger a 2×12 over at least the rim's last 12", or a 2×12 block at x 129.5–131, y 25.5–27; specify the hanger. |
| 4 | `slat[0]` → `beam` (bearing) | **0** | +0.75 | touch ✓ | **Does not exist — x fails.** Only the ¾" poplar wrap is under slat 0. | Fix #1 gives it a 1.5×0.75 seat on the ledger. |
| 5 | `stringer_c` → `lnd_rim` (face y) | **0** | 0 butt ✓ | +11.0 ✓ | **Does not exist — x fails.** Rim ends at 129.5 where stringer C begins. Text says "full 24" wall to wall"; Drawing 8 draws 22.5". | Run the rim the full 24" (x 107→131), notched around or lapped over the right-wall ledger. |
| 6 | `stringer_a/b/c` → `lnd_rim` | — | — | +11.00 (77%) | **Marginal.** A plumb cut against a vertical face is not bearing; ≈500 lb top reaction is in single shear on UNSPECIFIED fasteners. Engagement 11.00", not 11¼" (cut top = 49.71 − 1" tread). | Continuous 2× cleat under the stringer ends, or LSC/LSSU stringer hangers. Table E → 11.00. Caption line 951 still says "2×10 rim". |
| 7 | `lnd_side_member` → `hw_header` (6 × ¼×5, through ¾ ply) | 0 ✓ | +24 ✓ | +7.25 ✓ | **Sound, tight.** 5.00 − 2.25 = 2.75" into a 3.5" header → 0.75" into the far ply. | Hold 5" as a hard minimum; Rev R's 4" dies in the spacer. |
| 8 | `stringer_a` → `hw_king_b`/`hw_trimmer_b` (through ¾ ply) | 0 ✓ | +1.5 ✓ | +10.6 / +9.2 ✓ | **Marginal — fastener.** Screw crosses 2.25" before any stud. | ≥4" structural screws, 4 minimum, across trimmer and king. |
| 9 | `deck_joist[*]` → `beam` (×9) | +1.5 ✓ | 0 ✓ | +3.5 ✓ | **Geometry sound, fastener does not exist.** Caption says joists are "landing on" the beam; they share a bottom at 53.75 — this is a hung connection with no hardware called out. | LUS24 or equal; caption → "hung from". |
| 10 | `deck_joist[*]` → `rear_ledger` (×9) | ✓ | ✓ | ✓ | Sound; hanger model unspecified. | Name it. |
| 11 | `beam` → `hw_top_plate_2` | +3.5 ✓ | +3.0 ✓ | touch ✓ | **Sound.** Beam sits over trimmer_b + king_b, continuous to the bottom plate. | — |
| 12 | `deck_rim` → `hw_top_plate_2` | +1.5 ✓ | +45.5 ✓ | touch ✓ | **Sound over its whole length**, including across the opening (plate → header → trimmers). | — |
| 13 | `hw_header` → trimmers | ✓ | +1.5 each ✓ | touch ✓ | Sound. | — |
| 14 | `ledger_blocking[*]` → `rear_ledger` | ✓ | 0 ✓ | +3.5 ✓ | Sound and continuous x 1.5→106.25. Fasteners unspecified. | — |
| 15 | `slat[1..21]` → `beam` (×21) | +1.5 ✓ | **+0.75 of 1.5** | touch ✓ | **Marginal.** Every slat bears half on the beam, half on the ¾" wrap. Base fastener UNSPECIFIED. | Move the slat band to y 48.5–50, or a continuous 2× sill on the beam top fixed to the beam. |
| 16 | `slat[22]` → `beam` | **+0.75 of 1.5** | +0.75 | touch ✓ | **Marginal.** 0.56 in² bearing. | As #15; may shift to x 104.75–106.25. |
| 17 | `screen_top_plate` → ceiling | — | — | — | Open field measurement; honestly handled. | Keep flagged. |
| 18 | ledgers → walls | ✓ | — | — | Side ledger fastener UNSPECIFIED — the least-specified member carrying the most load (~450 lb beam reaction). | Specify the lags. |
| 19 | `hw_bottom_plate` → floor | ✓ | — | — | Fastener UNSPECIFIED; floor joists below never located. | See load path C. |

## 2 · Connections the drawings claim that `connections:` never declares

| Claimed where | Connection | Status |
|---|---|---|
| Structure table, Dwg 8 | Treads → stringers | Treads are not members in the yaml; only `tread_thickness` (ASSUMED) exists, and it silently sets the stringer drop. |
| Dwg 6, structure table | Deck ply → joists, "glued & screwed", "required — acts as the diaphragm" | The entire lateral system, undeclared; no screw schedule. |
| — | Deck ply front edge → beam | Ply y 1.5–47, beam y 47–50 → y overlap 0. Front edge butts the beam face with **no blocking between joists** over the 10.5" gaps — the rear edge got a blocking row for exactly this reason. Diaphragm front chord connection does not exist. |
| Dwg 7 caption | Strap both header-to-post joints | No strap member, no connection, no hardware. |
| Dwg 9, structure table | Kicker → floor | Position ASSUMED; anchorage undeclared. Bottom of the stair's load path. |
| — | `lnd_side_member` → `lnd_rim` (butt at y=25.5) | Real, needed, undeclared. |
| — | `stringer_c` → `lnd_ledger_rightwall` (butt at y=27, Δz +3.5) | Undeclared — stringer C's only remaining top support once #5 is accounted for. |
| — | Studs → plates; plate 2 → plate 1; sheathing → studs; landing ply → joists | Geometrically sound, undeclared. The half-wall sheathing is a structural interposer in #2, #7, #8 yet carries `role: sheet` with no attachment. |

## 3 · Load paths, applied load to floor

**A · Deck live load.** `deck_ply → deck_joist[*]` → rear: `rear_ledger` → bed-wall studs → floor (complete; studs unlocated). Front: `beam` → left end **1" of 3" backed (#1)**, window wall, fastener unspecified — *finding*; right end `hw_top_plate_2 → _1 → hw_header/hw_king_b → hw_trimmer_b → hw_bottom_plate → floor` — complete.

**B · Stair (≈500 lb top, ≈300 lb bottom).** Stringer A → rim left end → **hanger seat 3.79" below the header (#2)** — finding. Stringer B → rim midspan → right end → **2×12 into a 2×4 face, 31% (#3)** — finding. Stringer C → rim: **x overlap 0 (#5)** — a third of the stair's top reaction has no declared support. All three → kicker → floor, **anchorage undeclared**.

**C · Line loads into the existing floor.** `hw_bottom_plate` (x 102.75–106.25, y 0–50) takes the deck's right support plus the whole stair/landing reaction; `kicker` takes the stair's bottom. The structure table's "~17 psf vs 40 psf" averages over the whole footprint; the load is delivered on two short lines. Ceiling joists got a three-option note; **floor joists under the half-wall and kicker got nothing.**

**D · Screen lateral (200 lb).** Top plate → ceiling (open) and slats → beam, where slat 0 lands on nothing (#4) and the rest land half on trim (#15/16), base fastener unspecified.

## 4 · Built-up members

- **`hw_header`**: lamination *is* specified (16d @ 12", two rows). But when Rev S added the ¾" facing nobody redid the arithmetic: to reach 1" into the far ply a hanger fastener must be 0.75 + 1.5 + 0.5 + 1.0 = **3.75"**. Rev O said this face "must be left unsheathed"; Rev S sheathed it. Traceable regression.
- **`beam`** (doubled 2×10): lamination **not specified anywhere**. Joists hang off one ply (#9) and the beam hangs off the ledger at one end (#1); both rely on load crossing plies through unspecified fastening.

## 5 · Communication defects

- Non-structural nook soffit panel drawn at `stroke-width` 8 (Dwg 5) and 5 (Dwg 9) — heavier than the stringer (2) and studs (1.3). Rev N fixed this for the gussets and missed the panel.
- Nook flat ceiling vs side member: ¾" panel top at 42.25 vs side member bottom 41.71 — **0.54" interference**. "Clears by ¼"" is clearance to the finish *face*, ignoring panel thickness. The raked portion is handled correctly. Fix: stop the flat panel at x=108.5 and scribe, or rip the side member to 6¾".
- Rim length stated three ways (24 / 22.5 / 22.5). Side member length stated three ways (24 / 25.5 / 25.5).
- Rear ledger: table says 107"; true clear length 104.75".
- Ledger blocking drawn 3½" wide (Dwg 6) and 3½" tall (Dwg 3).
- Stale caption line 951: "stringers → 2×10 rim" — 2×12 since Rev M.
- Table E drift: rim/stringer bearing 11¼ → 11.00; underside at 27: 34½ → 34.42.

## Recommended order of resolution

1. Rim → header hanger seat (#2).
2. Rim length to 131 (#5).
3. Right-wall ledger to 2×12 (#3).
4. Side ledger to 50" (#1) — fixes #4.
5. Specify every UNSPECIFIED hanger and screw, counting the ¾" sheathing in every length.
6. Add treads, the deck-ply diaphragm connection, header straps and kicker anchorage to `connections:` so `verify.py` can see them.
