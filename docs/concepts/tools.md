# Tools

Tools are how an Tulip agent
affects the world. The model decides *"call `query_siem` with query='src_ip:192.0.2.10'"*;
the SDK runs your `query_siem` function, captures the return value, and
feeds it back. From your side, a tool is **a regular Python function
with a `@tool` decorator** — the SDK introspects the signature and
docstring to build the schema the model sees.

This is the seam most production code touches. Get tools right and
the rest of the framework gets out of your way.

## When to write a tool

| You want… | Write a tool |
|---|---|
| The model to call your SIEM / threat-intel API / EDR | ✓ |
| Side-effecting actions the model should be able to invoke (host isolation, blocking) | ✓ |
| Read-only lookups (indicator reputation, alert status checks) | ✓ |
| To mutate the agent's *internal* state (system prompt, config) | use a [hook](hooks.md), not a tool |
| To intercept *every* tool call (logging, retry) | use a [hook](hooks.md) |

## Getting started

### 1. Decorate a function

```python
from tulip.tools import tool
@tool
def query_siem(query: str, limit: int = 10) -> list[str]:
    """Search the SIEM for events matching ``query``, up to ``limit`` results."""
    return siem.search(query, limit)
```

The docstring becomes the tool description the model reads. Type
hints (`str`, `int`, `list[str]`) build the JSON schema. Defaults
mark optional parameters.

### 2. Pass to the agent

```python
agent = Agent(model="anthropic:claude-sonnet-4-6", tools=[query_siem])
```

That's the wiring. The model now sees `query_siem` in its tool list and
can call it whenever it decides to.

### 3. Run it

```python
result = agent.run_sync("Pull all events for src_ip 192.0.2.10 in the last hour.")
```

If the model decides to call `query_siem("src_ip:192.0.2.10")`, the SDK
invokes your function with that argument, captures the return value, and
feeds it into the next model turn. You write Python; the SDK handles the
schema marshalling.

## What you get out of the box

### Idempotent tools — the model can retry; the side effect can't

This is the SDK's flagship tool primitive. Some side-effecting tools
must run *exactly once* per logical request — host isolation, paging
on-call, blocking an indicator. Mark them `idempotent=True`:

```python
@tool(idempotent=True)
def isolate_host(host_id: str, incident_id: str) -> dict:
    """Isolate the host from the network. Re-issuing the same
    (host_id, incident_id) within a single run returns the prior
    result; the body is not re-executed."""
    return edr.isolate(host_id, incident_id)
```

When the model re-issues a tool call with the same
`(name, arguments)` tuple that already ran in this agent run, the
ReAct loop **reuses the prior result instead of invoking the
function again**. Defends against:

- Models that re-emit the same call after seeing the result.
- Network glitches where a call appears failed but actually succeeded.
- Users re-prompting "do X" when X has already been done.
- Replays after a checkpoint resume.

Read the [idempotency concept page](idempotency.md) for the full
picture and the matching notebook.

### Sync and async bodies

Both shapes are supported. Async bodies run on the agent's event
loop directly; sync bodies run in a thread-pool executor so the loop
is never blocked.

```python
@tool
def score_severity(cvss: float, exposure: float) -> float:
    return cvss * exposure              # sync — runs in thread pool

@tool
async def lookup_hash(sha256: str) -> str:
    async with httpx.AsyncClient() as c:
        return (await c.get(f"https://ti.example/hash/{sha256}")).text  # async — runs on the loop
```

### Parallel by default — fast when the model wants multiple things

```python
agent = Agent(
    model=...,
    tools=[enrich_indicator, lookup_hash, query_siem],
    tool_execution="concurrent",   # default
)
```

When the model emits multiple tool calls in one turn, the SDK runs
them concurrently via `asyncio.gather`. Three independent enrichments
finish in `max(t1, t2, t3)`, not `t1+t2+t3`.

If your tools have side effects that must be ordered, switch to
`tool_execution="sequential"`.

### Error handling — tool failures don't crash the agent

If a tool raises, the loop catches the exception and turns it into a
`ToolResult(error=str(exc))`, then feeds that back into the next model
turn. (`ToolResult.success` is a read-only property derived from
`error` — it's `True` when `error is None`, not something you set.) The
model sees the failure and can react: retry, try a different tool, or
report to the user.

```python
@tool
def lookup_alert(alert_id: str) -> dict:
    record = siem.get_alert(alert_id)
    if record is None:
        raise ValueError(f"no alert with id={alert_id}")
    return record
```

The model sees `"no alert with id=A-4271"` and decides what to do.
Behind the scenes, the loop captures the exception's string form into
`ToolResult.error`; the raw exception is logged where the tool ran.

### Custom names and descriptions

Override the auto-derived defaults when the function name doesn't
read well to the model:

```python
@tool(name="enrich_indicator", description="Look up reputation and context for an IOC.")
async def _enrich_indicator_internal(indicator: str) -> Indicator:
    ...
```

The model sees `enrich_indicator`; your code keeps the internal name.

## Practical recipes

### Read-only lookups

```python
@tool
def get_alert_status(alert_id: str) -> dict:
    """Return the current triage status and assignment for an alert."""
    return alerts.get(alert_id)
```

No need for `idempotent=True` — read-only calls are safe to repeat.

### Idempotent writes

```python
@tool(idempotent=True)
def block_indicator(indicator: str, scope: str) -> dict:
    """Push a block for an indicator to the firewall. Re-fires return the cached block id."""
    return firewall.block(indicator, scope)
```

### A tool that's also exposed via MCP

If you've built a tool you want other agents to reach, expose it
through `TulipMCPServer` — same `@tool`, no rewrite. See
[MCP](mcp.md).

## Common gotchas

| Symptom | Likely cause |
|---|---|
| Model never calls the tool | Description / docstring isn't telling the model when to use it. Be explicit: *"Use this tool when the user asks about X."* |
| Tool fires twice on the same input | You're seeing the model retry. Add `idempotent=True` (a host gets isolated once, not twice). |
| `TypeError: missing 1 required positional argument` at call time | Function signature has a parameter without a default that you didn't surface in the docstring; the model omitted it. Add a default or explain the parameter. |
| Tool returns Python objects but the model echoes `<__main__.X object at 0x…>` | Tool return value isn't JSON-serialisable. Return a dict / Pydantic model / list of strings, not arbitrary objects. |
| Async tool blocks the event loop | The "async" body is calling sync I/O. Wrap the blocking call in `asyncio.to_thread(...)` or use an async client. |

## Source

- [`@tool` decorator and `Tool` class](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/tools/decorator.py)
- [`ToolRegistry`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/tools/registry.py)
- [Built-in tools](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/tools/builtins.py) — `get_today_date`. The agent also auto-injects `task_complete` and `ask_user` in explicit-completion mode.

## See also

- [Idempotency](idempotency.md) — the full story on `idempotent=True`.
- [Hooks](hooks.md) — for cross-cutting concerns (logging, retry, guardrails).
- [Executors](executors.md) — how concurrent vs sequential tool execution works.
- [MCP](mcp.md) — expose your tools to other agents over the Model Context Protocol.
- [Errors](errors.md) — how tool failures surface in the event stream.
