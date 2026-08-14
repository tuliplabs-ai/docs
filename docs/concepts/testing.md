# Testing agents

Testing an agent means controlling the one part you do not own: the model.
`tulip.testing` ships two doubles for that, so a test is deterministic, needs
no API key, and never touches the network.

```python
from tulip.agent import Agent
from tulip.testing import ScriptedModel, text, tool_call


async def test_refund_is_looked_up_first():
    model = ScriptedModel([
        tool_call("lookup_order", order_id="ord-4821"),
        text("That order is eligible for a refund."),
    ])
    agent = Agent(model=model, tools=[lookup_order, issue_refund])

    result = await agent.arun("Is ord-4821 refundable?")

    assert [t.tool_name for t in result.tool_executions] == ["lookup_order"]
    assert model.call_count == 2
```

## `ScriptedModel` — a fixed sequence

Each call returns the next turn. Build turns with `text()` for a plain answer
and `tool_call()` for a tool invocation; a bare string is shorthand for
`text()`.

```python
ScriptedModel([
    tool_call("issue_refund", order_id="ord-4821", amount=49.0),
    "Refunded.",
])
```

Arguments are keywords, so the call reads like the tool it names, and the
tool-call id is derived from the name rather than randomised — assertions
never depend on a value that changes per run.

!!! note "Running out of turns is an error"
    If the agent asks for more turns than you scripted, `ScriptedModel`
    raises rather than inventing a reply. An agent that keeps going has
    usually failed to terminate, and answering quietly would hide the bug the
    test exists to find.

    When the number of turns genuinely is not the point, pass
    `repeat_last=True` and the final turn is returned indefinitely.

## `FunctionModel` — decide per turn

A fixed script cannot express "call the tool, then answer using its result",
because the second turn depends on the first. `FunctionModel` takes a callable
that sees the conversation so far:

```python
from tulip.testing import FunctionModel, tool_call


def handler(messages, tools):
    if any(m.role == "tool" for m in messages):
        return "The order was refunded."
    return tool_call("issue_refund", order_id="ord-4821")


agent = Agent(model=FunctionModel(handler), tools=[issue_refund])
```

The handler may return a `ModelResponse` or a plain string.

## Assert on what the agent sent

The interesting failures are usually in the *inputs* the agent produced, not
the final string — a tool that was never bound, a second turn that lost the
tool result. Both doubles record every call:

| Attribute | What it holds |
|---|---|
| `call_count` | How many times the agent called the model |
| `received_messages` | The `messages` list for each call, in order |
| `offered_tools` | Tool names bound on each call — `[]` when none |
| `last_prompt` | Content of the most recent user turn |

```python
async def test_the_agent_binds_only_the_read_tool():
    model = ScriptedModel([text("ok")])
    await Agent(model=model, tools=[lookup_order]).arun("status?")

    assert model.offered_tools[0] == ["lookup_order"]
    assert "issue_refund" not in model.offered_tools[0]
```

That style catches a class of bug an output assertion cannot: the agent
answering plausibly while never having been given the tool it claimed to use.

## Streaming

`stream()` is implemented on both doubles, chunking whatever `complete()`
would have returned, so one double serves a streaming and a non-streaming
agent alike.

```python
chunks = [event async for event in model.stream(messages, None)]
assert chunks[-1].done is True
```

## What the doubles do not do

They return exactly what you scripted. Neither validates arguments against a
tool's schema, enforces token limits, or reproduces a provider's quirks — a
failing test should be telling you about your agent, not about a mock's
opinion of your JSON.

For the behaviours that *are* provider-specific — reasoning models returning
empty content at small token budgets, structured-output support varying by
model — test against a real endpoint. Any
[OpenAI-compatible provider](providers/openai-compatible.md) works, including
a local Ollama or vLLM server, so that does not require a vendor account
either.

→ [Agent](agent.md) · [Evaluation](evaluation.md) · [Hooks](hooks.md)
