# DeepAgent

Tulip ships two primitives for
long-horizon research:

| | `create_deepagent` | `create_research_workflow` |
|---|---|---|
| **Returns** | Plain `Agent` | `StateGraph` |
| **Grounding** | Per-turn (inside the loop) | Post-hoc on the final summary |
| **Replan** | Inside the ReAct loop | At the workflow level |
| **Best for** | Quick research, embedded in larger graphs | Production, verifiable summaries |

---

## `create_deepagent` — single agent loop

`create_deepagent` is a research-shaped `Agent` factory. It bundles
the standard deep-research configuration into one call and stays a
plain `tulip.Agent` underneath — every hook, plugin, checkpointer,
and evaluation primitive from the rest of the SDK attaches normally.

## What it is

A deep agent runs a tool loop until one of three exit conditions fires:

```python
termination = (
    ToolCalled(submit_tool) & ConfidenceMet(min_confidence)
) | TokenLimit(max_tokens) | MaxIterations(max_iterations)
```

The conditions are composable, greppable, and unit-testable without a
live model. The loop exits when the work is done — not after a fixed
number of steps.

**Defaults on by default:**

- `reflexion=True` — self-evaluates every turn; rewrites the plan when
  the last step was wrong.
- `grounding=True` — scores every claim against the tool-call evidence
  trail; below-threshold claims get dropped or sent back for re-research.
- `output_schema=` — the model provider's strict structured-output mode
  enforces the Pydantic schema before the result reaches the caller.

**Loop detection is argument-aware.** Calling the same tool with
*different* arguments — paged discovery, sweeping a list of inputs,
inspecting 29 metrics one at a time — is forward progress and does not
trigger the loop detector. Only identical `(name, args)` pairs repeated
across consecutive iterations count as a loop.

## Quickstart

```python
from tulip.deepagent import create_deepagent
from tulip.tools import tool
from pydantic import BaseModel, Field


class ResearchResult(BaseModel):
    summary: str
    sources: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


@tool
def search_kb(query: str) -> list[str]:
    """Search the knowledge base."""
    return kb.query(query)


@tool
def submit_research(result: ResearchResult) -> str:
    """Submit the completed report. Call when confidence ≥ 0.85."""
    return "submitted"


agent = create_deepagent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search_kb, submit_research],
    system_prompt="You are a market-research agent. Submit when confident.",
    output_schema=ResearchResult,
    submit_tool="submit_research",
    min_confidence=0.85,
    max_iterations=20,
)

result = agent.run_sync("Summarise the competitive landscape for mid-market CRM platforms.")
report: ResearchResult = result.parsed  # Pydantic-typed structured output
```

## Capability layers

All are opt-in — add only what the task needs.

### Filesystem scratchspace

```python
agent = create_deepagent(
    # model=..., tools=..., system_prompt=... (required)
    enable_filesystem=True,  # adds write_file, read_file, ls, edit_file, glob, grep
)
```

Tools write to an ephemeral in-memory `StateBackend` by default.
Pass `backend=FilesystemBackend(root=Path("./scratch"))` for real-disk
persistence.

### Todo tracking

```python
from tulip.deepagent import TodoState

todo_state = TodoState()
agent = create_deepagent(
    # model=..., tools=..., system_prompt=... (required)
    enable_todos=True,
    todo_state=todo_state,   # inspect after the run
)

result = agent.run_sync("...")
for todo in todo_state.snapshot():
    print(f"[{todo.status}] {todo.content}")
```

The `write_todos` / `read_todos` tools let the agent maintain a
structured task list across reasoning steps. The `todo_state` reference
gives the caller a live view after the run.

### Subagent dispatch

```python
from tulip.deepagent import SubAgentDef

competitor_analyst = SubAgentDef(
    name="competitor_analyst",
    description="Deep-dives on a single competitor's product and pricing.",
    system_prompt="Research the given competitor and return its positioning, pricing, and recent launches.",
    tools=[search_kb],
    max_iterations=4,
)

agent = create_deepagent(
    # model=..., tools=..., system_prompt=... (required)
    subagents=[competitor_analyst],
)
```

The parent calls the child via a `task()` tool. The child runs as a
stateless one-shot; only its final answer appears in the parent's
context, not the full subagent trajectory.

### Memory files

```python
agent = create_deepagent(
    # model=..., tools=..., system_prompt=... (required)
    memory_files=["~/AGENTS.md", "./project-notes.md"],
)
```

`AGENTS.md`-style Markdown files are prepended to the system prompt.
Missing paths are silently skipped so defaults like
`["~/AGENTS.md", "./AGENTS.md"]` work without pre-checking.

### Datastore auto-wiring

```python
from tulip.rag import OpenAIEmbeddings, RAGRetriever
from tulip.rag.stores.qdrant import QdrantVectorStore

retriever = RAGRetriever(
    embedder=OpenAIEmbeddings(model_id="cohere.embed-v4.0", ...),
    store=QdrantVectorStore(dsn=..., table_name="VECTOR_DOCUMENTS", dimension=1536),
)

agent = create_deepagent(
    # model=..., tools=..., system_prompt=... (required)
    datastores={
        "industry_reports": {
            "retriever": retriever,
            "description": "analyst reports: market sizing, competitor "
                           "pricing, launch timelines",
            "top_k": 6,
        },
        # additional named stores (e.g. "support_tickets") — agent routes between them
    },
)
```

For each entry, a `search_<name>` tool is auto-wired via
`tulip.rag.tools.create_rag_tool` (passing the retriever, top_k, and
threshold) and appended to the agent's tool list, and a per-store
description block is prepended to the system prompt so the model can
route each query to the right store. Mirrors a common deep-research
`create_deep_research_agent(datastores=...)` shape so existing recipes
translate 1:1.

The retriever's `store` can be any `BaseVectorStore` implementation —
the SDK ships five: `InMemoryVectorStore`, `PgVectorStore`,
`OpenSearchVectorStore`, `QdrantVectorStore`, and `ChromaVectorStore`. See
[`examples/projects/deep-research/`][dr] for working ports of seven
upstream deep-research gists across these backends.

[dr]: https://github.com/tuliplabs-ai/sdk-python/tree/main/examples/projects/deep-research

A few interop notes:

- Some model providers JSON-encode floats as strings — `gpt-5.x` sends
  `"min_score": "0.5"`. `RAGRetriever.retrieve` and `QdrantVectorStore.search`
  coerce defensively so the threshold comparison doesn't `TypeError`.
- From inside an async `def` use `async for event in agent.run(...)`,
  not `agent.run_sync(...)` — `run_sync` spawns a new thread + event
  loop where `AsyncOpenSearch` and similar loop-bound clients are
  unusable, producing silent empty tool results.

### Conversation summarisation

```python
agent = create_deepagent(
    # model=..., tools=..., system_prompt=... (required)
    summarize_after_messages=40,  # trigger threshold
    summarize_keep_recent=10,     # always preserve last 10 verbatim
)
```

Activates the SDK's `SummarizingManager` so older turns are condensed
once the conversation exceeds the threshold. Prevents context blowout
on long research runs without losing recent reasoning steps.

## Observability

`create_deepagent` returns a standard `tulip.Agent`, so all `deepagent.*`
SSE events stream out whenever a `run_context` is active:

```python
from tulip.observability import run_context, get_event_bus

async with run_context() as rid:
    result = agent.run_sync("Research the pricing history for this product line.")

    async for ev in get_event_bus().subscribe(rid):
        match ev.event_type:
            case "deepagent.subagent.spawned":
                print("↳ subagent:", ev.data["subagent_type"])
            case "deepagent.fs.write":
                print("  📝", ev.data["path"])
            case "deepagent.todo.added":
                print("  ☐", ev.data["content"])
            case "agent.terminate":
                print("  ✓", ev.data["final_message_preview"])
```

| Event | When |
|---|---|
| `deepagent.subagent.spawned` | `task()` dispatches a subagent |
| `deepagent.subagent.completed` | subagent returns its result |
| `deepagent.fs.read` / `deepagent.fs.write` | filesystem tool called |
| `deepagent.todo.added` / `deepagent.todo.completed` | todo state changes |

## KnowledgeProvider — multi-item scans

For research that iterates over a discoverable surface (e.g. every host
in an asset inventory), implement `KnowledgeProvider`:

```python
from tulip.deepagent import KnowledgeProvider, KnowledgeRow, ItemRef

class AssetInventoryProvider(KnowledgeProvider):
    def list_items(self) -> list[ItemRef]:
        return [ItemRef(id=h, label=h) for h in inventory.list_hosts()]

    def describe_item(self, ref: ItemRef) -> str:
        return inventory.describe_host(ref.id)

    def to_row(self, ref: ItemRef, result: ResearchResult) -> KnowledgeRow:
        return KnowledgeRow(id=ref.id, data=result.model_dump())
```

Feed the provider into your scan loop. Each item gets its own agent
run; results are collected as typed rows.

---

## `create_research_workflow` — StateGraph with quality loop

The production pattern for research that requires verifiable, grounded
summaries. Instead of checking claims per-turn inside the agent loop,
the workflow runs the full ReAct phase first, then evaluates the summary
post-hoc with an LLM-as-judge, and replans at the graph level when the
grounding score is too low.

```
START
  ↓
execute          ← Agent(reflexion=True) tool loop; collects evidence
  ↓
summarize        ← distill evidence into a summary (optionally structured)
  ↓
grounding_eval   ← GroundingEvaluator scores summary claims vs evidence
  ├── score ≥ threshold ──► END
  └── score < threshold ──► replan ──► execute   (up to max_replans)
```

```python
from tulip.deepagent.workflow import create_research_workflow
from pydantic import BaseModel

class Report(BaseModel):
    summary: str
    key_findings: list[str]
    confidence: float

workflow = create_research_workflow(
    model=get_model(),
    tools=[search_kb, enrich_indicator, submit_research],
    output_schema=Report,
    grounding_threshold=0.65,   # accept summary when ≥ 65% claims grounded
    max_replans=2,               # retry up to 2× with focused re-plan
)

result = await workflow.execute({"prompt": "Investigate indicator 198.51.100.7"})
report: Report = result.final_state["structured_output"]
print(f"grounding: {result.final_state['grounding_score']:.0%}")
print(f"replans used: {result.final_state['replan_count']}")
```

`create_research_workflow` accepts the same `datastores=` mapping as
`create_deepagent` — here with a threat-intel corpus as the
security-flavored variant. Internally both call `wire_datastores(...)`
so the execute agent gets the identical `search_<name>` tool surface
and system-prompt routing block:

```python
workflow = create_research_workflow(
    model=...,
    tools=[],
    output_schema=Report,
    datastores={"threat_intel": {"retriever": threat_intel_retriever, "top_k": 6}},
    grounding_threshold=0.65,
)
```

**When to use each:**

- Use `create_deepagent` when the agent runs *inside* a larger graph
  (e.g. as one specialist in an Orchestrator) or when per-turn grounding
  is sufficient.
- Use `create_research_workflow` when you need an end-to-end quality
  guarantee on the final output — the grounding eval runs after all
  evidence is collected, giving a more accurate picture of claim coverage.

## See also

- [DeepAgent](../notebooks/notebook_29_deepagent.md) — four-part
  walkthrough: basic factory, filesystem + todos, subagents, observability.
- [API reference — DeepAgent](../api/deepagent.md) — full class and
  function signatures including `create_research_workflow`.
- [Termination algebra](termination.md) — how `ToolCalled & ConfidenceMet`
  works under the hood.
- [SSE event catalogue](sse-events.md) — `deepagent.*` event payloads.
