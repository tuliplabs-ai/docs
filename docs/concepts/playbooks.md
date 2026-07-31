# Playbooks

A playbook is a **declarative execution plan** — an ordered list of
steps, each with a description, expected tools, hints, and validation
criteria. The `PlaybookEnforcer` checks that the agent runs the right
tools in the right order and reports any deviation.

If your agent issues refunds, rolls out changes, or isolates a host —
anything an auditor will review — you want a playbook. The model still
picks the wording; the *side effects* follow the plan.

```python
from tulip.playbooks import Playbook, PlaybookStep
from tulip.playbooks.hook import PlaybookEnforcerHook

# A refund-escalation runbook: verify, check eligibility, then pay out.
refund_escalation = Playbook(
    id="refund-escalation",
    name="Refund escalation",
    steps=[
        PlaybookStep(
            id="verify_order",
            description="Pull the order record and its payment history.",
            expected_tools=["lookup_order", "lookup_customer"],
            hints=["Start with the most recent charge", "Check for duplicates first"],
            max_tool_calls=5,
        ),
        PlaybookStep(
            id="check_eligibility",
            description="Check the refund against policy — window, amount cap, prior refunds.",
            expected_tools=["check_refund_policy"],
        ),
        PlaybookStep(
            id="issue_refund",
            description="Issue the refund and write a one-paragraph resolution note.",
            expected_tools=["issue_refund"],
        ),
    ],
    strict_sequence=True,
)

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[lookup_order, lookup_customer, check_refund_policy, issue_refund],
    hooks=[PlaybookEnforcerHook(playbook=refund_escalation)],
)
```

## When to reach for a playbook

| Situation | Playbook? |
|---|---|
| Regulated workflow (refund approval chains, change management, incident response) | **yes** |
| Multi-step process where order matters | **yes** |
| Repeatable runbook the team executes manually today | **yes — encode it** |
| Audit-trail requirement: "every refund follows the same sequence" | **yes — the enforcer's in-memory execution log captures the sequence** (persist it, or pair it with [`AuditTrail`](agentic-ai-security.md), for a durable record) |
| One-shot exploration, freeform Q&A | no — overhead's not worth it |
| You want the model to choose tools freely | no — that's what `Agent(tools=[...])` already gives you |

## Getting started

### 1. Build a `Playbook` in Python

The same shape carries a security-flavored example: a runnable
NIST SP 800-61 flow (the standard incident-response process) —
**detection → analysis → containment** — wired to a security toolset.
Detection pulls from the SIEM (a security team's log platform),
analysis enriches each IOC (indicator of compromise — a suspicious
hash, IP, or domain), and containment never fires before the IOCs
are enriched:

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

enforcer_hook = PlaybookEnforcerHook(playbook=nist_ir)
agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[query_siem, enrich_indicator, isolate_host],
    hooks=[enforcer_hook],
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

The enforcer maintains a `PlaybookPlan` — an in-memory record of
every step's status, tool calls, and counts. It lives on the hook's
`enforcer` (not on the result), so read it off the hook after the run:

```python
plan = enforcer_hook.enforcer.plan
for execution in plan.step_executions.values():
    print(f"{execution.step_id}: {execution.status.value} "
          f"({len(execution.tool_calls)} tool calls)")
```

`plan.step_executions` is a `dict[str, StepExecution]`; `StepStatus` is one of
`pending`, `in_progress`, `completed`, `skipped`, `failed`. The plan is an
ephemeral Pydantic object — serialize it (or wire an [`AuditTrail`](agentic-ai-security.md))
if you need a record that outlives the process.

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
