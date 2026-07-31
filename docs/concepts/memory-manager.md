# Long-term memory

A Tulip SDK agent is stateless
between sessions by default. Checkpointing preserves the full message
history for one thread, but the pricing exceptions learned handling
customer A are invisible when helping customer B — and when a thread is
deleted, everything the agent learned goes with it.

`MemoryManager` fills that gap. It runs two lifecycle hooks
on every agent invocation:

| Hook | When | What |
|---|---|---|
| `on_session_start` | Before the first model call | Retrieve stored memories → inject into system prompt |
| `on_session_end` | After the agent stops | Extract durable facts from the conversation → persist to store |

The result: a support agent accumulates standing rules, pricing
exceptions, and customer preferences across cases — without the
context window ever filling up with raw history.

## Where memories live

All memories are persisted via a
[`BaseStore`](checkpointers.md#the-built-in-store-inmemorystore) backend
— the same store abstraction used for cross-thread key-value storage.
The built-in `InMemoryStore` is the only `BaseStore` that ships — it
covers local development and tests, but it is process-local and not
durable. For distributed or persistent production workloads, implement
a custom `BaseStore` subclass over Redis / Postgres / etc. (or use
`Mem0MemoryManager`); no durable `BaseStore` backend ships out of the
box.

Storage layout inside the store:

```
(namespace_prefix..., memory_type)  →  key: memory.key  →  value: {...}
```

With the default prefix `("tulip_memory",)`:

```
("tulip_memory", "user")       →  "role":             {content: "Tier-2 support agent"}
("tulip_memory", "feedback")   →  "refund_approval":  {content: "Refunds over $500 need manager approval. Why: ..."}
("tulip_memory", "project")    →  "billing_rollout":  {content: "Driven by the new billing rollout, not backlog"}
("tulip_memory", "reference")  →  "orders_api":       {content: "Orders tracked in the 'orders' service API"}
```

Each memory key acts as a stable identifier: re-extracting the same
fact under the same key **updates** the record, not duplicates it.

## Memory types

| Type | What to store | Decays? |
|---|---|---|
| `user` | Operator role, tier, shift, expertise | Rarely |
| `feedback` | Standing rules, playbook steps — what to do/avoid and *why* | Rarely |
| `project` | Active cases, customer-specific exceptions, decisions taken | Fast — include a *Why* |
| `reference` | Pointers to external systems, tuned queries, data feeds, runbooks | Medium |

## Quick start

```python
from tulip.agent import Agent
from tulip.memory.manager import LLMMemoryManager, Memory, MemoryType
from tulip.memory.store import InMemoryStore

store = InMemoryStore()   # swap for a persistent backend in production

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    memory_manager=LLMMemoryManager(store=store),
)

# Session 1 — agent learns a standing rule
async for event in agent.run("Refunds over $500 need manager approval — page the duty manager first."):
    ...

# Session 2 — the agent already knows
async for event in agent.run("The customer on order ord-4821 wants a $750 refund. What do you do?"):
    ...
# → agent requests manager approval before refunding, no reminder needed
```

## Supplying an LLM extraction function

The built-in heuristic (pattern-matching on message text) is adequate
for demos.  For production, pass an async `extract_fn` that calls a
cheap model to identify what is worth remembering:

```python
from tulip.memory.manager import LLMMemoryManager, Memory, MemoryType

async def my_extractor(messages: list) -> list[Memory]:
    # Call a fast auxiliary model.
    # The model receives the conversation; it returns structured memory entries.
    raw = await auxiliary_model.complete(
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user",   "content": format_conversation(messages)},
        ]
    )
    return parse_memories(raw.message.content)

manager = LLMMemoryManager(
    store=store,
    extract_fn=my_extractor,
)
```

A minimal extraction prompt:

```
You are a memory extraction assistant. Given a conversation, identify
facts worth remembering across sessions. Return JSON:

[
  {"type": "user",      "key": "role",           "content": "..."},
  {"type": "feedback",  "key": "refund_approval","content": "... Why: ... How to apply: ..."},
  {"type": "project",   "key": "billing",        "content": "... Why: ..."},
  {"type": "reference", "key": "orders_api",     "content": "..."}
]

Only include facts that are non-obvious, durable, and actionable.
Return [] if nothing is worth remembering.
```

## Scoping per user or tenant

Pass a richer `namespace_prefix` to isolate memories per user, team,
or tenant:

```python
manager = LLMMemoryManager(
    store=shared_store,
    namespace_prefix=("tenants", tenant_id, "users", user_id),
)
```

Each combination gets its own set of memories — no cross-contamination.

## Persistent backends

The SDK exposes memory along a spectrum, from "works everywhere" to
"fully managed":

| Path | Manager class | When to pick it |
|---|---|---|
| Portable / multi-backend | `LLMMemoryManager` + any `BaseStore` (the built-in `InMemoryStore` or a custom subclass) | You need backend portability, an LLM-free extractor, or a test-friendly path |
| Managed | `Mem0MemoryManager` ([`mem0ai`](https://pypi.org/project/mem0ai/)) | You want a managed memory layer with LLM-tuned recall and scoped retrieval by `user_id` without writing your own extractor |

### Managed memory — `Mem0MemoryManager`

`Mem0MemoryManager` is a thin adapter that implements the
`BaseMemoryManager` contract on top of [mem0](https://mem0.ai). You get
LLM-backed extraction, prompt-ready context, and scoped retrieval —
without changing how your `Agent` consumes memory.

```python
from tulip.memory.managers import Mem0MemoryManager

manager = Mem0MemoryManager(user_id="agent-7")
agent = Agent(model="anthropic:claude-sonnet-4-6", memory_manager=manager)

# Pass user_id (and optional thread_id) via metadata to scope retrieval:
agent.run_sync(
    "I'm on the night shift — I prefer concise case summaries.",
    metadata={"user_id": "agent-7", "thread_id": "t-a"},
)
```

Install the optional extra:

```bash
pip install 'tulip-agents[mem0]'
```

When you need a fully-deterministic LLM-free extractor or a custom
backend, fall back to the portable path below.

### Portable path (any BaseStore backend)

`LLMMemoryManager` works against any `BaseStore` implementation. Use
this for the built-in `InMemoryStore`, or a custom `BaseStore`
subclass over your own backend, or when you need a deterministic
regex-based extractor:

```python
from tulip.memory.store import InMemoryStore

# In-memory — tests, demos, single process
manager = LLMMemoryManager(store=InMemoryStore())

# For durable cross-thread memory, implement BaseStore over your
# backend of choice and pass it the same way.
```

## What gets injected

At session start, all retrieved memories are formatted as a
`[Long-term Memory]` block and inserted as a system message immediately
after the main system prompt:

```
[System Prompt]
You are a customer-support assistant.

[Memory Block — injected by MemoryManager]
[Long-term Memory]
USER [role]: Tier-2 support agent, covers the night shift.
FEEDBACK [refund_approval]: Refunds over $500 need manager approval. Why: prior chargeback from an unreviewed refund.
PROJECT [billing_rollout]: Active billing migration, prioritise invoice disputes.
REFERENCE [orders_api]: Orders tracked in the 'orders' service API.

[Conversation continues...]
```

The main system prompt stays first and intact. The memory block sits
in position 2, visible to the model on its very first call.

## NoopMemoryManager

Use `NoopMemoryManager` as a test double or placeholder:

```python
from tulip.memory.manager import NoopMemoryManager

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    memory_manager=NoopMemoryManager(),  # wires the hook, stores nothing
)
```

## Writing a custom MemoryManager

Subclass `BaseMemoryManager` and implement three abstract methods:

```python
from tulip.memory.manager import BaseMemoryManager, Memory

class MyMemoryManager(BaseMemoryManager):

    async def extract(self, messages: list) -> list[Memory]:
        """Return memories worth keeping from this conversation."""
        ...

    async def retrieve(self, limit: int = 20) -> list[Memory]:
        """Return memories to inject at session start."""
        ...

    async def save(self, memories: list[Memory]) -> None:
        """Persist a list of memories (upsert by key)."""
        ...
```

The base class provides `on_session_start` and `on_session_end`
by default — you don't need to implement them unless you need custom
injection or extraction timing.

## Observability

Two events are emitted on the agent event bus:

| Event | When | Payload |
|---|---|---|
| `memory.manager.injected` | Session start, after memories are injected | `memory_count`, `types` |
| `memory.manager.extracted` | Session end, after memories are saved | `memory_count`, `types`, `keys` |

Subscribe via the standard hook or SSE stream:

```python
from tulip.observability.emit import EV_MEMORY_MANAGER_INJECTED, EV_MEMORY_MANAGER_EXTRACTED
```

## Context bloat vs. recall

The memory manager is designed to keep injected context small.
At session start the built-in injection calls `retrieve()` with its
default `limit=20`, so at most 20 memories are injected. Each memory is
a single line in the injected block — typically 50–150 tokens total,
regardless of how many sessions have accumulated.

!!! note
    `LLMMemoryManager` accepts a `retrieve_limit` constructor argument,
    but the built-in `on_session_start` injection calls `retrieve()`
    without passing it — so today `retrieve_limit` does **not** change
    how many memories are injected (the effective cap is the `retrieve()`
    default of 20). To use a different cap, override `retrieve()` as
    shown below and pass your own `limit`.

For larger memory sets, plug in a vector-capable `BaseStore` backend
and override `retrieve` to run a semantic similarity search against the
current prompt before injecting:

```python
async def retrieve(self, limit: int = 20) -> list[Memory]:
    query_vec = await embedder.embed(self._current_prompt)
    results = await self.store.search_by_embedding(
        self._ns(MemoryType.FEEDBACK), query_vec, limit=limit
    )
    return [Memory.from_store_value(r.item.value) for r in results]
```

## See also

- [Conversation management](conversation-management.md) — in-session
  context-window management (`SlidingWindowManager`, `LLMCompactor`).
- [Checkpointers](checkpointers.md) — thread-level state persistence
  and the native checkpointer backends.
- [Cross-thread store](checkpointers.md#cross-thread-store) — the
  `BaseStore` interface. Note: only `InMemoryStore` ships as a
  `BaseStore` today; the checkpointer backends are a separate KV
  interface and do **not** implement `BaseStore`, so durable cross-thread
  memory means writing your own `BaseStore` (or using `Mem0MemoryManager`).
- [Hooks](hooks.md) — intercept `memory.manager.*` events for custom
  logging or routing.
