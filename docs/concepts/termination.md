# Termination

When does a SOC agent stop working an incident? Tulip
answers that with a typed, composable **algebra of stop conditions** —
small classes that each return `True` when the run should end, combined
with `&` (and) and `|` (or).

```python
from tulip.core.termination import (
    MaxIterations, ToolCalled, ConfidenceMet, TextMention,
)

termination = (
    (ToolCalled("isolate_host") & ConfidenceMet(0.9))
    | TextMention(r"\bESCALATE\b")
    | MaxIterations(10)
)
```

Read it left to right: *stop when the host is isolated and we're
confident in the call, **or** the model flagged it for analyst review
("ESCALATE"), **or** we hit ten iterations* — the last branch caps
runaway tool calls during a live incident.

This is one of the SDK's signature primitives. Every stop condition is
inspectable, unit-testable, and serialisable — no hand-rolled `if`
ladders sprinkled through the response loop.

## When to pick which condition

| Situation | Use |
|---|---|
| Hard cap on tool calls during a live incident / runaway protection | `MaxIterations`, `TokenLimit`, `TimeLimit` |
| Containment is "done" when one specific tool fires | `ToolCalled("isolate_host")` |
| The model is confident and Reflexion agrees | `ConfidenceMet(0.85)` (requires `reflexion=True`) |
| The agent should write a triage summary, not call more tools | `NoToolCalls()` |
| The run ends when the model flags for analyst review | `TextMention(r"\bESCALATE\b")` |
| Custom predicate over `AgentState` | `CustomCondition(fn)` |

## Getting started

### 1. Pick one condition

```python
from tulip.agent import Agent
from tulip.core.termination import MaxIterations

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[query_siem, enrich_indicator],
    termination=MaxIterations(8),
)
```

A single condition is a perfectly fine starting point. `MaxIterations`
is the safety net every production SOC agent should have — it stops the
loop from grinding the SIEM forever on a noisy alert.

### 2. Combine with `&` and `|`

```python
from tulip.core.termination import (
    MaxIterations, ToolCalled, ConfidenceMet,
)

termination = (
    ToolCalled("isolate_host")        # the host was contained
    & ConfidenceMet(0.85)             # we believe the containment call
) | MaxIterations(8)                  # …or the safety cap
```

`&` and `|` are real Python operator overloads (`__and__` / `__or__`)
on `TerminationCondition`, so the result is a typed
`AndCondition` / `OrCondition` you can keep composing, log, or pass
through tests.

### 3. Inspect what stopped the run

```python
result = agent.run_sync(prompt)
print(result.stop_reason)
# → "terminal_tool"   (a fixed StopReason literal)
```

`result.stop_reason` is **normalized** to one of a fixed set of
`StopReason` literals (`complete`, `terminal_tool`, `confidence_met`,
`max_iterations`, `tool_loop`, `no_tools`, `grounding_failed`,
`token_budget`, `time_budget`, `interrupted`, `error`, `cancelled`).
The fuller, branch-level string is on the `TerminateEvent.reason` event
field — each condition's `check()` returns a short reason token
(e.g. `tool_called:isolate_host`, `confidence_met`), and a composite
joins them with `AND`. So watch `TerminateEvent.reason` in your event
stream when you need to know *exactly* which branch fired; key metrics
and control flow on the normalized `result.stop_reason`.

## Built-in conditions

| Condition | Triggers when |
|---|---|
| `MaxIterations(n)` | The ReAct loop has run `n` turns. |
| `TokenLimit(n)` | Cumulative model tokens exceed `n`. |
| `TimeLimit(seconds)` | Wall-clock budget exceeded. |
| `NoToolCalls()` | The most recent turn produced a triage summary and zero tool calls. |
| `ToolCalled(name, args=None)` | A specific tool fired — e.g. `ToolCalled("isolate_host")` (with optional args predicate). |
| `ConfidenceMet(threshold)` | Reflexion confidence ≥ threshold. |
| `TextMention(pattern)` | Final message contains a regex match — e.g. an `ESCALATE` sentinel. |
| `CustomCondition(fn)` | `fn(state) -> bool` — anything you can write in Python. |

Every condition takes `AgentState` and its `check()` returns a
`(stop: bool, reason: str | None)` tuple. They run after each
iteration; the first one that stops wins.

## Custom conditions

Write any predicate over `AgentState`:

```python
from tulip.core.termination import CustomCondition

def host_contained(state) -> bool:
    # Stop only once isolate_host actually returned a containment ticket —
    # not just when the call was emitted.
    return any(
        e.tool_name == "isolate_host" and (e.result or {}).get("ticket")
        for e in state.tool_executions
    )

termination = CustomCondition(host_contained) | MaxIterations(15)
```

Custom conditions compose with built-ins exactly the same way — `&`
and `|` work across the whole hierarchy.

## Common gotchas

| Symptom | Likely cause |
|---|---|
| Agent always stops at `MaxIterations` | The containment condition never fires — model isn't calling `isolate_host`, or confidence never reaches the threshold. Lower the threshold or check the tool name. |
| `&` / `\|` precedence surprises | Python's normal precedence applies: `&` binds tighter than `\|`. Add parentheses when in doubt — `(A & B) \| C` reads cleaner anyway. |
| `ConfidenceMet` never trips | `reflexion=True` is required — without it, confidence stays at the default, so the agent never early-stops on a high-confidence containment. |
| `ToolCalled("isolate_host")` fires before containment completes | It checks the *call*, not the *result*. Pair with `ConfidenceMet` or a `CustomCondition` that inspects `tool_executions` for the returned ticket. |

## Source and notebook

- [`notebook_15_termination.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_15_termination.py) — runnable algebra examples.
- [`tulip.core.termination`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/core/termination.py) — every condition class, plus `__or__` / `__and__`.

## See also

- [Reasoning](reasoning.md) — pair `ConfidenceMet` with `reflexion=True`.
- [Events](events.md) — `TerminateEvent.reason` carries the branch-level reason token(s).
- [Agent loop](agent-loop.md) — where conditions evaluate inside the ReAct cycle.
