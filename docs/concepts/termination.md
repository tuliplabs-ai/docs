# Termination

When does an agent stop — the refund resolved, the deploy verified,
the incident contained? Tulip
answers that with a typed, composable **algebra of stop conditions** —
small classes that each return `True` when the run should end, combined
with `&` (and) and `|` (or).

```python
from tulip.core.termination import (
    MaxIterations, ToolCalled, ConfidenceMet, TextMention,
)

termination = (
    (ToolCalled("issue_refund") & ConfidenceMet(0.9))
    | TextMention(r"\bESCALATE\b")
    | MaxIterations(10)
)
```

Read it left to right: *stop when the refund is issued and we're
confident in the call, **or** the model flagged it for human review
("ESCALATE"), **or** we hit ten iterations* — the last branch caps
runaway tool calls on a live account. A containment flow reads the
same way — `ToolCalled("isolate_host") & ConfidenceMet(0.9)` — the
algebra doesn't care which domain the tools come from.

This is one of the SDK's signature primitives. Every stop condition is
inspectable, unit-testable, and serialisable — no hand-rolled `if`
ladders sprinkled through the response loop.

## When to pick which condition

| Situation | Use |
|---|---|
| Hard cap on tool calls against live systems / runaway protection | `MaxIterations`, `TokenLimit`, `TimeLimit` |
| The run is "done" when one specific tool fires | `ToolCalled("issue_refund")` |
| The model is confident and Reflexion agrees | `ConfidenceMet(0.85)` (requires `reflexion=True`) |
| The agent should write a summary, not call more tools | `NoToolCalls()` |
| The run ends when the model flags for human review | `TextMention(r"\bESCALATE\b")` |
| Custom predicate over `AgentState` | `CustomCondition(fn)` |

## Getting started

### 1. Pick one condition

```python
from tulip.agent import Agent
from tulip.core.termination import MaxIterations

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[lookup_order, issue_refund],
    termination=MaxIterations(8),
)
```

A single condition is a perfectly fine starting point. `MaxIterations`
is the safety net every production agent should have — it stops the
loop from grinding your APIs forever on a request it can't resolve.

### 2. Combine with `&` and `|`

```python
from tulip.core.termination import (
    MaxIterations, ToolCalled, ConfidenceMet,
)

termination = (
    ToolCalled("issue_refund")        # the refund went out
    & ConfidenceMet(0.85)             # we believe the call
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
| `NoToolCalls()` | The most recent turn produced a summary and zero tool calls. |
| `ToolCalled(name, args=None)` | A specific tool fired — e.g. `ToolCalled("issue_refund")` (with optional args predicate). |
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

def refund_settled(state) -> bool:
    # Stop only once issue_refund actually returned a receipt —
    # not just when the call was emitted.
    return any(
        e.tool_name == "issue_refund" and (e.result or {}).get("receipt")
        for e in state.tool_executions
    )

termination = CustomCondition(refund_settled) | MaxIterations(15)
```

Custom conditions compose with built-ins exactly the same way — `&`
and `|` work across the whole hierarchy.

## Common gotchas

| Symptom | Likely cause |
|---|---|
| Agent always stops at `MaxIterations` | The "done" condition never fires — model isn't calling `issue_refund`, or confidence never reaches the threshold. Lower the threshold or check the tool name. |
| `&` / `\|` precedence surprises | Python's normal precedence applies: `&` binds tighter than `\|`. Add parentheses when in doubt — `(A & B) \| C` reads cleaner anyway. |
| `ConfidenceMet` never trips | `reflexion=True` is required — without it, confidence stays at the default, so the agent never early-stops on a high-confidence resolution. |
| `ToolCalled("issue_refund")` fires before the refund settles | It checks the *call*, not the *result*. Pair with `ConfidenceMet` or a `CustomCondition` that inspects `tool_executions` for the returned receipt. |

## Source and notebook

- [`notebook_15_termination.py`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/examples/notebook_15_termination.py) — runnable algebra examples.
- [`tulip.core.termination`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/src/tulip/core/termination.py) — every condition class, plus `__or__` / `__and__`.

## See also

- [Reasoning](reasoning.md) — pair `ConfidenceMet` with `reflexion=True`.
- [Events](events.md) — `TerminateEvent.reason` carries the branch-level reason token(s).
- [Agent loop](agent-loop.md) — where conditions evaluate inside the ReAct cycle.
