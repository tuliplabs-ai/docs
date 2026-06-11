---
hide:
  - navigation
  - toc
---

<div class="tulip-hero" markdown>
<div class="tulip-hero__copy" markdown>

<p class="tulip-product-name"><span class="tpn-brand">tulip agents</span><span class="tpn-sep"> · </span>the cybersecurity agent SDK</p>

# Security agents that <span class="accent">show their work.</span>

Build agent teams for security work where every finding is traced to evidence, every action is a typed event you can replay, and every risky step is gated. An ungrounded finding is a false positive *by construction* — Tulip won't let an agent ship one.

<div class="tulip-stat-strip" markdown><span style="white-space:nowrap">[MITRE&nbsp;ATLAS](concepts/security.md)</span> · <span style="white-space:nowrap">[OWASP&nbsp;LLM&nbsp;Top&nbsp;10](concepts/security.md)</span> · <span style="white-space:nowrap">[OWASP&nbsp;ASI](concepts/security.md)</span> · <span style="white-space:nowrap">[NIST&nbsp;AI&nbsp;RMF](concepts/security.md)</span></div>

<div class="tulip-hero__cta" markdown>
[Get started](how-to/quickstart.md){ .md-button .md-button--primary }
[GitHub](https://github.com/tuliplabs-ai/sdk-python){ .md-button }
</div>

```bash
pip install "tulip-agents[openai]"   # OpenAI · Anthropic
```

</div>

<div class="tulip-hero__code" markdown>

```python
from tulip.agent import Agent
from tulip.tools import tool
from tulip.observability import run_context, get_event_bus

@tool
def enrich_indicator(value: str) -> dict:
    """Reputation, first-seen, and category for an IP / domain / hash."""
    return intel.lookup(value)

@tool
def query_siem(query: str) -> list[dict]:
    """Run a detection query against the SIEM."""
    return siem.search(query)

@tool(idempotent=True)
def isolate_host(host: str) -> str:
    """Network-isolate a host. Fires exactly once per host."""
    return edr.isolate(host)

agent = Agent(
    model="openai:gpt-4o",
    tools=[enrich_indicator, query_siem, isolate_host],
    grounding=True,        # every claim verified against tool output
    system_prompt="You are a SOC triage analyst. Cite evidence for every verdict.",
)

async with run_context() as rid:
    result = await agent.run(
        "Outbound beaconing from 192.0.2.14 to a domain "
        "registered yesterday — triage and contain if warranted."
    )
    async for ev in get_event_bus().subscribe(rid):
        match ev.event_type:
            case "agent.tool.started": print("🔧", ev.data["tool_name"])
            case "agent.terminate":    print("✓", ev.data["final_message_preview"])
```

</div>
</div>

## Grounded, or it doesn't ship

Security is the one domain where a hallucinated claim isn't an
embarrassment — it's a false positive that burns an analyst's night, or
a false negative that ships a breach. `tulip.security` turns a GSAR
evidence partition into a typed `Finding` **only** when it clears the
grounding threshold; otherwise you get an auditable `Abstention`, never
a finding. There is no public constructor that builds a `Finding`
without a score.

```python
from tulip.security import ground_finding, Severity, is_finding
from tulip.reasoning.gsar import Claim, EvidenceType, Partition

result = ground_finding(
    title="Expired TLS certificate on 192.0.2.10:443",
    description="Serving endpoint presents an expired certificate.",
    severity=Severity.HIGH,
    asset="192.0.2.10:443",
    remediation="Rotate the certificate; enforce automated renewal.",
    partition=Partition(grounded=[
        Claim(text="cert expired 2026-05-30", type=EvidenceType.TOOL_MATCH,
              evidence_refs=["tool:tls_scan:not_after=2026-05-30"]),
    ]),
)
print(result.title if is_finding(result) else f"withheld: {result.reason}")
# Grounded partition → a typed Finding. Ungrounded → an Abstention.
```

Findings carry **MITRE ATLAS** (`AML.Txxxx`), **OWASP Top 10 for LLM
Applications**, and **OWASP Top 10 for Agentic Applications** tags, so
they drop into a SIEM or a **NIST AI RMF** report without translation.

[The security layer →](concepts/security.md) · [GSAR grounding →](concepts/gsar.md)

## What Tulip gives you

<div class="grid cards tulip-feature-cards" markdown>

- :material-shield-search:{ .lg .middle } **[Grounded findings](concepts/security.md)**

    ---
    `ground_finding()` emits a typed `Finding` only above the GSAR
    threshold — else an auditable `Abstention`. Ungrounded is
    unshippable by construction. Tagged to ATLAS · OWASP LLM · OWASP ASI.

- :material-radar:{ .lg .middle } **[AI-threat coverage](notebooks/index.md)**

    ---
    Prompt injection, jailbreaks, RAG and memory poisoning, model
    extraction, excessive agency, and timing side-channel inference
    fingerprinting — the latter with a cookbook pattern for dispatching
    probes to dedicated GPU clusters. Plus a classic SOC/IR track.

- :material-routes:{ .lg .middle } **[Risk-gated routing](concepts/router.md)**

    ---
    The cognitive router ranks each task by risk; HIGH-risk actions
    (isolate a host, block a domain) compile to an approval gate that
    survives restarts. The model classifies; it never authors topology.

- :material-shield-check:{ .lg .middle } **[Idempotent containment](concepts/idempotency.md)**

    ---
    `@tool(idempotent=True)` deduplicates on `(name, args)` inside the
    Execute node. No double-isolate, double-page, or double-block — even
    on model retry or checkpoint resume.

- :material-eye:{ .lg .middle } **[Audit trail by default](concepts/observability.md)**

    ---
    One `run_context()` streams 60+ canonical events from every layer.
    Every model call, tool call, guardrail verdict, and approval is an
    immutable event you can ship to a SIEM and replay in a postmortem.

- :material-graph:{ .lg .middle } **[Multi-agent coordination](concepts/multi-agent.md)**

    ---
    Eight shapes — pipeline, fan-out, debate, orchestrator, swarm,
    handoff, StateGraph, A2A — for IR war-rooms, tiered escalation, and
    red-team-vs-detection. One `Agent` class, one event stream.

</div>

## Risk decides what runs

Describe the task in plain language. The cognitive router extracts a
typed `GoalFrame` (intent · domain · complexity · **risk**), picks one
of eight protocols, and compiles it onto real primitives — and the
PolicyGate, not the model's confidence, decides whether a step
auto-runs or waits for a human.

| Protocol | Compiled shape | Security use |
|---|---|---|
| `direct_response` | Single `Agent` | summarise an advisory |
| `plan_execute_validate` | `SequentialPipeline` | roll out a detection / MFA change |
| `specialist_fanout` | `ParallelPipeline` of probes | triage a failed-login spike |
| `debate` | Two debaters + judge | adjudicate true-positive vs false-positive |
| `codegen_test_validate` | `LoopAgent` (stops on `PASS`) | write a detection rule + test it |
| `approval_gated_execution` | `Agent` + approval interrupt | scan a subnet · isolate a host |
| `handoff_chain` | `SequentialPipeline` of one-tool Agents | L1 → L2 → L3 escalation |
| `a2a_delegate` | Cross-process A2A | cross-org threat-intel sharing |

```python
result = await router.dispatch("Authorized scan of 192.0.2.0/24; isolate hosts beaconing out.")
print(result.protocol_id)   # "approval_gated_execution"  → held for a human
```

[Cognitive router →](concepts/router.md)

## Walk the cookbook

Every example is a single self-contained file under [`examples/`][gh-examples]
with a matching docs page. **AI-security is the primary track**; classic
SOC/IR is the second.

| Track | Start here |
|---|---|
| **Grounded findings (flagship)** | [GSAR typed grounding](notebooks/notebook_37_gsar_typed_grounding.md) · [typed findings](notebooks/notebook_35_structured_output.md) |
| **Prompt injection · red-team** | [injection guardrails](notebooks/notebook_50_guardrails_security.md) · [purple-team patterns](notebooks/notebook_20_advanced_patterns.md) · [report vs. skeptic](notebooks/notebook_31_supervisor_critic_loop.md) |
| **Inference fingerprinting** | [forensics specialist](notebooks/notebook_27_specialist_agents.md) · [security MCP tooling](notebooks/notebook_45_mcp_integration.md) |
| **Threat-intel · RAG poisoning** | [ATLAS knowledge base](notebooks/notebook_38_rag_basics.md) · [advisory KB](notebooks/notebook_39_rag_providers.md) · [intel copilot](notebooks/notebook_40_rag_agents.md) |
| **SOC triage · IR** | [triage agent](notebooks/notebook_06_basic_agent.md) · [IR war-room](notebooks/notebook_24_swarm_multiagent.md) · [containment approval](notebooks/notebook_19_human_in_the_loop.md) · [incident response](notebooks/notebook_63_incident_response.md) |
| **Audit · compliance** | [forensic event trail](notebooks/notebook_59_observability_basics.md) · [vendor security review](notebooks/notebook_64_procurement_approval.md) · [DPA review](notebooks/notebook_65_contract_review.md) |

Full catalog → [Notebooks index](notebooks/index.md) · [Capabilities matrix](capabilities.md) · [API reference](api/agent.md)

[gh-examples]: https://github.com/tuliplabs-ai/sdk-python/tree/main/examples

---

**Evidence-grounded. Standards-aligned. Open to everyone.**
