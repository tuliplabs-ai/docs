# Quickstart

A working Tulip SOC agent in five
minutes.

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

the model's `base_url` — no key needed. See
[Models](../concepts/models.md) for the per-provider matrix. With no key
set, Tulip falls back to a bundled mock model so the quickstart still
runs offline.

## 3. Your first agent

Save this as `soc_agent.py`:

```python
from tulip.agent import Agent
from tulip.tools.decorator import tool

@tool
def scan_endpoint(ip: str, port: int) -> dict:
    """Scan an endpoint for cert expiry and known CVEs."""
    return {"ip": ip, "port": port, "cert_not_after": "2026-05-30",
            "cves": ["CVE-2024-3094"]}

@tool
def check_domain_reputation(domain: str) -> dict:
    """Look up a domain in the threat-intel feeds."""
    return {"domain": domain, "verdict": "malicious", "sources": 4}

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[scan_endpoint, check_domain_reputation],
    system_prompt="You are a SOC analyst triaging alerts. "
                  "Cite the evidence behind every verdict.",
)

result = agent.run_sync(
    "Scan 192.0.2.10:443 for cert expiry and check its reputation "
    "in our threat feeds."
)
print(result.message)
```

Run:

```bash
python soc_agent.py
```

You should see something like:

```text
192.0.2.10:443 serves an expired cert (not_after 2026-05-30) and is
vulnerable to CVE-2024-3094. Evidence: scan_endpoint + threat feeds
flag the host malicious across 4 sources. Verdict: HIGH, isolate.
```

## 3.5 Gate the action

Finding the problem is the easy half. The moment an agent goes from
*advising* to *acting* — isolating that host, refunding that customer,
disabling that account — you need a gate it cannot talk its way past.
That's the whole point of Tulip: wrap the action in `admit()` and it runs
**only** after it clears policy, holds for a human when the blast radius
warrants it, and lands on a tamper-evident audit trail either way.

```python
from tulip.security import (
    Action, admit, SecurityPolicy, AuditTrail, AdmissionError)

policy = SecurityPolicy()   # conservative defaults: production → human
trail = AuditTrail()        # hash-chained, replayable, can't forge

# The triage above said "isolate 192.0.2.10". Don't just do it — admit it.
risky = Action(
    name="isolate_host", asset="192.0.2.10",
    blast_radius=1, kind="containment", environment="production")

async def isolate():
    ...  # your real containment call (CrowdStrike, firewall, etc.)

try:
    await admit(risky, isolate, policy=policy, trail=trail)
except AdmissionError as e:
    print(e.decision.outcome)   # -> "require_human"; isolate did NOT run

# Either way it's on the record:
print(trail.verify())           # True — chain intact
print(trail.export_jsonl())     # SIEM-ready, one event per line
```

A production-environment action with no human approval is held, not run —
and the decision is recorded whether it ran or not. That `admit()` call is
the difference between a library that *suggests* and a runtime that
*enforces*. See [Why Tulip](../why-tulip.md) for how this compares to a
bare model or framework guardrails, and the [Admission gate
concept](../concepts/security.md) for the full policy surface.

## 4. Stream the events

For UIs and real-time logging, switch to async and consume the typed
event stream:

```python
import asyncio
from tulip.core.events import (
    ThinkEvent, ToolStartEvent, ToolCompleteEvent, TerminateEvent,
)

async def main():
    async for event in agent.run("Scan 192.0.2.10:443 and triage it."):
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
    model="anthropic:claude-sonnet-4-6",
    tools=[...],
    system_prompt="...",
    checkpointer=FileCheckpointer(directory="./threads"),
)

# Day 1
agent.run_sync("Open the investigation for alert A-42.", thread_id="case-4821")

# Day 2 — same thread_id, the investigation continues
agent.run_sync("What did we establish so far?", thread_id="case-4821")
```

For vendor-neutral durability, swap to `S3Backend(bucket=..., namespace=...)`.
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
def isolate_host(host_id: str, incident_id: str) -> dict:
    return edr.isolate(host_id, incident_id)

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[query_siem, isolate_host],
    system_prompt="...",
    reflexion=True,
    checkpointer=S3Backend(bucket="tulip-threads", namespace="..."),
    termination=(
        ToolCalled("isolate_host") & ConfidenceMet(0.9)
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

server = AgentServer(agent=agent)
server.run(host="0.0.0.0", port=8080)
```

`POST /invoke`, `POST /stream`, `GET /threads/{id}`. Deploys
anywhere FastAPI runs — see [Deploy](deploy.md).

## Where to next

- **Read deeper.** [Agent Loop](../concepts/agent-loop.md) is the
  architectural reference for how all of this fits together.
- **Browse examples.** Forty progressive notebooks at
  [`examples/`](https://github.com/tuliplabs-ai/sdk-python/tree/main/examples).
  Each is a single runnable file that adds one idea on top of the
  previous.
- **Steer it.** [Hooks](../concepts/hooks.md) give you logging,
  telemetry, retry, guardrails, and steering as one-line additions.
