---
hide:
  - navigation
  - toc
---

<div class="tulip-hero" markdown>
<div class="tulip-hero__copy" markdown>

<p class="tulip-product-name"><span class="tpn-brand">tulip agents</span><span class="tpn-sep"> · </span><span class="tpn-tag">the safest way to build agentic AI</span></p>

# Agents that act. <span class="accent">Safe by construction.</span>

Tulip is an open-source **agentic harness** with one hard rule: **the model never holds
the trigger.** A jailbreak can talk your agent into anything — it can't talk past the
gate. Build agents on it, or [govern the ones you already run](integrations/frameworks.md)
in LangChain, CrewAI, or the OpenAI Agents SDK.

<div class="tulip-hero__cta" markdown>
[Get started](how-to/quickstart.md){ .md-button .md-button--primary }
[Try it live ↗](https://play.tulipagents.ai){ .md-button }
[GitHub](https://github.com/tuliplabs-ai/sdk-python){ .md-button }
</div>

<p style="margin-top:0.6rem;font-size:0.85rem;color:var(--md-default-fg-color--light)">No install — the live workbench runs in your browser with your own model key.</p>

```bash
pip install "tulip-agents[anthropic]"
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

## Control in the core

A model can be brilliant and still be talked into the wrong action. That's a control
problem, not an intelligence problem — so Tulip puts the control in code the model
can't reach:

- The **[router](concepts/router.md)** picks which shape runs — deterministically. The
  model classifies the task; it never authors the topology.
- **[GSAR](concepts/gsar.md)** scores every claim against typed evidence — below threshold
  the agent regenerates or abstains, never guesses.
- The **[admission gate](concepts/security-context.md)** clears every side-effecting call:
  `admit()` allows it, holds it for a human, or denies it — and records the decision on a
  hash-chained trail either way.

```python
from tulip.control import (
    Action, AuditTrail, ControlPolicy, admit, AdmissionError,
)

policy = ControlPolicy(require_human_for={"production"})
trail = AuditTrail()

async def safe_refund(order_id: str, usd: float):
    try:  # the gate runs before money moves
        return await admit(
            Action(name="refund", asset=order_id,
                   kind="payment", environment="production"),
            lambda: payments.refund(order_id, usd),
            policy=policy, trail=trail,
        )
    except AdmissionError:
        return "Held for a human — not run."
```

A prompt rule is advisory: a jailbreak talks the model past it. The gate is structural —
the wrong action isn't caught in a filter, it never runs.
[How this compares to prompt rules and guardrails →](why-tulip.md)

## Govern the agents you already run

You don't rebuild anything. Wrap a tool once with
[`tulip-frameworks`](integrations/frameworks.md) and drop it back in — same name, same
schema — and every call now goes through the same gate and audit trail:

```python
from tulip.control import Action, AuditTrail
from tulip_frameworks.langchain import gate_langchain_tool
from tulip_frameworks.policy_presets import action_gate_policy

safe_refund = gate_langchain_tool(
    refund,  # your existing LangChain @tool, unchanged
    action=lambda name, a: Action(
        name=name, asset=a["order_id"],
        kind="payment", environment="production",
    ),
    policy=action_gate_policy(),  # production → held for a human
    trail=AuditTrail(),
)
```

Bridges ship for LangChain, LangGraph, CrewAI, the OpenAI Agents SDK, LlamaIndex, and
Google ADK.

## What you get

<div class="grid cards tulip-feature-cards" markdown>

- :material-robot-happy:{ .lg .middle } **[A real agent framework](capabilities.md)**

    ---
    One `Agent` class — tools, memory, RAG, streaming — over vendor-neutral
    backends. Swap models with a string.

- :material-routes:{ .lg .middle } **[Cognitive router](concepts/router.md)**

    ---
    A plain-language task compiles to the right shape — direct answer,
    pipeline, fan-out, debate, or a gated action.

- :material-graph:{ .lg .middle } **[Multi-agent workflows](concepts/multi-agent.md)**

    ---
    Sequential, parallel, loop, graph, orchestrator, swarm, handoff, and
    cross-process A2A — one `Agent` class, one event stream.

- :material-shield-search:{ .lg .middle } **[Grounded by construction](concepts/gsar.md)**

    ---
    `ground_finding()` emits a typed result only above the GSAR threshold —
    else an auditable `Abstention`, never a guess.

- :material-shield-lock:{ .lg .middle } **[Gate + human-in-the-loop](concepts/security-context.md)**

    ---
    `require_human_for` pauses the actions that matter and resumes on a
    human's decision. Approvals survive restarts.

- :material-eye:{ .lg .middle } **[Audit trail by default](concepts/observability.md)**

    ---
    Every call, verdict, and approval is a typed, hash-chained event —
    `verify()` fails on any edit. Replay any run.

</div>

## Build it across any domain

Every example is a single self-contained file under [`examples/`][gh-examples] with a
matching docs page.

<div class="tulip-domain-table" markdown>

| You're building… | Start here |
|---|---|
| **A support / ops agent that acts** | [human-in-the-loop approvals](notebooks/notebook_19_human_in_the_loop.md) · [incident response](notebooks/notebook_63_incident_response.md) |
| **An agent on your own data (RAG)** | [RAG basics](notebooks/notebook_38_rag_basics.md) · [RAG agents](notebooks/notebook_40_rag_agents.md) |
| **A multi-agent workflow** | [swarm / war-room](notebooks/notebook_24_swarm_multiagent.md) · [supervisor + critic](notebooks/notebook_31_supervisor_critic_loop.md) |
| **A task-routed agent** | [cognitive router](notebooks/notebook_58_cognitive_router.md) · [procurement approval](notebooks/notebook_64_procurement_approval.md) |
| **A security / AI-safety agent** | [GSAR grounding](notebooks/notebook_37_gsar_typed_grounding.md) · [injection guardrails](notebooks/notebook_50_guardrails_security.md) |

</div>

Full catalog → [Notebooks index](notebooks/index.md) · [Capabilities matrix](capabilities.md) · [API reference](api/agent.md)

[gh-examples]: https://github.com/tuliplabs-ai/sdk-python/tree/main/examples

## When Tulip is overkill

If your agent only reads and summarizes, you may not need an admission gate yet — the
control layer earns its keep the moment an action can **cost** something.

## Start building

```bash
pip install "tulip-agents[openai]"
```

[Get started →](how-to/quickstart.md){ .md-button .md-button--primary }
[Try it live ↗](https://play.tulipagents.ai){ .md-button }
[Why Tulip →](why-tulip.md){ .md-button }

---

**The open-source agentic harness — control the action, prove what it did. Safe by construction. Apache-2.0.**
