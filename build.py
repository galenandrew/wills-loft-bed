#!/usr/bin/env python3
"""
build.py — render the drawing site from dimensions.yaml.

    python3 build.py                     # → site/ (index, one page per sheet, figs/*.svg, manifest.json)
    python3 build.py --single out.html   # also write the whole set as one file (for publishing / printing)
    python3 build.py --yaml other.yaml   # render a different model (e.g. archive/dimensions-T.yaml)
    python3 build.py --quiet             # one-line report only (what the hook prints)

Always rebuilds every page — it takes well under a second — and reports which
FIGURES changed against the previous build, with the labels that moved, so
you only need to look at those. Exit code 1 on any error.
"""
import os, sys
args = sys.argv[1:]
def opt(name, default=None):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default
yaml_path = opt("--yaml"); single = opt("--single"); quiet = "--quiet" in args
site_dir = opt("--out", "site")
if yaml_path: os.environ["LOFT_YAML"] = os.path.abspath(yaml_path)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from drawings import site
rep = site.build(site_dir, single)
print(site.summary(rep, site_dir))
if single and not quiet: print(f"single file: {single}")
