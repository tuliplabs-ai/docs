---
hide:
  - navigation
  - toc
title: tulip agents — the open-source Python agent framework
description: Build Python agents with typed tools, memory, RAG, streaming, and eight multi-agent shapes behind one Agent class — and put a policy gate in front of the actions that change real systems.
---

<div class="tulip-hero" markdown>
<div class="tulip-hero__copy" markdown>

<p class="tulip-product-name"><span class="tpn-brand">tulip agents</span><span class="tpn-sep"> · </span><span class="tpn-tag">open-source Python agent framework</span></p>

# Build agents that <span class="accent">do real work.</span>

Typed tools, memory, RAG, streaming, and eight multi-agent shapes behind one
`Agent` class, on any OpenAI-compatible provider. And when an agent needs to
change a real system, the same runtime puts a policy gate in front of the
side effect.

<div class="tulip-hero__cta" markdown>
[Get started](how-to/quickstart.md){ .md-button .md-button--primary }
[See an example](notebooks/notebook_84_infra_deploy_gate.md){ .md-button }
</div>

```bash
python -m pip install "tulip-agents[openai]"
```

</div>

<div class="tulip-hero__code" markdown>

```python
from tulip import Agent, tool


@tool
def lookup_order(order_id: str) -> dict:
    """Look up one order."""
    return {"id": order_id, "status": "shipped"}


agent = Agent(
    model="{{ tulip_example_model }}",
    tools=[lookup_order],
    system_prompt="Answer order questions.",
)

result = agent.run_sync("Where is ORD-7842?")
print(result.message)
```

</div>
</div>

## Everything an agent needs, in one API

<div class="grid cards tulip-feature-cards" markdown>

- :material-function-variant:{ .lg .middle } **[Typed tools](concepts/tools.md)**

    ---
    Decorate a Python function with `@tool` and the signature becomes the
    schema. Mark one `idempotent=True` and identical calls dedupe.

- :material-database:{ .lg .middle } **[Memory, state, and RAG](concepts/rag.md)**

    ---
    Conversation memory, durable checkpoints you can resume after a crash,
    and vector-store adapters for retrieval.

- :material-radio-tower:{ .lg .middle } **[Typed event streaming](concepts/streaming.md)**

    ---
    One `run_context()` streams {{ tulip_event_count }} canonical events from every layer —
    agent, multi-agent, RAG, memory — and allocates nothing when unused.

- :material-graph-outline:{ .lg .middle } **[Eight multi-agent shapes](concepts/multi-agent.md)**

    ---
    Sequential, parallel, loop, orchestrator, swarm, handoff, state graph,
    and cross-process A2A. Same `Agent` class, same event stream.

- :material-cloud-outline:{ .lg .middle } **[Any provider](concepts/models.md)**

    ---
    OpenAI and Anthropic direct, plus OpenRouter, Together.ai, Bedrock, Azure,
    and self-hosted compatible endpoints, routed by model prefix.

- :material-brain:{ .lg .middle } **[Reasoning you can stop](concepts/reasoning.md)**

    ---
    Reflexion, grounding, and causal nodes in the loop — with a termination
    algebra that is real, testable Python.

</div>

## What makes it different: the agent has to earn the action

Anything can call a function. The hard part of shipping an agent is the moment
it stops suggesting and starts changing a system — a refund, a deploy, a
deletion. Tulip routes that call through
[`admit()`](concepts/control-layer.md), which runs it only on an allow
decision, can hold it for a named human, and records what happened in a
hash-chained [audit trail](concepts/observability.md). Separately,
[GSAR](concepts/gsar.md) scores whether the claim driving the action is
supported by evidence at all.

Pick a proposed action. Nothing below calls a model or touches a cluster —
the deploy is an in-memory simulation, so the whole thing runs offline.

<div class="action-demo" data-action-demo>
  <div class="action-demo__tabs" role="tablist" aria-label="Actions the agent proposed">
    <button type="button" role="tab" id="demo-tab-staging" aria-controls="demo-panel" data-demo-scenario="staging">Deploy to staging</button>
    <button type="button" role="tab" id="demo-tab-production" aria-controls="demo-panel" data-demo-scenario="production">Deploy to production</button>
    <button type="button" role="tab" id="demo-tab-prohibited" aria-controls="demo-panel" data-demo-scenario="prohibited">Deploy a prohibited change</button>
    <button type="button" role="tab" id="demo-tab-unsupported" aria-controls="demo-panel" data-demo-scenario="unsupported">Act on an unsupported claim</button>
  </div>
  <div class="action-demo__workspace">
    <div class="action-demo__code" aria-label="Python policy used by the demo">
      <div class="action-demo__bar"><span>control.py</span><span>tested example</span></div>
      <pre><code><span>policy = ControlPolicy(</span>
<span data-code-line="blast">    max_blast_radius=4,</span>
<span data-code-line="human">    require_human_for={"production"},</span>
<span data-code-line="deny">    deny_for={"prohibited"},</span>
<span>)</span>
<span></span>
<span data-code-line="ground">decision = decide(gsar_score(partition))</span>
<span>await admit(action, deploy,</span>
<span>            policy=policy, trail=trail)</span></code></pre>
    </div>
    <div class="action-demo__result" id="demo-panel" role="tabpanel" aria-labelledby="demo-tab-staging" aria-live="polite">
      <span class="action-demo__status" data-demo-status>✓ Allowed</span>
      <p data-demo-summary>The staging rollout passes policy and the simulated deploy function runs.</p>
      <dl>
        <dt>Evidence</dt><dd data-demo-evidence>CI passed · image checkout-api:1.8.2 · staging</dd>
        <dt>Decision returned</dt><dd><code data-demo-decision>allow</code></dd>
        <dt>Audit record</dt><dd data-demo-audit>deploy checkout-api · allow · policy checks passed</dd>
      </dl>
    </div>
  </div>
  <p class="action-demo__note">Deterministic offline simulation · no external operation is performed</p>
</div>

<div class="execution-flow" role="img" aria-label="Evidence is checked, a proposed action passes through policy and optional approval, the side effect is conditionally executed, and the decision is recorded">
  <div class="execution-flow__node"><strong>Evidence</strong><span>support or challenge claims</span></div>
  <div class="execution-flow__arrow" aria-hidden="true">→</div>
  <div class="execution-flow__node execution-flow__node--gate"><strong>Admission</strong><span>allow · hold · deny</span></div>
  <div class="execution-flow__arrow" aria-hidden="true">→</div>
  <div class="execution-flow__node"><strong>Action</strong><span>runs only when admitted</span></div>
  <div class="execution-flow__audit"><strong>Decision record</strong><span>evidence · policy · approval · result</span></div>
</div>

[Read the executable source](https://github.com/tuliplabs-ai/docs/blob/main/examples/homepage_control_demo.py)
of everything above.

## What the runtime enforces, and what you configure

The controls are specific rather than absolute, and it matters which is which.
`admit()` calls your function only after an allow decision and records that
decision when you supply a trail — but you classify the actions and route every
consequential path through the gate. Grounding applies your thresholds to a
judge's typed partition; claim extraction and judge reliability remain
judgment. Idempotency dedupes matching calls inside its documented scope, not
across differently shaped calls that mean the same real operation.

Read the [guarantees and boundaries](why-tulip.md) before putting Tulip behind
a high-stakes workflow.

## Build your first agent

Requires Python 3.11 or newer. This site was built and tested against
`tulip-agents` **{{ tulip_sdk_version }}**.

| Build | Start here |
|---|---|
| A first working agent | [Get started](how-to/quickstart.md) |
| A typed Python tool | [Add tools](concepts/tools.md) |
| A controlled side effect | [Control an action](how-to/first-controlled-action.md) |
| A paused workflow | [Request approval](concepts/interrupts.md) |
| Evidence-aware output | [Check evidence](concepts/gsar.md) |
| Durable work | [Persist and resume](how-to/persist-conversations.md) |
| Coordinated agents | [Compose multiple agents](concepts/multi-agent.md) |
| Another model host | [Model providers](concepts/models.md) |
| A run without credentials | [Offline examples](notebooks/index.md) |

[Get started](how-to/quickstart.md){ .md-button .md-button--primary }

## Limits and research

The [policy-blindness study](research/policy-blindness.md) reports where model
judges failed, separates row-weighted from deduplicated results, and preserves
the evaluated configuration. Research artifacts are evidence about those
experiments, not product guarantees.

---

Apache-2.0 · [Maintainers and project history](about.md) ·
[Compatibility policy](compatibility.md) ·
[Contribute](https://github.com/tuliplabs-ai/tulip-agents/blob/main/CONTRIBUTING.md)
