# Models

Native providers: **OpenAI** (`openai:`), **Anthropic** (`anthropic:`),
**Azure OpenAI** (`azure:`) and **Amazon Bedrock** (`bedrock:`). Also
routed by name: a table of OpenAI-compatible prefixes, such as `ollama:`,
`vllm:`, `lmstudio:`, `groq:`, `together:`, `openrouter:`, `deepseek:`,
`mistral:` and `gemini:`. Each prefix has its own default endpoint and
API-key variable. Any other OpenAI-compatible endpoint works through
`openai-compatible:<model>` with an explicit `base_url=`. See
[OpenAI-compatible providers](../concepts/providers/openai-compatible.md).
A model is a string — the prefix before the colon selects the provider.

For the concepts, start with [Model providers](../concepts/models.md).

## Registry

String factory — routes `"openai:gpt-4o"`,
`"anthropic:claude-sonnet-4-6"`, etc. to the right client.

::: tulip.models.registry.get_model
::: tulip.models.registry.list_providers
::: tulip.models.registry.register_provider
::: tulip.models.providers.CompatibleProvider
::: tulip.models.providers.register_compatible_providers

## Base contract

Every model provider implements `ModelProtocol`. `RequestBuilder` and
`ResponseParser` are the per-provider seams for translating between
Tulip's `ModelConfig` / `Message` types and the provider's wire
format.

::: tulip.models.base.ModelProtocol
::: tulip.models.base.ModelConfig
::: tulip.models.base.ModelResponse
::: tulip.models.base.RequestBuilder
::: tulip.models.base.ResponseParser

## OpenAI

::: tulip.models.native.openai.OpenAIModel
::: tulip.models.native.openai.OpenAIConfig

## Anthropic

::: tulip.models.native.anthropic.AnthropicModel
::: tulip.models.native.anthropic.AnthropicConfig

## Azure OpenAI

See [Azure OpenAI](../concepts/providers/azure.md).

::: tulip.models.native.azure.AzureOpenAIModel
::: tulip.models.native.azure.AzureOpenAIConfig

## Amazon Bedrock

Needs the `bedrock` extra (`pip install "tulip-agents[bedrock]"`). See
[Amazon Bedrock](../concepts/providers/bedrock.md).

::: tulip.models.native.bedrock.BedrockModel
::: tulip.models.native.bedrock.BedrockConfig
