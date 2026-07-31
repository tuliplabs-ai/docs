# Memory

Three orthogonal layers, each with its own contract:

1. **Conversation management** — what to do with the message history
   *within* a single run (keep, window, summarize) when it grows past
   the model's context window.
2. **Cross-thread store** — durable key-value scoped by namespace, used
   for long-term memory entries the agent reads at session start and
   writes at session end.
3. **Long-term memory manager** — the policy layer that decides *what*
   to extract from a run and *when* to retrieve, sitting on top of any
   `BaseStore` backend.

For checkpointing (state persistence between runs), see
[Checkpointers](checkpointers.md) — those backends live in
`tulip.memory.backends`, with S3-compatible object storage as a
production target. Note those are *checkpointer* backends (per-thread
state); the cross-thread **store** layer below is a separate contract.

## Conversation management

::: tulip.memory.conversation.ConversationManager
::: tulip.memory.conversation.NullManager
::: tulip.memory.conversation.SlidingWindowManager
::: tulip.memory.conversation.SummarizingManager

## Cross-thread store

The cross-thread KV the long-term memory manager writes to.
`InMemoryStore` is the only `BaseStore` implementation that ships today
(in-process, lost on exit) — `tulip.memory.store_backends` is a stub
(`__all__ = []`). For a durable store, subclass `BaseStore` yourself or
front a third-party service (e.g. Mem0). The drivers in
`tulip.memory.backends` referenced by [Checkpointers](checkpointers.md)
implement `BaseCheckpointer` (per-thread state), **not** `BaseStore`.

::: tulip.memory.store.BaseStore
::: tulip.memory.store.InMemoryStore
::: tulip.memory.store.NamespacedStore
::: tulip.memory.store.StoreContext
::: tulip.memory.store.StoreItem
::: tulip.memory.store.StoreCapabilities
::: tulip.memory.store.StoreCapabilityError
::: tulip.memory.store.SemanticSearchResult

## Long-term memory manager

`LLMMemoryManager` is the default — it uses an auxiliary model to
extract and categorize memories at session end and retrieves the
top-k relevant entries at session start. `NoopMemoryManager` is the
pass-through used in tests.

::: tulip.memory.manager.BaseMemoryManager
::: tulip.memory.manager.LLMMemoryManager
::: tulip.memory.manager.NoopMemoryManager
::: tulip.memory.manager.Memory
::: tulip.memory.manager.MemoryType

## Delta checkpointing

Storage-efficient checkpointer that persists only the diff between
consecutive states (the module targets ~77% storage reduction on long
conversations; actual savings depend on workload). Layered on top of
any `DeltaStorage` backend.

::: tulip.memory.delta.DeltaCheckpointer
::: tulip.memory.delta.DeltaCheckpoint
::: tulip.memory.delta.CheckpointMetadata
::: tulip.memory.delta.DeltaStorage
::: tulip.memory.delta.InMemoryDeltaStorage

## Registry

String-based checkpointer lookup — used when configuration passes a
provider name (e.g. `"s3"`, `"redis"`) instead of an instance.
Custom backends register themselves via `register_checkpointer`.

::: tulip.memory.registry.get_checkpointer
::: tulip.memory.registry.register_checkpointer
::: tulip.memory.registry.list_checkpointers
