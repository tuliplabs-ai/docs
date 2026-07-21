---
hide:
  - navigation
  - toc
---

<div class="tulip-hero" markdown>
<div class="tulip-hero__copy" markdown>

<p class="tulip-product-name"><span class="tpn-brand">tulip agents</span><span class="tpn-sep"> · </span>the safest way to build agentic AI</p>

# Agents that act. <span class="accent">Safe by construction.</span>

Tulip is an open-source **agentic harness** — the control runtime for agents that act. **Build** agents that are safe by construction, or **govern** [the ones you already run](integrations/frameworks.md) in LangChain, CrewAI, or the OpenAI Agents SDK.

Three control points, all in code the model can't reach: the **[cognitive router (PRISM)](concepts/router.md)** picks which shape runs, **[GSAR](concepts/gsar.md)** grounds every claim or abstains, and the **admission gate** clears every consequential action against a policy you write. A jailbreak can't talk its way past any of them.

Need more than one agent? Every orchestration shape is first-class, from the same `Agent` class:

<div class="tulip-stat-strip" markdown><span style="white-space:nowrap">[Sequential](concepts/multi-agent.md)</span> · <span style="white-space:nowrap">[Parallel](concepts/multi-agent.md)</span> · <span style="white-space:nowrap">[Loop](concepts/multi-agent.md)</span> · <span style="white-space:nowrap">[Graph](concepts/multi-agent.md)</span> · <span style="white-space:nowrap">[Orchestrator](concepts/multi-agent.md)</span> · <span style="white-space:nowrap">[Swarm](concepts/multi-agent.md)</span> · <span style="white-space:nowrap">[Handoff](concepts/multi-agent.md)</span> · <span style="white-space:nowrap">[A2A](concepts/multi-agent.md)</span></div>

<div class="tulip-hero__cta" markdown>
[Get started](how-to/quickstart.md){ .md-button .md-button--primary }
[Try it live ↗](https://play.tulipagents.ai){ .md-button }
[GitHub](https://github.com/tuliplabs-ai/sdk-python){ .md-button }
</div>

<p style="margin-top:0.6rem;font-size:0.85rem;color:var(--md-default-fg-color--light)">No install — run governed agents in your browser at <a href="https://play.tulipagents.ai"><strong>play.tulipagents.ai</strong></a> with your own model key.</p>

```bash
pip install "tulip-agents[anthropic]"   # OpenAI · Anthropic
```

</div>

<div class="tulip-hero__code" markdown>

```python
from tulip import Agent, tool

@tool
def search_flights(
    origin: str, dest: str, date: str
) -> list[dict]:
    "Find flights between two cities."
    return flights.search(origin, dest, date)

# A model is a string; a tool is a function.
agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search_flights],
    system_prompt="You are a travel agent.",
)

print(agent.run_sync(
    "Cheapest flight Lisbon to Berlin Friday?"
).text)
```

</div>
</div>

## A complete agent framework

One `Agent` class — tools, durable memory, RAG, streaming, sync or async. Swap models with
a string. Five lines to a working agent; the same class scales to any multi-agent shape.

```python
from tulip import Agent, tool

@tool
def lookup_order(order_id: str) -> str:
    """Look up an order's status."""
    return orders.get(order_id)          # your data — @tool exposes it to the model

agent = Agent(
    model="anthropic:claude-sonnet-4-6",  # or openai:gpt-4o — swap with a string
    tools=[lookup_order],
    system_prompt="You are a support assistant.",
)

print(agent.run_sync("What's the status of order ord-4821?").text)
# -> "Order ord-4821 has shipped — arrives Tuesday."
```

## What makes it the *safest* — control in the core

A frontier model can be brilliant and still be talked into the wrong action. The one thing
it *structurally* cannot do — no matter how smart — is **prove it won't**. That's a control
problem, not an intelligence problem. Tulip wires control through three points:

- **The router controls *which shape* runs.** The [cognitive router](concepts/router.md) fills a typed `GoalFrame`
  and a **deterministic** picker compiles the task to the right runtime shape. The model
  classifies — it never authors the topology.
- **[GSAR](concepts/gsar.md) controls *what gets asserted*.** Every claim is partitioned grounded / ungrounded /
  contradicted / complementary against typed evidence; below threshold the agent regenerates,
  replans, or **abstains**. An ungrounded claim never ships.
- **The admission gate controls *what actions fire*.** A side-effecting call runs only after
  it clears `admit()` — a policy check outside the model, held for a human when the stakes
  warrant, recorded on a tamper-evident trail either way.

A rule in the prompt is advisory by definition — a jailbreak, an injected document, or a
confused chain talks the model past it. Tulip makes the rule **structural**: the action runs
only after it clears the gate, which the model has no way to reach around.

### Three ways to "make agents safe"

| | Bare model + prompt rules | Framework guardrails | **Tulip** |
|---|---|---|---|
| **Where safety lives** | in a prompt the model can be argued out of | input/output filters around the call | an admission gate **around the action** |
| **Can a jailbreak bypass it?** | yes — talk the model out of the rule | often — filters score text, not blast radius | **no** — the action runs only if `admit()` allows |
| **Human-in-the-loop** | ad-hoc, if you wire it | sometimes | first-class: `require_human_for` by environment / kind / tag |
| **Proof of what happened** | logs you can edit | app logs | **hash-chained `AuditTrail`** — `verify()` fails on any edit |

Guardrails and grounding are good — Tulip ships both. The difference is the gate: a wrong
action isn't filtered after the fact, it's **prevented before it runs** — and the decision
is recorded either way.

[Why Tulip — the full argument →](why-tulip.md)

## What you get

<div class="grid cards tulip-feature-cards" markdown>

- :material-robot-happy:{ .lg .middle } **[A real agent framework](capabilities.md)**

    ---
    One `Agent` class — tools, memory, RAG, streaming, sync or async. Swap
    models with a string (`anthropic:…` or `openai:…`). Control is built
    in, not bolted on.

- :material-routes:{ .lg .middle } **[Cognitive router](concepts/router.md)**

    ---
    Describe a task in plain language; the PRISM router fills a typed
    `GoalFrame` and compiles it to the right shape — direct answer, pipeline,
    fan-out, debate, or an approval-gated action. The model classifies; routing
    is deterministic.

- :material-graph:{ .lg .middle } **[Multi-agent workflows](concepts/multi-agent.md)**

    ---
    Every shape for building multi-agent workflows — pipeline, fan-out,
    loop, state graph, orchestrator, swarm, handoff, and cross-process A2A.
    Whatever topology you need, one `Agent` class and one event stream.

- :material-shield-search:{ .lg .middle } **[Grounded by construction](concepts/gsar.md)**

    ---
    `ground_finding()` emits a typed result only above the GSAR threshold —
    else an auditable `Abstention`, never a guess. An ungrounded claim is a
    false result by construction and never ships.

- :material-shield-lock:{ .lg .middle } **[The admission gate](concepts/security-context.md)**

    ---
    `admit()` runs a consequential action **only if** your `ControlPolicy`
    allows — else holds it for a human or denies it, and records the attempt
    either way. The one thing a jailbroken model can't reach around.

- :material-account-check:{ .lg .middle } **[Human-in-the-loop](notebooks/notebook_19_human_in_the_loop.md)**

    ---
    `require_human_for` pauses on the actions that matter — by environment,
    kind, or tag — and resumes on a human's decision. Approvals survive
    restarts; an interrupted run picks up where it left off.

- :material-eye:{ .lg .middle } **[Audit trail by default](concepts/observability.md)**

    ---
    Every model call, tool call, guardrail verdict, and approval is a typed,
    hash-chained event — `verify()` fails on any edit. Replay a run in a
    postmortem, or ship the stream to your warehouse or SIEM.

- :material-database:{ .lg .middle } **[Vendor-neutral backends](concepts/rag.md)**

    ---
    RAG over five vector stores, durable memory across eight checkpoint
    backends, pluggable embeddings and rerankers — all behind small contracts,
    nothing wired to one vendor, most with a free local test path.

- :material-link-variant:{ .lg .middle } **[Govern agents you already run](integrations/frameworks.md)**

    ---
    `tulip-frameworks` wraps LangChain, LangGraph, CrewAI, OpenAI Agents,
    LlamaIndex, and Google ADK tools with the same `admit()` gate and
    `AuditTrail` — about three lines, no rebuild. Same harness, same
    governance, any agent.

</div>

## How the admission gate works

Route an action through Tulip and "no action without an approved warrant" stops being a
convention and becomes enforced code. The chain is short and every link is real:

**action → policy → approval → admission → audit**

- **Policy + approval** — `approve()` weighs your `ControlPolicy` (blast radius,
  `require_human_for`, and — when you have it — a verification score) and returns allow, hold
  (`require_human`), or deny.
- **Admission** — `admit()` runs the side-effecting action **only if** approval allows,
  recording the decision to the `AuditTrail` you pass either way; otherwise it raises
  `AdmissionError`. The model never touches this step.
- **Audit** — the trail is hash-chained, so `verify()` catches any edit after the fact.

That last gate is what makes Tulip a *runtime*, not a library: the rule isn't a docstring the
model is asked to respect — it's a line of code the action has to pass.

```python
from tulip.control import Action, AuditTrail, ControlPolicy, admit, AdmissionError

policy = ControlPolicy(require_human_for={"production"})
trail = AuditTrail()

async def safe_refund(order_id: str, usd: float):
    try:                                              # the gate runs before money moves
        return await admit(
            Action(name="refund", asset=order_id, kind="payment", environment="production"),
            lambda: payments.refund(order_id, usd),
            policy=policy, trail=trail,
        )
    except AdmissionError:
        return "Held for a human — not run."
```

[The control layer →](concepts/security-context.md) · [Grounding & verification →](concepts/security.md)

## Agent security

Security is where control matters most, so it's where Tulip is hardened first. A finding
ships only when it's grounded: `tulip.security` has no public constructor that builds an
`Evidence` without a score, so an ungrounded claim becomes an auditable abstention instead
of a false alarm.

```python
from tulip.security import ground_finding, Severity, is_finding
from tulip.reasoning.gsar import Claim, EvidenceType, Partition

result = ground_finding(
    title="Expired TLS certificate on 192.0.2.10:443",
    description="Serving endpoint presents an expired certificate.",
    severity=Severity.HIGH,
    asset="192.0.2.10:443",
    remediation="Rotate the certificate; enforce automated renewal.",
    partition=Partition(grounded=[
        Claim(text="cert expired 2026-05-30", type=EvidenceType.TOOL_MATCH,
              evidence_refs=["tool:tls_scan:not_after=2026-05-30"]),
    ]),
)
print(result.title if is_finding(result) else f"withheld: {result.reason}")
# Grounded partition → a typed Evidence. Ungrounded → an Abstention.
```

Findings carry **MITRE ATLAS**, **OWASP Top 10 for LLM**, and **OWASP Top 10 for Agentic
Applications** tags, so they drop into a SIEM without translation. The same discipline —
evidence before action — is what makes Tulip safe to let act *anywhere*: in payments, in
infra, in support.

[The security layer →](concepts/security.md) · [GSAR grounding →](concepts/gsar.md)

## Build it across any domain

Every example is a single self-contained file under [`examples/`][gh-examples] with a
matching docs page — gated actions in payments, infrastructure, support, and data, plus the
security track Tulip was hardened on.

| You're building… | Start here |
|---|---|
| **A support / ops agent that acts** | [human-in-the-loop approvals](notebooks/notebook_19_human_in_the_loop.md) · [incident response](notebooks/notebook_63_incident_response.md) |
| **An agent on your own data (RAG)** | [RAG basics](notebooks/notebook_38_rag_basics.md) · [RAG providers](notebooks/notebook_39_rag_providers.md) · [RAG agents](notebooks/notebook_40_rag_agents.md) |
| **A multi-agent workflow** | [swarm / war-room](notebooks/notebook_24_swarm_multiagent.md) · [supervisor + critic](notebooks/notebook_31_supervisor_critic_loop.md) · [advanced patterns](notebooks/notebook_20_advanced_patterns.md) |
| **A task-routed agent** | [cognitive router](notebooks/notebook_58_cognitive_router.md) · [procurement approval](notebooks/notebook_64_procurement_approval.md) · [contract review](notebooks/notebook_65_contract_review.md) |
| **A security / AI-safety agent** | [GSAR grounding](notebooks/notebook_37_gsar_typed_grounding.md) · [injection guardrails](notebooks/notebook_50_guardrails_security.md) · [verify findings](notebooks/notebook_78_verify_findings.md) |

Full catalog → [Notebooks index](notebooks/index.md) · [Capabilities matrix](capabilities.md) · [API reference](api/agent.md)

[gh-examples]: https://github.com/tuliplabs-ai/sdk-python/tree/main/examples

## When Tulip is overkill

If your agent only reads and summarizes — no side effects, no money, no infrastructure, no
irreversible writes — you may not need an admission gate yet. Tulip still gives you a clean
agent framework and a typed event stream, but the control layer earns its keep the moment an
action can **cost** something.

## Start building

Prefer to try before you install? The **[live workbench ↗](https://play.tulipagents.ai)** runs every pattern in your browser — bring your own OpenAI, Anthropic, or OpenAI-compatible key.

```bash
pip install "tulip-agents[openai]"
```

[Get started →](how-to/quickstart.md){ .md-button .md-button--primary }
[Try it live ↗](https://play.tulipagents.ai){ .md-button }
[Why Tulip →](why-tulip.md){ .md-button }
[GitHub →](https://github.com/tuliplabs-ai/sdk-python){ .md-button }

---

**The open-source agentic harness — control the action, prove what it did. Safe by construction. Apache-2.0.**
