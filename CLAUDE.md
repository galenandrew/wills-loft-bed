# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Build documentation for a lofted twin bed in a child's room (131" × 186", 8' ceiling, second floor). Not a software project. The user is an experienced builder with full tool access and a flexible budget. The design is essentially finalized; the remaining work is closing the open findings, then the materials list and cut list.

Read `archive/KICKOFF.md` for the original brief (historical; its file names predate Rev U), `AGENTS.md` for when to use subagents, and `audits/` for past review findings.

## Source of truth and workflow

**`dimensions.yaml` is the model.** Every member's framing extents in x (from the window wall), y (from the bed wall), z (above floor), plus every claimed structural connection. The drawing site in `site/` is a *rendering* of it and is subordinate to it. Where they disagree, the yaml wins — unless the yaml mis-encoded the design, in which case fix the yaml and say so.

**`python3 verify.py`** recomputes every derived quantity (schedule table E), checks every connection for real three-axis overlap, hanger engagement, and fastener path, and finds volume clashes. It exits non-zero on any FAIL.

**`python3 build.py`** renders `site/` from the yaml: four scrolling pages — `index.html` (Overview: conventions, locked dimensions, Drawings 1–2, open items), `stairs.html` (Drawings 4, 5, 8, 9), `loft.html` (Drawings 3, 6, 7), `appendix.html` (schedule, structure, revisions) — plus standalone figures in `site/figs/<key>.svg` and `manifest.json`. Drawing numbers are unchanged; `PAGE_SHEETS` in `drawings/site.py` says which page a sheet is on. It always rebuilds everything (under a second) and **reports which figures changed and which labels moved**. `--single out.html` also writes the whole set as one file, for publishing or printing only.

**The hook does both for you.** A PostToolUse hook (`tools/hook.sh`) runs on every Write/Edit: editing `dimensions.yaml` or `verify.py` runs verify (FAIL/WARN lines come back to you) and then the build; editing `drawings/`, `content/`, or `tools/svgview.py` runs the build. The one-line change report is injected into your context. You should rarely need to run either script by hand.

The loop for any change:

1. Change `dimensions.yaml` (member extents, connections, `expected:` values). Read the hook's verify output. Fix until clean, or explain to the user why a FAIL is accepted (currently two parked FAILs: beam left end, slat 0).
2. Read the hook's build report. Look **only** at the figures it names — open `site/figs/<key>.svg`, or screenshot them. Do not read the whole site.
3. If a label or caption needs to move, edit that sheet's module in `drawings/`; if prose needs to change, edit `content/`. The hook rebuilds.
4. Bump `rev:` in the yaml and add a row at the top of `content/revisions.json`. One letter per design change; `.1` suffixes for drawing-only cleanups. Update the cut list / materials list to match once they exist.
5. Before cutting material: run `drawing-auditor` and `connection-checker` (see `AGENTS.md`), scoped to the sheets the build reports changed.

Never hand-edit anything in `site/`. It is overwritten on every build.

## Token discipline

The restructure exists so that a change touches a few small files, not one big one. Keep it that way:

- **To change one drawing**, read only `drawings/d<N>_*.py` (20–60 lines) and, if you need a helper, the header of `drawings/model.py`. Geometry comes from the yaml; the module holds only view setup, which members to draw, labels, and its caption.
- **To check a drawing**, read `site/figs/<key>.svg` (6–10 KB) or screenshot it — never a whole page unless you need its captions, and never a `--single` file. Captions live in the sheet module.
- **To change prose** (structure table, open items, conventions, revisions), edit `content/`. Model values go in as `{placeholders}` from `drawings.model.VALS`; an unknown name fails the build. Hand-typed numbers in prose and labels are the one thing that can still drift — `python3 tools/literals.py d4 d8` lists them with file:line so you check those, not everything.
- **Don't re-render to see what changed.** The build report already says which figures changed and which labels moved. Trust it; the same code produces the site and the report.
- Sheets are numbered by their module name (`d4_stair_section.py` → Drawing 4). Add a sheet by adding a module with `NUMBER`, `TITLE`, `FIGURES`, `CAPTION`, appending it to `SHEET_MODULES` in `drawings/site.py`, and placing it in `PAGE_SHEETS` (the build asserts every sheet is on exactly one page).

## Coordinate and encoding conventions

- Inches, decimal in the yaml. `verify.py` prints nearest-sixteenth alongside; `fr()` formats sixteenths or two decimals.
- Extents are **framing** extents (actual lumber size). Finished faces (wrap, sheathing, ply) are their own members. Cut lists use the framing numbers; layout marks use the finished ones.
- Repeated members use `repeat:`; ids become `id[0]…`. Wildcards in connections are quoted: `"deck_joist[*]"`.
- Stringers are `kind: stringer`; their bbox is ignored and the true sloped profile is computed from `stair:`.
- Anything not stated in the drawings and guessed during encoding is marked `ASSUMED` in a `note:`. Resolve these with the user, don't silently keep them.
- `expected:` holds the values Rev T states. When a change legitimately moves one, update it deliberately — that's the audit trail.
- View conventions (stated on the index page): plans bed-wall-up, window wall left; x–z views look toward the bed wall; y–z views keep the bed wall on the left, mirrored where needed.
- **The yaml's axes are LEFT-handed as they map onto the room, and that is load-bearing.** Facing the closet wall (+y), the window wall (x = 0) is on your RIGHT — so yaml +x runs to your left and `x × y = −z`. The naming is consistent from the other vantage: facing the BED wall, +x really is on your right, which is how the sheets are read. This is harmless in 2D — every figure maps two yaml axes onto the page and all twelve come out correct (plans are true from-above plans; d4's half-wall really is in front of the cut; d8b really does look toward the bed wall). It is **not** harmless for a solid: feeding these coordinates straight into a CAD kernel builds the mirror image of the room. `cad/export.py:to_room_frame()` mirrors x into a right-handed room frame (`X = room.x − x`, from the stair/door wall toward the window) for STEP and STL only. Everything else stays in yaml coordinates. Do not "fix" the drawings' mirroring — it is what makes them right. The export is **Z-up**, the CAD standard; some previewers assume Y-up and will show it lying on its back — rotate in the viewer, don't change the export.

## Working rules (hard-won — do not relitigate)

- **Never assert a geometric relationship from memory. Compute it.** If it isn't in `verify.py`'s output, it isn't verified.
- **Distinguish framing from finished everywhere.** Platform 50¾" finished / 50" framed. Half-wall 5" finished / 3½" studs. Deck 107" finished / 106¼" structural rim.
- **Errors cluster where two assemblies meet.** Before claiming two members connect, they must be in `connections:` and pass. A connection whose fastener is UNSPECIFIED is not done.
- **Some depths are set by connection requirements, not load.** The nook header is a 2×10 sandwich at ~140 psi because the landing rim needs 7½" to hang from. Never "optimise" a member down without re-running the connection it exists for.
- **Fastener penetration counts what it passes through.** A 1½" hanger nail through ¾" sheathing reaches ¾". Hanger flange holes below the supporting member's bottom hit air.
- **Flag now-or-never decisions** — things that get much harder after a prior step (nook power before sheathing; joist location before the screen top plate).
- **Outside-run dimension lines go outside the wall they measure**, clear of the wall rect, the way d3 and d7 place them — not on or inside the wall face. d8a and d8b currently violate this (noted inline at their `dim_h` calls); fix opportunistically when touching those sheets. If this keeps recurring across sheets, bake the clearance into `dim_h`/`dim_v` in `tools/svgview.py` instead of relying on each sheet module to get it right.
- **Push back on the user.** The design improved every time a session did.
- **Never commit unprompted.** Make the change, say what changed, and stop. Suggest a commit when it makes sense; the user gives the command. This includes `--amend` and `revert`.
- **Keep replies concise.** No long responses. State the error/update plainly, make the fix, name what changed. The detailed reasoning belongs in the commit message and in `audits/`, not in chat — the user asks when they want more.
- **Design and geometry changes happen inline, with the full model in context.** Subagents audit; they don't design.

## Model choice

The user does not want Fable for everything. Guidance:
- Inline design work, yaml edits, drawing/label updates, prose, cut/materials lists: the session's default model is fine, because `verify.py` and the build report are the safety net.
- `drawing-auditor` is pinned to Opus: it runs rarely (per rev, pre-cut), and a miss costs lumber. Scope it to changed sheets so the cost stays small. (Was Fable; switched 2026-09-05 when Fable ran out of usage credits mid-session. Revisit if Fable becomes reliably available again — the point is spending more on a rare, high-stakes check, not the specific model.)
- `connection-checker` and `materials-pricer` run on Sonnet; the script does the arithmetic.

## Field measurements still owed

Assumed in the model until measured; anything depending on them is provisional:
- Ceiling joist nearest 50¾" from the bed wall (joists run parallel to it) — sets the screen top-plate fixing.
- Actual mattress thickness (`mattress.thickness`, assumed 6").
- Stud locations in the bed wall, window wall, and right wall — every ledger and the beam's left-end support depend on them.

## Files

- `dimensions.yaml` — the model. Edit this.
- `verify.py` — the checker. Don't "fix" a failure by editing the checker. `compute_derived()` is shared with the drawings.
- `build.py` — renders `site/` (and `--single`). Thin CLI over `drawings/site.py`.
- `drawings/` — the generator package. `model.py` loads the yaml once and exposes `M`, `ST`, `DER`, constants, `fr()`, `m()`, `R()`, `View`, and `VALS` (named values for prose). `d1_floor_plan.py` … `d9_framing_overlay.py` are one sheet each. `schedule.py` is tables A–E and the locked-dimension cards. `site.py` assembles pages, CSS, the manifest, and the change report.
- `content/` — the only hand-written prose: `conventions.yaml`, `structure.yaml`, `open-items.yaml`, `revisions.json` (Rev U row first, then Rev T's history).
- `site/` — generated Rev U set, four pages with sticky tabs and ←/→ arrows (buttons and keyboard). **Never hand-edit.** `site/index.html` is where the builder starts.
- `tools/` — `svgview.py` (the SVG `View` helper), `hook.sh` (the PostToolUse hook), `literals.py` (hand-typed numbers finder), and the landing sketches from the Rev U decision.
- `archive/` — Rev T's hand-drawn set, its yaml encoding (`dimensions-T.yaml`), its revisions log, the original brief (`KICKOFF.md`), and `dimensions-U.yaml` (a frozen snapshot restored 2026-09-05 so `tools/sketch_U.py` has a real default instead of silently mixing Rev U literals with whatever yaml happens to be passed to it).
- `cad/` — a **derived** build123d kernel layer (`audits/V-kernel-spike.md`). `python3 -m cad.spike` builds the stair and landing as real solids *from* the yaml — `model.py` (boxes from framing extents, stringers extruded from `drawings.stringer_pts()`, plus treads/risers/soffit/header laminations the yaml does not carry), `section.py` (plane cuts + hidden-line removal, emitted in `svgview.View`'s own inch coordinates), `check.py` (solid interference, minimum distance, fastener ray casts), `export.py` (STEP/STL) — and writes `spike/` in under a second. It is **not** a source of truth and does **not** replace `verify.py`, `drawings/` or `site/`: it answers the three questions boxes cannot (notched stringer volume, what a screw actually passes through, true sections), and it agreed with `verify.py` to five decimals everywhere both could answer. Run it before cutting material, alongside `drawing-auditor` and `connection-checker`. It found the Rev W joinery error. **Drawing 4 is generated from it**: `kernel_cut(v, "x", CUT_X, skip=(...))` in `drawings/model.py` asks the plane what it crosses instead of the sheet listing members, and returns closed loops in `View`'s own inch coordinates. Styling defaults by stock (framing hatched, sheet goods plain) and a sheet overrides per member. Every other sheet still uses `R()` box projection, which is exact for axis-aligned members and costs nothing. Installing needs `python3 -m pip install build123d` (~220 MB of OCCT).
- `spike/` — `cad.spike` outputs. Gitignored except `REPORT.md` (the run log). Regenerated every run; never hand-edit.
- `.kernel-cache/` — cut results keyed by a hash of every input that can change them (`dimensions.yaml`, `verify.py`, `drawings/model.py`, `cad/*.py`). Importing build123d costs ~3 s against a build that is otherwise 0.06 s, and the hook builds on every edit — so a label or caption change hits the cache and stays at 0.06 s, while touching geometry misses and runs the kernel. Cached output is byte-identical to a live run (verified). `LOFT_KERNEL_NOCACHE=1 python3 build.py` forces a real run; `cad.spike` never uses it. Gitignored, safe to delete.
- `audits/` — dated reports from the subagents. Read the latest before starting design work.
- `.claude/settings.json` — the hook wiring. `/hooks` to inspect or disable.
