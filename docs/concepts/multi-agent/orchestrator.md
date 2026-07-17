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
- a `specialist_type` — a short type tag (e.g. `"forensics"`)
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
- ✅ **Auditability** matters — the dispatch log is your trail.

## When NOT to use it

- ❌ The flow is **linear, not delegated** — use [Composition](composition.md).
- ❌ No central coordinator should exist; agents should
  **self-organise** — use [Swarm](swarm.md).
- ❌ The conversation itself moves between roles — use [Handoff](handoff.md).

## Code

```python
from tulip.multiagent import Specialist, create_orchestrator

model = "anthropic:claude-sonnet-4-6"

triage = Specialist(
    name="triage",
    specialist_type="triage",
    description="Reads the alerts. Enriches indicators. Scores severity.",
    system_prompt="You are the Triage specialist.",
    tools=[fetch_alerts, enrich_ioc],
)

forensics = Specialist(
    name="forensics",
    specialist_type="forensics",
    description="Reconstructs the host timeline. Confirms compromise. Flags blast radius.",
    system_prompt="You are the Forensics specialist.",
    tools=[pull_edr_timeline, scan_host, search_iocs],
)

containment = Specialist(
    name="containment",
    specialist_type="containment",
    description="Isolates hosts and pages the on-call. Only after triage + forensics agree.",
    system_prompt="You are the Containment specialist.",
    tools=[isolate_host, page_oncall],     # ← idempotent writes
)

orchestrator = create_orchestrator(
    name="incident commander",
    specialists=[triage, forensics, containment],
    model=model,                           # the coordinator's routing model
)
orchestrator.system_prompt = (
    "You are the incident commander. Delegate enrichment to triage, "
    "host analysis to forensics, and only after both confirm call containment."
)

result = await orchestrator.execute(
    "Sev-1: ransomware detected on ws-0042. Investigate, contain, and recommend remediation.",
)
```

`create_orchestrator` registers the specialists and propagates the
coordinator's `model` into any specialist that doesn't carry its own.
`execute()` is async — `await` it (or wrap in `asyncio.run`).

## What runs in parallel

Specialists fire **concurrently** when the coordinator dispatches to
several of them in one turn. So when the coordinator says "in
parallel: triage, enrich the indicators on ws-0042; forensics, pull
the host's EDR timeline" — both specialists run at the same time and
their results merge back before the coordinator's next Think.

## Confidence thresholds

Each specialist carries a `confidence_threshold` (default `0.85`).
Every `SpecialistResult` reports a self-estimated `confidence`, so you
can compare it against the threshold and decide whether to trust the
output or route the sub-task to another expert:

```python
Specialist(
    name="malware-rev",
    specialist_type="malware_analysis",
    description="Reverse-engineers suspicious binaries and flags capabilities.",
    system_prompt="You reverse-engineer suspicious binaries.",
    tools=[disassemble, sandbox_detonate],
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
