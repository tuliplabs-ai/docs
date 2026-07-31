# Handoff

Handoff is what an escalation desk does. One agent owns the
case, decides it needs a different tier, and hands a
**structured summary** — findings, progress, and key context — to the
next agent, who picks up where it left off.

![Handoff pattern — L1 support agent classifies the ticket, hands the full transcript to an L2 billing specialist who resolves the case](../../img/patterns/handoff.svg){ .diagram }

## What it is

A handoff flow has:

- A pool of **`HandoffAgent`s** — each a named agent that can receive a
  handoff, with optional `can_escalate_to` / `can_delegate_to` paths.
- A **`Handoff` manager** (build it with `create_handoff_manager`) — it
  registers the agents, enforces a max handoff-chain length, and records
  the chain of custody.

When the manager runs `execute_handoff(...)`, it packages the source
agent's progress into a typed **`HandoffContext`** — original task,
findings, a progress summary, and instructions — and hands it to the
target agent. The target reads that context as the next turn of the
same case.

## When to use it

- ✅ **Support-desk escalation (L1 support → L2 billing)** where the
  case is the unit of work.
- ✅ **SOC tier escalation (L1 → L2 → L3)** — the same shape for a
  security operations center.
- ✅ **"Pass to a human"** — the on-call human simply replaces
  one of the targets.
- ✅ **Escalation** when the first agent realises the case is above
  its tier (after a few turns of triage, not on first read).
- ✅ The case should **carry its findings and progress
  forward** so the next tier doesn't re-triage from scratch when
  control transfers.

## When NOT to use it

- ❌ The coordinator delegates a **sub-task** and waits for the
  answer (the conversation belongs to the coordinator) — use
  [Orchestrator](orchestrator.md) instead.
- ❌ Multiple agents should **process the conversation in parallel**
  — use [Composition](composition.md) or [Swarm](swarm.md).
- ❌ The flow is **fully scripted** — handoff is for cases where
  the routing emerges from the conversation.

## Difference vs Orchestrator

| | Handoff | Orchestrator |
|---|---|---|
| Case owner | **moves** between agents | stays with the coordinator |
| Routing decision | the agent that's currently in charge | always the coordinator |
| Receiving agent's view of history | the handoff summary (findings + progress) | just the sub-task they were dispatched for |
| Drives the live case? | usually yes | usually no |

## Code

```python
from tulip.multiagent import (
    HandoffReason,
    create_handoff_agent,
    create_handoff_manager,
)

model = "anthropic:claude-sonnet-4-6"

triage = create_handoff_agent(
    name="L1 Support",
    system_prompt=(
        "You are L1 support triage on incoming tickets. "
        "Decide whether this is a billing, shipping, or account case, "
        "then escalate to the right specialist."
    ),
    tools=[lookup_order, lookup_customer],
    model=model,
)
billing = create_handoff_agent(
    name="L2 Billing",
    system_prompt="You are an L2 billing specialist handling escalations.",
    tools=[lookup_order, issue_refund],
    model=model,
)
accounts = create_handoff_agent(
    name="L3 Accounts",
    system_prompt="You are an L3 account specialist handling account takeovers.",
    tools=[lock_account],
    model=model,
)

# Declare the escalation paths (by agent id).
triage.can_escalate_to = [billing.id, accounts.id]

manager = create_handoff_manager(agents=[triage, billing, accounts])

# Hand the case from L1 support up to the L2 billing specialist.
result = await manager.execute_handoff(
    source_agent=triage,
    target_agent_id=billing.id,
    task="Customer 4821 reports a duplicate charge on order ord-4821.",
    reason=HandoffReason.ESCALATION,
    findings={"ticket_id": "t-8804", "order": "ord-4821"},
)
```

`execute_handoff` is async — `await` it. It returns a `HandoffResult`
from the target agent. `HandoffReason` enumerates why the handoff
happened (`SPECIALIZATION`, `ESCALATION`, `DELEGATION`, ...).

## What transfers across the handoff

The `HandoffContext` the target agent receives carries:

- `original_task` — the task the chain started from.
- `findings` and `progress_summary` — what the source agent learned,
  rendered into the target's opening prompt.
- `confidence` — the source agent's self-estimated confidence so far.
- `instructions` — any specific guidance for the next tier.
- `handoff_chain` — the chain of custody (who handed to whom).

By default the raw message transcript is **not** forwarded —
`preserve_full_history` is `False`, so the next tier reads the summary,
not every prior turn. Set `preserve_full_history=True` on the manager to
attach key messages (the system message plus the last few), but the
prompt the target sees is still built from the findings and progress
summary above.

## Notebooks

- [`notebook_25_agent_handoff.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_25_agent_handoff.py)
  — full L1 triage + malware + phishing + intrusion escalation flow.
- [`notebook_33_multiagent_human_in_loop.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_33_multiagent_human_in_loop.py)
  — handoff to a human via `interrupt()` (one of three
  human-in-the-loop (HITL) patterns in the same file).

## Source

[`multiagent/handoff.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/multiagent/handoff.py).

## See also

- [Conversation Management](../conversation-management.md) — how the
  thread is checkpointed across the handoff.
- [Multi-agent overview](../multi-agent.md) — pick a shape.
