# Agents — loft bed build

Three subagents live in `.claude/agents/`. They exist because this project's failure mode is self-review: the person producing a drawing shares the assumptions that made it wrong, so checking your own work finds nothing.

Since Rev T the mechanical checks live in `verify.py`, not in an agent. Every agent runs it first and spends its effort on what the script can't judge.

| Agent | Model | When | What it adds beyond `verify.py` |
|---|---|---|---|
| `drawing-auditor` | fable | After any change to drawings or dimension data. Always before cutting. | Is the yaml a faithful encoding of the drawings? Do captions, tables, SVG coordinates and the revisions log agree? Is anything unspecified that the builder will have to guess? |
| `connection-checker` | sonnet | Whenever a connection is added or changed. Before the cut list is final. | Connections the drawings claim but the yaml doesn't declare. Fastener reach through sheathing and into built-up members. Load paths end to end with rough reactions. |
| `materials-pricer` | sonnet | Once the materials list is settled. | Current pricing, part numbers for hardware, stock vs special-order. Never changes a depth. |

Save each report to `audits/<rev>-<agent>.md` so the next session starts from findings, not recollection.

## Do not use agents for

- **Design changes or geometry work.** These need the full model in context. A cold agent re-derives it badly — which is exactly how the errors happened. Change `dimensions.yaml` inline, let the hook run `verify.py`, then audit.
- **Producing the cut list or materials list.** Generate them inline from `dimensions.yaml`, then audit with a subagent.
- **Conversation with the builder.** Ask directly.

## Rules

- The agent that audits must never be the agent that produced. If a subagent drafted something, a different one checks it — or it gets checked inline against `dimensions.yaml`, never against recollection.
- **Never tell an auditor what to expect.** Its value is in not knowing. Give it the files and the question, not the answer.
- A FAIL from `verify.py` is not "known, ignore it" to an auditor — it's the baseline. The auditor's job is the next layer.
