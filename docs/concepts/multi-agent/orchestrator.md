# Orchestrator + Specialists

One coordinator picks which specialist handles each sub-task. The
specialists never talk to each other — only to the orchestrator.
Think *project manager + team*.

![Orchestrator pattern — Coordinator at top, three Specialists below, parallel dispatch with results merging back](../../img/patterns/orchestrator.svg){ .diagram }

## What it is

The coordinator uses its `model` to pick which specialists handle a
task, then runs each selected specialist's full agent loop and
correlates the results. When the coordinator dispatches to multiple
specialists in one turn they run in parallel (bounded by
`max_parallel_specialists`).

Each `Specialist` is its own self-contained agent. Its fields:

- a `name` — what the coordinator calls it by
- a `specialist_type` — a short type tag (e.g. `"research"`)
- a `description` — what the specialist is good at (the coordinator reads this)
- a `system_prompt` — the specialist's own instructions
- its own `tools` and `model`
- an optional `confidence_threshold` (default `0.85`) — the bar the
  specialist's self-estimated confidence is measured against

## When to use it

- ✅ The work splits cleanly into **expert domains** (Research, Data,
  Writing; or Triage, Forensics, Containment).
- ✅ You want **one place to attribute decisions to** — the coordinator.
- ✅ Specialists need their **own playbooks, skills, or models** (a
  cheap model for triage, a strong one for compliance).
- ✅ **Auditability** matters — the dispatch log tells you who ran and
  why; for consequential actions, route the tool through
  [`admit()`](../security-context.md) so every decision lands on the
  hash-chained `AuditTrail`.

## When NOT to use it

- ❌ The flow is **linear, not delegated** — use [Composition](composition.md).
- ❌ No central coordinator should exist; agents should
  **self-organise** — use [Swarm](swarm.md).
- ❌ The conversation itself moves between roles — use [Handoff](handoff.md).

## Code

```python
from tulip.multiagent import Specialist, create_orchestrator

model = "anthropic:claude-sonnet-4-6"

research = Specialist(
    name="research",
    specialist_type="research",
    description="Searches sources. Collects evidence. Summarises what it found.",
    system_prompt="You are the Research specialist.",
    tools=[web_search, fetch_page],
)

data = Specialist(
    name="data",
    specialist_type="data",
    description="Queries the warehouse. Reconstructs timelines. Quantifies impact.",
    system_prompt="You are the Data specialist.",
    tools=[query_metrics, query_warehouse],
)

writing = Specialist(
    name="writing",
    specialist_type="writing",
    description="Drafts and publishes the report. Only after research + data agree.",
    system_prompt="You are the Writing specialist.",
    tools=[draft_report, publish_report],  # ← idempotent writes
)

orchestrator = create_orchestrator(
    name="coordinator",
    specialists=[research, data, writing],
    model=model,                           # the coordinator's routing model
)
orchestrator.system_prompt = (
    "You are the coordinator. Delegate source-gathering to research, "
    "metrics to data, and only after both report back call writing."
)

result = await orchestrator.execute(
    "Why did checkout conversion drop last week? Investigate and draft a report.",
)
```

`create_orchestrator` registers the specialists and propagates the
coordinator's `model` into any specialist that doesn't carry its own.
`execute()` is async — `await` it (or wrap in `asyncio.run`). The same
shape runs an incident commander: triage, forensics, and containment
specialists, with containment gated behind the other two.

## What runs in parallel

Specialists fire **concurrently** when the coordinator dispatches to
several of them in one turn. So when the coordinator says "in
parallel: research, pull the release notes for deploy-77; data, pull
last week's funnel metrics" — both specialists run at the same time and
their results merge back before the coordinator's next Think.

## Confidence thresholds

Each specialist carries a `confidence_threshold` (default `0.85`).
Every `SpecialistResult` reports a self-estimated `confidence`, so you
can compare it against the threshold and decide whether to trust the
output or route the sub-task to another expert:

```python
Specialist(
    name="data-quality",
    specialist_type="data_quality",
    description="Audits metric definitions and flags unreliable numbers.",
    system_prompt="You audit metrics before they are cited.",
    tools=[query_warehouse, profile_table],
    confidence_threshold=0.7,    # the bar this specialist's
                                 # self-estimated confidence is held to
)
```

## Notebooks

- [`notebook_26_orchestrator_pattern.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_26_orchestrator_pattern.py)
  — router + three parallel specialists, results merged.
- [`notebook_27_specialist_agents.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_27_specialist_agents.py)
  — confidence floors and per-specialist playbooks.
- [`notebook_64_procurement_approval.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_64_procurement_approval.py)
  — vendor security review with risk-tiered approval gates and a typed
  `VendorDecision` artifact.

## Source

[`multiagent/orchestrator.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/multiagent/orchestrator.py)
— `Orchestrator`, `Specialist`.

## See also

- [Multi-agent overview](../multi-agent.md) — pick a shape.
- [Handoff](handoff.md) — when the conversation itself transfers, not just sub-tasks.
- [Playbooks](../playbooks.md) — declarative step plans per specialist.
