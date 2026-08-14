# Environment variables

Tulip configures itself from environment variables. The notebook harness in
`examples/config.py` reads them with a consistent fallback chain; the SDK
itself reads provider API keys directly.

This page is the answer when an example prints *"skipped — missing env
vars"*.

## Minimum set for a notebook run

```bash
export TULIP_MODEL_PROVIDER=openai
export TULIP_MODEL_ID=gpt-4o
export OPENAI_API_KEY=sk-...

python examples/notebook_06_basic_agent.py
```

`TULIP_MODEL_PROVIDER` is the switch. **Unset, it defaults to `mock`** and
the notebooks run offline against a bundled model — setting only
`TULIP_MODEL_ID` still gives you the mock.

## Model selection

| Variable | Used by |
|---|---|
| `TULIP_MODEL_PROVIDER` | `examples/config.py:get_model` — `mock` (default), `openai`, `anthropic` |
| `TULIP_MODEL_ID` | Model id for the selected provider (e.g. `gpt-4o`, `claude-sonnet-4-6`) |
| `TULIP_MODEL_ID_B` | Secondary "model B" slot — comparison notebooks |
| `TULIP_MODEL_ID_C` | Tertiary "model C" slot |
| `TULIP_RESEARCH_MODEL` | Overrides the model for the research/eval scripts |
| `TULIP_NOTEBOOK_BOOT` | Set by the notebook harness during boot; not user-facing |

## Provider keys

| Variable | Used by |
|---|---|
| `OPENAI_API_KEY` | `OpenAIModel`, `OpenAIEmbeddings` |
| `ANTHROPIC_API_KEY` | `AnthropicModel` |
| `COHERE_API_KEY` | `CohereEmbeddings`, `CohereReranker` |

### OpenAI-compatible providers

Every prefix in the [compatible-provider table](../concepts/providers/openai-compatible.md)
reads its own key variable — `GROQ_API_KEY`, `TOGETHER_API_KEY`,
`OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `XAI_API_KEY`,
`FIREWORKS_API_KEY`, `CEREBRAS_API_KEY`, `PERPLEXITY_API_KEY`,
`NVIDIA_API_KEY` — and each accepts a `TULIP_<PREFIX>_BASE_URL` override for
self-hosted deployments and proxies. Local servers (`ollama`, `vllm`,
`lmstudio`, `llamacpp`) need no key.

## Storage backends

| Variable | Used by |
|---|---|
| `REDIS_URL` | Redis checkpointer — notebooks 08, 68 |
| `S3_BUCKET` | S3 checkpointer — notebook 52 |
| `S3_ENDPOINT_URL` | S3-compatible endpoint (MinIO, R2) — notebook 52 |

## Serving

| Variable | Used by |
|---|---|
| `TULIP_SERVER_API_KEY` | `AgentServer` bearer token — notebook 68 |
| `TULIP_A2A_API_KEY` | `A2AServer.__init__` bearer token |

## LiteLLM gateway

Notebooks 71 and 72. See [the gateway how-to](litellm-gateway.md).

| Variable | Used by |
|---|---|
| `LITELLM_GATEWAY_URL` | Gateway base URL |
| `LITELLM_GATEWAY_KEY` | Virtual key the agent presents |
| `LITELLM_GATEWAY_MODEL` | Model id as the gateway names it |
| `LITELLM_MASTER_KEY` | Admin key — `/key/generate` and `/spend/*` (needs Postgres) |

## Cloud and security domain

| Variable | Used by |
|---|---|
| `TULIP_AWS_PROFILE` | AWS cloud-posture tools — notebook 73 |
| `AWS_ACCESS_KEY_ID` | Standard AWS credential chain |
| `AWS_SECRET_ACCESS_KEY` | Standard AWS credential chain |
| `SCANNER_API_KEY` | Vulnerability-scanner adapter — notebook 70 |
| `DATAMAP_URL` | Data-map adapter — notebook 70 |
| `DATAMAP_API_KEY` | Data-map adapter — notebook 70 |
| `DATAMAP_TOKEN` | Data-map adapter — notebook 70 |

## Model fingerprinting

Notebook 80. See [cloud posture](../concepts/cloud-posture.md).

| Variable | Used by |
|---|---|
| `FINGERPRINT_MODEL` | Model id under test |
| `FINGERPRINT_ASSET` | Asset label recorded on the finding |
| `FINGERPRINT_SAMPLES` | Number of timing samples to collect |

## Other

| Variable | Used by |
|---|---|
| `OPENCLAW_DIR` | OpenClaw workspace root — the red-team example |
