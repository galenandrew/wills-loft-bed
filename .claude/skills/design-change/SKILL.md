---
name: design-change
description: The loop for changing the loft bed design — member dimensions or positions, connections, fasteners, stair/nook geometry, the CAD solids, or a drawing label, caption or prose. Use for any edit to dimensions.yaml, drawings/, content/, or cad/. Encodes the validation gates (verify.py, the build report, the kernel, the rev bump) and the read budget that keeps a change cheap without letting an error drift in.
---

# Making a design or drawing change

`dimensions.yaml` is the model. `site/` and `cad-out/` are renderings of it. The
checks are **scripts, not judgement** — they cost no tokens, so run them every time
and never skip one to save effort. What you *read* is the expensive part; that is
where to be frugal.

## 1 · Pick the lane, and read only its files

| Change | Edit | Read first (nothing else) |
|---|---|---|
| Member size / position, new member | `dimensions.yaml` | the member's rows + every `connections:` row naming it (`grep -n '<id>' dimensions.yaml`) |
| Connection, fastener, `through:` | `dimensions.yaml` | that connection row + both members' rows |
| Stair, nook, room, `expected:` | `dimensions.yaml` | the `stair:`/`nook:`/`expected:` block |
| A label, dimension line, what a view draws | `drawings/d<N>_*.py` | that module (20–60 lines); `drawings/model.py`'s header only if you need a helper |
| Caption | the sheet module's `CAPTION` | that module |
| Prose (structure, open items, conventions, revisions) | `content/*` | that one file |
| A number quoted in prose | `content/*` — use `{m:<id>.size.x}` / `{m:<id>.z0}`, never a typed digit | the member's yaml rows |
| Which page a sheet sits on | `drawings/site.py` `PAGE_SHEETS` | that dict |
| Solids: laminations, notches, scope, fastener rays | `cad/model.py`, `cad/__main__.py` | the `SCOPE` / `LAMINATIONS` / `NOTCHED` / `FASTENERS` table you are changing |

Do **not** open `site/*.html`, a `--single` file, `verify.py`, or the whole yaml to
make a change. Never hand-edit `site/` or `cad-out/` — both are overwritten.

Geometry and design work happens **inline**, with the model in context. Subagents
audit; they do not design (`AGENTS.md`).

## 2 · Let the hook validate

The PostToolUse hook runs `verify.py` (on yaml/verify edits) and `build.py` (on
yaml, `drawings/`, `content/`, `cad/` edits) and injects the result.

- **A FAIL comes back to you.** Fix the model, or state to the user why the FAIL is
  accepted. Never edit `verify.py` to make a failure go away, and never lower an
  `expected:` value to match a mistake.
- **Read the build report, not the site.** It names the figures that changed and the
  labels that moved. Open only `site/figs/<key>.svg` for those keys — 6–10 KB each —
  or screenshot them. If the report says nothing changed, look at nothing.
- A figure that changed when you did not expect it to is a finding, not noise.
- If you ran the scripts by hand instead: `python3 verify.py --quiet` then
  `python3 build.py --quiet`.

## 3 · Chase the numbers the scripts cannot see

Hand-typed numbers in labels, captions and prose are the only place drift still
enters. For every sheet the build report named:

```
python3 tools/literals.py d4 d8        # file:line for every hand-typed number
```

Check those lines against the model, and convert any that is a **dimension** into a
`{m:...}` reference so it cannot drift again. What legitimately stays literal: nominal
stock and hardware names, stated design constants, historical parentheticals, and the
hand-computed load figures (psi, lb, psf, deflection) — nothing in the model derives
those, so re-check them by hand whenever a member they depend on moves.

This is cheap and mandatory — do not skip it
because the change "was only geometry"; geometry is exactly what the labels state.

## 4 · Run the kernel when solids moved

```
python3 -m cad          # ~2.5 s, rewrites the tracked files in cad-out/
```

Required when: a member's extents changed, a joint or notch changed, `cad/` changed,
or you are about to cut material. It answers what boxes cannot — real notched volume,
bearing areas, what a screw actually passes through, true sections — and it is what
caught the Rev W joinery error. Read `cad-out/loft.txt` and `cad-out/clash.txt` only
if the run flags something. Not needed for a label, caption or prose edit.

`cad-out/`'s tracked files carry no timings, so they change only when the model does:
**a dirty `cad-out/` in `git status` means the kernel has not been re-run since the
geometry moved.** Check it before you call a change done.

## 5 · Record it

Every design change (not a drawing-only cleanup):

1. Bump `rev:` in `dimensions.yaml` — one letter per design change, `.1` for a
   drawing-only fix.
2. Add a row at the **top** of `content/revisions.json` saying what changed and why.
3. Update `expected:` deliberately when a change legitimately moves one — that is the
   audit trail, not a nuisance.
4. Update the cut list / materials list to match, once they exist.
5. Resolve any `ASSUMED` note you touched with the user rather than leaving it.

## 6 · Audit — the right agent, or none

Cheapest sufficient check, in order:

- **Label, caption, prose, page move** → no agent. Build report + `literals.py`.
- **A connection or fastener changed** → `connection-checker` (sonnet). Name the
  connections in scope.
- **New rev letter, or before cutting material** → `drawing-auditor` (opus), scoped to
  the sheets the build report named: *"sheets 4 and 8 changed; audit those plus the
  schedule."* A full-set audit is for pre-cut only. Never tell an auditor what to
  expect — its value is in not knowing.
- **Materials list settled** → `materials-pricer` (sonnet).

Save each report to `audits/<rev>-<agent>.md`.

## Before cutting material — all four

`verify.py` 0 FAIL · `python3 -m cad` clean · `drawing-auditor` full set ·
`connection-checker` on every connection.

## Traps

- Never assert a geometric relationship from memory. Compute it, or it is not verified.
- Framing vs finished: platform 50¾ finished / 50 framed, half-wall 5 / 3½, deck 107 / 106¼.
- Some depths exist for a connection, not a load (the nook header's 7½" for the landing
  rim). Re-run that connection before slimming any member.
- The yaml's axes are left-handed as they map onto the room. Do not "fix" a drawing's
  mirroring; `cad/export.py:to_room_frame()` handles it for STEP/STL only.
- Never commit unprompted. Say what changed and stop.
