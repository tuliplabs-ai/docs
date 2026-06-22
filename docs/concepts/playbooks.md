# Playbooks

A playbook is a **declarative execution plan** — an ordered list of
steps, each with a description, expected tools, hints, and validation
criteria. The `PlaybookEnforcer` checks that the agent runs the right
tools in the right order and reports any deviation.

If your agent isolates a host, files a case, or touches anything an
auditor will review, you want a playbook. The model still picks the
wording; the *side effects* follow the plan.

```python
from tulip.playbooks import Playbook, PlaybookStep
from tulip.playbooks.hook import PlaybookEnforcerHook

# NIST SP 800-61 detection & analysis phase, encoded as a runbook.
incident_triage = Playbook(
    id="incident-triage",
    name="Incident detection & analysis",
    steps=[
        PlaybookStep(
            id="gather_alerts",
            description="Pull the alert and correlated events from the SIEM.",
            expected_tools=["query_siem", "enrich_indicator"],
            hints=["Start with the most recent", "Prioritise HIGH severity first"],
            max_tool_calls=5,
        ),
        PlaybookStep(
            id="analyze_indicators",
            description="Group indicators by type, note first/last seen.",
            expected_tools=["lookup_hash", "enrich_indicator"],
        ),
        PlaybookStep(
            id="summarize_findings",
            description="Write a one-paragraph root-cause summary.",
            expected_tools=[],
        ),
    ],
    strict_sequence=True,
)

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[query_siem, enrich_indicator, lookup_hash],
    hooks=[PlaybookEnforcerHook(playbook=incident_triage)],
)
```

## When to reach for a playbook

| Situation | Playbook? |
|---|---|
| Regulated workflow (NIST 800-61 IR phases, evidence handling, host isolation) | **yes** |
| Multi-step process where order matters | **yes** |
| Repeatable runbook the team executes manually today | **yes — encode it** |
| Audit-trail requirement: "every containment follows the same sequence" | **yes — the execution log *is* the audit trail** |
| One-shot exploration, freeform Q&A | no — overhead's not worth it |
| You want the model to choose tools freely | no — that's what `Agent(tools=[...])` already gives you |

## Getting started

### 1. Build a `Playbook` in Python

A runnable NIST SP 800-61 IR flow — **detection → analysis →
containment** — wired to the real security toolset. Containment never
fires before the IOCs are enriched:

```python
from tulip.playbooks import Playbook, PlaybookStep

nist_ir = Playbook(
    id="nist-800-61-ir",
    name="NIST 800-61 incident response",
    description="Detect from the SIEM, analyze the IOCs, then contain.",
    steps=[
        PlaybookStep(
            id="detection",
            description="Pull the alert and its correlated events from the SIEM.",
            expected_tools=["query_siem"],
            hints=["Filter on the alert's src_ip", "Last hour first"],
            required=True,
        ),
        PlaybookStep(
            id="analysis",
            description="Enrich every IOC from detection; confirm it's malicious.",
            expected_tools=["enrich_indicator"],
            hints=["Do not contain on an unenriched indicator"],
            required=True,
        ),
        PlaybookStep(
            id="containment",
            description="Isolate the affected host from the network.",
            expected_tools=["isolate_host"],
            required=True,
        ),
    ],
    strict_sequence=True,
    allow_extra_tools=False,
)
```

`PlaybookStep` fields:

| Field | Meaning |
|---|---|
| `id` | Unique step identifier. |
| `description` | Human-readable; the agent sees this as a hint. |
| `expected_tools` | Tools the agent is supposed to call during this step. |
| `hints` | Extra steering text. |
| `required` | If `False`, the step can be skipped. |
| `max_tool_calls` | Hard cap on tool calls for this step. |
| `validation` | Optional dict of post-step checks. |

### 2. Load from YAML or JSON

For checked-in playbooks, use the loader:

```python
from tulip.playbooks import load_playbook

nist_ir = load_playbook("playbooks/nist_800_61_ir.yaml")
```

```yaml
# playbooks/nist_800_61_ir.yaml
id: nist-800-61-ir
name: NIST 800-61 incident response
description: Detect from the SIEM, analyze the IOCs, then contain.
strict_sequence: true
allow_extra_tools: false
steps:
  - id: detection
    description: Pull the alert and its correlated events from the SIEM.
    expected_tools: [query_siem]
  - id: analysis
    description: Enrich every IOC from detection; confirm it's malicious.
    expected_tools: [enrich_indicator]
  - id: containment
    description: Isolate the affected host from the network.
    expected_tools: [isolate_host]
```

### 3. Wire the enforcer

```python
from tulip.playbooks.hook import PlaybookEnforcerHook

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[query_siem, enrich_indicator, isolate_host],
    hooks=[PlaybookEnforcerHook(playbook=nist_ir)],
)

result = agent.run_sync("Triage alert ALT-7 (host WS-014) and contain if malicious.")
```

The hook injects step descriptions and hints into the agent's
context, validates each tool call against the current step's
`expected_tools`, and records the executions. The detection →
analysis → containment order is enforced: an `isolate_host` call
during the `detection` step is rejected, so the host can't be
contained before its IOCs are enriched.

## Strict vs lenient enforcement

| Setting | Effect |
|---|---|
| `strict_sequence=True` (default) | Steps must run in order; skipping ahead rejects the call. |
| `strict_sequence=False` | Steps can run in any order, but each must complete. |
| `allow_extra_tools=False` (default) | Only `expected_tools` may fire during a step. |
| `allow_extra_tools=True` | Any registered tool may fire — playbook is a recommendation, not a contract. |

For compliance-grade workflows, keep both at their defaults. For
"loose runbook" guidance, flip them.

## Inspecting execution

The enforcer maintains a `PlaybookPlan` — an audit-grade record of
every step's status, tool calls, and timestamps. Read it after the
run:

```python
plan = result.playbook_plan
for execution in plan.executions:
    print(f"{execution.step_id}: {execution.status.value} "
          f"({len(execution.tool_calls)} tool calls)")
```

`StepStatus` is one of `pending`, `in_progress`, `completed`,
`skipped`, `failed`.

## Common gotchas

| Symptom | Likely cause |
|---|---|
| Agent skips a step it shouldn't | The current step's `description` isn't specific enough — the model is interpreting the user's request as already satisfying the step. Sharpen the description. |
| Enforcer rejects a tool that *should* be allowed | The tool isn't in `expected_tools` for the current step. Add it, or set `allow_extra_tools=True` if the policy allows. |
| `max_tool_calls` exhausts mid-step | Bump the limit or split the step in two — the model may need search-and-refine cycles. |
| YAML loads but the agent doesn't follow it | Pass it through `PlaybookEnforcerHook(...)` — `Playbook` alone is just data. |

## Source and notebook

- [`notebook_46_playbooks.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_46_playbooks.py) — runnable end-to-end with execution tracking.
- [`tulip.playbooks`](https://github.com/tuliplabs-ai/sdk-python/tree/main/src/tulip/playbooks) — `Playbook`, `PlaybookStep`, `PlaybookEnforcerHook`, `load_playbook`.

## See also

- [Skills](skills.md) — the natural-language analogue: filesystem-first capability bundles.
- [Hooks](hooks.md) — `PlaybookEnforcerHook` is a normal hook; you can add it alongside guardrails / steering / telemetry.
- [Tools](tools.md) — playbook steps reference the tools you registered with `@tool`.
