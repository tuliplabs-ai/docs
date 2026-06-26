---
hide:
  - navigation
  - toc
---

<div class="tulip-hero" markdown>
<div class="tulip-hero__copy" markdown>

<p class="tulip-product-name"><span class="tpn-brand">tulip agents</span><span class="tpn-sep"> · </span>agents you can let act</p>

# Let your agent act. <span class="accent">You stay in control.</span>

Tulip is an open-source framework for building agents — tools, memory, multi-agent, RAG — with one thing the others don't have: **a control layer in the core.** Every action your agent takes — refund a customer, ship a deploy, delete a row — runs only after it clears rules you write, stops for a human when the stakes are real, and lands on an audit trail you can't forge.

The check is real code, **outside the model.** Jailbreak it, poison its context, confuse its reasoning — the action still can't run if your policy says no. A wall, not a warning.

Build your whole agent on Tulip, or bolt the control layer onto one you already have — LangChain, CrewAI, the OpenAI Agents SDK, your own loop. Hardened first in security, where a wrong move is a breach.

<div class="tulip-stat-strip" markdown><span style="white-space:nowrap">[LangChain](integrations/frameworks.md)</span> · <span style="white-space:nowrap">[CrewAI](integrations/frameworks.md)</span> · <span style="white-space:nowrap">[OpenAI&nbsp;Agents](integrations/frameworks.md)</span> · <span style="white-space:nowrap">[LlamaIndex](integrations/frameworks.md)</span> · <span style="white-space:nowrap">[MCP](concepts/mcp.md)</span></div>

<div class="tulip-hero__cta" markdown>
[Get started](how-to/quickstart.md){ .md-button .md-button--primary }
[GitHub](https://github.com/tuliplabs-ai/sdk-python){ .md-button }
</div>

```bash
pip install "tulip-agents[openai]"   # OpenAI · Anthropic
```

</div>

<div class="tulip-hero__code" markdown>

```python
from tulip import Agent, tool
from tulip.control import (
    Action, admit, ControlPolicy,
    AuditTrail, AdmissionError)

policy = ControlPolicy(
    require_human_for={"production"})
trail = AuditTrail()

@tool
async def refund(order_id: str, usd: float) -> str:
    "Refund a customer order."
    act = Action(
        name="refund", asset=order_id,
        kind="payment", environment="production")
    try:  # the gate runs before money moves
        return await admit(
            act, lambda: pay.refund(order_id, usd),
            policy=policy, trail=trail)
    except AdmissionError:
        return "Held for a human — not run."

# Build the agent the usual way.
agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[refund])

# Jailbreak the model all you like — it still
# can't move the money. The gate holds the
# action for a human, on the audit trail.
print(agent.run_sync(
    "Refund order ord-4821 for $250.").text)
# -> "...held for human review."
```

</div>
</div>

## Two ways to use Tulip

**Build your agent on Tulip.** A complete agentic framework — tools, memory, multi-agent, RAG, streaming — with the control layer native to every action.

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

**Already on another framework? Add just the control layer.** Wrap one tool — a risky action is now policy-gated, human-approvable, and audited. The rest of your LangChain / CrewAI / OpenAI-Agents agent doesn't change.

```python
from langchain_core.tools import tool
from tulip.control import Action, AuditTrail
from tulip_frameworks.langchain import gate_langchain_tool
from tulip_frameworks.policy_presets import action_gate_policy

@tool
def refund(order_id: str, amount_usd: float) -> str:
    """Issue a customer refund."""
    return payments.refund(order_id, amount_usd)   # in real life, this moves money

safe_refund = gate_langchain_tool(
    refund,
    action=lambda name, a: Action(name=name, asset=a["order_id"],
                                  blast_radius=1, kind="payment", environment="production"),
    policy=action_gate_policy(),          # production → human
    trail=AuditTrail(),
)
# Hand `safe_refund` to your agent in place of `refund`. A $250 production refund now returns:
#   {"status": "held_for_approval", "reason": "labels ['production'] require human approval"}
```

`pip install "tulip-frameworks[langchain]"` — bridges for LangChain, LangGraph, CrewAI, the OpenAI Agents SDK, LlamaIndex, and Google ADK.

## Most frameworks help the model *decide*. Tulip governs what it *does*.

The moment an agent stops advising and starts **acting** — moving money, deleting a
resource, disabling an account — the risk stops being a bad sentence and becomes a
real consequence. A frontier model can be brilliant and still be talked into the
catastrophic action; the one thing it *structurally* cannot do — no matter how smart
— is **prove it won't**. That's not an intelligence problem. It's a control problem.

A rule in the prompt is advisory by definition — a jailbreak, an injected document, or
a confused chain talks the model past it. Tulip makes the rule **structural**: the
side-effecting call runs only after it clears `admit()`, a gate the model has no way
to reach around.

### Three ways to "make agents safe"

| | Bare model + prompt rules | Framework guardrails | **Tulip** |
|---|---|---|---|
| **Where safety lives** | in a prompt the model can be argued out of | input/output filters around the call | an admission gate **around the action** |
| **Can a jailbreak bypass it?** | yes — talk the model out of the rule | often — filters score text, not blast radius | **no** — the action runs only if `admit()` allows |
| **Human-in-the-loop** | ad-hoc, if you wire it | sometimes, per-framework | first-class: `require_human_for` by environment / kind / tag |
| **Proof of what happened** | logs you can edit | app logs | **hash-chained `AuditTrail`** — `verify()` fails on any edit |
| **Works with your stack** | — | you adopt the framework | **drop-in**: wrap a call your agent already makes, on any framework |

Guardrails and grounding are good — Tulip ships both. The moat is the gate: a wrong
action isn't filtered after the fact, it's **prevented before it runs**, and the
decision is recorded whether it ran or not.

[Why Tulip — the full argument →](why-tulip.md) · [Drop it into your framework →](integrations/frameworks.md)

## What you get

<div class="grid cards tulip-feature-cards" markdown>

- :material-robot-happy:{ .lg .middle } **[A real agent framework](capabilities.md)**

    ---
    One `Agent` class — tools, memory, RAG, streaming, sync or async. Swap
    models with a string (`anthropic:…` or `openai:…`). Everything you'd
    build an agent with, with control built in rather than bolted on.

- :material-shield-lock:{ .lg .middle } **[The admission gate](concepts/security-context.md)**

    ---
    `admit()` runs an action **only if** your `ControlPolicy` allows —
    else holds it for a human or denies it, and records the attempt either
    way. The one thing a jailbroken model can't reach around.

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

- :material-graph:{ .lg .middle } **[Multi-agent coordination](concepts/multi-agent.md)**

    ---
    Seven shapes — pipeline, fan-out, loop, orchestrator, swarm, handoff,
    and cross-process A2A — for tiered escalation, parallel work, and
    debate-to-decision. One `Agent` class, one event stream.

- :material-routes:{ .lg .middle } **[Risk-gated routing](concepts/router.md)**

    ---
    Describe a task in plain language; the cognitive router ranks it by risk
    and compiles high-risk steps onto an approval gate that survives
    restarts. The model classifies — it never authors the control.

- :material-puzzle:{ .lg .middle } **[Drop into any framework](integrations/frameworks.md)**

    ---
    Already on LangChain, LangGraph, CrewAI, the OpenAI Agents SDK,
    LlamaIndex, or Google ADK? Wrap one tool with `gate_*_tool` — the rest
    of your agent is untouched.

- :material-shield-search:{ .lg .middle } **[Grounded, when it has to be](concepts/security.md)**

    ---
    Hardened in security, where a hallucinated claim is a false alarm or a
    missed breach: `ground_finding()` emits a typed `Evidence` only above
    the GSAR threshold — else an auditable `Abstention`, never a guess.

</div>

## How the gate can't be bypassed

Route an action through Tulip and "no action without an approved warrant" stops being
a convention and becomes enforced code. The chain is short and every link is real:

**action → policy → approval → admission → audit**

- **Policy + approval** — `approve()` weighs your `ControlPolicy` (blast radius,
  `require_human_for`, and — when you have it — a verification score) and returns
  allow, hold, or deny.
- **Admission** — `admit()` runs the side-effecting action **only if** approval
  allows, recording the decision to the `AuditTrail` you pass either way; otherwise it
  raises `AdmissionError`. The model never touches this step.
- **Audit** — the trail is hash-chained, so `verify()` catches any edit after the
  fact.

That last gate is what makes Tulip a *runtime*, not a library: the rule isn't a
docstring the model is asked to respect — it's a line of code the action has to pass.
For security work, the chain extends upstream with **grounding** (a claim becomes a
typed `Evidence` only above threshold) and **verification** (`verify()` independently
re-scores a finding before it can drive an action).

[The control layer →](concepts/security-context.md) · [Grounding & verification →](concepts/security.md)

## Proven where a wrong action is a breach

Tulip earned the gate in the hardest place to act on a machine's say-so: security.
There, a hallucinated claim isn't an embarrassment — it's a false positive that burns
an analyst's night or a false negative that ships a breach. So `tulip.security` makes
a finding *unshippable* unless it's grounded: there is no public constructor that
builds an `Evidence` without a score.

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

Findings carry **MITRE ATLAS**, **OWASP Top 10 for LLM**, and **OWASP Top 10 for
Agentic Applications** tags, so they drop into a SIEM without translation. The same
discipline — evidence before action — is what makes Tulip safe to let act *anywhere*:
in payments, in infra, in support.

[The security layer →](concepts/security.md) · [GSAR grounding →](concepts/gsar.md)

## Build it across any domain

Every example is a single self-contained file under [`examples/`][gh-examples] with a
matching docs page — gated actions in payments, infrastructure, support, and data, plus
the security track Tulip was hardened on.

| You're building… | Start here |
|---|---|
| **A support / ops agent that acts** | [human-in-the-loop approvals](notebooks/notebook_19_human_in_the_loop.md) · [incident response](notebooks/notebook_63_incident_response.md) |
| **An agent on your own data (RAG)** | [RAG basics](notebooks/notebook_38_rag_basics.md) · [RAG providers](notebooks/notebook_39_rag_providers.md) · [RAG agents](notebooks/notebook_40_rag_agents.md) |
| **A multi-agent workflow** | [swarm / war-room](notebooks/notebook_24_swarm_multiagent.md) · [supervisor + critic](notebooks/notebook_31_supervisor_critic_loop.md) · [advanced patterns](notebooks/notebook_20_advanced_patterns.md) |
| **An approval / review pipeline** | [procurement approval](notebooks/notebook_64_procurement_approval.md) · [contract review](notebooks/notebook_65_contract_review.md) · [forensic event trail](notebooks/notebook_59_observability_basics.md) |
| **A security / AI-safety agent** | [GSAR grounding](notebooks/notebook_37_gsar_typed_grounding.md) · [injection guardrails](notebooks/notebook_50_guardrails_security.md) · [verify findings](notebooks/notebook_78_verify_findings.md) |

Full catalog → [Notebooks index](notebooks/index.md) · [Capabilities matrix](capabilities.md) · [API reference](api/agent.md)

[gh-examples]: https://github.com/tuliplabs-ai/sdk-python/tree/main/examples

## When Tulip is overkill

If your agent only reads and summarizes — no side effects, no money, no
infrastructure, no irreversible writes — you may not need an admission gate yet.
Tulip still gives you a clean agent framework and a typed event stream, but the
control layer earns its keep the moment an action can **cost** something.

## Start building

```bash
pip install "tulip-agents[openai]"
```

[Get started →](how-to/quickstart.md){ .md-button .md-button--primary }
[Why Tulip →](why-tulip.md){ .md-button }
[GitHub →](https://github.com/tuliplabs-ai/sdk-python){ .md-button }

---

**Open-source agent framework with control built in. Evidence-grounded. Apache-2.0.**
