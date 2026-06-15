# Notebooks

Runnable `examples/notebook_NN_*.py` files. Every one runs end-to-end
against the bundled `MockModel` (no credentials required) and upgrades
to a live provider — OpenAI / Anthropic — by setting one
environment variable.

<div class="notebook-filter">
  <input
    type="search"
    id="notebook-filter-input"
    class="notebook-filter__input"
    placeholder="Filter notebooks (e.g. rag, hooks, agents)…  press ⌘K"
    autocomplete="off"
    autocorrect="off"
    spellcheck="false" />
</div>

Run any notebook directly:

```bash
git clone https://github.com/tuliplabs-ai/sdk-python.git
cd sdk-python && pip install -e .
python examples/notebook_06_basic_agent.py
```

The **#** column is the real file number, so `06` is
`examples/notebook_06_basic_agent.py`. They're in suggested reading order —
start at the foundations and walk forward; each builds on the last.

!!! tip "Here for the security capabilities?"
    Jump to **[Agentic AI-security](#agentic-ai-security)** — red-team, verify,
    policy-gated actions, and SecurityContext. The sections before it build the
    agent foundations those capstones rely on.

## 06–15 · Agent foundations

The agent loop, tools, memory, streaming, hooks. Where to send a
brand-new developer.

| # | Notebook |
|---|---|
| 06 | [Basic agent][nb06] |
| 07 | [Agent with tools][nb07] |
| 08 | [Conversation memory][nb08] |
| 11 | [Streaming events][nb11] |
| 12 | [Lifecycle hooks][nb12] |
| 13 | [SSE streaming][nb13] |
| 14 | [Hooks (advanced)][nb14] |
| 15 | [Termination conditions][nb15] |

## 16–23 · Graphs & composition

`StateGraph`, conditional edges, reducers, retries, the functional API.

| # | Notebook |
|---|---|
| 16 | [Basic graph][nb16] |
| 17 | [Conditional routing][nb17] |
| 18 | [State reducers][nb18] |
| 19 | [Human-in-the-loop][nb19] |
| 20 | [Command + advanced patterns][nb20] |
| 21 | [Composition (Sequential / Parallel / Loop)][nb21] |
| 22 | [Graph (advanced) — retries, subgraphs][nb22] |
| 23 | [Functional API (`@task`, `@entrypoint`)][nb23] |

## 24–34 · Multi-agent

In-process patterns plus A2A, DeepAgent, and real-world crew workflows.

| # | Notebook | Shape |
|---|---|---|
| 24 | [Swarm][nb24] | Peer-to-peer shared context |
| 25 | [Agent handoff][nb25] | Sequential escalation |
| 26 | [Orchestrator pattern][nb26] | Coordinator + parallel specialists |
| 27 | [Specialist agents][nb27] | Named domain experts |
| 28 | [A2A protocol (cross-process)][nb28] | HTTP + SSE mesh |
| 29 | [DeepAgent — research factory][nb29] | Reflexion + grounding + subagents |
| 30 | [Map-reduce code review][nb30] | `Send` fan-out / reduce |
| 31 | [Supervisor + critic loop][nb31] | Refinement loop with cycles |
| 32 | [Adversarial debate + judge][nb32] | Typed `Verdict` via `output_schema` |
| 33 | [Multi-agent + human-in-the-loop][nb33] | Three HITL patterns in one file |
| 34 | [Emergent routing][nb34] | Opt-in LLM-as-picker |

## 35–37 · Reasoning & structured output

Pydantic schemas, Reflexion, grounding, GSAR.

| # | Notebook |
|---|---|
| 35 | [Structured output (Pydantic)][nb35] |
| 36 | [Reasoning patterns][nb36] |
| 37 | [GSAR — typed grounding][nb37] |

## 38–40 · RAG

| # | Notebook |
|---|---|
| 38 | [RAG basics][nb38] |
| 39 | [RAG providers (vector stores, embeddings)][nb39] |
| 40 | [RAG agents][nb40] |

## 45–49 · Skills, playbooks & plugins

| # | Notebook |
|---|---|
| 45 | [MCP integration][nb45] |
| 46 | [Playbooks][nb46] |
| 47 | [Plugins][nb47] |
| 48 | [Skills][nb48] |
| 49 | [Steering (LLM-as-policy hook)][nb49] |

## 50–57 · Hardening for production

Guardrails, checkpointers, evaluation, the provider matrix, multi-modal.

| # | Notebook |
|---|---|
| 50 | [Guardrails & security (basics)][nb50] |
| 51 | [Guardrails (advanced)][nb51] |
| 52 | [Checkpoint backends][nb52] |
| 55 | [Evaluation][nb55] |
| 56 | [Model providers][nb56] |
| 57 | [Multi-modal providers (web, images, audio)][nb57] |

## 58–62 · Cognitive router & observability

| # | Notebook |
|---|---|
| 58 | [Cognitive router (PRISM)][nb58] |
| 59 | [Observability basics — opt-in SSE telemetry][nb59] |
| 60 | [Agent yield bridge + token usage][nb60] |
| 61 | [EventBus subscriber patterns][nb61] |
| 62 | [Full event catalogue tour][nb62] |

## 63–67 · Real-world workflows

End-to-end use cases — incident response, vendor review, voice.

| # | Notebook |
|---|---|
| 63 | [On-call incident response][nb63] |
| 64 | [Vendor security review with risk-tiered approval][nb64] |
| 65 | [DPA & security-addendum review][nb65] |
| 66 | [Spoken security advisory (TTS)][nb66] |
| 67 | [Security-hotline voice assistant (voice in → voice out)][nb67] |

## 68–72 · Server, pipelines & gateway

| # | Notebook |
|---|---|
| 68 | [Agent server (FastAPI)][nb68] |
| 69 | [Research workflow (full pipeline)][nb69] |
| 70 | [Live vendor integrations (IOC intel, SIEM, GPU probe)][nb70] |
| 71 | [LiteLLM AI Gateway][nb71] |
| 72 | [LiteLLM AI Gateway — cost tracking][nb72] |

## Agentic AI-security

The flagship trust layer — point at another AI and red-team it, verify a
finding before acting, gate the action by policy, and investigate by domain.

| # | Notebook |
|---|---|
| 73 | [Grounded cloud-posture agent][nb73] |
| 74 | [SOC playbooks over the security toolset][nb74] |
| 75 | [Red-team an AI agent (grounded findings or abstentions)][nb75] |
| 76 | [Red-team a customer-support chatbot][nb76] |
| 77 | [A CI security gate for AI agents][nb77] |
| 78 | [Verify findings — prevent security hallucinations][nb78] |
| 79 | [SOC alert triage with SIEM-grounded verdicts][nb79] |
| 80 | [Model & hardware fingerprinting (timing side-channels)][nb80] |
| 81 | [Incident response with a tamper-evident audit chain][nb81] |
| 82 | [Investigate an incident with SecurityContext][nb82] |

[nb06]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_06_basic_agent.py
[nb07]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_07_agent_with_tools.py
[nb08]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_08_agent_memory.py
[nb11]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_11_agent_streaming.py
[nb12]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_12_agent_hooks.py
[nb13]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_13_sse_streaming.py
[nb14]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_14_hooks_advanced.py
[nb15]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_15_termination.py
[nb16]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_16_basic_graph.py
[nb17]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_17_conditional_routing.py
[nb18]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_18_state_reducers.py
[nb19]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_19_human_in_the_loop.py
[nb20]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_20_advanced_patterns.py
[nb21]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_21_composition.py
[nb22]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_22_graph_advanced.py
[nb23]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_23_functional_api.py
[nb24]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_24_swarm_multiagent.py
[nb25]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_25_agent_handoff.py
[nb26]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_26_orchestrator_pattern.py
[nb27]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_27_specialist_agents.py
[nb28]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_28_a2a_protocol.py
[nb29]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_29_deepagent.py
[nb30]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_30_map_reduce_code_review.py
[nb31]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_31_supervisor_critic_loop.py
[nb32]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_32_debate_with_judge.py
[nb33]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_33_multiagent_human_in_loop.py
[nb34]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_34_emergent_routing.py
[nb35]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_35_structured_output.py
[nb36]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_36_reasoning_patterns.py
[nb37]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_37_gsar_typed_grounding.py
[nb38]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_38_rag_basics.py
[nb39]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_39_rag_providers.py
[nb40]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_40_rag_agents.py
[nb45]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_45_mcp_integration.py
[nb46]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_46_playbooks.py
[nb47]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_47_plugins.py
[nb48]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_48_skills.py
[nb49]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_49_steering.py
[nb50]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_50_guardrails_security.py
[nb51]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_51_guardrails_advanced.py
[nb52]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_52_checkpoint_backends.py
[nb55]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_55_evaluation.py
[nb56]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_56_model_providers.py
[nb57]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_57_multimodal_providers.py
[nb58]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_58_cognitive_router.py
[nb59]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_59_observability_basics.py
[nb60]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_60_agent_yield_bridge.py
[nb61]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_61_eventbus_subscribers.py
[nb62]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_62_event_catalogue.py
[nb63]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_63_incident_response.py
[nb64]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_64_procurement_approval.py
[nb65]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_65_contract_review.py
[nb66]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_66_audio_response.py
[nb67]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_67_audio_chat.py
[nb68]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_68_agent_server.py
[nb69]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_69_research_workflow.py
[nb70]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_70_vendor_integrations.py
[nb71]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_71_litellm_gateway.py
[nb72]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_72_litellm_gateway_cost.py
[nb73]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_73_cloud_posture_agent.py
[nb74]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_74_security_playbooks.py
[nb75]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_75_agent_red_team.py
[nb76]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_76_redteam_support_bot.py
[nb77]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_77_ci_security_gate.py
[nb78]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_78_verify_findings.py
[nb79]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_79_soc_alert_triage.py
[nb80]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_80_model_fingerprint.py
[nb81]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_81_ir_audit_trail.py
[nb82]: https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_82_investigate_with_ctx.py
