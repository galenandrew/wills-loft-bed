#!/usr/bin/env python3
"""build2.py — render docs/ from dimensions.yaml, through the CAD kernel.

Thin CLI over sheets.site, the way build.py is over drawings.site. The Rev-U set
in site/ is untouched; the two build independently until v2 covers everything.
Named docs/ so GitHub Pages can publish it directly.

    python3 build2.py                rebuild docs/
    python3 build2.py --quiet        one line, for the edit hook
    LOFT_KERNEL_NOCACHE=1 …          ignore the view cache and run the kernel
"""
import sys
import time

from sheets import geometry, site

quiet = "--quiet" in sys.argv

t0 = time.time()
figs = site.build()
dt = time.time() - t0

kb = sum(len(f.svg) for f in figs.values()) / 1024
switches = sum(len(f.components) + len(f.layers) for f in figs.values())
ran = sorted(set(geometry.MISSES))
line = (f"docs: {len(figs)} figures · {kb:.0f} kB · {switches} switches · {dt:.2f}s"
        + (f" · kernel ran for {', '.join(ran)}" if ran else " · all views cached"))
print(line)

if not quiet:
    for key, f in figs.items():
        if f.off:
            print(f"  {key}: starts with {', '.join(c[4:] for c in f.off)} off")
