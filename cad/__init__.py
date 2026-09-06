"""cad — a build123d kernel model derived from dimensions.yaml (adopted Rev V).

Nothing in here is a source of truth. dimensions.yaml is the model; verify.py
and drawings/ are unchanged. This package builds solids *from* the yaml so that
questions boxes cannot answer — notched stringer volume, fastener paths through
real material, true sections — can be asked of a kernel instead of by hand.
"""
