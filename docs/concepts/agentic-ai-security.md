# Agentic AI-security

**In plain terms:** you've deployed an AI — a chatbot, an agent with tools, or a
model behind an API. Can someone jailbreak it, make it leak data, or trick it
into doing something it shouldn't? Tulip lets you build an agent that checks,
automatically and continuously, and reports only the flaws it can actually
**prove**. Think of it as a penetration tester for AI that refuses to cry wolf.

**How it works, in three steps:**

1. **Point** Tulip at a target AI — `Target.endpoint("https://bot.example/chat")`.
2. **Run** a job — `red_team(target)` attacks it; `assure(target)` scores its defenses.
3. **Get evidence** — each result is an `Evidence` finding (the attack worked, here's the proof)
   or an `Abstention` (no proof, so no claim). Never a guess.

More precisely: Tulip builds agents whose **subject is another AI system** —
agents that **red-team** and **assess** other AI (continuous **monitoring** is
on the roadmap), and produce a grounded `Evidence` record or an explicit
`Abstention`, never a hallucinated verdict.

> **A cybersecurity agent** = a *target* (an AI system) × a *job*
> (red-team · assure; monitor is roadmap) × an *output* (grounded `Evidence` |
> `Abstention`) × being *itself trustworthy by construction*.

![The trust chain: a Target is probed by red_team or assure, grounded by GSAR into a Finding or an Abstention, and only an approved action passes the admission gate](../img/patterns/trust-chain.svg){ .diagram }

## Why this, and why now

Companies ship LLM agents — with tools, memory, autonomy, and access to data
and actions — into production. That is a new, largely unguarded attack
surface: prompt injection (direct and indirect), tool abuse / excessive
agency, data exfiltration, memory and RAG poisoning, A2A identity confusion,
unknown model and hardware provenance.

The tools that exist miss it. SIEM/SOC platforms see infrastructure, not agent
semantics. Guardrail libraries *filter* I/O but don't *test* or *assess*.
Cloud AI-SPM is *static* posture, not *dynamic adversarial testing of a live
agent*. And AI red-team tooling that does test AI **hallucinates findings** —
the literature is explicit that AI scorers lack grounding. Tulip's answer is
**abstain-by-construction grounding** (GSAR): no evidence, no claim.

## The `Target` — what you point at

A `Target` is a uniform handle to the AI system under assessment. One
`.send()` contract over four constructors:

```python
from tulip.security import Target

Target.endpoint("https://bot.example/chat")   # a remote LLM / agent endpoint
Target.agent(my_tulip_agent)                   # an in-process tulip.Agent
Target.a2a(peer_send)                          # an A2A peer's send coroutine
Target.from_callable(fn)                       # any sync/async str -> str
```

Everything below operates on a `Target`, so the same probe runs against a
black-box endpoint, an agent you built, or an offline stub in CI.

## `red_team` — attack, grounded

`red_team` runs the OWASP-ASI / MITRE-ATLAS probe suite against a target and
grounds each outcome. A probe whose attack *landed* yields an `Evidence`
finding; an inconclusive one yields an `Abstention`.

```python
from tulip.security import Target, red_team, is_finding

report = await red_team(Target.endpoint("https://bot.example/chat"), suite="owasp-asi")
for r in report:
    if is_finding(r):
        print(r.severity.value, r.title, r.taxonomy)   # e.g. LLM01, ASI02, AML.T0054
    else:
        print("abstained:", r.reason)
```

The bundled catalogue covers direct and indirect prompt injection, jailbreak,
excessive agency / tool misuse, and sensitive-information disclosure — each
tagged with the taxonomy a SOC and an AI-assurance reviewer expect.

## `assure` — assess, grounded

Where `red_team` asks *can I break it?*, `assure` asks *how well does it hold
up?* `guardrail_coverage` runs the suite and grounds a posture finding in the
direct observations — INFO when fully hardened, escalating to CRITICAL at 0%
coverage, with the taxonomy listing exactly the gaps.

```python
from tulip.security import assure
posture = await assure(target)   # grounded guardrail-coverage posture
```

This is a *grounded finding*, not a compliance attestation. `assure` never
asserts posture it cannot evidence — it abstains. (Checkbox-style posture
attestation is ground well held by Cisco DefenseClaw and Microsoft's Agent
Governance Toolkit.) Tulip's governance lives one layer down, where the
consequence is: the [admission gate on the action
itself](#enforce-it-before-it-acts) — enforced policy, a human on the actions
that warrant one, and a tamper-evident record.

## Secure by default — the floor

An agent that red-teams or assures other AI must itself be trustworthy.
`governed_agent` builds a `tulip.Agent` with the security spine on by default —
GSAR grounding, guardrails (PII / injection / a dangerous-tool denylist;
allowlist is opt-in), and a tamper-evident audit trail — and returns it
alongside that trail.

```python
from tulip.control import governed_agent

secured = governed_agent(model="openai:gpt-4o", tools=[...])
result = secured.run_sync("...")
assert secured.audit_trail.verify()   # the chain is intact (tamper-evident)
```

The `AuditTrail` is a keyless, in-memory SHA-256 hash chain: every action
commits to the hash before it, so any later edit, deletion, or reorder breaks
`verify()` against a trusted head hash. That makes it tamper-*evident* (it
**detects** edits) rather than tamper-proof — there is no signing or external
anchoring yet. It exports as JSONL for shipping to a SIEM, where signing or
write-once anchoring can harden it further.

## Enforce it before it acts

Grounding, verification, and the audit trail make an agent *trustworthy*; the
**admission gate** makes that trust *binding*. Run a side-effecting action through
`admit()` (or `ctx.actions.execute()`): it fires only if the action clears the
policy chain (`approve()` → ALLOW), holds it for a named person when policy
answers `require_human`, and denies the rest — recording every decision, allowed,
held, or denied, and raising `AdmissionError` whenever the action does not run. That's the line between an agent that *could* be safe
and a runtime that *enforces* safety — no action reaches production without a
verified, approved, audited warrant. See
[SecurityContext](security-context.md#admission-control-the-enforcement-point).

## Regular cyber — the second pillar

This page covers securing *AI* (pillar B). The same engine, pointed at
*infrastructure* instead of an AI system, is the other pillar of "agentic AI for
cybersecurity": classic security operations — the bundled SOC-analyst factory,
the IR playbooks (`phishing_triage`, `ransomware_containment`, `nist_800_61_ir`),
and read-only cloud-posture auditing. Different target, different taxonomy — same
`Target` + grounded-`Evidence` contract. It's first-class, not a demo: grounding
is exactly what makes an AI SOC agent's verdicts trustworthy, answering the
false-positive pain teams hit with AI-graded triage.

See also: [Grounded findings](security.md) · [GSAR typed grounding](gsar.md) ·
[Threat scenarios](threat-scenarios.md) · [Cloud-posture agent](cloud-posture.md).
