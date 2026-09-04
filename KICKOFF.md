I'm building a lofted bed for my son's room. The design is finalized; I need build documentation and help working through construction.

START HERE: `loft-bed-drawings.html` is the complete drawing set (Rev T) — 9 scale drawings plus a dimension schedule. Read it first. The schedule near the top is the controlling reference: every height and plan extent, derived once. Where anything disagrees with it, the schedule wins.

PROJECT SETUP I WANT:
1. Extract the dimension schedule into `dimensions.yaml` — every controlling dimension as data, including each member's full x/y/z extents. The extents matter: connection checking depends on them.
2. Write `verify.py` that recomputes the derived quantities from that data and asserts they match: clear spans, member overlaps, stringer geometry, the room depth chain. I want to re-run it after any change.
3. A CLAUDE.md capturing the working rules below.
4. Agents are already defined in `.claude/agents/` — read `AGENTS.md` for when to use them.

THEN, in this order:
- Materials list, generated from the dimension data
- Run `materials-pricer` on it
- Cut list, generated from the dimension data
- Run `connection-checker` and `drawing-auditor` before I cut anything

WORKING RULES (these came from painful experience):
- Never assert a geometric relationship from memory. Compute it.
- Distinguish framing from finished dimensions everywhere. Platform is 50¾" finished / 50" framed. Half-wall 5" finished / 3½" framed. Deck 107" finished / 106¼" structural rim.
- Errors cluster where two assemblies meet. Before claiming two members connect, verify their coordinate ranges overlap in all three axes.
- Several member depths are set by connection requirements, not by load. The nook header is a 2×10 at ~140 psi against ~900 allowable — it is that deep so the landing rim has something to hang from. Do not "optimise" these.
- Flag now-or-never decisions — things that get much harder after a prior step.
- Push back on me. The design improved every time you did.

FIELD MEASUREMENTS I STILL OWE YOU:
- Ceiling joist nearest 50¾" from the bed wall (joists run parallel to it) — sets the screen's top plate fixing
- Actual mattress thickness (schedule assumes 6")
- Stud locations in the bed wall and window wall

CONTEXT: Experienced builder, full tool access, flexible budget. Room is 131" × 186", 8' ceiling, second floor.
