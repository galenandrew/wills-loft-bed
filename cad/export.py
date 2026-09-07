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

UNITS. The kernel is unitless: a yaml inch is one OCCT unit, and OCCT's unit is a
millimetre unless the file says otherwise. Left alone, both exports therefore claim
the bed is 107 mm wide — the right numbers, the wrong size, 25.4× small.

  STEP carries its unit, so it is told the truth: the XDE document is declared in
  inches (`unit=Unit.IN`) and the writer is told to keep inch numbers in the file
  (`write.step.unit = INCH`, which emits a CONVERSION_BASED_UNIT('INCH')). The
  coordinates in the file are then the yaml's own numbers AND a reader scales them
  correctly — 107" reads as 107", or as 2717.8 mm in a metric viewer.

  STL carries no unit at all and is read as millimetres by essentially everything,
  so it is written scaled ×25.4. It is the one output whose numbers are not inches;
  that is what makes it open at true size.
"""
from __future__ import annotations

import os

from build123d import (Compound, Plane, Pos, Unit, export_step, export_stl,
                        mirror)
from OCP.Interface import Interface_Static
from OCP.STEPCAFControl import STEPCAFControl_Controller
from OCP.STEPControl import STEPControl_Controller

import drawings.model as _dm

ROOM_X = float(_dm.room["x"])
MM_PER_INCH = 25.4


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
    """STEP in inches — inch numbers in the file, declared as inches (see UNITS)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    # global OCCT setting, so set it on every call rather than once at import — and
    # init the controllers FIRST: export_step inits them after it would read this,
    # which silently resets it to MM on the first call of a session (the file is then
    # still the right size, but written in mm, so file A and file B disagree).
    STEPCAFControl_Controller.Init_s()
    STEPControl_Controller.Init_s()
    Interface_Static.SetCVal_s("write.step.unit", "INCH")
    export_step(compound(pieces, name), path, unit=Unit.IN)
    return path


def stl(pieces, path, tolerance=0.01, angular_tolerance=0.2):
    """STL in millimetres — the format has no unit and every reader assumes mm.
    Tolerances are inches, applied before the scale, so they mean what they say."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    export_stl(compound(pieces).clean().scale(MM_PER_INCH), path,
               tolerance=tolerance * MM_PER_INCH,
               angular_tolerance=angular_tolerance)
    return path
