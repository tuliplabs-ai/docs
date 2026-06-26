# Anthropic

The Anthropic provider connects Tulip directly to Anthropic's API (`api.anthropic.com`). Use it when you want **the Claude family** —
Opus for the hardest problems, Sonnet as the everyday workhorse,
Haiku for high-volume cheap calls — and want to talk to Anthropic
without going through an intermediary.

What makes this provider distinct is **prompt caching**: a long
threat-intel block or SOC playbook reused across an investigation pays
1/10th the input cost on repeat turns. Each turn's assistant message is
also surfaced as a typed `ThinkEvent`, so a UI can show the model's
working as it streams.

## When to pick Anthropic

| You want… | This is the right provider |
|---|---|
| Claude Opus / Sonnet / Haiku from Anthropic directly | ✓ |
| Threat-intel context / SOC playbooks amortised across a long investigation | ✓ — built-in prompt caching |
| Each turn's reasoning surfaced for the analyst to follow | ✓ — `ThinkEvent` stream |

## Getting started

### 1. Set your API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Pick a Claude model

```python
from tulip.agent import Agent
agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="You are a SOC triage analyst.",
)
```

The string `"anthropic:claude-sonnet-4-6"` tells the SDK the
provider (`anthropic:`) and the exact model id. Any model id
Anthropic accepts, the SDK accepts.

### 3. Run it

```python
result = agent.run_sync("Summarise the triage findings for alert A-42 in three bullets.")
print(result.message)
```

That's the full setup. Streaming, tool calling, and prompt caching
work without extra configuration.

## What you get out of the box

### The whole Claude family

Whatever Anthropic ships, you can address by name:

| Model | When to pick it |
|---|---|
| `claude-opus-4-8` | Hardest problems — incident timeline reconstruction, deep threat hunting, multi-step forensics |
| `claude-sonnet-4-6` | Everyday workhorse — fast enough, smart enough, cheap enough for routine triage |
| `claude-haiku-4-5` | High-volume cheap calls — alert classification, indicator routing, log summaries |

### Real SSE streaming

Token-level streaming. The model emits content deltas; the SDK
converts them to `ModelChunkEvent`s; your `async for` loop reads
them as they arrive.

```python
async for event in agent.run("Summarise the timeline of alert A-42."):
    if isinstance(event, ModelChunkEvent) and event.content:
        print(event.content, end="", flush=True)
```

### Tool calling — the Anthropic tool-use protocol

`@tool` functions are translated into Anthropic's `tools` schema; the
model's structured `tool_use` blocks are parsed back into SDK
`ToolCall`s. Parallel tool calls are supported (the model can
request multiple tools per turn; the SDK runs them concurrently via
the `ConcurrentExecutor`).

### Structured output — tool-as-schema

Anthropic doesn't expose a `response_format` field, so the SDK uses
the standard "single-tool" trick: define the schema as a tool, force
the model to call it. From your side, the API is identical to the
other providers:

```python
from pydantic import BaseModel

class Triage(BaseModel):
    severity: str
    needs_human: bool

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    output_schema=Triage,
)
result = agent.run_sync("Beacon from WIN-7731 to a known C2 endpoint.")
print(result.parsed)        # Triage(severity='high', needs_human=True)
```

### Prompt caching — opt in for long prompts

This is the biggest cost saver if your system prompt or tool block is
long (SOC playbooks, threat-intel feeds, detection rules). Re-feeding
the same threat-intel context on every turn of an investigation is the
common case — and the expensive one. Anthropic's prompt-caching
mechanism marks a span of the request as cacheable; subsequent turns
within the cache window pay **1/10th** the input cost on the cached
span.

Opt in with `prompt_cache=True` on `AnthropicModel`. The SDK then sends
the system prompt as a block list with `cache_control: ephemeral` and
tags the last entry of the tool catalog the same way (Anthropic walks
markers in order — the last tag anchors the cache point).

```python
from tulip.agent import Agent
from tulip.models.native.anthropic import AnthropicModel

agent = Agent(
    model=AnthropicModel(
        model="claude-sonnet-4-6",
        prompt_cache=True,
    ),
    tools=[...],
    system_prompt="<a long system prompt — SOC playbooks, threat-intel context, detection rules>",
)

result = agent.run_sync("...")
print(f"cache writes: {result.metrics.cache_creation_input_tokens}")
print(f"cache reads:  {result.metrics.cache_read_input_tokens}")
# → cache writes: 4092      (turn 1, written once)
# → cache reads:  4092       (turn 2 — same prefix, ~10× cheaper input)
```

When it kicks in:

- A 5-minute "ephemeral" cache (rolling window).
- Subsequent turns reusing the same prefix pay `0.1× input rate` on
  the cached portion.
- Most effective when system prompts ≥ ~1024 tokens, or you've loaded
  a big skill / playbook / RAG block.

`cache_creation_input_tokens` and `cache_read_input_tokens` surface
on `AgentResult.metrics` so observability hooks can chart cache hits
and the cost saved.

### Per-turn reasoning — visible message stream

Each agent turn surfaces the model's assistant message as a
`ThinkEvent` before any tool calls run, so the analyst can follow how
the model is working through a triage call. The SDK builds the
`ThinkEvent` from the turn's `message.content` (the Anthropic response
parser handles `text` and `tool_use` blocks); it does **not** send an
extended-thinking request param, so this is the normal per-turn message
text, not a separate hidden chain-of-thought channel:

```python
async for event in agent.run("..."):
    match event:
        case ThinkEvent(reasoning=r) if r:
            print(f"💭 {r}")
        case ModelChunkEvent(content=c) if c:
            print(c, end="", flush=True)
```

## Common gotchas

| Symptom | Likely cause |
|---|---|
| `401 authentication_error` | `ANTHROPIC_API_KEY` not set, or set to a key without console access |
| `404 not_found_error` on the model id | Model id is wrong; check `https://docs.anthropic.com/en/docs/about-claude/models/all-models` |
| `429 overloaded_error` | Anthropic capacity; the `ModelRetryHook` re-tries with backoff if installed |
| Prompt caching not visible in usage stats | Cache window expired (5 min ephemeral) or prompt below the threshold |
| `ThinkEvent`s never fire | The turn produced no assistant `message.content` (e.g. tool-call-only turn) |

## Source

[`AnthropicModel` in `src/tulip/models/native/anthropic.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/models/native/anthropic.py)

## See also

- [Models overview](../models.md) — the full provider tree.
- [OpenAI](openai.md) — GPT family direct.
