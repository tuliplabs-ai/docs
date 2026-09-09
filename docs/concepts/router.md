# Cognitive router

Describe a task in plain language and the router compiles it onto a real
runtime primitive — an `Agent`, a `SequentialPipeline`, an `Orchestrator`,
a `LoopAgent`, a `Handoff` chain, an `A2AClient`. You do not pick the
shape and neither does the model.

The model does exactly one thing: it fills a typed
[`GoalFrame`](#the-goalframe). Everything after that — which protocol
handles the frame, which capabilities bind to it, whether policy allows
it, what gets compiled — is a pure function of that frame and the
registry. **The model classifies; routing is deterministic. It never
authors the topology.**

That split is the whole point. A model that picks its own control flow
can pick a different one next time, and there is nothing to review. A
model that fills a schema produces an artifact you can diff, replay,
and gate.

## When to reach for the router

| You want… | Use |
|---|---|
| One known shape you already chose | the primitive directly — [Multi-agent](multi-agent.md) |
| A front door over many shapes, chosen per request | ✓ the router |
| Risk to decide whether something runs at all | ✓ the router's [policy gate](#the-policy-gate) |
| To ban a shape outright for a deployment | ✓ `PolicyGate(denied_protocols=…)` |
| To audit why a request routed the way it did | ✓ [`router.explain()`](#asking-why) |
| Conditional edges inside one known graph | [StateGraph](multi-agent/graph.md), not the router |

## The pipeline

```text
  "drain node 7 and restart payments"
                │
                ▼
       ┌─────────────────┐
       │   extractor     │  one model call — Agent(output_schema=GoalFrame)
       └────────┬────────┘
                │  GoalFrame  (typed, frozen)
                ▼
       ┌─────────────────┐
       │  filter gates   │  handles ∋ primary_goal
       │                 │  risk_max ≥ frame.risk
       │                 │  requires_capabilities ⊆ available
       └────────┬────────┘
                │  surviving protocols
                ▼
       ┌─────────────────┐
       │      rank       │  complexity-fit → canonical → cost → specificity
       └────────┬────────┘
                │  one protocol
                ▼
       ┌─────────────────┐
       │   policy gate   │  deny · allow · allow-behind-approval
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │    compile      │  a real Agent / Pipeline / Orchestrator / …
       └─────────────────┘
```

Only the first box calls a model. Everything below it is deterministic,
which is why `explain()` can replay the whole decision for free.

## The GoalFrame

The one object the model authors. It is frozen once extracted.

| Field | What it drives |
|---|---|
| `primary_goal` | The `TaskType` the protocol registry filters on |
| `secondary_goals` | Tiebreaker only |
| `domain` | Scopes the capability pool via `CapabilityIndex.for_domain` |
| `complexity` | Ranks candidates — the *first* rank term |
| `risk` | Checked against each protocol's `risk_max` and the gate's thresholds |
| `required_capabilities` | Must all be available or the protocol is filtered out |
| `success_criteria` | Plain-text criteria a validator stage checks against |
| `requires_tools` / `_memory` / `_code_generation` / `_multi_agent` / `approval_required` | Builder hints |

`TaskType` is a closed set of thirteen: `answer`, `explain`, `plan`,
`build`, `modify`, `diagnose`, `remediate`, `generate_code`, `research`,
`compare`, `monitor`, `coordinate`, `escalate`. `Risk` and `Complexity`
are each `low` / `medium` / `high`.

## The eight protocols

`builtin_protocols()` returns the full catalogue. Register all of them or
a subset — a registry holding three protocols can only ever compile three
shapes, which is itself a control.

| Protocol | What it compiles to | `risk_max` | Cost / latency | Canonical for |
|---|---|---|---|---|
| `direct_response` | one agent | low | low / low | `answer`, `explain` |
| `plan_execute_validate` | three-stage pipeline | medium | medium / medium | `plan`, `build`, `modify` |
| `specialist_fanout` | fan out, then correlate | medium | high / high | `diagnose`, `monitor`, `research` |
| `debate` | two debaters + a judge | low | high / high | `compare` |
| `codegen_test_validate` | loop until the agent declares `PASS` | medium | medium / high | `generate_code` |
| `approval_gated_execution` | one agent behind a forced approval interrupt | **high** | medium / medium | `escalate`, `remediate` |
| `a2a_delegate` | hand off to a remote agent over A2A | medium | medium / high | `coordinate` |
| `handoff_chain` | sequential one-tool agents, each adding a fact | medium | medium / high | `coordinate` |

`a2a_delegate` additionally needs `BuilderContext.a2a_endpoint` set at
compile time.

## How one is chosen

**Three gates.** A protocol survives only if it clears all three:

- `frame.primary_goal in protocol.handles`
- `protocol.risk_max >= frame.risk`
- `set(protocol.requires_capabilities) <= available_capabilities`

An empty survivor list is a valid outcome and raises
`NoMatchingProtocolError` at the caller. Nothing falls back to a default
shape.

**Four-part rank**, lower wins, applied in order:

1. **Complexity fit** — distance between the protocol's declared cost and
   the frame's complexity. This is deliberately first: a `low`-complexity
   task should never land on a `high`-cost protocol just because that
   protocol claims the goal type.
2. **Canonical** — does the protocol name this `primary_goal` in
   `primary_for`? Breaks fit ties.
3. **Cost** — cheaper wins.
4. **Specificity** — fewer `handles` wins. Rarely reached.

## The policy gate

`PolicyGate` runs after selection, on the `(frame, protocol)` pair, and
returns a `PolicyVerdict` with three possible shapes.

```python
from tulip.router import PolicyGate
from tulip.router.goal_frame import Risk

gate = PolicyGate(
    max_risk=Risk.HIGH,                  # strictly above → denied
    require_approval_above=Risk.MEDIUM,  # strictly above → approval interrupt
    denied_protocols={"a2a_delegate"},   # never compile this shape here
)
```

Two thresholds and one ban list:

- **`max_risk`** — anything strictly above is denied outright. Defaults
  to `HIGH`, so nothing is denied by risk alone until you lower it.
- **`require_approval_above`** — within `max_risk` but above this band,
  the run compiles and then parks on an approval interrupt. Defaults to
  `MEDIUM`, so `HIGH`-risk frames need a human by default.
- **`denied_protocols`** — protocol ids this deployment refuses. Checked
  **before any risk math**, so a banned shape is refused whatever the
  frame says.

That last one is the part worth dwelling on. The other two govern *how
risky an action may be*; `denied_protocols` governs **the shape choice
itself** — the control plane's answer to "goals from this team must never
compile to an `a2a_delegate`, no matter how the model frames them."

!!! note "Risk decides, not confidence"
    The frame's risk band is what gates execution — never the model's
    confidence in its own classification. A `low`-risk "summarise this
    runbook" runs straight through. A `high`-risk "drain a prod node and
    restart payments" compiles behind an approval interrupt and does not
    execute until a human says so.

## Asking why

Routing computes a full evidence trail and then throws it away.
`explain()` returns it instead, and executes nothing.

```python
async def why() -> None:
    explanation = await router.explain("Delete every record older than 7 years")

    print(explanation)      # human-readable
    explanation.rejected    # every protocol ruled out, and which gate stopped it
    explanation.candidates  # survivors, best first, with their rank terms
```

One model call, for the extraction. Pass a `frame=` you already have and
it costs nothing at all, because selection, ranking and the policy check
are pure functions.

This is **structured evidence, not chain-of-thought**. Every field is a
fact about the registry, the frame and the policy — which gate rejected
what, how survivors ranked and on which term, what the verdict was. The
model's private reasoning is deliberately not exposed; when the opt-in
LLM picker runs, only the short rationale it returned *as data* is
carried.

## Pinning a frame

`dispatch()` accepts a `frame=` that skips extraction entirely.

```python
async def resume(user_input: str, approved_frame: GoalFrame) -> None:
    result = await router.dispatch(user_input, frame=approved_frame)
```

This is the resume seam. A dispatch that parked on an approval hold must
replay under the **same frame the approval was granted against**. A live
extractor re-reading the goal can frame it differently, select a
different protocol, and re-hold what a human already approved — forever.
A pinned frame still flows through `on_frame` and the event bus, so
consumers see an identical stream either way.

Pass `run_id=` to correlate a dispatch with your own request id, Slack
thread, or trace. It scopes every emitted `StreamEvent` and is attached
to the result payload; omit it and you get a fresh `uuid4`.

## Getting started

```python
import asyncio

from tulip import Agent, tool
from tulip.router import (
    Router, CognitiveCompiler, ProtocolRegistry,
    PolicyGate, CapabilityIndex, GoalFrame, builtin_protocols,
)
from tulip.tools.registry import create_registry


@tool
def search(q: str) -> str:
    """Search the knowledge base."""
    ...


tools = create_registry(search)
capabilities = CapabilityIndex(tools)
capabilities.annotate(
    "kb_search",
    tool_name="search",
    description="Knowledge base search.",
    domain="research",
)

protocols = ProtocolRegistry()
protocols.register_many(builtin_protocols())

extractor = Agent(model="...", output_schema=GoalFrame)
compiler = CognitiveCompiler(
    protocols=protocols,
    capabilities=capabilities,
    policy=PolicyGate(),
    model="...",
)
router = Router(extractor=extractor, compiler=compiler)

async def main() -> None:
    result = await router.dispatch("What does the retention policy say?")
    print(result.text, result.protocol_id)


asyncio.run(main())
```

## Reference

- [`tulip/router/`](https://github.com/tuliplabs-ai/tulip-agents/tree/main/src/tulip/router) — the whole layer.
- [`goal_frame.py`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/src/tulip/router/goal_frame.py) — the schema the model fills.
- [`protocol.py`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/src/tulip/router/protocol.py) — the eight protocols, the gates, the rank.
- [`policy.py`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/src/tulip/router/policy.py) — `PolicyGate` and `PolicyVerdict`.
- [`explain.py`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/src/tulip/router/explain.py) — the evidence trail.
- [`notebook_58_cognitive_router.py`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/examples/notebook_58_cognitive_router.py) — risk-gated routing for infra requests, end to end.

## See also

- [Multi-agent](multi-agent.md) — the eight shapes the router compiles onto.
- [Interrupts](interrupts.md) — how an approval-gated dispatch parks and resumes.
- [The control layer](security-context.md) — where routing decisions meet the gate.
- [Structured output](structured-output.md) — the `output_schema` mechanism the extractor uses.
