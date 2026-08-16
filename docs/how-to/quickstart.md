# Quickstart

A working Tulip agent in five minutes.

## 1. Install

```bash
pip install "tulip-agents[openai]"
```

This installs the SDK plus the OpenAI provider. For other
providers add the corresponding extra:

```bash
pip install "tulip-agents[openai]"        # OpenAI directly
pip install "tulip-agents[anthropic]"     # Anthropic directly
pip install "tulip-agents[sdk]"           # everything
```

## 2. Configure your provider

Set the API key for whichever provider you're using:

```bash
export OPENAI_API_KEY=sk-...          # OpenAI
export ANTHROPIC_API_KEY=sk-ant-...   # Anthropic
```

For OpenAI-compatible gateways or local servers, point `OpenAIModel` at
the model's `base_url` instead. See
[Models](../concepts/models.md) for the per-provider matrix. A provider
key is required for real model output; the example notebooks can also run
offline against the `MockModel` bundled with the examples.

## 3. Your first agent

Save this as `support_agent.py`:

```python
from tulip.agent import Agent
from tulip.tools.decorator import tool

@tool
def lookup_order(order_id: str) -> dict:
    """Look up an order: status, amount, and delivery events."""
    return {"order_id": order_id, "status": "delivered", "amount_usd": 42.50,
            "delivery_events": ["shipped", "delivered", "damage reported"]}

@tool
def check_refund_eligibility(order_id: str) -> dict:
    """Check an order against the refund policy."""
    return {"order_id": order_id, "eligible": True,
            "reason": "damage reported within the 30-day window"}

agent = Agent(
    model="openai:gpt-4o",
    tools=[lookup_order, check_refund_eligibility],
    system_prompt="You are a support agent handling refund requests. "
                  "Cite the evidence behind every recommendation.",
)

result = agent.run_sync(
    "Order ORD-7842 arrived damaged. Look it up and check whether "
    "it qualifies for a refund."
)
print(result.message)
```

Run:

```bash
python support_agent.py
```

You should see something like:

```text
ORD-7842 ($42.50) shows a damage report in its delivery events, and the
policy check confirms it was reported within the 30-day window.
Evidence: lookup_order + check_refund_eligibility. Verdict: eligible
for refund — issuing it requires approval.
```

## 3.5 Gate the action

Finding the problem is the easy half. The moment an agent goes from
*advising* to *acting* — isolating that host, refunding that customer,
disabling that account — you need a gate it cannot talk its way past.
That's the whole point of Tulip: wrap the action in `admit()` and it runs
**only** after it clears policy, holds for a human when the blast radius
warrants it, and lands on a tamper-evident audit trail either way.

```python
import asyncio

from tulip.control import (
    Action, admit, ControlPolicy, AuditTrail, AdmissionError)

policy = ControlPolicy()    # conservative defaults: production → human
trail = AuditTrail()        # tamper-evident and replayable — editing any record breaks verification

# The check above said "eligible for refund". Don't just issue it — admit it.
risky = Action(
    name="issue_refund", asset="ORD-7842",
    blast_radius=1, kind="payment", environment="production")

async def do_refund():
    ...  # your real payment call (Stripe, your billing service, etc.)

async def main():
    try:
        await admit(risky, do_refund, policy=policy, trail=trail)
    except AdmissionError as e:
        print(e.decision.outcome)   # -> "require_human" — held; the refund did NOT run

    # Either way it's on the record:
    print(trail.verify())           # True — chain intact
    print(trail.export_jsonl())     # one JSON event per line — ready for your log pipeline or audit store

asyncio.run(main())
```

That `admit()` call is the difference between a library that *suggests*
and a runtime that *enforces*. See [Why Tulip](../why-tulip.md) for the
comparison, and the [Admission gate concept](../concepts/security.md) for
the full policy surface.

## 4. Stream the events

For UIs and real-time logging, switch to async and consume the typed
event stream:

```python
import asyncio
from tulip.core.events import (
    ThinkEvent, ToolStartEvent, ToolCompleteEvent, TerminateEvent,
)

async def main():
    async for event in agent.run("Look up ORD-7842 and assess the refund request."):
        match event:
            case ThinkEvent(reasoning=r) if r:
                print(f"💭 {r}")
            case ToolStartEvent(tool_name=n, arguments=a):
                print(f"🔧 {n}({a})")
            case ToolCompleteEvent(result=r):
                print(f"   ↳ {r}")
            case TerminateEvent(final_message=m):
                print(f"\n✅ {m}")

asyncio.run(main())
```

See [Streaming](../concepts/streaming.md) for the full event taxonomy.

## 5. Persist conversations across restarts

For real applications you'll want state to survive a restart. Wire a
checkpointer and a `thread_id`:

```python
from tulip.memory.backends.file import FileCheckpointer

agent = Agent(
    model="openai:gpt-4o",
    tools=[...],
    system_prompt="...",
    checkpointer=FileCheckpointer(base_dir="./threads"),
)

# Day 1
agent.run_sync("Open case C-4821 for the billing dispute.", thread_id="case-4821")

# Day 2 — same thread_id, the case continues
agent.run_sync("What did we establish so far?", thread_id="case-4821")
```

For vendor-neutral durability, swap to `S3Backend(bucket=..., prefix=...)`.
See [Conversation Management](../concepts/conversation-management.md).

## 6. Make it production-grade

Add idempotency to side-effecting tools, Reflexion to catch wrong
premises, and termination algebra to stop when the work is done:

```python
from tulip.memory.backends import S3Backend
from tulip.core.termination import (
    MaxIterations, ToolCalled, ConfidenceMet,
)

@tool(idempotent=True)
def issue_refund(order_id: str, amount: float) -> dict:
    return payments.refund(order_id, amount)

agent = Agent(
    model="openai:gpt-4o",
    tools=[lookup_order, issue_refund],
    system_prompt="...",
    reflexion=True,
    checkpointer=S3Backend(bucket="tulip-threads", prefix="..."),
    termination=(
        ToolCalled("issue_refund") & ConfidenceMet(0.9)
    ) | MaxIterations(8),
)
```

Each piece in detail:

- **`@tool(idempotent=True)`** → [Idempotency](../concepts/idempotency.md)
- **`reflexion=True`** → [Reasoning](../concepts/reasoning.md)
- **`checkpointer=...`** → [Checkpointers](../concepts/checkpointers.md)
- **`termination=...`** → [Termination](../concepts/termination.md)

## 7. Multi-agent

When one agent isn't enough — pick the coordination shape that fits
the problem:

| Shape | When |
|---|---|
| [Composition](../concepts/multi-agent/composition.md) | linear chain, fan-out + merge |
| [Orchestrator + Specialists](../concepts/multi-agent/orchestrator.md) | one router, parallel experts |
| [Swarm](../concepts/multi-agent/swarm.md) | open-ended research, peer-to-peer |
| [Handoff](../concepts/multi-agent/handoff.md) | escalation desks |
| [StateGraph](../concepts/multi-agent/graph.md) | review-loops, retry-until-confidence |
| [Functional API](../concepts/multi-agent/functional.md) | map/reduce over agents |
| [A2A](../concepts/multi-agent/a2a.md) | cross-process meshes |

## 8. Deploy

`AgentServer` is a drop-in FastAPI app:

```python
from tulip.server import AgentServer

server = AgentServer(agent=agent, api_key="change-me")
server.run(host="0.0.0.0", port=8080)
```

`POST /invoke`, `POST /stream`, `GET /threads/{id}`, `GET /health`.
Binding to a non-loopback host requires an `api_key` (or
`allow_unauthenticated=True`); every route except `/health` then
expects that bearer token. Deploys anywhere FastAPI runs — see
[Deploy](deploy.md).

## Where to next

- **Read deeper.** [Agent Loop](../concepts/agent-loop.md) is the
  architectural reference for how all of this fits together.
- **Browse examples.** Progressive notebooks at
  [`examples/`](https://github.com/tuliplabs-ai/tulip-agents/tree/main/examples).
  Each is a single runnable file that adds one idea on top of the
  previous. A security-flavored variant of this quickstart — SOC alert
  triage with the same gate — lives in the
  [security notebooks](../notebooks/notebook_79_soc_alert_triage.md).
- **Steer it.** [Hooks](../concepts/hooks.md) give you logging,
  telemetry, retry, guardrails, and steering as one-line additions.
