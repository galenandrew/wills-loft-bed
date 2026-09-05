# tools/

- `svgview.py` — orthographic `View` helper (plan / elevation / section, dimension strings, hatching) used by every sheet module in `drawings/`.
- `hook.sh` — the PostToolUse hook wired in `.claude/settings.json`: verify on model edits, build on model/drawing/content edits, change report injected as context.
- `literals.py` — lists hand-typed numbers in drawing labels and `content/` prose with file:line; the auditor's worklist. `python3 tools/literals.py d4 d8`.
- `sketch_U.py <out.json> [yaml]` / `sketch_T.py <out.json> [yaml]` — the landing figures used for the Rev U decision (from `archive/dimensions-U.yaml`; Rev T's from `archive/dimensions-T.yaml`). Both default to their frozen snapshot — every non-yaml constant in either file (HB, CEIL, the 2x8-landing-box literals) is pinned to that decision, so passing the live `dimensions.yaml` mixes current geometry with historical numbers rather than reproducing anything real. Historical; `build.py` supersedes them for the drawing set.

Everything imports `verify.py` for member expansion and stair geometry, so no figure can disagree with the checker.
