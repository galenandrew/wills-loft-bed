"""cad.export — STEP and STL of the whole model or one assembly.

HANDEDNESS. dimensions.yaml's axes are LEFT-handed as they map onto the room:
facing the closet wall (+y) the window wall (x = 0) is on your RIGHT, so yaml +x
runs to your left, and yaml_x × yaml_y = −z. (The naming is consistent from the
other vantage — facing the BED wall, +x really is on your right, which is how the
drawings are read.) That is fine for 2D: every sheet maps two yaml axes onto the
page and comes out correct, which is why all twelve figures check out.

It is NOT fine for a solid. Feeding left-handed coordinates into a CAD kernel's
right-handed space builds the mirror image of the room — the half-wall lands on the
wrong side of the stair. So the export mirrors x into a right-handed ROOM FRAME:

    X = room.x − x   from the stair/door wall toward the window wall
    Y = y            from the bed wall toward the closet     (unchanged)
    Z = z            up                                       (unchanged)

X × Y = Z, so STEP and STL now open the same way round as the room. Everything
upstream — checks, ray casts, sections, the Drawing 4 port — stays in yaml
coordinates, where it agrees with the drawings to 0.0000".
"""
from __future__ import annotations

import os

from build123d import Compound, Plane, Pos, export_step, export_stl, mirror

import drawings.model as _dm

ROOM_X = float(_dm.room["x"])


def to_room_frame(shape):
    """yaml coordinates → the right-handed room frame. A mirror, so it flips
    handedness; the translation just keeps the model in positive space."""
    return Pos(ROOM_X, 0, 0) * mirror(shape, about=Plane.YZ)


def compound(pieces, name="loft-stair", room_frame=True):
    """Assembly of the pieces. `room_frame=False` keeps raw yaml coordinates —
    only useful for comparing against the yaml, never for a viewer."""
    # mirror per piece: mirror() flattens a Compound's children and loses the labels
    children = []
    for p in pieces:
        solid = to_room_frame(p.solid) if room_frame else p.solid
        c = Compound(solid.solids())
        c.label = p.id
        children.append(c)
    return Compound(children=children, label=name)


def subset(pieces, *assemblies):
    return [p for p in pieces if p.assembly in assemblies]


def step(pieces, path, name="loft-stair"):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    export_step(compound(pieces, name), path)
    return path


def stl(pieces, path, tolerance=0.01, angular_tolerance=0.2):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    export_stl(compound(pieces).clean(), path,
               tolerance=tolerance, angular_tolerance=angular_tolerance)
    return path
