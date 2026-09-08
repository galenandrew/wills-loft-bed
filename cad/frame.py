"""cad.frame — the view frame, in plain arithmetic.

Both the kernel (cad.view3d, which needs build123d Vectors) and the sheets
(sheets.geometry, which must not pay the 3 s OCCT import just to place a label)
have to agree on where the camera is. They agree by both calling this, which
imports nothing.
"""
import math


def _norm(v):
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def frame(direction, up=(0, 0, 1)):
    """(direction, right, up) orthonormal. `direction` is where the camera LOOKS."""
    d = _norm(direction)
    u = tuple(a - b for a, b in zip(up, tuple(c * _dot(up, d) for c in d)))
    if math.sqrt(sum(c * c for c in u)) < 1e-9:
        u = (0, 1, 0) if abs(d[2]) > 0.9 else (0, 0, 1)
        u = tuple(a - b for a, b in zip(u, tuple(c * _dot(u, d) for c in d)))
    u = _norm(u)
    return d, _norm(_cross(u, d)), u


def flip(right, mirror):
    return tuple(-c for c in right) if mirror else right


def project(pt, right, up):
    """A 3D point in the view's own (h, v) inches."""
    return (_dot(pt, right), _dot(pt, up))
