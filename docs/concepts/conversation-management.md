# Conversation management

An Tulip agent holds one user's
conversation in `state.messages`. To make that conversation **survive
across requests** — across deploys, restarts, and "I'll come back
tomorrow" gaps — you wire a checkpointer and a `thread_id`.

## The minimum

```python
from tulip.agent import Agent
from tulip.memory.backends import S3Backend

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[...],
    checkpointer=S3Backend(
        bucket_name="tulip-threads",
        namespace="<your-namespace>",
    ),
)

# Day 1
agent.run_sync("Investigate the beacon from host WIN-7731.", thread_id="case-7731")

# Day 2 — same thread_id, conversation continues
agent.run_sync("What did we conclude?",                      thread_id="case-7731")
# → "We traced the WIN-7731 beacon to a known C2 endpoint. Want me to draft the containment ticket?"
```

The `thread_id` is the unit of conversation. Every node that runs
saves state to the checkpointer; every fresh `agent.run_sync(...,
thread_id=...)` call rehydrates state before the first Think.

## Threads, not sessions

The SDK uses **thread** as the term — borrowing from chat UIs and
issue trackers — because a single investigation can have many
simultaneous conversations:

| Thread | Use |
|---|---|
| `case-7731-triage` | an open SOC triage conversation for one alert |
| `case-7731-hunt` | a parallel threat-hunt the same analyst kicked off |
| `hunt-c2-sweep-q3` | a long-running autonomous sweep not tied to a single case |

A thread is a string. Pick the convention that matches your domain.

## What gets persisted

The checkpointer saves the full `AgentState`:

- **`messages`** — system prompt, every user message, every model
  message, every tool result.
- **`tool_executions`** — the dedup history Execute walks for
  idempotent calls.
- **`iterations`** — the running counter (so termination conditions
  resume correctly).
- **`metadata`** — your application's per-thread state.

Hooks see frozen events on save and load. Custom application data
goes in `metadata`.

## Thread lifecycle

```python
# List all threads in a bucket
threads = await checkpointer.list_threads()
# → ["case-7731-triage", "case-7731-hunt", ...]

# Inspect one
state = await checkpointer.load("case-7731-triage")
print(len(state.messages), "messages")

# Branch — new thread, copy of an existing one
await checkpointer.copy_thread(
    source_thread_id="case-7731-triage",
    dest_thread_id="case-7731-triage-replay",
)

# Drop
await checkpointer.delete("case-7731-replay")

# Vacuum old threads via lifecycle policy (per backend)
```

For S3-compatible object storage, retention is enforced by the bucket's
lifecycle policy — *not* by tulip. Configure
`days_until_archive` / `days_until_delete` once at the bucket
level and the store handles the cleanup.

## Concurrent updates to the same thread

Two `agent.run(...)` calls against the same `thread_id` are usually a
bug — you'll race on the checkpoint. Three patterns to avoid that:

1. **Per-case lock at the application layer.** Most SOC consoles already
   serialise messages per session.
2. **Distinct sub-threads.** If the analyst asks two things in
   parallel, give them two thread ids.
3. **Last-write-wins is the default.** The SDK's checkpointers do not
   currently expose a conflict exception — if you need optimistic
   concurrency, layer it at the application or database level.

## Compaction — keep long threads in budget

After dozens of turns, even the most disciplined conversation
exceeds the model's context window. The `LLMCompactor` is the
built-in `ConversationManager` that summarises old turns while
protecting:

- The system prompt.
- The first N user/assistant turns (the "anchor" of the
  conversation).
- A trailing fraction of recent turns (the context the model needs).

```python
from tulip.memory.compactor import LLMCompactor

async def summarise(messages: list) -> str:
    """Your summarise function — typically a small-model call."""
    ...

agent = Agent(
    ...,
    conversation_manager=LLMCompactor(
        context_length=128_000,        # the model's context window
        trigger_fraction=0.85,         # compact when usage hits 85%
        head_turns=2,                  # first 2 turns kept verbatim
        tail_token_fraction=0.4,       # ~40% of budget reserved for recent turns
        summarize_fn=summarise,
    ),
)
```

The compactor runs on the way **into** Think — only when estimated
token usage exceeds `trigger_fraction * context_length`. In short
threads it never fires.

## Retrieving a single thread for a UI

The reference `AgentServer` (`POST /invoke`, `POST /stream`,
`GET /threads/{id}`) reads the thread directly from the checkpointer
and returns the message list — useful for rendering chat history on
page load.

```python
GET /threads/case-7731-triage
# → { "messages": [...], "iterations": 9, ... }
```

## See also

- [Checkpointers](checkpointers.md) — the nine native backends and
  their tradeoffs.
- [Streaming & Server](server.md) — `AgentServer` and SSE.
- [Hooks](hooks.md) — observe save/load events.
