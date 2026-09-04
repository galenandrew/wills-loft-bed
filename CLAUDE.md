# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Not a software project. This is the build documentation for a lofted bed for the user's son (design finalized), built for a room 131" × 186", 8' ceiling, second floor. The user is an experienced builder with full tool access and a flexible budget. The deliverables are drawings, a dimension model, a verification script, and materials/cut lists — read `KICKOFF.md` for the full project brief and `AGENTS.md` for when to use the subagents in `.claude/agents/`.

## Current state / setup still to do

`KICKOFF.md` defines a project setup that has not yet been built out. In order:

1. Extract the dimension schedule from `loft-bed-drawings.html` into `dimensions.yaml` — every controlling dimension as data, including each member's full x/y/z extents (needed for connection checking).
2. Write `verify.py` to recompute derived quantities from `dimensions.yaml` and assert they match: clear spans, member overlaps, stringer geometry, the room depth chain. Re-run after any change to the dimensions.
3. Generate a materials list from the dimension data, then run the `materials-pricer` agent on it.
4. Generate a cut list from the dimension data, then run `connection-checker` and `drawing-auditor` before anything is cut.

If `dimensions.yaml` and `verify.py` exist when you read this, they are the source of truth going forward — treat this section as historical and update it to describe the current pipeline instead.

## The controlling reference

`loft-bed-drawings.html` (currently Rev T) is the complete drawing set: 9 scale SVG drawings plus a dimension schedule (`Dimension schedule — the controlling reference`, around line 91). The schedule is the single source every height and plan extent is derived from once. **Where any drawing, caption, or note disagrees with the schedule, the schedule wins.** Once `dimensions.yaml` exists, it supersedes the HTML schedule as the actual source of truth — the HTML should be regenerated from it, not hand-edited to match.

The schedule is organized as:
- A · Vertical datums
- B · Stair heights
- C · Plan — x, from the window wall
- D · Plan — y, out from the bed wall
- E · Derived — do not measure these independently

Section E matters: those values are computed from A–D, not independent measurements. `verify.py` exists to make that computation auditable instead of manual.

Check the `Revisions` table at the bottom of the HTML before trusting any specific number — it documents exactly which past values were wrong and why, which is useful context for the kind of error this project tends to produce (see Working rules below).

## Working rules (hard-won, do not relitigate)

- **Never assert a geometric relationship from memory. Compute it.** This is the project's single most common failure mode — see the agent rationale in `AGENTS.md`.
- **Distinguish framing from finished dimensions everywhere.** Example pairs already established: platform 50¾" finished / 50" framed; half-wall 5" finished / 3½" framed; deck 107" finished / 106¼" structural rim.
- **Errors cluster where two assemblies meet.** Before claiming two members connect, verify their coordinate ranges overlap in all three axes — this is exactly what the `connection-checker` agent automates.
- **Some member depths are set by connection requirements, not load.** E.g. the nook header is a 2×10 at ~140 psi against ~900 allowable — oversized so the landing rim has something to hang from. Do not "optimize" these down to a load-only size.
- **Flag now-or-never decisions** — anything that gets much harder after a prior construction step — as soon as they're visible, not after the fact.
- **Push back on the user.** The design has improved every time a past session did.

## Outstanding field measurements

These are assumed in the current schedule and owed by the user before final cut:
- Ceiling joist location nearest 50¾" from the bed wall (joists run parallel to it) — sets the screen's top-plate fixing.
- Actual mattress thickness (schedule currently assumes 6").
- Stud locations in the bed wall and window wall.

Treat any drawing output depending on these as provisional until confirmed.

## Subagents (`.claude/agents/`)

Three subagents exist because self-review doesn't catch this project's errors — whoever produces a drawing shares the assumptions that made it wrong. Full detail in `AGENTS.md`; summary:

| Agent | When |
|---|---|
| `drawing-auditor` | After any change to drawings or dimension data; always before cutting. Read-only, never told what to expect. |
| `connection-checker` | Whenever a structural connection is added or changed; before the cut list is final. Verifies real x/y/z overlap, not prose claims. |
| `materials-pricer` | Once the materials list is settled. Independent web research, doesn't need design context. |

**Do not use agents for:** design/geometry changes (need full context, a cold agent re-derives it badly), producing the cut list (generate inline from `dimensions.yaml`, then audit with a subagent), or conversation with the builder (ask directly).

**Rule:** the agent that audits must never be the agent that produced the artifact. A subagent's draft gets checked by a *different* agent, or checked inline against `dimensions.yaml` — never against recollection.

## Working with `loft-bed-drawings.html`

It's a single self-contained HTML file with inline SVG drawings and CSS — no build step, no dependencies. Open directly in a browser to view. When editing:
- Update the dimension schedule (or `dimensions.yaml` once it exists) first, then propagate to prose/captions/SVG — the Revisions log shows this project's recurring bug is a value updated in one place and not the others.
- Add a new row to the `Revisions` table at the bottom describing what changed and why, following the existing terse style (see Rev T/S/S.1 entries for the level of detail expected).
- Bump the `REV` letter shown in the header (line ~67).
