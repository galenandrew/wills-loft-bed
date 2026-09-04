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

## Working rules (hard-won — do not relitigate)

- **Never assert a geometric relationship from memory. Compute it.** If it isn't in `verify.py`'s output, it isn't verified.
- **Distinguish framing from finished everywhere.** Platform 50¾" finished / 50" framed. Half-wall 5" finished / 3½" studs. Deck 107" finished / 106¼" structural rim.
- **Errors cluster where two assemblies meet.** Before claiming two members connect, they must be in `connections:` and pass. A connection whose fastener is UNSPECIFIED is not done.
- **Some depths are set by connection requirements, not load.** The nook header is a 2×10 sandwich at ~140 psi because the landing rim needs 7½" to hang from. Never "optimise" a member down without re-running the connection it exists for.
- **Fastener penetration counts what it passes through.** A 1½" hanger nail through ¾" sheathing reaches ¾". Hanger flange holes below the supporting member's bottom hit air.
- **Flag now-or-never decisions** — things that get much harder after a prior step (nook power before sheathing; joist location before the screen top plate).
- **Push back on the user.** The design improved every time a session did.
- **Design and geometry changes happen inline, with the full model in context.** Subagents audit; they don't design.

## Model choice

The user does not want Fable for everything. Guidance:
- Inline design work, yaml edits, drawing/label updates, prose, cut/materials lists: the session's default model is fine, because `verify.py` and the build report are the safety net.
- `drawing-auditor` is pinned to Fable: it runs rarely (per rev, pre-cut), and a miss costs lumber. Scope it to changed sheets so the cost stays small.
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
- `archive/` — Rev T's hand-drawn set, its yaml encoding, its revisions log, and the original brief (`KICKOFF.md`).
- `audits/` — dated reports from the subagents. Read the latest before starting design work.
- `.claude/settings.json` — the hook wiring. `/hooks` to inspect or disable.
