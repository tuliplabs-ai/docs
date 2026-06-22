# Graph streaming

`StateGraph.stream(...)` yields events as nodes complete — not buffered
until the graph finishes. For an incident graph that means a live
forensic replay: you watch *which specialist decided what, when* —
triage scoring the alert, forensics pulling the timeline, containment
isolating the host — instead of seeing only the verdict at the end.

## Modes

```python
from tulip.multiagent import StateGraph, StreamMode

# graph: triage -> forensics -> containment
async for event in graph.stream(incident, mode=StreamMode.UPDATES):
    print(event.node_id, event.data)   # who decided, what they wrote to state
```

| Mode | Yields per node | Plus terminal event |
|---|---|---|
| `StreamMode.VALUES` *(default)* | A snapshot of full state after the node completes | `StreamEvent(mode=VALUES, data=final_state)` |
| `StreamMode.UPDATES` | Just the node's own output dict | — |
| `StreamMode.NODES` | The full `NodeResult` with status / duration / error | — |
| `StreamMode.DEBUG` | `{"result": NodeResult, "state": dict}` | — |
| `StreamMode.CUSTOM` | Whatever `emit_custom(...)` pushes from inside a node body | — |

## Custom events from inside a node

A forensics node sweeping many hosts can push intermediate progress with
`emit_custom` so the replay shows each host as it clears. Outside a
`stream()` context the call is a silent no-op, so the same node code runs
unchanged under `execute()` too.

```python
from tulip.multiagent import emit_custom

async def forensics_node(state: dict) -> dict:
    hosts = state["scope"]
    for i, host in enumerate(hosts):
        await emit_custom({"progress": i / len(hosts), "phase": f"timeline:{host}"})
        await scan_host(host)
    return {"compromised": ["web-07"]}

graph.add_node("forensics", forensics_node)

async for event in graph.stream(incident, mode=StreamMode.UPDATES):
    if event.mode == StreamMode.CUSTOM:
        ui.set_progress(event.data["progress"])     # sweep advancing, live
    elif event.mode == StreamMode.UPDATES:
        ui.mark_node_complete(event.node_id)         # specialist done deciding
```

`emit_custom` is exported from `tulip.multiagent` and accepts an
optional `node_id=` kwarg if you want the event tagged with the
emitting specialist's identity.

## Real-time delivery

Decisions arrive as each specialist finishes, not at the end. A
fast-triage / slow-forensics graph proves it:

```python
async def triage(state):
    return {"severity": "high"}             # ~ms

async def forensics(state):
    await asyncio.sleep(2)                  # 2 seconds: deep timeline pull
    return {"compromised": ["web-07"]}

graph.add_node("triage", triage)
graph.add_node("forensics", forensics)
graph.add_edge(START, "triage"); graph.add_edge("triage", "forensics"); graph.add_edge("forensics", END)

start = time.perf_counter()
async for ev in graph.stream(incident, mode=StreamMode.UPDATES):
    print(f"{time.perf_counter() - start:.2f}s  {ev.node_id}")
# 0.05s  triage
# 2.05s  forensics
```

If `stream()` were buffering, both events would arrive at 2.05s. The
unit test
[`test_stategraph_streaming.py`](https://github.com/tuliplabs-ai/sdk-python/-/blob/main/tests/unit/test_stategraph_streaming.py)
guards this property — fails the build if the first event lands at
≥ end / 2.

## Error and cancellation

A specialist that raises has its `NodeResult.success` set to `False`
with the error message; the stream still yields an event for it (no
consumer deadlock), so the replay records the failed step instead of
hanging. Breaking out of the iterator early — say the analyst already
saw the containment decision and closed the panel — cancels the
background driver task so no work continues in the background.

## Source

`src/tulip/multiagent/graph.py:emit_custom`,
`StateGraph.stream`, `StreamMode`.
