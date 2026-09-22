---
hide:
  - navigation
  - toc
title: Tulip Agents — controlled, evidence-backed actions
description: Build Python agents that check evidence, apply policy before consequential actions, and leave an inspectable decision record.
---

<div class="tulip-hero" markdown>
<div class="tulip-hero__copy" markdown>

<p class="tulip-product-name"><span class="tpn-brand">tulip agents</span><span class="tpn-sep"> · </span><span class="tpn-tag">open-source Python agent framework</span></p>

# Build agents that take <span class="accent">controlled, evidence-backed actions.</span>

Tulip helps Python agents move from suggesting work to changing systems.
Check claims against evidence, apply policy before a consequential action runs,
and inspect the decision record afterward.

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
await admit(
    action,
    deploy,
    policy=deployment_policy,
    trail=audit_trail,
)
```

```text
staging       ✓ allow          deploy runs
production    … require_human  waits
prohibited    × deny           stops
unsupported   ↺ replan         revise claim
```

</div>
</div>

## One proposal. Four inspectable outcomes.

Choose a scenario. The demo uses Tulip's real policy and grounding decisions;
the deployment itself is an in-memory simulation, so it runs without a model,
credentials, or a cluster.

<div class="action-demo" data-action-demo>
  <div class="action-demo__tabs" role="tablist" aria-label="Deployment scenarios">
    <button type="button" role="tab" data-demo-scenario="staging">Staging</button>
    <button type="button" role="tab" data-demo-scenario="production">Production</button>
    <button type="button" role="tab" data-demo-scenario="prohibited">Prohibited</button>
    <button type="button" role="tab" data-demo-scenario="unsupported">Unsupported diagnosis</button>
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
    <div class="action-demo__result" aria-live="polite">
      <span class="action-demo__status" data-demo-status>✓ Executes</span>
      <p data-demo-summary>The staging rollout passes policy and the simulated deploy function runs.</p>
      <dl>
        <dt>Evidence</dt><dd data-demo-evidence>CI passed · image checkout-api:1.8.2 · staging</dd>
        <dt>Decision</dt><dd><code data-demo-decision>allow</code></dd>
        <dt>Audit record</dt><dd data-demo-audit>deploy checkout-api · allow · policy checks passed</dd>
      </dl>
    </div>
  </div>
  <p class="action-demo__note">Deterministic offline simulation · no external operation is performed</p>
</div>

[Open the executable source](https://github.com/tuliplabs-ai/docs/blob/main/examples/homepage_control_demo.py)
or [run the infrastructure example](notebooks/notebook_84_infra_deploy_gate.md).

## Believe the conclusion. Control the action. Explain the run.

<div class="grid cards tulip-feature-cards" markdown>

- :material-shield-search:{ .lg .middle } **[Check evidence](concepts/gsar.md)**

    ---
    Partition claims by evidence support. A configured judge can trigger
    revision, replanning, or abstention; its assessment is not proof of truth.

- :material-shield-lock:{ .lg .middle } **[Control execution](concepts/control-layer.md)**

    ---
    Calls routed through `admit()` run only after an allow decision. Your
    application defines the labels, policy, and controlled paths.

- :material-eye:{ .lg .middle } **[Inspect decisions](concepts/observability.md)**

    ---
    Record evidence, policy outcome, approval, and result. A hash-chained
    `AuditTrail` detects later changes; durable storage remains your job.

</div>

## One workflow, end to end

<div class="execution-flow" role="img" aria-label="Evidence is checked, a proposed action passes through policy and optional approval, the side effect is conditionally executed, and the decision is recorded">
  <div class="execution-flow__node"><strong>Evidence</strong><span>support or challenge claims</span></div>
  <div class="execution-flow__arrow" aria-hidden="true">→</div>
  <div class="execution-flow__node execution-flow__node--gate"><strong>Admission</strong><span>allow · hold · deny</span></div>
  <div class="execution-flow__arrow" aria-hidden="true">→</div>
  <div class="execution-flow__node"><strong>Action</strong><span>runs only when admitted</span></div>
  <div class="execution-flow__audit"><strong>Decision record</strong><span>evidence · policy · approval · result</span></div>
</div>

The same pattern fits refunds, infrastructure, support operations, security,
and internal workflows. Start with the [offline deployment gate](notebooks/notebook_84_infra_deploy_gate.md),
then read the [runtime architecture](concepts/control-layer.md).

## A full agent framework behind the control path

Use one `Agent` API for typed tools, streaming, durable state, RAG, structured
output, and multi-agent workflows. Run models through OpenAI, Anthropic,
OpenRouter, Together.ai, Amazon Bedrock, Azure OpenAI, or maintained
OpenAI-compatible routes.

| Build | Start here |
|---|---|
| A first working agent | [Create an agent](how-to/quickstart.md) |
| A typed Python tool | [Add tools](concepts/tools.md) |
| A controlled side effect | [Control an action](how-to/first-controlled-action.md) |
| A paused workflow | [Request approval](concepts/interrupts.md) |
| Evidence-aware output | [Check evidence](concepts/gsar.md) |
| Durable work | [Persist and resume](how-to/persist-conversations.md) |
| Coordinated agents | [Compose multiple agents](concepts/multi-agent.md) |
| Another model host | [Model providers](concepts/models.md) |

## Evidence, boundaries, and research

Tulip's controls are specific rather than absolute. Admission protects action
paths routed through the gate. Grounding depends on supplied evidence and judge
quality. Idempotency deduplicates matching calls only within its documented
scope. See [guarantees and boundaries](why-tulip.md) before using Tulip for a
high-stakes workflow.

The [policy-blindness study](research/policy-blindness.md) reports where model
judges failed, distinguishes row-weighted from deduplicated results, and
preserves the evaluated configuration. Research artifacts are evidence about
those experiments, not product guarantees.

## Start building

Requires Python 3.11 or newer. This site was built and tested against
`tulip-agents` **{{ tulip_sdk_version }}**.

```bash
python -m pip install "tulip-agents[openai]"
```

[Get started →](how-to/quickstart.md){ .md-button .md-button--primary }
[Browse examples →](notebooks/index.md){ .md-button }

---

Apache-2.0 · [Maintainers and project history](about.md) ·
[Compatibility policy](compatibility.md) ·
[Contribute](https://github.com/tuliplabs-ai/tulip-agents/blob/main/CONTRIBUTING.md)
