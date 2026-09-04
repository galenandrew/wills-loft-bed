# Agents — loft bed build

Three subagents live in `.claude/agents/`. They exist because this project's failure mode is self-review: the person producing a drawing shares the assumptions that made it wrong, so checking your own work finds nothing.

| Agent | When | Why a subagent |
|---|---|---|
| `drawing-auditor` | After any change to drawings or dimension data. Always before cutting. | Value is in *not* knowing the intended answer. Never tell it what to expect. |
| `connection-checker` | Whenever a connection is added or changed. Before the cut list is final. | Narrow, mechanical, high-yield — every past error was a connection asserted without checking overlap. |
| `materials-pricer` | Once the materials list is settled. | Independent research; doesn't need design context. |

## Do not use agents for

- **Design changes or geometry work.** These need the full model in context. A cold agent re-derives it badly — which is exactly how the errors happened.
- **Producing the cut list.** Generate it inline from `dimensions.yaml`, then audit it with a subagent.
- **Conversation with the builder.** Ask directly.

## Rule

The agent that audits must never be the agent that produced. If a subagent drafted something, a different one checks it — or it gets checked inline against `dimensions.yaml`, never against recollection.
