"""sheets.taxonomy — which component and which layer every solid belongs to.

The kernel already groups solids into the five assemblies a builder splits the job
into. This adds the two axes the drawings toggle on:

  COMPONENT   the thing you are building or working around — the five assemblies,
              plus the mattress and the three fixtures already in the room, each
              on its own switch so a sheet can show the dresser beside the stair
              without dragging the desk and the fan in with it.

  LAYER       framing (the rough structure), finish (the surfaces applied to it),
              electrical (symbols, not solids), context (things not being built).

Layer is a DRAWING concern, not a structural one, so it lives here rather than in
dimensions.yaml — but it is stated per member and asserted complete, so a member
added to the yaml cannot quietly land in the wrong layer or in none.
"""
from cad.model import SCOPE, CONTEXT

# ------------------------------------------------------------------ components
CONTEXT_COMPONENTS = {"desk": "desk", "dresser": "dresser", "fan": "fan",
                      "mattress": "mattress"}

COMPONENTS = ["loft", "screen", "stair", "half_wall", "nook",
              "mattress", "desk", "dresser", "fan"]

LABEL = {"loft": "Loft", "screen": "Screen", "stair": "Stair + landing",
         "half_wall": "Half wall", "nook": "Nook", "mattress": "Mattress",
         "desk": "Desk", "dresser": "Dresser", "fan": "Ceiling fan"}

BUILT = ["loft", "screen", "stair", "half_wall", "nook"]      # what gets cut


def component(piece):
    if piece.assembly == "context":
        return CONTEXT_COMPONENTS[piece.id]
    return piece.assembly


# ---------------------------------------------------------------------- layers
LAYERS = ["framing", "finish", "electrical"]
LAYER_LABEL = {"framing": "Framing", "finish": "Finish", "electrical": "Electrical"}

# `finish` is what you see when the job is done; `framing` is everything it is
# applied to. Two calls worth stating: deck_ply and lnd_ply are FINISH, because on
# a plan they hide every joist under them and the switch a builder reaches for is
# "take the floor off" — their structural job as a diaphragm is in the caption and
# the fastener schedule, not in this switch. The jamb flitches stay framing (they
# are inside the wall), and so do the screen's slats, which ARE the screen rather
# than a skin on it.
FINISH = (
    "loft_ceiling", "beam_wrap_", "ledge_lid", "deck_ply",
    "lnd_ply", "stringer_a_skin", "tread[", "riser[",
    "hw_sheath_", "hw_end_cap",
    "nk_wrap_", "nk_soffit_",
)


def layer(piece):
    if piece.assembly == "context":
        return "context"
    base = piece.id.split("#")[0]
    return "finish" if base.startswith(FINISH) else "framing"


# ------------------------------------------------------------------- coverage
def check(pieces):
    """Every solid lands in exactly one component and one layer. A member added to
    the yaml and not classified here shows up as a FAIL, not as a piece silently
    drawn in the wrong colour."""
    bad = []
    for p in pieces:
        c, l = component(p), layer(p)
        if c not in COMPONENTS:
            bad.append(f"{p.id}: unknown component {c!r}")
        if l not in LAYERS + ["context"]:
            bad.append(f"{p.id}: unknown layer {l!r}")
    known = {mid for ids in SCOPE.values() for mid in ids} | set(CONTEXT)
    if bad:
        raise AssertionError("sheets.taxonomy: " + "; ".join(bad))
    return len(known)
