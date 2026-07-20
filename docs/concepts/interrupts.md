# Interrupts & human-in-the-loop

Sometimes the agent shouldn't decide alone. A human approves
isolating a production host. An incident lead signs off before an
indicator is blocked fleet-wide. Policy requires an audit checkpoint
between investigation and containment.

Tulip treats human approval as
**a tool the model can call** — same shape as any other tool, except
it surfaces a question to your app and resumes when the human
responds.

For consequential actions the same pause is enforced by the runtime,
not offered to the model — a policy answering `require_human` holds the
action at the [admission gate](security-context.md).

## The shape

The SDK ships a built-in `ask_user` tool. The model calls it like any
other tool; instead of returning a value, the run **pauses** — the
agent yields an `InterruptEvent` and stops. Your app reads the question
off the event, gets an answer, and calls `agent.resume(answer)` to
continue.

```python
from tulip.agent import Agent
from tulip.core.events import InterruptEvent
from tulip.tools.decorator import tool

@tool(idempotent=True)
def isolate_host(host_id: str, incident_id: str) -> dict:
    return edr.isolate(host_id, incident_id)

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[query_siem, isolate_host],   # ask_user is auto-registered
    system_prompt=(
        "You are a SOC incident responder. "
        "Always call ask_user for approval before isolate_host."
    ),
)

async for event in agent.run("Contain host WS-014 if the beacon is malicious."):
    if isinstance(event, InterruptEvent):
        answer = input(f"{event.question} ")   # or Slack / web / email
        async for resumed in agent.resume(answer):
            print(resumed)
```

When the model calls `ask_user`, the runtime captures the question and
yields an `InterruptEvent(question=..., options=..., interrupt_id=...)`,
then pauses. Your app surfaces the question to a human and threads the
answer back via `agent.resume(...)`. You can also expose your own
pause-for-input by calling
[`interrupt(...)`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/core/interrupt.py)
from inside a tool body — `ask_user` is just the built-in wrapper.

## Three ways the human responds

### Synchronous — read from stdin

The simplest case for CLI agents and demos: write your tool to call
`input("[y/N] ")` directly. The thread blocks until the human types.

```python
@tool
def cli_approval(reason: str) -> dict:
    answer = input(f"{reason}\nApprove? [y/N] ").strip().lower()
    return {"approved": answer == "y", "reason": reason}
```

### Async — checkpointer-mediated

For long-running workflows, the agent yields an `InterruptEvent` and
pauses when the model calls `ask_user`. A separate process (browser,
Slack action, email link) eventually resumes. `agent.resume(...)` is an
**async generator**, so you iterate it — you don't `await` it:

```python
async for event in agent.resume("approved"):
    handle(event)
```

The loop threads the response into the next Think and continues
streaming events.

### Steering — a second model votes

Not strictly human-in-the-loop, but lives in the same family. The
`SteeringHook` runs an LLM-as-judge on every tool call before it
fires:

```python
from tulip.hooks.builtin.steering import SteeringHook

agent = Agent(
    ...,
    hooks=[SteeringHook(
        model="anthropic:claude-sonnet-4-6",
        policy="Reject any tool call that doesn't match the analyst's stated request.",
    )],
)
```

When the judge votes "no", the call is rejected and the agent
re-plans. This is policy enforcement, not human review — but it's
the same shape: a checkpoint between Think and Execute.

## Cancelling a run mid-flight

Three ways to stop a running agent without waiting for the
termination algebra to fire:

1. **Hook raises to short-circuit the loop.** Any hook callback can
   raise to abort the run. Useful for budget guards.

   ```python
   class BudgetGuard(HookProvider):
       async def on_iteration_start(
           self, iteration: int, state: AgentState
       ) -> None:
           if state.total_tokens_used > 100_000:
               raise RuntimeError("token budget exceeded")
   ```

2. **Caller cancels the task.** Standard `asyncio` cancellation:

   ```python
   run = asyncio.create_task(agent.run(prompt))
   # ... later
   run.cancel()
   ```

3. **`agent.cancel()`.** Sets a flag the runner polls between nodes;
   the loop exits at the next safe point with
   `TerminateEvent(reason="cancelled")` (and `result.stop_reason ==
   "cancelled"`). State still flushes to the checkpointer first, so the
   conversation can resume cleanly later.

In the `agent.cancel()` case the loop emits a final
`TerminateEvent(reason="cancelled")` so your downstream observability
gets a clean signal.

## What you don't lose on cancel

Cancelled runs **still persist state** to the checkpointer. The
`thread_id` retains the conversation up to the moment of cancel.
You can resume later with the same thread, inspect the state for
debugging, or branch off a new thread from the partial conversation.

## See also

- [Agent Loop](agent-loop.md) — where cancellation is observed in the
  runner.
- [Hooks](hooks.md) — write custom hooks that raise to abort the run.
- [Conversation Management](conversation-management.md) — how
  `thread_id` resumption works.
- [Human in the loop](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_19_human_in_the_loop.py)
  — a full runnable example.
- [Multi-agent + HITL](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_33_multiagent_human_in_loop.py)
  — three HITL patterns in one file (approval gate, human-as-tool,
  long-pause snapshot/resume).
- [Incident response](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_63_incident_response.py)
  — `interrupt()` as the page-the-human gate after severity
  classification.
- [Vendor security review](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_64_procurement_approval.py)
  — three stacked `interrupt()` gates on the top tier.
- [Contract review](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_65_contract_review.py)
  — `interrupt()` for human counsel inside a refinement loop.
