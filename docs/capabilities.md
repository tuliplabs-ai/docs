# Capabilities

Everything Tulip ships, what it
does, and where to find it.

## Status at a glance

| Capability group | Status | Execution mode and requirements | Important limitation |
|---|---|---|---|
| Agent loop, tools, control policy, events | Supported | Core install; provider required only for model calls | Controls apply only where configured and wired |
| OpenAI, Anthropic, Azure OpenAI, Bedrock, OpenRouter, and Together.ai model access | Supported | Live; provider extra and credential required | Azure and Bedrock are native transports; OpenRouter and Together.ai use the OpenAI-compatible transport; model capabilities vary |
| Checkpointer and vector-store adapters | Supported interfaces | Live infrastructure for non-memory backends; matching extra/config required | Operate and test the backing service yourself |
| `SecurityContext` reference adapters | Offline simulation | No credentials | Vendor write templates return simulated receipts unless replaced and verified |
| Published research and evaluation artifacts | Research-only | See each research page | Some source datasets and evaluated model artifacts are not publicly available |

This build targets `tulip-agents` {{ tulip_sdk_version }} on Python 3.11–3.14. See the
[compatibility policy](compatibility.md) for label definitions and upgrade
guidance.

{{ tulip_diagram trust-chain }}

!!! sdk-distinctive "Distinctive to the SDK"
    - **The control runtime — let an agent act, on your terms.** A
      side-effecting action (a refund, a production deploy, a GDPR deletion)
      runs only after it clears a `ControlPolicy` you write: `approve()`
      weighs it, `admit()` runs it only on an allow, or on a hold a named
      person approves (`approved_by=`), and a supplied
      `AuditTrail` records each decision (each entry is chained to
      the one before it — editing any record breaks `verify()`). Policy →
      approval → admission → audit, enforced in code, not convention.
    - **Eight native multi-agent shapes** — Composition
      (Sequential / Parallel / Loop), Orchestrator + Specialists, Swarm,
      Handoff, StateGraph, and cross-process A2A — plus the Functional API
      (`@task` / `@entrypoint`) and DeepAgent (a research factory built on
      top).
      Use them directly, or reach for them from the loop as tools.
    - **In-process observability** — opt-in `EventBus` with agent yield
      bridge. One `run_context()` streams {{ tulip_event_count }} canonical events from every
      layer (agent, multi-agent, RAG, memory, A2A). Zero allocations
      when unused.
    - **Reasoning loop nodes** — Reflexion, Grounding, Causal as first-class
      Think → Execute → **Reflect** → Think nodes, not bolted-on libraries.
    - **GSAR** — typed-grounding safety layer from
      [arXiv:2604.23366 (2026)](https://arxiv.org/abs/2604.23366):
      four-way claim partition (grounded / ungrounded / contradicted /
      complementary) + tiered replanning decisions. A claim graded by
      `ground_finding()` becomes a typed `Evidence` only above the threshold,
      else it **abstains**, and
      `verify()` challenges it before it drives an action.
    - **Termination algebra** — `MaxIterations(10) | TextMention("DONE") & ConfidenceMet(0.9)` is real Python (`__or__` / `__and__` overloads). Greppable, unit-testable, serialisable.
    - **Idempotent tools** — `@tool(idempotent=True)` dedupes identical
      `(name, args)` calls inside the documented run/checkpoint scope. External
      systems still need stable idempotency keys for crash recovery.
    - **OpenAI, Anthropic, Azure OpenAI, Bedrock, and compatible providers** —
      OpenAI, Anthropic, Azure OpenAI and Bedrock as native transports, plus
      hosted and self-hosted OpenAI-compatible endpoints (OpenRouter,
      Together.ai and more) auto-routed by model prefix. One
      `get_model()` call, any provider.

## Agent core

| Feature | What it does | Surface |
|---|---|---|
| **Agent** + `AgentConfig` + `AgentResult` | The Think → Execute → Reflect → Terminate loop | `tulip.agent` · [Agent loop](concepts/agent-loop.md) |
| **Termination algebra** | Stop conditions for a write — `(ToolCalled("issue_refund") & ConfidenceMet(0.9)) \| TextMention("ESCALATE") \| MaxIterations(10)` caps a refund run | `tulip.core.termination` · [Termination](concepts/termination.md) |
| **Idempotent tools** | `@tool(idempotent=True)` reuses results for identical calls in the documented run/checkpoint scope | `tulip.tools.decorator` · [Idempotency](concepts/idempotency.md) |
| **Reflexion** | Self-evaluation node in the ReAct cycle; rewrites the next turn when the last one was wrong | `Agent(reflexion=True)` · [Reasoning](concepts/reasoning.md) |
| **Grounding** | LLM-as-judge claim verification against tool results; below-threshold triggers replanning | `Agent(grounding=True)` · [Reasoning](concepts/reasoning.md) |
| **Causal chains** | Cause-effect graph builder with cycle/contradiction detection | `tulip.reasoning.causal.CausalChain` · [Reasoning](concepts/reasoning.md) |
| **GSAR** | Typed-grounding safety layer ([arXiv:2604.23366 (2026)](https://arxiv.org/abs/2604.23366)) — four-way claim partition + tiered replanning | `Agent(gsar=GSARConfig(...))` · [GSAR](concepts/gsar.md) |
| **Cancel** | Thread-safe abort during a run; emits `TerminateEvent` with reason | `agent.cancel()` · [Agent loop](concepts/agent-loop.md) |
| **Interrupts (HITL)** | Pause via `InterruptEvent`; resume with `agent.resume(...)` | `tulip.core.interrupt` · [Interrupts](concepts/interrupts.md) |
| **Structured output** | Pass `output_schema=` (Pydantic), final answer is parsed into a typed instance | `tulip.agent.config`, `tulip.core.structured` · [Structured output](concepts/structured-output.md) |
| **Hooks** | before/after × invocation × tool × model lifecycle observation + steering | `tulip.hooks.provider` · [Hooks](concepts/hooks.md) |
| **Plugins** | Bundle hooks + tools as one drop-in unit | `tulip.hooks.plugin` · [Hooks](concepts/hooks.md) |

## Multi-agent — operational shapes

Every pattern maps to a real workflow across domains — payments, infra,
support, data, security. The shape *is* the discipline: who runs in
parallel and who hands off. No shape gates whether a refund clears, a host
is isolated, or a record is deleted — route that side effect through
`admit()`.

{{ tulip_diagram orchestrator }}

| Shape | Maps to | Surface |
|---|---|---|
| **Composition** | Payments: sequential fraud-check → risk-score → settle; parallel enrichment fan-out over a transaction's signals | `tulip.agent.composition` · [Composition](concepts/multi-agent/composition.md) |
| **Orchestrator** | Security: one coordinator dispatches the triage, forensics and containment specialists it picks, in parallel, then correlates their findings | `tulip.multiagent.orchestrator` · [Orchestrator](concepts/multi-agent/orchestrator.md) |
| **Swarm** | Data & privacy: peers claim the tasks of a GDPR deletion from a shared queue and post their findings to a shared context | `tulip.multiagent.swarm` · [Swarm](concepts/multi-agent/swarm.md) |
| **Handoff** | Customer support: tier-1 hands the ticket + full history to tier-2, with context preserved | `tulip.multiagent.handoff` · [Handoff](concepts/multi-agent/handoff.md) |
| **StateGraph** | Infra: re-run a DB migration until the schema is healthy, conditional rollback edges | `tulip.multiagent.graph` · [StateGraph](concepts/multi-agent/graph.md) |
| **Functional API** | Cloud: map a config audit over N instances, reduce to one posture verdict | `tulip.multiagent.functional` · [Functional](concepts/multi-agent/functional.md) |
| **A2A** | Cross-process handoff to a remote payouts, IR, or threat-intel service | `tulip.a2a` · [A2A](concepts/multi-agent/a2a.md) |

```python
# Orchestrator over fraud-check, risk-score and settlement: the desk's model
# picks which run, the picked ones run in parallel, then the desk correlates
# and summarizes. Specialists never see each other's work, and their tool
# calls are not executed — send the refund itself through admit().
from tulip.models import get_model
from tulip.multiagent import Orchestrator, Specialist

model = get_model("{{ tulip_example_model }}")
settlement = Specialist(
    name="settlement",
    specialist_type="settlement",
    description="Recommends how to settle a dispute.",
    system_prompt="Recommend a settlement, citing the evidence in the task.",
    model=model,
)
desk = Orchestrator(model=model)
desk.register_specialists([fraud_check, risk_score, settlement])
result = await desk.execute("Recommend how to resolve the duplicate charge on order 8842.")
```

## Security — a worked example domain

The most fully built domain package, and the proof the chain holds under
pressure: point an agent at an AI or at infrastructure, and every finding comes
back grounded or abstained, ready to be verified, gated, and audited. The same
chain — grounding, gating, audit — applies to any domain: a claim graded by
`ground_finding()` becomes evidence only when it clears the GSAR threshold, a
side effect routed through `admit()` runs only on an allow decision or on a hold
a named person approves, and `admit()` records every decision it makes (allowed,
held or denied) on the trail you pass. What it cannot do is gate a side effect
that never passes through it, or classify your actions for you — an action left
labelled `environment="staging"` never matches a policy that holds production,
so see [Guarantees and boundaries](why-tulip.md).

{{ tulip_diagram grounded-findings }}

| Feature | What it does | Surface |
|---|---|---|
| **Grounded findings** | `ground_finding` returns a typed `Evidence` only when the claim clears the GSAR threshold — else an `Abstention`. Build findings through it, not by constructing `Evidence` directly. | `ground_finding` · [Grounded findings](concepts/security.md) |
| **Target** | One handle over any AI under assessment — remote endpoint, in-process `Agent`, A2A peer, or callable | `Target.endpoint/.agent/.a2a/.from_callable` · [Agentic AI-security](concepts/agentic-ai-security.md) |
| **Red-teaming** | OWASP-ASI probe suite → grounded `Evidence` (tagged OWASP LLM / ASI / MITRE ATLAS) or `Abstention` | `red_team(target)` · [Agentic AI-security](concepts/agentic-ai-security.md) |
| **Assurance** | Grounded guardrail-coverage posture across the suite | `assure(target)` |
| **Verification** | An independent skeptic challenges a finding's evidence and rescores confidence | `verify(finding) -> VerificationResult` · [Verify findings](notebooks/notebook_78_verify_findings.md) |
| **Policy + approval** | Weigh an action against evidence, verification, and a `ControlPolicy` → allow / hold / deny (`allow` / `require_human` / `deny` in the API) | `approve(action, policy=…)` · [SecurityContext](concepts/security-context.md) |
| **Admission gate** | Run a side-effecting action only if it clears the chain; `admit(trail=...)` records the decision to the audit trail you pass; else raises `AdmissionError` | `admit(...)` · `ctx.actions.execute(...)` · [SecurityContext](concepts/security-context.md) |
| **SecurityContext** | Investigate by domain (logs / endpoint / identity / cloud / threat-intel / actions), not by vendor | `SecurityContext()` · [SecurityContext](concepts/security-context.md) |
| **Audit trail** | Hash-chained, tamper-evident record of every entry written to it, including each decision `admit(trail=...)` makes; exports JSONL for a SIEM | `AuditTrail` · [Observability](concepts/observability.md) |
| **Cloud posture (read-only)** | Spec-driven AWS auditing — `describe_aws` introspects botocore models; `use_aws` runs read-only calls, writes refused by construction | `tulip.security.aws` · [Cloud posture](concepts/cloud-posture.md) |
| **Inference fingerprinting** | Timing side-channel model/hardware fingerprint → grounded `FingerprintFinding` or abstention | `fingerprint_to_finding` · [Grounded findings](concepts/security.md) |
| **Governed agent** | An `Agent` with grounding + guardrails + audit trail on by default | `governed_agent(...)` · [Agentic AI-security](concepts/agentic-ai-security.md) |

```python
# A finding only exists above the GSAR bar — else it abstains. ground_finding never
# returns an ungrounded Evidence.
from tulip.security import ground_finding, Severity, is_finding

result = ground_finding(
    title="Expired TLS certificate on 192.0.2.10:443",
    description="Certificate expired 3 days ago; clients see TLS errors.",
    severity=Severity.HIGH, asset="192.0.2.10:443",
    remediation="Renew and redeploy the certificate.",
    partition=partition,  # GSAR claim partition from tool evidence
)
if is_finding(result):
    print("SHIPPED", result.title, result.gsar_score)
else:
    print("ABSTAINED", result.decision, "—", result.reason)
```

```python
# The action chain: investigate → verify → policy → admission gate.
# isolate_host fires only if the chain clears; production → hold (require_human).
from tulip.control import Action
from tulip.security import SecurityContext, verify

ctx = SecurityContext()
verdict = await verify(finding)
await ctx.actions.execute(
    Action(name="isolate_host", asset="WS-0142", environment="production"),
    lambda: ctx.endpoint.isolate("WS-0142"),   # side effect, gated
    finding=finding, verdict=verdict,
)   # raises AdmissionError unless the policy allows (here production → hold); call admit(..., trail=trail, approved_by=...) directly to record it or approve the hold
```

## Observability

| Feature | What it does | Surface |
|---|---|---|
| **`EventBus`** | Singleton in-process pub/sub — per-run + global subscribers, bounded queues, history replay, drop accounting | `tulip.observability.EventBus` · [Observability](concepts/observability.md) |
| **`run_context()`** | ContextVar-based opt-in gate — zero allocations when inactive | `tulip.observability.run_context` |
| **Agent yield bridge** | `@_bus_bridge` on `Agent.run` transparently republishes 9 `TulipEvent` types as `agent.*` SSE events | `tulip.agent.runtime_loop` |
| **`EventBusHook`** | `HookProvider` that bridges all agent lifecycle hooks onto the bus (for non-async / pre-built agents) | `tulip.observability.EventBusHook` |
| **Canonical event catalogue** | {{ tulip_event_count }} `EV_*` constants across {{ tulip_event_prefixes }} | `tulip.observability.emit` · [SSE event catalogue](concepts/sse-events.md) |

## Reasoning

{{ tulip_diagram gsar-decision }}

| Feature | What it does | Surface |
|---|---|---|
| **Reflexion** | After each turn, the agent self-evaluates and re-plans on wrong premises | `Agent(reflexion=True)` · [Reasoning](concepts/reasoning.md) |
| **Grounding** | LLM-as-judge over claims vs the tool results that produced them | `Agent(grounding=True)` · [Reasoning](concepts/reasoning.md) |
| **Causal** | Build a cause-effect graph from the trace; surface contradictions | `build_causal_chain()` · [Reasoning](concepts/reasoning.md) |
| **GSAR** | Typed claim partition (grounded / ungrounded / contradicted / complementary) + `proceed`/`regenerate`/`replan`/`abstain` decision | `Agent(gsar=GSARConfig(...))` · [GSAR](concepts/gsar.md) |

## Tools

| Feature | What it does | Surface |
|---|---|---|
| `@tool` decorator | Function → JSON-Schema-typed tool the model can call | `tulip.tools.decorator` · [Tools](concepts/tools.md) |
| Idempotent dedup | `@tool(idempotent=True)` skips repeat calls (same args) in the loop | `tulip.tools.decorator` · [Idempotency](concepts/idempotency.md) |
| **Sequential executor** | Run tool calls one at a time | `tulip.tools.executor` · [Executors](concepts/executors.md) |
| **Concurrent executor** | Run tool calls in parallel | `tulip.tools.executor` · [Executors](concepts/executors.md) |
| **CircuitBreaker executor** | Auto-disable a tool after N failures | `tulip.tools.executor` · [Executors](concepts/executors.md) |
| Result-store offload | Move large tool results to object storage; agent sees a pointer | `tulip.tools.result_storage` |
| Path / URL safety | Validate filesystem and network access from tool args | `tulip.tools.path_safety`, `tulip.tools.url_safety` · [Safety](concepts/safety.md) |
| **MCP — client + server** | Talk to / be talked to by Anthropic-spec MCP servers | `tulip.integrations.fastmcp` · [MCP](concepts/mcp.md) |

## Memory — checkpointer backends

| Backend | Best for | Surface |
|---|---|---|
| `MemoryCheckpointer` | Tests, REPL — in-process dict | `tulip.memory.backends.memory` · [Checkpointers](concepts/checkpointers.md) |
| `FileCheckpointer` | Local dev — JSON files on disk | `tulip.memory.backends.file` |
| `HTTPCheckpointer` | A remote checkpoint service you already run | `tulip.memory.backends.http` |
| **`S3Backend`** | vendor-neutral, lifecycle policies, region replication | `tulip.memory.backends.s3` |
| `RedisBackend` | Multi-replica, fast, TTLs (a managed Redis) | `tulip.memory.backends.redis` |
| `PostgreSQLBackend` | Production DB with metadata queries | `tulip.memory.backends.postgresql` |
| `MySQLBackend` | Production MySQL with official async Connector/Python | `tulip.memory.backends.mysql` |
| `OpenSearchBackend` | Full-text search across past runs | `tulip.memory.backends.opensearch` |

## Memory — context management

| Feature | What it does | Surface |
|---|---|---|
| `SlidingWindowManager` | Keeps the last N messages; drops the rest | `tulip.memory.conversation` · [Conversation management](concepts/conversation-management.md) |
| `SummarizingManager` | LLM rollup of older turns | `tulip.memory.conversation` |
| **`LLMCompactor`** | Budget-aware compaction with head + tail protection | `tulip.memory.compactor` |
| Long-term key-value store | Cross-run user prefs / results with optimistic-locking `version` counter | `tulip.memory.store` |

## Hooks (built-in)

| Hook | What it does | Import |
|---|---|---|
| `LoggingHook` / `StructuredLoggingHook` | Stdlib / structured-JSON logs of every event | `tulip.hooks.builtin` · [Observability](concepts/observability.md) |
| **`TelemetryHook`** | OpenTelemetry traces + metrics (counters, histograms) | `tulip.hooks.builtin` |
| `NoOpTelemetryHook` | Opt-out variant for tests | `tulip.hooks.builtin` |
| `ModelRetryHook` | Auto-retry model calls on throttle/empty with exponential back-off | `tulip.hooks.builtin` · [Retry](concepts/retry.md) |
| **`GuardrailsHook`** | Block dangerous tools, redact PII, enforce content/topic policies | `tulip.hooks.builtin` · [Safety](concepts/safety.md) |
| `ContentFilterHook` | Standalone content moderation | `tulip.hooks.builtin` |
| **`SteeringHook`** | LLM-as-judge approval gate on every tool call | `tulip.hooks.builtin` · [Safety](concepts/safety.md) |

## Streaming + Server

| Feature | What it does | Surface |
|---|---|---|
| **Typed events** | Frozen Pydantic events for `match`-statement consumers | `tulip.core.events` · [Events](concepts/events.md) |
| `StructuredStream` | Incremental Pydantic-partial parsing during streaming | `tulip.core.structured` |
| Console + SSE handlers | Render to terminal or stream over Server-Sent Events | `tulip.core.events` · [Streaming](concepts/streaming.md) |
| **`AgentServer`** | Drop-in FastAPI app: `/invoke`, `/stream`, `/threads/{id}`, `/health` | `tulip.server` · [Agent Server](concepts/server.md) |
| Thread scoping | Bearer-token auth + thread-id namespacing; one shared `api_key` per instance (single-principal — run one keyed instance per tenant for isolation) | `AgentServer(api_key=...)` · [Agent Server](concepts/server.md) |
| Graph streaming | Multi-agent state-graph event streams | `tulip.multiagent.graph` · [Graph streaming](concepts/graph-streaming.md) |

## RAG

| Component | Options | Surface |
|---|---|---|
| Vector stores | pgvector · OpenSearch · Qdrant · Chroma · in-memory | `tulip.rag.stores` · [RAG](concepts/rag.md) |
| Embeddings | `OpenAIEmbeddings` · `CohereEmbeddings` | `tulip.rag.embeddings` |
| Multimodal processors | Text · PDF (text + OCR) · Image (OCR) · Audio (transcription) | `tulip.rag.multimodal` |
| Tool wiring | `create_rag_tool(retriever)` exposes the retriever as a `@tool` | `tulip.rag.tools` |

## Models

| Provider | Models | Surface |
|---|---|---|
| OpenAI | All commercial models (gpt-5.5, o-series, etc) | `tulip.models.native.openai` · [OpenAI](concepts/providers/openai.md) |
| Anthropic | Claude 4.x (e.g. `claude-sonnet-4-6`) — direct API | `tulip.models.native.anthropic` · [Anthropic](concepts/providers/anthropic.md) |
| Azure OpenAI | OpenAI models on a deployment-named Azure resource | `tulip.models.native.azure` · [Azure OpenAI](concepts/providers/azure.md) |
| Amazon Bedrock | Chat models on Bedrock (Nova, Claude, Llama, Mistral and more) through one Converse-API client | `tulip.models.native.bedrock` · [Amazon Bedrock](concepts/providers/bedrock.md) |
| Auto-routing | `get_model("anthropic:claude-sonnet-4-6")` picks transport from id | `tulip.models.registry.get_model` |
| Resilience helpers | Failover classification, credential pooling, prompt-cache breakpoints, rate-limit buckets | `tulip.models.failover` · `tulip.models.pooled` · `tulip.models.caching` · `tulip.models.rate_limits` · [Resilience](concepts/providers/resilience.md) |

## Skills + Playbooks

| Feature | What it does | Surface |
|---|---|---|
| **Skills** | AgentSkills.io progressive disclosure (catalog → instructions → resources) | `tulip.skills.SkillsPlugin` · [Skills](concepts/skills.md) |
| `Skill.from_directory()` | Load a folder of `SKILL.md` bundles | `tulip.skills.models.Skill` |
| **Playbooks** | Numbered execution plans with per-step `PlaybookEnforcer` | `tulip.playbooks` · [Playbooks](concepts/playbooks.md) |
| YAML / JSON / Python loaders | Author playbooks in any of three formats | `tulip.playbooks.loader` |

## Evaluation

| Class | What it does | Surface |
|---|---|---|
| `EvalCase` | A single test case — expected tools / output / iteration / duration budgets | `tulip.evaluation` · [Evaluation](concepts/evaluation.md) |
| `EvalRunner` | Runs a list of cases against an agent, returns `EvalReport` | `tulip.evaluation` |
| `EvalResult` | Per-case pass / score / duration + diagnostic checks | `tulip.evaluation` |
| `EvalReport` | Aggregate stats with `summary()` + JSON serialisation | `tulip.evaluation` |

## Where to next

- **For first-time visitors**: [Quickstart](how-to/quickstart.md) ships a working agent in five minutes.
- **For architecture**: [Agent loop](concepts/agent-loop.md) is the canonical reference.
- **For depth on any feature**: every row in this matrix links to its concept page. Source lives at [`src/tulip/`](https://github.com/tuliplabs-ai/tulip-agents/tree/main/src/tulip); canonical entry is [`src/tulip/__init__.py`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/src/tulip/__init__.py).
