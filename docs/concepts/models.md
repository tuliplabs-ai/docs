# Model providers

A model is a string. The prefix before the colon (`openai:` or
`anthropic:`) tells the Tulip SDK which provider to use; the rest is the
model id that provider expects. `get_model()` parses the string and
returns a ready client.

```python
# tools, system_prompt, and other kwargs are the same across providers
Agent(model="openai:gpt-4o", tools=security_toolset())                # OpenAI direct
Agent(model="anthropic:claude-sonnet-4-6", tools=security_toolset())  # Anthropic direct
```

To reach a **self-hosted model** (Ollama, vLLM, or any OpenAI-compatible
server), use the `openai` provider with a custom `base_url` — point it at
your endpoint and no prompt leaves your network:

```python
from tulip.models.native.openai import OpenAIModel

# Ollama / vLLM expose an OpenAI-compatible API — reach it via base_url.
local = OpenAIModel(model="llama-3.3-70b",
                    base_url="http://localhost:11434/v1",  # Ollama default
                    api_key="ollama")                      # any non-empty string
Agent(model=local, tools=security_toolset())               # on-prem, no data egress
```

The same SOC agent works against any provider — only the model id, the
`base_url`, and the credentials change. Provider choice is a **security
control**: it decides where triage prompts (which carry SIEM rows, host
names, and indicators) are sent, who logs them, and which jurisdiction
holds them.

## The provider tree at a glance

```text
tulip.models
│
├── openai:                                ── OpenAI direct · OpenAIModel
│   ├─ chat completions       — gpt-* family
│   ├─ reasoning models       — o-series (adds reasoning_effort)
│   └─ base_url override      — Azure · Portkey · LiteLLM · vLLM ·
│                               Ollama · together.ai · fireworks · groq —
│                               any OpenAI-compatible endpoint, incl.
│                               self-hosted / air-gapped (no data egress)
│
├── anthropic:                             ── Anthropic direct · AnthropicModel
│   ├─ Claude family          — opus · sonnet · haiku
│   ├─ prompt caching         — cache the playbook + GSAR rubric once;
│   │                           subsequent triage turns pay 1/10th input cost
│   └─ extended thinking      — forensic-depth reasoning over an alert
│                               chain; thinking blocks → ThinkEvent
│
└── custom:                                ── register_provider("myco", MyModel)
    └─ implement BaseModel    — complete · stream · count_tokens
```

Pick the prefix that matches both your auth surface and your data-handling
rules. The hosted API endpoints send prompts off-box — fine when the
vendor's audit logging and data-residency terms cover your telemetry. For
**air-gapped SOCs / classified telemetry**, point `openai` at a
self-hosted OpenAI-compatible server (Ollama / vLLM) via `base_url` so
alert payloads never leave the network.

| Provider | Detail page |
|---|---|
| **OpenAI** | [OpenAI →](providers/openai.md) |
| **Anthropic** | [Anthropic →](providers/anthropic.md) |

## Custom providers

Implement the `BaseModel` Protocol — three methods (`complete`,
`stream`, `count_tokens`) — and you are a first-class provider. No
adapter layer, no inheritance from `OpenAIModel`. Register the class
with the prefix you want; it becomes a valid model id. This is the hook
for a self-hosted model behind your own audit proxy — every triage
prompt logged to your SIEM before it reaches the LLM.

```python
from tulip.models import register_provider
from tulip.models.base import BaseModel

class AuditedModel(BaseModel):
    async def complete(self, request): ...   # tee request → SIEM, then forward
    async def stream(self, request): ...
    def count_tokens(self, text): ...

register_provider("soc", lambda model_id, **kw: AuditedModel(model_id, **kw))

agent = Agent(model="soc:internal-triage-llm", tools=security_toolset())
```

Source: [`register_provider` in `models/registry.py:21`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/models/registry.py#L21).

## Provider failover & pooling

Incident response can't stall on a rate-limited provider. For
always-on triage, wrap the model in a pool:

```python
from tulip.models.pooled import PooledModel

agent = Agent(
    model=PooledModel(
        primary="anthropic:claude-sonnet-4-6",
        fallbacks=["openai:gpt-4o", "anthropic:claude-sonnet"],
    ),
    tools=security_toolset(),
)
```

The pool tries the primary first; on `RateLimitError`, `TimeoutError`,
or persistent 5xx it fails over to the next entry. Source:
[`PooledModel` in `models/pooled.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/models/pooled.py).

## Notebook

[`notebook_56_model_providers.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_56_model_providers.py)
runs the same SOC triage agent against OpenAI and Anthropic by swapping one string.

## Source

| Area | Path |
|---|---|
| Provider registry | [`models/registry.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/models/registry.py) |
| `OpenAIModel` | [`models/native/openai.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/models/native/openai.py) |
| `AnthropicModel` | [`models/native/anthropic.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/models/native/anthropic.py) |
| `PooledModel` | [`models/pooled.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/models/pooled.py) |
