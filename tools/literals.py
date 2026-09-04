#!/usr/bin/env python3
"""
tools/literals.py — list every hand-typed number in drawing labels and site prose.

    python3 tools/literals.py            # all sheets + content/ (revisions history skipped)
    python3 tools/literals.py d4 d8      # only those sheet modules (+ content/)
    python3 tools/literals.py --all      # include content/revisions.json

Geometry is generated from the model and cannot drift; the residual risk is a
number typed into a label, caption, or table by hand ("24 × 27", "104¾").
This prints each one with its file:line so a reviewer checks those, not the
whole set. Anything inside {…} is computed and skipped, as are member ids.
"""
import re, sys, glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sel = [a for a in sys.argv[1:] if not a.startswith("-")]
files = sorted(glob.glob(f"{ROOT}/drawings/d*_*.py")) + sorted(glob.glob(f"{ROOT}/content/*"))
if "--all" not in sys.argv: files = [f for f in files if not f.endswith("revisions.json")]
if sel: files = [f for f in files if any(os.path.basename(f).startswith(s + "_") for s in sel) or "/content/" in f]
NUM = re.compile(r"(?<![\w.#/-])\d+(?:\.\d+)?(?:[½¼¾⅛⅜⅝⅞]|/\d+)?(?![\w.]|px)")
STR = re.compile(r'''f?(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')''')
MEMBER_ID = re.compile(r'''f?["'][a-z_]+\[\d+\]["']''')
skip = re.compile(r"\{[^}]*\}|<[^>]*>|url\(#\w+\)|#[0-9a-f]{3,6}")
n = 0
for f in files:
    rel = os.path.relpath(f, ROOT)
    for i, line in enumerate(open(f, encoding="utf-8"), 1):
        if rel.startswith("drawings/") and line.lstrip().startswith(("#", '"""', "NUMBER, TITLE")): continue
        pieces = [m.group(0) for m in STR.finditer(line)] if rel.endswith(".py") else [line]
        for s in pieces:
            if MEMBER_ID.fullmatch(s): continue
            nums = NUM.findall(skip.sub(" ", s))
            if not nums: continue
            n += len(nums)
            print(f"{rel}:{i}  {' '.join(nums):<28} {s.strip()[:110]}")
print(f"-- {n} literal numbers in {len(files)} files", file=sys.stderr)
