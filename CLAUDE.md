# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Build documentation for a lofted twin bed in a child's room (131" × 186", 8' ceiling, second floor). Not a software project. The user is an experienced builder with full tool access and a flexible budget. The design is essentially finalized; the remaining work is closing the open findings, then the materials list and cut list.

Read `KICKOFF.md` for the brief, `AGENTS.md` for when to use subagents, and `audits/` for past review findings.

## Source of truth and workflow

**`dimensions.yaml` is the model.** Every member's framing extents in x (from the window wall), y (from the bed wall), z (above floor), plus every claimed structural connection. `loft-bed-drawings.html` is a *rendering* of it and is subordinate to it. Where they disagree, the yaml wins — unless the yaml mis-encoded the drawing, in which case fix the yaml and say so.

**`python3 verify.py`** recomputes every derived quantity (schedule table E), checks every connection for real three-axis overlap, hanger engagement, and fastener path, and finds volume clashes. It exits non-zero on any FAIL. A PostToolUse hook runs it automatically on every edit to `dimensions.yaml` and feeds failures back to you.

The loop for any change:

1. Change `dimensions.yaml` (member extents, connections, `expected:` values).
2. Read the verify output the hook returns. Fix until clean, or explain to the user why a FAIL is accepted.
3. Run `python3 drawings.py` to regenerate the HTML; update the cut list / materials list to match.
4. Bump `rev:` in the yaml and add a row to `REV_NOTE`/the revisions log in `drawings.py` (Rev T's rows are carried from `archive/revisions-T.json`). One letter per design change; `.1` suffixes for drawing-only cleanups.
5. Before cutting material: run `drawing-auditor` and `connection-checker` (see `AGENTS.md`).

Never hand-edit a number in the HTML without first changing it in the yaml. Drift between them is this project's recurring bug.

## Coordinate and encoding conventions

- Inches, decimal in the yaml. `verify.py` prints nearest-sixteenth alongside.
- Extents are **framing** extents (actual lumber size). Finished faces (wrap, sheathing, ply) are their own members. Cut lists use the framing numbers; layout marks use the finished ones.
- Repeated members use `repeat:`; ids become `id[0]…`. Wildcards in connections are quoted: `"deck_joist[*]"`.
- Stringers are `kind: stringer`; their bbox is ignored and the true sloped profile is computed from `stair:`.
- Anything not stated in the drawings and guessed during encoding is marked `ASSUMED` in a `note:`. Resolve these with the user, don't silently keep them.
- `expected:` holds the values Rev T states. When a change legitimately moves one, update it deliberately — that's the audit trail.

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
- Inline design work, yaml edits, drawing updates, cut/materials lists: the session's default model is fine, because `verify.py` is the safety net.
- `drawing-auditor` is pinned to Fable: it runs rarely (per rev, pre-cut), and a miss costs lumber.
- `connection-checker` and `materials-pricer` run on Sonnet; the script does the arithmetic.

## Field measurements still owed

Assumed in the model until measured; anything depending on them is provisional:
- Ceiling joist nearest 50¾" from the bed wall (joists run parallel to it) — sets the screen top-plate fixing.
- Actual mattress thickness (`mattress.thickness`, assumed 6").
- Stud locations in the bed wall, window wall, and right wall — every ledger and the beam's left-end support depend on them.
- Tread stock thickness (`stair.tread_thickness`, assumed 1") — sets the stringer drop.

## Files

- `dimensions.yaml` — the model. Edit this.
- `verify.py` — the checker. Don't "fix" a failure by editing the checker.
- `drawings.py` — **generates** `loft-bed-drawings.html` from `dimensions.yaml` (`python3 drawings.py`). Every rect is a member projection; every schedule number is `verify.py`'s. Hand-written prose lives only in the NOTES block at the bottom. View conventions are stated on the sheet: plans bed-wall-up; y–z views bed-wall-left.
- `loft-bed-drawings.html` — the generated Rev U set. **Never hand-edit it**; change the yaml or `drawings.py` and regenerate. Rev T's hand-drawn set is in `archive/`.
- `tools/` — the SVG view helper (`svgview.py`) shared by `drawings.py`, plus the small landing sketches used during the Rev U decision.
- `audits/` — dated reports from the subagents. Read the latest before starting design work.
- `.claude/settings.json` — the verify hook. `/hooks` to inspect or disable.
