# tools/

- `hook.sh` — the PostToolUse hook wired in `.claude/settings.json`: verify on model edits, build on model/drawing/content/cad edits, change report injected as context.
- `literals.py` — lists hand-typed numbers in drawing labels and `content/` prose with file:line; the auditor's worklist. `python3 tools/literals.py d4 d8`.

The `View` helper the sheets draw with is `drawings/svgview.py` (it moved out of
here so `drawings/` and `cad/` import it as a package instead of by sys.path).
The Rev T / Rev U landing sketches are in `archive/`.
