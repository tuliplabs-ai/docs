# Bring Tulip's control layer to an existing agent

Tulip is an agentic harness — a full-stack agent framework with a control runtime
wired through it — and its admission gate, human-in-the-loop, and tamper-evident
audit trail are the same control layer whether or not the agent runs on Tulip. So you don't have to rebuild
to get it. If you already have an agent in **LangChain / LangGraph, CrewAI, the
OpenAI Agents SDK, LlamaIndex, or Google ADK**, keep it — put Tulip's gate around
the *actions* it takes. The model and orchestration stay yours; the gate, the
human-in-the-loop, and the tamper-evident audit trail come from Tulip.

The [`tulip-frameworks`](https://github.com/tuliplabs-ai/tulip-frameworks) package
ships a thin bridge per framework. You wrap a tool once and give the gated version to
your agent in its place — same name, same schema. From then on, when the agent
decides to act, the gate decides whether that action runs, is held for a human, or is
denied — and records the decision either way.

## Install

```bash
pip install "tulip-frameworks[langchain]"        # or [langgraph] / [openai-agents]
pip install "tulip-frameworks[crewai]"           # or [llama-index] / [adk]
pip install "tulip-frameworks[all]"              # everything
```

`import tulip_frameworks` pulls in **no** framework package; each bridge imports its
framework lazily and tells you which extra to install if it's missing.

## Wrap a tool — LangChain

```python
from langchain_core.tools import tool
from tulip.control import Action, AuditTrail
from tulip_frameworks.langchain import gate_langchain_tool
from tulip_frameworks.policy_presets import action_gate_policy

@tool
def refund(order_id: str, amount_usd: float) -> str:
    "Issue a customer refund."
    return payments.refund(order_id, amount_usd)

trail = AuditTrail()
safe_refund = gate_langchain_tool(
    refund,
    action=lambda name, a: Action(name=name, asset=a["order_id"],
        blast_radius=1, kind="payment", environment="production"),
    policy=action_gate_policy(),   # production → held for a human
    trail=trail,
)
# Drop it in where `refund` went: agent = create_react_agent(model, tools=[safe_refund])
```

Your agent is otherwise unchanged — but the moment it decides to refund a production
order, the action is **held for a human**, the function never executes, and the
decision (run or held) is on a trail you can `verify()` and `export_jsonl()` into a
SIEM. A prompt injection that talks the model into a thousand refunds produces a
thousand *held* actions and zero executed ones.

!!! note "This is tested against a real model, not a mock"
    The package's integration suite runs a real LangChain agent (Claude) and a real
    OpenAI Agents agent (GPT) that genuinely decide to call a gated production action
    — and asserts the side effect never executes, even under a `SYSTEM OVERRIDE`
    prompt injection. The model can be fooled; the gate still can't be talked past.

## The same shape, every framework

Pass the tool you already have, an `action`, and a `policy`; get back a gated tool in
that framework's native type.

| Framework | Bridge | Returns |
|---|---|---|
| LangChain | `gate_langchain_tool(tool, …)` | `StructuredTool` |
| LangGraph | `gate_langchain_tool` (for `ToolNode`); `gate_node(node_fn, …)` for a raw side-effect node | gated tool / node |
| OpenAI Agents SDK | `gate_openai_tool(function_tool, …)` | `FunctionTool` |
| CrewAI | `gate_crewai_tool(tool, …)` | `BaseTool` |
| LlamaIndex | `gate_llamaindex_tool(tool, …)` | `FunctionTool` |
| Google ADK | `gate_adk_tool(tool_or_fn, …)` | `FunctionTool` |

Each bridge keeps the original name, description, and argument schema, so it drops
into the agent or graph that consumed the original — nothing else changes.

## What the gate decides on

Every bridge wraps one primitive — `gate_callable` — which is the only thing that
calls the core SDK's `admit()`. Three inputs drive it:

- **Action** — what the agent is about to do: its `asset`, `blast_radius`,
  `environment`, `kind`, `tags`. Pass a constant `Action`, or (recommended) a
  `(name, kwargs) -> Action` callable that derives risk from the call's arguments — a
  $5 refund in staging is not the same action as a $50,000 refund in production.
- **Policy** — `action_gate_policy()` gates ordinary tools on labels + blast radius;
  or bring a full `ControlPolicy` and pass grounded `finding` / `verdict` for the
  complete trust chain.
- **Trail** — an `AuditTrail` that hash-chains every decision so tampering is
  detectable.

The outcome is one of **allow**, **require_human**, or **deny** — and the side effect
runs only on *allow*. The audit record is written **before** a hold or denial
surfaces, so a held action can never become an un-recorded side effect.

## Held or raised

`mode` controls how a non-admitted action surfaces inside your agent loop:

- **`mode="soft"`** (default) — the gated call returns a structured *held-for-approval*
  result the model can read and react to (explain to the user, try a safer path, poll
  for the human decision). The run stays alive.
- **`mode="raise"`** — the gate re-raises `AdmissionError` to stop a deterministic
  pipeline cold.

For an out-of-band human decision, pass an `ApprovalBridge`: the held result then
carries an `approval_id` the agent can poll while a person approves elsewhere on a
channel the agent can't reach. The [`tulip-gateway`](index.md) broker satisfies it.

## Test your gate offline

`tulip_frameworks.testing` asserts a tool admits or holds **without a model or
network**, so the behaviour you check in CI is the behaviour production gets:

```python
from tulip_frameworks import gate_callable, action_gate_policy
from tulip_frameworks.testing import Spy, assert_held
from tulip.control import Action

async def test_production_refund_is_held():
    spy = Spy()
    gated = gate_callable(spy, name="refund",
        action=Action(name="refund", environment="production", kind="payment"),
        policy=action_gate_policy())
    assert_held(await gated(order_id="ord-9"), spy)   # never ran; held
```

## Under the hood: raw `admit()`

The bridges are convenience. The gate itself is framework-agnostic and depends on
nothing but the core SDK, so you can call it directly with no extra package:

```python
from tulip.control import admit, Action, ControlPolicy, AuditTrail, AdmissionError

@tool
async def refund(order_id: str, amount_usd: float) -> str:
    """Issue a customer refund."""
    action = Action(name="refund", asset=order_id, blast_radius=1,
                    kind="payment", environment="production")
    try:
        await admit(action, lambda: payments.refund(order_id, amount_usd),
                    policy=ControlPolicy(), trail=trail)
        return f"refunded {order_id}"
    except AdmissionError as e:
        return f"HELD for approval: {e.decision.outcome} — {e.decision.reason}"
```

`admit()` takes an `Action` and `perform` — **any** zero-argument async callable that
does the work. That callable can wrap a LangChain tool's function, a CrewAI task, a
raw OpenAI tool-call handler, or a plain function. Nothing about it is framework-
specific; the `gate_*_tool` helpers just remove this boilerplate and handle the
sync↔async bridge for you.

## Gate vs. compose vs. assure

"Integrating with X" means three different things depending on what X is — don't
force them into one mould:

| If X is… | …the relationship is | …how |
|---|---|---|
| an **agent framework** (LangChain, LangGraph, CrewAI, OpenAI Agents, LlamaIndex, ADK) | **Gate** its tools | `gate_*_tool` (above) |
| a **model-call gateway** (LiteLLM, Portkey) | **Compose** — it routes the model call, Tulip gates the action | point your model at the gateway *and* wrap the action in `admit()`; they stack |
| an **agent outside Python** (a TypeScript agent, an OpenClaw-style runtime, Vercel AI) | **Gate over the wire** — the gate is a language-neutral network call | the [`tulip-gateway`](index.md) `/v1/admit` endpoint, with the [`tulip-frameworks-js`](https://github.com/tuliplabs-ai/tulip-frameworks-js) TypeScript client |
| **another agent** you don't control (a chatbot, an endpoint) | **Assure** — red-team it | the core SDK's `Target` + [`red_team()`](../concepts/security.md) |

A model-call gateway is **not** something you gate — it governs *which model, whose
key, within what budget*; Tulip governs *whether the action runs*. They're different
layers and they stack cleanly. Trying to "gate LiteLLM" confuses the two.

→ [Why Tulip](../why-tulip.md) · [The security layer](../concepts/security.md) · [Build a vendor integration](build.md)
