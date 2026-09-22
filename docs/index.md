---
hide:
  - navigation
  - toc
title: Tulip agents — policy-controlled AI agents
description: Build AI agents whose consequential actions pass through a policy gate, can wait for human approval, and leave a verifiable decision record.
---

<div class="tulip-hero" markdown>
<div class="tulip-hero__copy" markdown>

<p class="tulip-product-name"><span class="tpn-brand">tulip agents</span><span class="tpn-sep"> · </span><span class="tpn-tag">the agent framework where control is native</span></p>

# Agents that act. <span class="accent">Policy before execution.</span>

Build open-source AI agents with tools, memory, RAG, streaming, and multi-agent
workflows. Route consequential actions through a policy gate that can allow,
hold, or deny them before their side effects run.

<div class="tulip-hero__cta" markdown>
[Run your first agent](how-to/quickstart.md){ .md-button .md-button--primary }
[See a controlled action](how-to/first-controlled-action.md){ .md-button }
</div>

```bash
pip install "tulip-agents[openai]"
```

</div>

<div class="tulip-hero__code" markdown>

```python
policy = ControlPolicy(
    require_verification_score=0,
    max_blast_radius=1,
    require_human_for={"high_value"},
    deny_for={"prohibited"},
)

await admit(action, issue_refund,
            policy=policy, trail=trail)
```

```text
$12.50 refund    → ALLOW → paid
$4,000 refund    → HOLD  → not run
prohibited call  → DENY  → not run

audit trail: 3 decisions · chain valid
```

</div>
</div>

## See control happen

The model proposes an action. Your application classifies it as an `Action`.
The runtime evaluates that action against your `ControlPolicy` before invoking
the function that produces the side effect.

<div class="execution-flow" role="img" aria-label="An agent proposes an action, the policy gate allows, holds, or denies it, and every decision is recorded in the audit trail">
  <div class="execution-flow__node"><strong>Agent</strong><span>proposes an action</span></div>
  <div class="execution-flow__arrow" aria-hidden="true">→</div>
  <div class="execution-flow__node execution-flow__node--gate"><strong>Policy gate</strong><span>evaluates declared labels</span></div>
  <div class="execution-flow__arrow" aria-hidden="true">→</div>
  <div class="execution-flow__outcomes">
    <span class="flow-allow">allow · run</span>
    <span class="flow-hold">hold · wait</span>
    <span class="flow-deny">deny · stop</span>
  </div>
  <div class="execution-flow__audit"><strong>Audit trail</strong><span>records every decision</span></div>
</div>

[Run the complete offline refund example →](notebooks/notebook_83_payment_refund_gate.md)

## Three controls, with different boundaries

<div class="grid cards tulip-feature-cards" markdown>

- :material-shield-lock:{ .lg .middle } **[Control execution](concepts/control-layer.md)**

    ---
    Calls routed through `admit()` run only on an `allow` decision. You define
    the policy and must route every consequential path through the gate.

- :material-shield-search:{ .lg .middle } **[Check evidence](concepts/gsar.md)**

    ---
    GSAR partitions claims and scores their evidence. A configured judge can
    support revision, replanning, or abstention; its assessment is not proof
    that a claim is true.

- :material-eye:{ .lg .middle } **[Inspect decisions](concepts/observability.md)**

    ---
    Admission decisions can be written to a hash-chained `AuditTrail`.
    `verify()` detects changes to that chain; durable storage is your
    deployment responsibility.

</div>

## What Tulip includes

One `Agent` API covers tools, durable state, RAG, typed event streaming,
provider-neutral models, and eight coordination shapes. These framework
features are useful on their own; the control layer is explicit and opt-in so
you can see exactly which actions it protects.

| Need | Start here |
|---|---|
| A first working agent | [Five-minute first agent](how-to/quickstart.md) |
| Allow, hold, and deny an action | [First controlled action](how-to/first-controlled-action.md) |
| Understand the runtime | [Architecture](concepts/control-layer.md) |
| Run without credentials | [Offline examples](notebooks/index.md) |
| Build a multi-agent workflow | [Coordination patterns](concepts/multi-agent.md) |
| Evaluate the evidence | [GSAR grounding](concepts/gsar.md) |

## What is enforced—and what you configure

| Layer | Runtime does | You must do | Still judgment-dependent |
|---|---|---|---|
| Admission | Calls `perform` only after `allow`; records a decision when a trail is supplied | Classify actions accurately, cover every side-effecting path, configure policy and durable approvals | Whether your labels and rules cover the real-world risk |
| Grounding | Applies configured scoring and thresholds to a judge's typed partition | Enable GSAR, supply evidence, choose thresholds and failure behavior | Claim extraction, evidence classification, and judge reliability |
| Idempotency | Deduplicates identical tool calls in its documented run/checkpoint scope | Mark tools, preserve checkpoints, and use downstream idempotency keys | Whether two differently shaped calls mean the same real-world operation |

Read the [guarantees and boundaries](why-tulip.md) before using Tulip for a
high-stakes workflow.

## Selected workflows

| Workflow | Execution mode | What it demonstrates |
|---|---|---|
| [Payment refund gate](notebooks/notebook_83_payment_refund_gate.md) | Offline simulation | A small refund proceeds and a large refund waits |
| [Infrastructure deploy gate](notebooks/notebook_84_infra_deploy_gate.md) | Offline simulation | Staging proceeds while production requires a person |
| [Data deletion gate](notebooks/notebook_86_data_deletion_gate.md) | Offline simulation | Export and erasure receive different policy outcomes |
| [Policy-blindness research](research/policy-blindness.md) | Reproducible evaluation | Why a sound gate still depends on complete classification |

## Start building

Requires Python 3.11 or newer. The current documentation targets
`tulip-agents` 2.15.x.

```bash
python -m pip install "tulip-agents[openai]>=2.15,<2.16"
```

[Run your first agent →](how-to/quickstart.md){ .md-button .md-button--primary }
[Browse examples →](notebooks/index.md){ .md-button }

---

Apache-2.0 · [Maintainers and project history](about.md) ·
[Compatibility policy](compatibility.md)
