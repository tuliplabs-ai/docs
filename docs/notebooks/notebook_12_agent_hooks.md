# Agent Hooks

Hooks are middleware for agents. Subclass `HookProvider`, override the
callbacks you need, and Tulip invokes them at four lifecycle points:
before/after the invocation, and before/after each tool call. Use them
to add logging, timing, validation, guardrails, or any cross-cutting
concern without touching the agent or its tools.

The scenario here is a cloud-ops agent that scales service instances
with an `adjust_capacity` tool. The hooks give it an audit trail,
latency telemetry, a quota clamp that keeps the bill in check, and a
secrets guardrail over untrusted deployment-manifest text — all bolted
on from the outside.

What you'll learn:

- Writing a `HookProvider` and registering it on an `Agent`.
- The four callback points and what they receive.
- Using `HookPriority` to control execution order.
- Mutating `event.arguments` from `on_before_tool_call` to rewrite the
  call before the tool runs — here, clamping `adjust_capacity` to a
  maximum instance count.
- Composing several hooks on one agent.

Run it:

```
.venv/bin/python examples/notebook_12_agent_hooks.py
```

Uses the bundled mock model by default. Set `TULIP_MODEL_PROVIDER` to
openai / anthropic for a live model; keep `TULIP_MODEL_PROVIDER=mock`
for offline runs.

Prerequisite: the agent-streaming notebook.

## Source

```python
--8<-- "examples/notebook_12_agent_hooks.py"
```
