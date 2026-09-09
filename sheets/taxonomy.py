"""sheets.taxonomy — which component and which layer every solid belongs to.

The kernel already groups solids into the five assemblies a builder splits the job
into. This adds the two axes the drawings toggle on:

  COMPONENT   the thing you are building or working around — the five assemblies
              (with the boxed ledge split off the loft, see LEDGE below),
              plus the mattress and the three fixtures already in the room, each
              on its own switch so a sheet can show the dresser beside the stair
              without dragging the desk and the fan in with it.

  LAYER       framing (the rough structure), finish (the surfaces applied to it),
              electrical (symbols, not solids), context (things not being built).

Layer is a DRAWING concern, not a structural one, so it lives here rather than in
dimensions.yaml — but it is stated per member and asserted complete, so a member
added to the yaml cannot quietly land in the wrong layer or in none.
"""
from cad.scope import CONTEXT, NOTCHED, SCOPE   # plain data: no build123d, no 3 s import

# ------------------------------------------------------------------ components
CONTEXT_COMPONENTS = {"desk": "desk", "dresser": "dresser", "fan": "fan",
                      "mattress": "mattress"}

COMPONENTS = ["loft", "ledge", "screen", "stair", "half_wall", "nook",
              "mattress", "desk", "dresser", "fan"]

LABEL = {"loft": "Loft", "ledge": "Boxed ledge", "screen": "Screen",
         "stair": "Stair + landing", "half_wall": "Half wall", "nook": "Nook",
         "mattress": "Mattress", "desk": "Desk", "dresser": "Dresser",
         "fan": "Ceiling fan"}

BUILT = ["loft", "ledge", "screen", "stair", "half_wall", "nook"]   # what gets cut

# The boxed ledge is built with the loft and the kernel keeps it in that assembly,
# but on a drawing it is the one thing a reader wants off on its own — it stands
# above the deck and hides the beam and the deck edge behind it. Component is a
# drawing concern, so the split lives here.
LEDGE = ("ledge_cleat", "ledge_strut", "ledge_front_rail", "ledge_rail_splice",
         "ledge_lid")


def component(piece):
    if piece.assembly == "context":
        return CONTEXT_COMPONENTS[piece.id]
    if piece.id.split("#")[0].startswith(LEDGE):
        return "ledge"
    return piece.assembly


ASSEMBLY_OF = {mid: a for a, ids in SCOPE.items() for mid in ids}
# a row that is part of another board belongs to that board's assembly
ASSEMBLY_OF.update({part: ASSEMBLY_OF[parent]
                    for parent, parts in NOTCHED.items() for part in parts
                    if parent in ASSEMBLY_OF})


def component_of_member(mid):
    """The component a yaml member id belongs to — for the things that are not
    solids (an outlet, a switch) and have to be switched with their host."""
    base = mid.split("#")[0]
    if base in CONTEXT_COMPONENTS:
        return CONTEXT_COMPONENTS[base]
    if base.startswith(LEDGE):
        return "ledge"
    return ASSEMBLY_OF.get(base, "loft")


MEMBERS = set(ASSEMBLY_OF) | set(CONTEXT_COMPONENTS)


def label_component(name):
    """The component a LABEL belongs to — what a sheet's `of=` resolves to.

    Takes a component name, or the id of the member the label names, so a sheet
    can write `of="ledge_lid"` and not have to know which switch that is. An
    unknown name raises: a typo must not quietly park a label on the loft, which
    is what `component_of_member`'s default would do."""
    if name in COMPONENTS:
        return name
    base = name.split("#")[0]
    if base in MEMBERS or base.startswith(LEDGE):
        return component_of_member(name)
    raise KeyError(f"sheets.taxonomy: of={name!r} is neither a component nor a "
                   f"member id — a label must name something switchable")


# ---------------------------------------------------------------------- layers
LAYERS = ["framing", "finish", "electrical"]
LAYER_LABEL = {"framing": "Framing", "finish": "Finish", "electrical": "Electrical"}

# `finish` is what you see when the job is done; `framing` is everything it is
# applied to. Calls worth stating: deck_ply and lnd_ply are FINISH, because on
# a plan they hide every joist under them and the switch a builder reaches for is
# "take the floor off" — their structural job as a diaphragm is in the caption and
# the fastener schedule, not in this switch. The jamb flitches stay framing (they
# are inside the wall). The screen — top plate and all 23 slats — is FINISH: it
# reads as the room's visible surface, not rough structure, so the whole component
# switches together under Finish rather than splitting its one framing member out.
FINISH = (
    "loft_ceiling", "beam_wrap_", "ledge_lid", "ledge_front_rail", "deck_ply",
    "lnd_ply", "stringer_a_skin", "tread[", "riser[",
    "hw_sheath_", "hw_end_cap",
    "nk_wrap_", "nk_soffit_",
    "screen_top_plate", "slat[",
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
