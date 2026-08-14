# OpenAI-compatible providers

Most of the model ecosystem speaks the OpenAI wire protocol. Managed
services (Groq, Together, OpenRouter, DeepSeek, Mistral, xAI, Fireworks,
Cerebras, Perplexity, NVIDIA NIM) and self-hosted servers (Ollama, vLLM,
LM Studio, llama.cpp, LiteLLM) differ only in **base URL** and **which
environment variable holds the key** — so Tulip reaches all of them through
the same `OpenAIModel`, with no extra client dependency.

Address one by prefix:

```python
from tulip.agent import Agent

Agent(model="groq:llama-3.3-70b-versatile")
Agent(model="ollama:qwen3")
Agent(model="deepseek:deepseek-chat")
```

## The table

| Prefix | Provider | Endpoint | API key |
|---|---|---|---|
| `openai` | OpenAI | (default) | `OPENAI_API_KEY` |
| `anthropic` | Anthropic | (default) | `ANTHROPIC_API_KEY` |
| `ollama` | Ollama | `http://localhost:11434/v1` | `OLLAMA_API_KEY` _(optional)_ |
| `vllm` | vLLM | `http://localhost:8000/v1` | `VLLM_API_KEY` _(optional)_ |
| `lmstudio` | LM Studio | `http://localhost:1234/v1` | `LMSTUDIO_API_KEY` _(optional)_ |
| `llamacpp` | llama.cpp server | `http://localhost:8080/v1` | `LLAMACPP_API_KEY` _(optional)_ |
| `litellm` | LiteLLM gateway | `http://localhost:4000/v1` | `LITELLM_API_KEY` |
| `groq` | Groq | `https://api.groq.com/openai/v1` | `GROQ_API_KEY` |
| `together` | Together AI | `https://api.together.xyz/v1` | `TOGETHER_API_KEY` |
| `openrouter` | OpenRouter | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` |
| `deepseek` | DeepSeek | `https://api.deepseek.com/v1` | `DEEPSEEK_API_KEY` |
| `mistral` | Mistral AI | `https://api.mistral.ai/v1` | `MISTRAL_API_KEY` |
| `xai` | xAI (Grok) | `https://api.x.ai/v1` | `XAI_API_KEY` |
| `fireworks` | Fireworks AI | `https://api.fireworks.ai/inference/v1` | `FIREWORKS_API_KEY` |
| `cerebras` | Cerebras | `https://api.cerebras.ai/v1` | `CEREBRAS_API_KEY` |
| `perplexity` | Perplexity | `https://api.perplexity.ai` | `PERPLEXITY_API_KEY` |
| `nvidia` | NVIDIA NIM | `https://integrate.api.nvidia.com/v1` | `NVIDIA_API_KEY` |
| `openai-compatible` | Any OpenAI-compatible endpoint | _(supply `base_url`)_ | `OPENAI_COMPATIBLE_API_KEY` _(optional)_ |

Anything not listed is still reachable without a code change — give the base
URL explicitly:

```python
from tulip.models import get_model

model = get_model("openai-compatible:my-model", base_url="https://host/v1")
Agent(model=model)
```

## Resolution order

For both the endpoint and the key, the first value found wins:

**Endpoint** — explicit `base_url=` → `TULIP_<PREFIX>_BASE_URL` → the
vendor's own variable where one exists (`OLLAMA_BASE_URL`, `VLLM_BASE_URL`,
`LMSTUDIO_BASE_URL`, `LLAMACPP_BASE_URL`, `LITELLM_GATEWAY_URL`) → the
default in the table.

**Key** — explicit `api_key=` → the provider's variable from the table. A
hosted provider with no key raises immediately, naming the variable to set.
Local servers need none.

```bash
# Point the ollama prefix at a GPU box instead of localhost
export TULIP_OLLAMA_BASE_URL=http://gpu-box:11434/v1
```

!!! note "Passing configuration inline"
    `AgentConfig` rejects unknown keyword arguments, so
    `Agent(model="groq:x", api_key=...)` raises. Build the model first when
    the configuration is not in the environment:

    ```python
    Agent(model=get_model("groq:llama-3.3-70b", api_key="..."))
    ```

## What this does not change

- **The Responses API is never auto-selected against a custom base URL.**
  `api="auto"` routes to `/v1/responses` only for model families that
  require it, and only against `api.openai.com` itself — a gateway serves
  chat-completions and would 404 on the Responses path. Set
  `api="responses"` explicitly if your endpoint does serve it.
- **Capability still varies by model.** A prefix makes an endpoint
  reachable; it does not promise that the model behind it supports tool
  calling, structured output, or vision. See
  [Structured output](../structured-output.md) for the fallbacks Tulip
  applies when a model cannot constrain its own decoding.
- **`temperature` / `top_p` left unset are omitted** from the request, so a
  self-hosted server's own `generation_config.json` defaults apply rather
  than being silently overridden.

→ [Models overview](../models.md) · [OpenAI provider](openai.md) ·
[LiteLLM gateway](../../how-to/litellm-gateway.md)
