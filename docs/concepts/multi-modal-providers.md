# Multi-modal providers

The model is one provider a SOC agent depends on. Production triage
agents pull from more: a threat-intel index for IOC reputation, a
SIEM/log fetcher, a malware-sandbox image reader, an incident-call
transcriber. Tulip exposes those as a small set of **Protocol** types
under `tulip.providers` and an opt-in auto-registration step that turns
each one into a model-callable tool.

```python
from tulip.agent import Agent
from tulip.providers.web_fetch import HTTPXWebFetcher
from tulip.providers.web_search import OpenAISearchPreviewProvider
from tulip.providers.image import OpenAIImageProvider
from tulip.providers.speech import OpenAISpeechProvider
from tulip.models.native.openai import OpenAIModel

agent = Agent(
    model="openai:gpt-4o-mini",
    web_search=OpenAISearchPreviewProvider(OpenAIModel("gpt-4o-search-preview")),  # IOC reputation lookups
    web_fetch=HTTPXWebFetcher(),         # pull SIEM/log pages, advisories, PCAP exports
    image_generator=OpenAIImageProvider(model="dall-e-3"),  # render attack-path diagrams
    speech_provider=OpenAISpeechProvider(),  # transcribe incident-bridge calls
)
```

Setting any of those four kwargs on `Agent` (or `AgentConfig`) registers
a matching `@tool`:

| Provider kwarg | Auto-registered tool(s) | Signature |
|---|---|---|
| `web_search=` | `web_search` | `query: str, max_results: int = 5` |
| `web_fetch=` | `web_fetch` | `url: str, max_chars: int = 50000` |
| `image_generator=` | `generate_image` | `prompt: str, size: str = "1024x1024", n: int = 1` |
| `speech_provider=` | `speak` and/or `transcribe` | depends on `provider.capabilities` |

The model can call these alongside the security `@tool` set — `query_siem`,
`enrich_indicator`, `lookup_hash`, `isolate_host`, `block_indicator` —
sharing the same registry, the same idempotency machinery, the same hooks.

## The protocols

Each provider is a one- or two-method `typing.Protocol` decorated with
`@runtime_checkable`, so any duck-typed object that implements the
methods is accepted. You don't need to subclass.

- `BaseWebSearchProvider`: `async search(query, max_results)` →
  `list[SearchResult]`.
- `BaseWebFetchProvider`: `async fetch(url, max_chars, keep_html)` →
  `WebPage`.
- `BaseImageGenerationProvider`: `async generate(prompt, size, n)` →
  `list[ImageResult]`.
- `BaseSpeechProvider`: `capabilities: frozenset[str]` plus
  `async speak(text, voice)` and/or `async transcribe(audio_bytes,
  content_type)`.

The shared Pydantic types live in `tulip.providers.types` (`SearchResult`,
`WebPage`) and beside each protocol (`ImageResult`, `SynthesizedAudio`,
`SpeechTranscript`).

## Built-in implementations

- `HTTPXWebFetcher` — uses the `httpx` dep that's already in core, plus a
  stdlib `HTMLParser` shim that strips `<script>` / `<style>` and
  collapses whitespace. No `beautifulsoup` dep. Good for pulling vendor
  advisories, SIEM/log export pages, and CVE detail.
- `OpenAISearchPreviewProvider` — wraps OpenAI's `gpt-4o-search-preview`
  chat-completions model. The model performs the retrieval itself and
  returns annotated results; the provider pins them through a strict
  JSON schema and returns a list of `SearchResult` — handy for IOC
  reputation pivots before you commit to a hard `enrich_indicator` call.
- `OpenAIImageProvider` — `images.generate` (`dall-e-3` /
  `gpt-image-1`). Surfaces hosted URLs when the API returns them and
  base64 PNG bytes otherwise. Use it to render attack-path / kill-chain
  diagrams in an incident report.
- `OpenAISpeechProvider` — `audio.speech.create` (TTS,
  default `tts-1`) plus `audio.transcriptions.create` (Whisper, default
  `whisper-1`). Transcribe incident-bridge calls into text the triage
  agent can reason over.

All four lazy-import `openai` / `httpx` so the SDK core stays free of
optional dependencies until you actually wire one of these in.

## Bring your own

The protocols are the contract — implement them and you're in. A SOC
team might wrap a threat-intel API (VirusTotal/GreyNoise) for search,
`trafilatura` for fetching advisories, a malware-sandbox image API for
detonation screenshots, or a transcription API for incident-bridge
audio. The agent glue stays identical: set the kwarg on `AgentConfig`,
the SDK registers the tool.

```python
class ThreatIntelSearch:
    async def search(self, query, *, max_results=5):
        ...  # call the threat-intel API, return list[SearchResult]
              # of IOC reputation hits (domains, hashes, ASNs)

agent = Agent(
    model=...,
    web_search=ThreatIntelSearch(),  # picked up via runtime_checkable Protocol
)
```

## What this is not

- **Not a replacement for `@tool`.** Hand-written security tools still
  call your SIEM, EDR, and intel platforms (`query_siem`,
  `enrich_indicator`, `isolate_host`). The provider registry is for the
  small set of modalities almost every triage agent needs.
- **Not multi-modal model wiring.** This is *capability* wiring — the
  model itself is still text-in / text-out. If you want a vision model
  reading sandbox-detonation screenshots, configure that on the model side.
- **Not a multi-modal output channel.** `speak` returns a tool-string
  summary so the model isn't fed raw audio bytes; the actual audio
  lives on the provider and your application code retrieves it from
  there when it's time to emit on a voice channel.

## Source and tests

- `src/tulip/providers/` — the four protocols, four implementations,
  and the `auto_register()` glue.
- `tests/unit/test_providers.py` — runtime-checkable protocols, tool
  factories, `AgentConfig` wiring.
- `tests/integration/test_providers_live.py` — live `httpx` fetch,
  live OpenAI search / image / speech (gated behind env vars).
