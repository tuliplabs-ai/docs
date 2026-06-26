# Advanced Hooks

The agent-hooks notebook covered hook basics. This one focuses on the safety
properties Tulip enforces on the event objects hooks see, and on the
control levers a hook can pull mid-flight: `event.cancel` to skip a tool
call, and `event.retry` to re-issue a model call.

The scenario is RELEASE GUARD — the change-gating layer that sits between a
deploy-ops agent and the production cluster. A deploy agent that can delete a
namespace or destroy an environment on its own has an unbounded blast radius;
RELEASE GUARD is the bound on that agency.

What you'll learn:

- Most fields on hook event objects are read-only. Mutating
  `event.tool_name` raises `AttributeError` — that's the framework
  protecting the agent's invariants (and your change log).
- `event.arguments` and `event.cancel` *are* writable.
- Setting `event.cancel = "<reason>"` in `on_before_tool_call` skips the
  call and feeds the reason back as the tool's result — here, blocking a
  `delete_namespace` call during an active change freeze.
- Priority ordering is reversed on "after" callbacks so cleanup unwinds
  LIFO.

Run it:

```
.venv/bin/python examples/notebook_14_hooks_advanced.py
```

Uses the bundled mock model by default. Set `TULIP_MODEL_PROVIDER` to
openai / anthropic for a live model; keep `TULIP_MODEL_PROVIDER=mock`
for offline runs.

Prerequisite: the agent-hooks notebook.

## Source

```python
--8<-- "examples/notebook_14_hooks_advanced.py"
```
