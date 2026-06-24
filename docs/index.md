---
hide:
  - navigation
  - toc
---

<div class="tulip-hero" markdown>
<div class="tulip-hero__copy" markdown>

<p class="tulip-product-name"><span class="tpn-brand">tulip agents</span><span class="tpn-sep"> · </span>the SDK for agents you can let act</p>

# Your agent is one <span class="accent">jailbreak</span> from production.

A frontier model can be brilliant — and still be talked into wiring the money or wiping the database. Tulip puts every risky action behind a **policy gate**, a **human approval**, and an **audit trail it can't forge** — before it runs.

**You can fool the model; you can't talk past the runtime.**

A drop-in for the agent you already have. Proven first in security — SOC, EDR, identity — where a wrong action is a breach.

<div class="tulip-stat-strip" markdown><span style="white-space:nowrap">[MITRE&nbsp;ATLAS](concepts/security.md)</span> · <span style="white-space:nowrap">[OWASP&nbsp;LLM&nbsp;Top&nbsp;10](concepts/security.md)</span> · <span style="white-space:nowrap">[OWASP&nbsp;ASI](concepts/security.md)</span></div>

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
from tulip.security import (
    Action, admit, SecurityPolicy,
    AuditTrail, AdmissionError)

# Drop the gate around an action your agent
# already takes — policy + audit trail.
policy = SecurityPolicy()   # prod → human
trail = AuditTrail()

# The model decided to refund a customer.
risky = Action(
    name="refund", asset="cust:4821",
    blast_radius=1, kind="payment",
    environment="production")

try:
    await admit(
        risky, lambda: refund("cust:4821"),
        policy=policy, trail=trail)
except AdmissionError as e:
    print(e.decision.outcome)
    # -> "require_human"; refund NOT run.

# Held for a human, on the audit trail.
# Fool the model; you can't talk past it.
```

</div>
</div>

## The trust chain

A security agent that *finds* something still must not *act* on its own
authority. Tulip gives you the whole chain — and an admission gate that makes it
**enforceable, not advisory**:

**evidence → grounding → verification → policy → approval → admission → audit**

- **Grounding** — a claim becomes a typed `Finding` only above the GSAR
  threshold, else an `Abstention`. Enforced by the type: no ungrounded `Finding`
  can be constructed.
- **Verification** — `verify()` independently challenges the finding and rescores it.
- **Policy + approval** — `approve()` weighs a `SecurityPolicy` (verification
  score, blast radius, `require_human_for`).
- **Admission** — `admit()` (or `ctx.actions.execute()`) runs a side-effecting
  action **only if** approval allows, recording the decision to the audit trail
  either way; otherwise it raises `AdmissionError`.

That last gate is what makes Tulip a *runtime*, not a library: route an action
through it and "no action without a verified, approved warrant" stops being a
convention and becomes enforced code.

[The security layer →](concepts/security.md) · [SecurityContext →](concepts/security-context.md)

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
they drop into a SIEM without translation.

[The security layer →](concepts/security.md) · [GSAR grounding →](concepts/gsar.md)

## What Tulip gives you

<div class="grid cards tulip-feature-cards" markdown>

- :material-shield-search:{ .lg .middle } **[Grounded findings](concepts/security.md)**

    ---
    `ground_finding()` emits a typed `Finding` only above the GSAR
    threshold — else an auditable `Abstention`. Ungrounded is
    unshippable by construction. Tagged to ATLAS · OWASP LLM · OWASP ASI.

- :material-check-decagram:{ .lg .middle } **[Verification](notebooks/notebook_78_verify_findings.md)**

    ---
    `verify()` puts a finding through an independent skeptic that
    challenges its evidence and scores confidence — a hallucinated
    "critical" is refuted before it drives an action. Works on **any
    agent's** findings, not just Tulip's.

- :material-shield-lock:{ .lg .middle } **[Admission gate](concepts/security-context.md)**

    ---
    `approve()` weighs a `SecurityPolicy` (blast radius, verification
    score, `require_human_for={"production"}`); `admit()` then **runs the
    action only if that decision allows** — else raises `AdmissionError` —
    and records the attempt to the audit trail either way.

- :material-radar:{ .lg .middle } **[AI-threat coverage](notebooks/index.md)**

    ---
    Prompt injection, jailbreaks, RAG and memory poisoning, model
    extraction, excessive agency, and timing side-channel inference
    fingerprinting — the latter with a notebook pattern for dispatching
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
    Seven shapes — composition (pipeline / fan-out / loop), orchestrator,
    swarm, handoff, StateGraph, functional, and cross-process A2A — for IR
    war-rooms, tiered escalation, and red-team-vs-detection. One `Agent`
    class, one event stream.

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

## Walk the notebooks

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
