"""cad.scope — which assembly every yaml member belongs to, as plain data.

Split out of cad.model so it can be read without importing build123d: the sheets
need to know what assembly a member is in to put it on the right switch, and they
must not pay a 3-second OCCT import to find out. cad.model imports these names, so
there is still exactly one list.
"""

# ------------------------------------------------------------------ the scope
# Five assemblies, as the builder splits them. The landing is part of the STAIR — it
# is the top step — not a thing of its own. The nook's *framing* is the half-wall's
# rough opening and stays with the half-wall; what belongs to the nook is its lining
# and the two nailer walls that carry it. `loft` is the deck the bed sits on plus the
# beam and the boxed ledge; `screen` is the guard above the beam.
SCOPE = {
    "loft":      ["rear_ledger", "side_ledger",
                  *[f"deck_joist[{i}]" for i in range(9)], "deck_rim",
                  *[f"deck_blocking[{i}]" for i in range(8)], "deck_blocking_end",
                  *[f"deck_seam_blocking[{i}]" for i in range(5)],
                  "beam", "deck_ply", "loft_ceiling",
                  "beam_wrap_face", "beam_wrap_inner", "beam_wrap_top",
                  "ledge_cleat", "ledge_cleat_rail",
                  *[f"ledge_strut[{i}]" for i in range(3)],
                  "ledge_front_rail", "ledge_rail_splice", "ledge_lid"],
    "screen":    ["screen_top_plate", *[f"slat[{i}]" for i in range(23)]],
    "stair":     ["stringer_a", "stringer_b", "stringer_c", "kicker",
                  "lnd_ledger_bedwall", "lnd_ledger_rightwall", "lnd_side_member",
                  "lnd_joist[0]", "lnd_joist[1]", "lnd_rim",
                  "lnd_blocking[0]", "lnd_blocking[1]", "lnd_ply",
                  "stringer_a_skin", "stringer_a_skin_cleat"],
    "half_wall": ["hw_bottom_plate_a", "hw_bottom_plate_b",
                  "hw_king_a", "hw_king_b", "hw_trimmer_a", "hw_trimmer_b",
                  "hw_jamb_ply_a", "hw_jamb_ply_b",
                  "hw_header", "hw_top_plate_1", "hw_top_plate_2", "hw_rake_nailer",
                  "hw_sheath_loft_a", "hw_sheath_loft_head",
                  "hw_sheath_stair", "hw_end_cap"],
    "nook":      ["nk_bedwall_stud[0]", "nk_bedwall_stud[1]",
                  "nk_bedwall_stud[2]", "nk_bedwall_cap",
                  "nk_shortwall_strut[0]", "nk_shortwall_strut[1]",
                  "nk_shortwall_strut[2]",
                  "nk_wrap_bedwall", "nk_wrap_shortwall",
                  "nk_soffit_flat", "nk_soffit_rake"],
}

# Context, not the build: the mattress and the three things already in the room. They
# are what the clearance questions are asked *against* (headroom over the mattress, the
# fan over the screen), so the kernel needs them — but they are not material to cut and
# a section sheet must never hatch a dresser. build() leaves them out unless asked.
CONTEXT = ["desk", "dresser", "fan"]

# The inverse of LAMINATIONS: yaml rows that are ONE piece on the bench. The boxed
# ledge's front rail is a single 107 board notched 1 1/2 (x) x 5 (z) over the side
# ledger at the window wall; dimensions.yaml has no notch primitive, so it carries the
# board as the full-depth body plus the tongue left above the notch. Fusing the two
# boxes gives the L-shaped solid the board actually is — one solid, one volume, and a
# clash or ray cast sees the notch instead of a square end 1 1/2 short of the wall.
# Rev AD adds three more: the two faces of the half-wall are one board each side of a
# single seam, and the yaml carries each board as the two or three rectangles it is made
# of (a raked head panel is not a box, and the ledge and beam ends stand above the deck).
# As with the front rail, the fused rows are NOT listed in SCOPE — they are covered by
# NOTCH_PARTS, and listing them too would build them a second time and clash with the
# board they are part of. The stair face carries ledge_end_cap and beam_end_cap, so that
# one board is reported under half_wall even though both ends belong to the loft.
NOTCHED = {
    # Rev AG: the beam is one 1 3/4 x 14 LVL notched 3 x 3 1/2 out of its bottom left
    # corner, so its end can sit on the side ledger and the sistered joist beside it;
    # deck_joist[0] is one 48 1/2 2x4 that runs on under it while the other eight stop
    # at the beam face. Both are carried as two rows for the same reason the front rail
    # was — the yaml has no notch primitive.
    "beam": ["beam_tongue"],
    "deck_joist[0]": ["deck_joist_tail"],
    # Rev AG: the front rail's notch is gone with the 2x10 side ledger; it is a plain board.
    # the nook face: a 4 1/4 stile, then one 45 3/4 x 53 3/4 board with the opening in it
    "hw_sheath_loft_head": ["hw_sheath_loft_b"],
    # the stair face: floor-to-ledge-top on the bed-wall side, floor-to-beam-top beyond
    # Rev AE: the stair face is ONE skirt board, floor-to-ledge and floor-to-beam ends included
    "hw_sheath_stair": ["ledge_end_cap", "beam_end_cap"],
    # and the wall's end cap is one board with a corner cut out of it for stringer A
    "hw_end_cap": ["hw_end_cap_foot"],
}

NOTCH_PARTS = {p for parts in NOTCHED.values() for p in parts}
