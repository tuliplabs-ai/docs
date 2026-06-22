# Notebooks

Every example is a runnable `.py` file that works end-to-end against the bundled
`MockModel` — no credentials — and upgrades to a live provider (OpenAI /
Anthropic) by setting one environment variable. Within each track they build on
each other.

<div class="notebook-filter">
  <input
    type="search"
    id="notebook-filter-input"
    class="notebook-filter__input"
    placeholder="Filter the notebooks (e.g. rag, hooks, red-team)…  press ⌘K"
    autocomplete="off"
    autocorrect="off"
    spellcheck="false" />
</div>

Run any example — each link below opens its file:

```bash
git clone https://github.com/tuliplabs-ai/sdk-python.git
cd sdk-python && pip install -e .
python examples/<file>.py
```

!!! tip "New to Tulip?"
    Skim **Foundations** for the agent mechanics, then go to **Agentic
    AI-security** for the flagship capstones. In a hurry? The security track
    stands on its own — everything before it is the SOC plumbing it relies on.

## Agentic AI-security

The flagship trust layer — point at another AI and red-team it, verify a finding
before acting, gate the action by policy, and investigate by domain.

| Example | What it shows |
|---|---|
| [Red-team an AI agent][nb75] | Grounded findings or abstentions across the OWASP-ASI / MITRE-ATLAS suite |
| [Red-team a support chatbot][nb76] | Prompt-injection, jailbreak, and data-leak probes against a live endpoint |
| [Verify findings][nb78] | An independent skeptic refutes a hallucinated "critical" before it drives an action |
| [CI security gate][nb77] | Fail the build when an agent regression ships a vulnerability |
| [SOC alert triage][nb79] | SIEM-grounded verdicts — cite the evidence or abstain |
| [Investigate with SecurityContext][nb82] | One investigation across many vendors, no vendor names in your code |
| [Incident response + audit chain][nb81] | A tamper-evident trail of every decision and action |
| [SOC playbooks][nb74] | NIST 800-61 runbooks over the security toolset |
| [Grounded cloud-posture audit][nb73] | Read-only AWS posture findings that abstain without evidence |
| [Model & hardware fingerprinting][nb80] | Identify a co-tenant's model via timing side-channels |

## Foundations

The agent loop wired for security work — `security_toolset`,
`create_soc_analyst`, and `ground_finding` so a triage agent abstains when the
evidence isn't there. Hooks and termination are your kill-switch.

| Example | What it shows |
|---|---|
| [Basic agent][nb06] | Model + system prompt; blocking vs streaming run |
| [Agent with tools][nb07] | IOC enrichment via `@tool` in a ReAct loop |
| [Conversation memory][nb08] | Multi-turn investigation state |
| [Streaming events][nb11] | The typed event stream as the agent runs |
| [SSE streaming][nb13] | Server-sent events for a SOC console |
| [Lifecycle hooks][nb12] | Audit + guardrail hooks around every tool call |
| [Hooks — advanced][nb14] | Priority bands and steering |
| [Termination conditions][nb15] | Stop when isolated **and** confident; bound runaway loops |

## Graphs & composition

`StateGraph` for approval-gated escalation — conditional edges that route
high-blast-radius actions (`isolate_host`, `block_indicator`) through human
sign-off, reducers that fold SIEM evidence, retries on flaky enrichment.

| Example | What it shows |
|---|---|
| [Basic graph][nb16] | Nodes, edges, state |
| [Conditional routing][nb17] | Branch on severity / confidence |
| [State reducers][nb18] | Fold evidence from parallel branches |
| [Human-in-the-loop][nb19] | Pause for analyst sign-off before containment |
| [Command + advanced patterns][nb20] | Dynamic control flow |
| [Composition][nb21] | Sequential / Parallel / Loop pipelines |
| [Graph — advanced][nb22] | Retries, subgraphs |
| [Functional API][nb23] | `@task` / `@entrypoint` |

## Agent teams

IR war-room patterns — swarm and handoff put analysts on a shared incident
context, L1 → L2 → L3 escalation, a supervisor/critic loop to catch hallucinated
findings, and a judge to adjudicate red-team verdicts.

| Example | What it shows |
|---|---|
| [Swarm][nb24] | Peer-to-peer shared incident context |
| [Agent handoff][nb25] | Sequential L1 → L2 escalation with full transcript |
| [Orchestrator][nb26] | Coordinator + parallel specialists (triage / forensics / containment) |
| [Specialist agents][nb27] | Named domain experts |
| [A2A protocol][nb28] | Cross-process threat-intel ↔ SOC mesh |
| [DeepAgent][nb29] | Reflexion + grounding + subagents for threat research |
| [Map-reduce review][nb30] | `Send` fan-out / reduce over security findings |
| [Supervisor + critic loop][nb31] | Refinement loop that challenges weak findings |
| [Adversarial debate + judge][nb32] | True-positive vs benign, adjudicated to a typed `Verdict` |
| [Multi-agent + human-in-the-loop][nb33] | Three HITL patterns in one file |
| [Emergent routing][nb34] | Opt-in LLM-as-picker |

## Reasoning & grounding

Typed `Finding` / `Abstention`, Reflexion for self-correcting triage, and GSAR
grounding — abstain-by-construction, so no evidence means no claim, never a
guessed verdict.

| Example | What it shows |
|---|---|
| [Structured output][nb35] | Typed `Finding` over Pydantic |
| [Reasoning patterns][nb36] | Reflexion, causal chains |
| [GSAR — typed grounding][nb37] | The four-way claim partition + tiered replanning |

## Threat-intel RAG

Retrieval as grounding evidence — pull from IOC feeds and playbook stores, then
`ground_finding` against the retrieved context so the agent cites or abstains.

| Example | What it shows |
|---|---|
| [RAG basics][nb38] | Index + retrieve threat-intel |
| [RAG providers][nb39] | Vector stores, embeddings, rerankers |
| [RAG agents][nb40] | Retrieval wired into a triage agent |

## Skills, playbooks & policy

Codify SOC runbooks as playbooks, wire MCP-backed security tools, and add
LLM-as-policy steering to veto unsafe `block_indicator` / `isolate_host` calls
before they run.

| Example | What it shows |
|---|---|
| [MCP integration][nb45] | Expose / consume security tools over MCP |
| [Playbooks][nb46] | NIST-shaped runbooks with enforced tool order |
| [Plugins][nb47] | Package and share capabilities |
| [Skills][nb48] | Tool-restricted, multi-step procedures |
| [Steering — LLM-as-policy][nb49] | Veto an unsafe action before it executes |

## Hardening for production

Guardrails as the injection-detection layer (PII / prompt-injection /
tool-allowlist), checkpointers that survive a containment restart, and
evaluation harnesses that score detection.

| Example | What it shows |
|---|---|
| [Guardrails & security][nb50] | Injection / PII / allowlist basics |
| [Guardrails — advanced][nb51] | Custom validators and filters |
| [Checkpoint backends][nb52] | Redis / Postgres / S3 durability |
| [Evaluation][nb55] | Score triage accuracy as regression tests |
| [Model providers][nb56] | The provider matrix |
| [Multi-modal providers][nb57] | Threat-intel search, log fetch, transcription |

## Routing & observability

Route alerts to the right analyst (PRISM) and stream SSE telemetry into the
audit trail — every tool call, token, and decision on the EventBus for forensic
replay.

| Example | What it shows |
|---|---|
| [Cognitive router (PRISM)][nb58] | Risk-tiered task routing |
| [Observability basics][nb59] | Opt-in SSE telemetry |
| [Token usage bridge][nb60] | Yield bridge + cost accounting |
| [EventBus subscribers][nb61] | Subscribe and forward to a SIEM |
| [Event catalogue tour][nb62] | Every canonical event |

## Real-world security workflows

End-to-end security operations — on-call incident response, risk-tiered vendor
and DPA review, and a voice-driven security hotline.

| Example | What it shows |
|---|---|
| [On-call incident response][nb63] | Detect → triage → contain, gated |
| [Vendor security review][nb64] | Risk-tiered approval over a questionnaire |
| [DPA & security-addendum review][nb65] | Parse → assess → revise with sign-off |
| [Spoken security advisory][nb66] | Text-to-speech briefing |
| [Security-hotline voice assistant][nb67] | Voice in → voice out |

## Serving & gateways

Ship the SOC agent behind FastAPI, run a full investigation pipeline, and wire
live vendor integrations (IOC intel, SIEM) through a cost-tracked gateway.

| Example | What it shows |
|---|---|
| [Agent server (FastAPI)][nb68] | Multi-tenant SOC service over SSE |
| [Research workflow][nb69] | Full investigation pipeline |
| [Live vendor integrations][nb70] | IOC intel, SIEM, GPU probe |
| [LiteLLM gateway][nb71] | Route through a model gateway |
| [LiteLLM gateway — cost tracking][nb72] | Per-investigation cost accounting |

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
