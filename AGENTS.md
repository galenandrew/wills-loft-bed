# Agents and skills — loft bed build

The loop itself is a skill: **`/design-change`** (`.claude/skills/design-change/`) —
which files to open for each kind of edit, the validation gates in order (hook →
`literals.py` → `python3 -m cad` → rev bump), and which auditor is cheap enough to be
worth running. Invoke it for any change to `dimensions.yaml`, `drawings/`, `content/`
or `cad/`; the agents below are its step 6.

Three subagents live in `.claude/agents/`. They exist because this project's failure mode is self-review: the person producing a drawing shares the assumptions that made it wrong, so checking your own work finds nothing.

Since Rev T the mechanical checks live in `verify.py`, not in an agent, and since the Rev U restructure the drawings are generated from the yaml, so SVG geometry cannot drift from it. Every agent runs the script first and spends its effort on what the script can't judge.

| Agent | Model | When | What it adds beyond `verify.py` and the build |
|---|---|---|---|
| `drawing-auditor` | opus | After any change to drawing modules, content, or the model. Always before cutting. | Is the yaml a faithful encoding of the design decisions? Do hand-typed numbers in labels, captions, tables and the revisions log agree with the model? Is each view drawing the right members? Is anything unspecified that the builder will have to guess? |
| `connection-checker` | sonnet | Whenever a connection is added or changed. Before the cut list is final. | Connections the drawings claim but the yaml doesn't declare. Fastener reach through sheathing and into built-up members. Load paths end to end with rough reactions. |
| `materials-pricer` | sonnet | Once the materials list is settled. | Current pricing, part numbers for hardware, stock vs special-order. Never changes a depth. |

Save each report to `audits/<rev>-<agent>.md` so the next session starts from findings, not recollection.

`python3 -m cad` is the fourth check and costs no tokens at all: it builds the whole bed
as real solids from the yaml and answers what boxes cannot — notched volume, bearing
areas, ray-cast fasteners, true sections. Run it before any of these agents, so they
audit a model the kernel already agrees with.

## Scope the auditor — this is where the tokens go

The build report names the figures that changed. Pass that list to `drawing-auditor` as its scope ("sheets 4 and 8 changed; audit those plus the schedule") and it reads only `drawings/d4_*.py`, `drawings/d8_*.py`, `site/figs/d4.svg`, `site/figs/d8a.svg`, `site/figs/d8b.svg`, the schedule in `site/appendix.html`, and the yaml. A full-set audit (every sheet, every content file) is for a new rev letter or the pre-cut check, not for a label move.

`python3 tools/literals.py d4 d8` gives an auditor the hand-typed numbers in those sheets with file:line — the only place drift can still enter.

## Do not use agents for

- **Design changes or geometry work.** These need the full model in context. A cold agent re-derives it badly — which is exactly how the errors happened. Change `dimensions.yaml` inline, let the hook run `verify.py` and the build, then audit.
- **Moving a label or editing a caption.** That's a 20–60 line module in `drawings/`; do it inline and read the build report.
- **Producing the cut list or materials list.** Generate them inline from `dimensions.yaml`, then audit with a subagent.
- **Conversation with the builder.** Ask directly.

## Rules

- The agent that audits must never be the agent that produced. If a subagent drafted something, a different one checks it — or it gets checked inline against `dimensions.yaml`, never against recollection.
- **Never tell an auditor what to expect.** Its value is in not knowing. Give it the files, the scope, and the question, not the answer.
- A FAIL from `verify.py` is not "known, ignore it" to an auditor — it's the baseline. The auditor's job is the next layer.
