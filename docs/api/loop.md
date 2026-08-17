# ReAct loop

!!! warning "Deprecated — removed in 3.0.0"

    `tulip.loop` is a second ReAct implementation, parallel to the one
    [`Agent`](agent.md) runs, and `Agent` has never used it. Two
    implementations of the same idea drift, and a bug fixed in one stays live
    in the other. Nothing here is a capability `Agent` lacks.

    Everything below still imports and works until 3.0.0, per the
    [deprecation policy](https://github.com/tuliplabs-ai/tulip-agents/blob/main/DEPRECATION.md).
    Each access emits `TulipDeprecationWarning`; to find them in your own code:

    ```
    python -W error::DeprecationWarning -m pytest
    ```

    | Instead of | Use |
    |---|---|
    | `ReActLoop`, `create_react_loop` | [`Agent`](agent.md) |
    | `ReActLoopConfig` | [`AgentConfig`](agent.md) |
    | `LoopRunner` | `await agent.arun(prompt)` |
    | `BatchRunner` | [`EvalRunner`](evaluation.md) |
    | `StreamingCollector` | `async for event in agent.run(prompt)` |
    | `ConditionalRouter` | [`StateGraph`](multiagent.md) conditional edges |
    | `ThinkNode` / `ExecuteNode` / `ReflectNode` | internal to `Agent`; hook them with [hooks](hooks.md) |

The low-level ReAct (reason + act) loop primitives, kept here for reference
while the deprecation runs.

## Loop

::: tulip.loop.react.ReActLoop
::: tulip.loop.react.ReActLoopConfig
::: tulip.loop.react.create_react_loop

## Nodes

::: tulip.loop.nodes.Node
::: tulip.loop.nodes.NodeResult
::: tulip.loop.nodes.ThinkNode
::: tulip.loop.nodes.ExecuteNode
::: tulip.loop.nodes.ReflectNode

## Router

::: tulip.loop.router.Router
::: tulip.loop.router.ConditionalRouter
::: tulip.loop.router.NodeType
::: tulip.loop.router.RouteDecision

## Runner

::: tulip.loop.runner.LoopRunner
::: tulip.loop.runner.BatchRunner
::: tulip.loop.runner.StreamingCollector
::: tulip.loop.runner.create_runner
