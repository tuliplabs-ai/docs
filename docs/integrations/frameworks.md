# Drop Tulip into your agent framework

You don't have to rebuild your agent on Tulip to get the control runtime. If you
already have an agent in **LangChain / LangGraph, CrewAI, the OpenAI Agents SDK,
or LlamaIndex**, keep it — and put Tulip's admission gate around the *actions* it
takes. The model and orchestration stay yours; the gate, the human-in-the-loop,
and the tamper-evident audit trail come from Tulip.

The reason this works is that the gate is framework-agnostic by construction:

```python
from tulip.security import admit, Action, SecurityPolicy, AuditTrail
await admit(action, perform, policy=policy, trail=trail)
```

`admit()` takes an `Action` (the *what*, with its blast radius and environment)
and `perform` — **any** zero-argument callable that does the work. That callable
can be a LangChain tool's function, a CrewAI task, a raw OpenAI tool-call
handler, or a plain Python function. Nothing about it is Tulip-specific.

## The pattern: wrap the tool's body

Take a tool your agent already calls and route its side effect through the gate.
Here it is inside a LangChain tool:

```python
from langchain_core.tools import tool
from tulip.security import admit, Action, SecurityPolicy, AuditTrail, AdmissionError

policy = SecurityPolicy()   # production → human
trail = AuditTrail()

@tool
async def refund(order_id: str, amount_usd: float) -> str:
    """Issue a customer refund."""
    action = Action(name="refund", asset=order_id, blast_radius=1,
                    kind="payment", environment="production")
    try:
        await admit(action, lambda: payments.refund(order_id, amount_usd),
                    policy=policy, trail=trail)
        return f"refunded {order_id}"
    except AdmissionError as e:
        # Soft mode: hand the model a result it can act on, don't crash the run.
        return f"HELD for approval: {e.decision.outcome} — {e.decision.reason}"
```

Now your existing LangChain agent is unchanged — but the moment it decides to
refund a production order, the action is held for a human, and the decision (run
or held) is on a trail you can `verify()` and `export_jsonl()` into a SIEM. A
prompt injection that talks the model into a thousand refunds still can't get one
*executed*.

The same three moves apply to every framework:

- **LangGraph** — wrap the tool (above); `ToolNode` consumes it unchanged. For a
  raw graph node that performs a side effect, wrap the node body the same way.
- **CrewAI** — call `admit()` inside the tool's `_run` / async run.
- **OpenAI Agents SDK** — wrap the function behind your `function_tool`.
- **LlamaIndex** — wrap the function behind your `FunctionTool`.

## Raise vs. soft mode

`admit()` raises `AdmissionError` when an action is denied or held for a human.
You have two sensible responses inside an agent loop:

- **Soft** (shown above) — catch it and return a structured "held for approval"
  string the model can see and react to (explain to the user, try a safer path,
  poll for the human decision). The run stays alive.
- **Raise** — let it propagate to stop a deterministic pipeline cold.

Either way the audit record is written *before* the exception, so a held action
can never become an un-audited side effect.

## Convenience wrappers — `tulip-frameworks`

The pattern above works today with core `tulip-agents` alone. For less
boilerplate, the **`tulip-frameworks`** package ships thin per-framework wrappers
that do the wrapping for you — e.g. `gate_langchain_tool(tool, action=..., policy=...,
trail=...)` returns a gated tool in the framework's native format, with a
`mode="soft"|"raise"` switch and an optional out-of-band approval bridge. It
depends one-way on core (the same core + community split as
[`tulip-integrations`](index.md)), with a per-framework install extra
(`tulip-frameworks[langchain]`, `[crewai]`, …).

→ [Why Tulip](../why-tulip.md) · [The security layer](../concepts/security.md) · [Build a vendor integration](build.md)
