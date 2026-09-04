"""cad.export — STEP and STL of the whole model or one assembly."""
from __future__ import annotations

import os

from build123d import Compound, export_step, export_stl


def compound(pieces, name="loft-stair"):
    children = []
    for p in pieces:
        c = Compound(p.solid.solids())
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
