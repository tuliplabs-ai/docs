# Idempotency

> Tulip deduplicates identical tool calls within a documented execution scope.

The model may retry. With `idempotent=True`, an identical call in the same
agent run reuses the recorded result instead of invoking the tool body again.
When supported execution state is restored from a checkpoint, that recorded
result can also prevent a replay after resume.

If you ever plan to run an agent that **refunds**, **deploys**,
**pages**, **emails**, or **writes**, this is the most important
single page on the docs site.

## When to use `idempotent=True`

| Situation | `idempotent=True`? |
|---|---|
| Side-effecting tool with real-world cost (issue a refund, ship a deploy, page on-call) | Usually yes, plus a downstream idempotency key |
| Database write you can't trivially roll back | **yes** |
| External service that's already idempotent on its end | yes — the SDK dedupes the round-trip too |
| Read-only order lookup | no — re-reads are cheap, leave it to the model |
| Tool that *intentionally* generates a new entity each call (e.g. `mint_case_id`) | no — that breaks the contract |

## How it works

Inside a single agent run, the SDK hashes the tool's
`(name, arguments)` tuple as the model emits each call. **The first
call with a given key hits the function body** and the result is
recorded. **Every subsequent call with the same key short-circuits
to the cached response** without invoking the body.

```python
from tulip.tools import tool
@tool(idempotent=True)
def issue_refund(order_id: str, amount: float) -> dict:
    """Refund an order. Re-fires within a run return the cached receipt."""
    return billing.refund(order_id, amount)
```

The argument hash is the trust boundary:

- **Same call**: the model re-emits `issue_refund("ord-4821", 120.0)` after
  seeing the receipt → cache hit, body skipped.
- **Different call**: the model emits `issue_refund("ord-4822", 120.0)` →
  different key, body runs.

Dedup compares the **raw arguments dict** the model emitted, exactly as
it emitted it — a plain `dict == dict` equality on `(tool_name,
arguments)`. There is no JSON canonicalization and **no schema
normalization**: defaults are *not* filled in before the comparison, so
a call that omits an optional argument and a call that passes that
argument's default value are treated as **different keys** and both fire
the body. (Dict equality is itself order-independent, so key order alone
won't break a match.)

## Why this matters

### Actions with real-world cost

The model that calls `issue_refund` twice in one run is more common
than you think. Sometimes it sees an ambiguous tool result and tries
again "to be sure". Sometimes the network glitches and the model
believes the call failed. Without idempotency, the customer is refunded
twice and finance opens a ticket for the duplicate.

```python
@tool(idempotent=True)
def issue_refund(order_id: str, amount: float) -> dict:
    return billing.refund(order_id, amount)
```

Within the active run, an identical second call reuses the first result. The
same mechanism applies to a deploy (`deploy_service`), a page (`page_oncall`),
and the security-operations variant (`isolate_host`).

### Outbound side-effects

`page_oncall`, `open_case`, `slack_alert`, `block_indicator` — anything
that touches a human or a downstream system. **One and done**.

### Database writes you can't roll back

Insert into an audit table, append to a Kafka topic, sign a JWT —
operations where retrying isn't free. Idempotent tools reduce duplicate calls
inside the agent runtime; they do not create distributed exactly-once delivery.

### Replays after checkpoint resume

When a checkpointer resumes a stalled run, the model may decide to
re-issue tool calls it's already seen. Idempotent tools see the
cache pre-populated from the checkpoint and skip the side effect on
replay. (This requires `tool_executions` to be restored from the
checkpoint; the SDK's [native checkpointers](checkpointers.md) handle
it.)

## What it is *not*

| Concept | Idempotency is… | Idempotency is *not*… |
|---|---|---|
| Scope | within a single agent run | cross-run — restart and the cache is gone (use a [checkpointer](checkpointers.md)) |
| Failure | one fire per identical call | retry — if the body raises, the exception propagates as the cached "result" |
| Boundary | per-agent | network — two different agents both calling `issue_refund(o, a)` each fire once |

If you need cross-run idempotency, configure a checkpointer and an idempotent
server-side endpoint. Generate a stable operation key from the business
operation (for example, `refund:ORD-4821:v1`) and send it to that endpoint on
every attempt.

## The external-success crash window

There is an unavoidable boundary between two systems:

1. the payment, deploy, or message succeeds in the external service;
2. the process stops before Tulip durably records the returned receipt;
3. the run resumes and cannot prove locally that the external call succeeded;
4. the call may be attempted again.

An in-memory cache cannot close that window. A checkpointer narrows it, but the
downstream system must recognize the same stable idempotency key and return the
original result rather than repeat the operation. Treat `idempotent=True` as
agent-loop deduplication and downstream keys as distributed-operation safety.

## Practical recipe — refund approval

A canonical multi-agent idempotency shape: an agent (or three of
them, debating) loops over a refund decision, then writes once.

```python
@tool(idempotent=True)
def issue_refund(order_id: str, amount: float) -> dict:
    return billing.refund(order_id, amount)

@tool(idempotent=True)
def page_oncall(case_id: str, summary: str) -> str:
    return pager.notify(team="support", subject=f"CASE {case_id}", body=summary)
```

The agent can iterate while reasoning about whether to refund. Repeated calls
with identical raw arguments reuse the cached result in the supported scope.
For a real payment or page, the tool body should also pass a stable
idempotency key to the provider.

## Common gotchas

| Symptom | Likely cause |
|---|---|
| Tool re-fires despite `idempotent=True` | Argument changed between calls. Check that the model isn't mutating order ids / amounts between turns. |
| Idempotent cache survives across runs unexpectedly | It shouldn't — only the checkpointer persists state. If you're seeing this, you're loading state from a checkpoint and don't want to. |
| Body raised first time, cache returns the exception | This is by design — the failure is part of the "result" of the first call. The model sees the failure and can react. To re-attempt, the model must change an argument. |
| Read-only lookup tagged `idempotent=True` | Harmless but wasteful — the cache hit savings are negligible vs the read itself. Leave it off. |

## Source and notebook

- [`@tool` decorator with idempotency hook](https://github.com/tuliplabs-ai/tulip-agents/blob/main/src/tulip/tools/decorator.py)
- [`_find_matching_execution`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/src/tulip/loop/nodes.py#L114) — where the dedup actually happens, in the ReAct loop's Execute node.
- [`notebook_07_agent_with_tools.py`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/examples/notebook_07_agent_with_tools.py) — walks through the `@tool` decorator end-to-end (idempotency covered in the agent-loop walkthrough).

## See also

- [Tools](tools.md) — the full `@tool` decorator surface.
- [Checkpointers](checkpointers.md) — durable runs where idempotency interacts with replay.
