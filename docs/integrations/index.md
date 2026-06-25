# Integrations

An integration lets a Tulip agent reach a real security tool — your SIEM, your
EDR, your identity provider — instead of a mock. Some integrations only **read
evidence** (search logs, look up a reputation, pull cloud posture); the
high-stakes ones let the agent **act** — network-contain a host, disable an
account. Tulip treats those two very differently.

Tulip follows a **core + community** split (the LangChain model):

- **`tulip-agents` (core)** ships the agent engine, the admission gate
  ([`admit()`](../concepts/security-context.md) / `approve()` / the
  tamper-evident audit trail), the grounding contracts (`Finding` /
  `ground_finding`), the domain ports (`LogSource`, `EndpointSource`,
  `IdentitySource`, …), the [`SecurityAdapter`](build.md) protocol, and
  **bundled offline reference adapters** so the SDK runs standalone with no
  credentials.
- **`tulip-integrations` (community)** ships the maintained, vendor-specific
  integrations. It **depends on core** (one-way — core never imports it).

## Reads are evidence; writes are governed

This is the point of integrating *through* Tulip rather than handing an agent a
raw vendor SDK. A read returns evidence, and a finding only ships if it clears
GSAR grounding. A **write is a real action**, so it doesn't run on the model's
say-so — it runs through the admission chain **policy → approval → admission →
audit**. You wrap the side effect in an `Action`; the gate runs it only if a
[`SecurityPolicy`](../concepts/security-context.md) (blast radius, verification
score, `require_human_for={"production"}`) allows — otherwise it raises
`AdmissionError`, and the attempt lands on the hash-chained audit trail either
way:

```python
from tulip.security import Action

# A write is an Action + the call that performs it. Under the default policy a
# production action is HELD for a human — so this raises AdmissionError instead
# of running, and the attempt is on the audit trail either way.
contain = Action(name="endpoint.isolate", asset="prod-db-01", blast_radius=50,
                 environment="production", kind="containment")
await ctx.actions.execute(contain, lambda: ctx.endpoint.isolate("prod-db-01"))
# → AdmissionError: REQUIRE_HUMAN — a prompt injection can't make this run on its own.
```

So even if an injected prompt talks the model into "isolate every host," the
write still has to clear the policy and (in production) a human — and every
attempt is on the record. **You can fool the model; you can't talk past the
runtime.** The integrations that actually take action: **CrowdStrike** (contain
a host), **Okta** / **Auth0** (disable an account). The rest are read-only
evidence sources.

## Two ways to use an integration

**1. As a domain provider** (recommended) — inject it into a
[`SecurityContext`](../concepts/security-context.md) and your investigation code
stays vendor-agnostic. Swap Okta for Auth0 by changing one line:

```python
from tulip.security import SecurityContext
from tulip_integrations.identity.auth0 import Auth0Identity
from tulip_integrations.threat_intel.virustotal import VirusTotalIntel

ctx = SecurityContext(identity=Auth0Identity(), threat_intel=VirusTotalIntel())
await ctx.identity.risk("mallory@corp.com")     # read: hits the real Auth0 tenant
# a write (ctx.identity.disable) goes through ctx.actions.execute — gated + audited
```

**2. As agent tools** — merge a vendor's `@tool`s into the toolset for an
autonomous agent:

```python
from tulip.agent import Agent
from tulip.security import security_toolset
from tulip_integrations.siem.splunk import splunk_siem_tool

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=security_toolset(siem=False, extra=[splunk_siem_tool]),
    system_prompt="You are a SOC analyst. Cite the evidence behind every verdict.",
)
```

Either way, the same two rules hold: a finding routes through GSAR
`ground_finding` so an ungrounded result **abstains**, and a write routes through
the admission gate so it **only runs gated and audited** — never on best
intentions. (All integrations bring their own credentials from the environment
and return JSON.)

## Governed MCP — hand the capability, not the authority

Tulip ships an [MCP server](../notebooks/notebook_45_mcp_integration.md), so you
can expose a tool to *another* agent — a Claude or GPT client, a separate
orchestrator — over the Model Context Protocol. The thing that makes this safe:
**the admission gate isn't part of the transport — it lives inside the action**,
where `admit()` wraps the side-effecting call. Build the tool so its body routes
the write through `admit()` / `ctx.actions.execute`, and the boundary holds no
matter who calls it across the wire. A remote agent gets the *capability* (it can
ask to isolate a host) without the *authority* to skip the policy: the write
still clears your `SecurityPolicy` (and, in production, a human) and still lands
in your audit trail. The gate is below the protocol, so the protocol can't route
around it.

## What each integration does

Action integrations first (they write), then read-only evidence sources:

| Integration | Domain | What it does | Provider | Install |
|---|---|---|---|---|
| **CrowdStrike Falcon** | EDR | Host forensic timeline, open detections, **network-contain a host** (write) | `CrowdStrikeEndpoint` | `edr-crowdstrike` |
| **Okta** | identity | Look up a user, risk + sign-ins, **disable an account** (write, SSWS API) | `OktaIdentity` | `identity-okta` |
| **Auth0** | identity | Look up a user, risk + sign-ins, **disable an account** (write, Management API) | `Auth0Identity` | `identity-auth0` |
| **Microsoft Entra ID** | identity | User, risk + impossible-travel + sign-ins → grounded finding, **disable an account** (write, Graph API) | `EntraIdentity` | `identity-entra` |
| **Cortex XSOAR** | SOAR | Read incidents, search, **close an incident** (write) + ground incidents to findings | `CortexXSOAR` | `soar-cortex-xsoar` |
| **Splunk** | SIEM | Search logs/events with an SPL query | `SplunkLogs` | `siem-splunk` |
| **VirusTotal** | threat-intel | Reputation for an IP, domain, or file hash | `VirusTotalIntel` | `threat-intel-virustotal` |
| **Wiz** | AI-SPM | AI-BOM inventory + posture issues → grounded findings | _(tools)_ | `vuln-wiz` |
| **AWS** | cloud | Read-only cloud-posture evidence (in core) | _(core)_ | `tulip-agents[aws]` |
| **OSV** | supply-chain | Dependency vulnerability lookup (in core) | _(core)_ | built-in |
| **RunPod / Lambda** | compute _(advanced)_ | Specialized: deploy a GPU endpoint to fingerprint-probe a model you operate | _(probe)_ | `compute-runpod` / `compute-lambda` |

→ [Build your own integration](build.md) · [SecurityContext](../concepts/security-context.md)
