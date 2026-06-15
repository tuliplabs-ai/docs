# Orchestrator + Specialists

One coordinator picks which specialist handles each sub-task. The
specialists never talk to each other — only to the orchestrator.
Think *project manager + team*.

![Orchestrator pattern — Coordinator at top, three Specialists below, parallel dispatch with results merging back](../../img/patterns/orchestrator.svg){ .diagram }

## What it is

The coordinator is a regular `Agent` whose tool-set is **the
specialists**. Calling a specialist runs that specialist's full
agent loop and returns the answer. When the coordinator dispatches
to multiple specialists in one turn they run in parallel.

Each `Specialist` has:

- a `name` — what the coordinator calls it by
- an `agent` — the specialist's own `Agent` (its own model, tools, system prompt)
- a `description` — what the specialist is good at (the coordinator reads this)
- an optional `confidence_floor` — below this the specialist declines

## When to use it

- ✅ The work splits cleanly into **expert domains** (Triage,
  Containment, Forensics; or Recon, Exploit-check, Reporting).
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
from tulip.multiagent import Orchestrator, Specialist

triage = Specialist(
    name="triage",
    agent=Agent(
        model="anthropic:claude-sonnet-4-6",
        tools=[fetch_alerts, enrich_ioc],
        system_prompt="You are the Triage specialist.",
    ),
    description="Reads the alerts. Enriches indicators. Scores severity.",
)

forensics = Specialist(
    name="forensics",
    agent=Agent(
        model="anthropic:claude-sonnet-4-6",
        tools=[pull_edr_timeline, scan_host, search_iocs],
        system_prompt="You are the Forensics specialist.",
    ),
    description="Reconstructs the host timeline. Confirms compromise. Flags blast radius.",
)

containment = Specialist(
    name="containment",
    agent=Agent(
        model="anthropic:claude-sonnet-4-6",
        tools=[isolate_host, page_oncall],     # ← idempotent writes
        system_prompt="You are the Containment specialist.",
    ),
    description="Isolates hosts and pages the on-call. Only after triage + forensics agree.",
)

orchestrator = Orchestrator(
    coordinator_model="anthropic:claude-sonnet-4-6",
    specialists=[triage, forensics, containment],
    system_prompt=(
        "You are the incident commander. Delegate enrichment to triage, "
        "host analysis to forensics, and only after both confirm call containment."
    ),
)

result = orchestrator.run_sync(
    "Sev-1: ransomware detected on ws-0042. Investigate, contain, and recommend remediation.",
    thread_id="inc-2026-0042",
)
```

## What runs in parallel

Specialists fire **concurrently** when the coordinator dispatches to
several of them in one turn. So when the coordinator says "in
parallel: triage, enrich the indicators on ws-0042; forensics, pull
the host's EDR timeline" — both specialists run at the same time and
their results merge back before the coordinator's next Think.

## Confidence floors

A specialist can **decline** with low confidence. The coordinator
sees the decline and tries another expert (or asks the user):

```python
Specialist(
    name="malware-rev",
    agent=malware_agent,
    description="Reverse-engineers suspicious binaries and flags capabilities.",
    confidence_floor=0.7,    # below 0.7 the specialist returns
                             # ("decline", reason) and the coordinator
                             # routes elsewhere
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
