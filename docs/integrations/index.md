# Integrations

An integration lets a Tulip agent reach a real security tool — your SIEM, your
EDR, your identity provider — instead of a mock. Tulip follows a **core +
community** split (the LangChain model):

- **`tulip-agents` (core)** ships the agent engine, the grounding contracts
  (`Finding` / `ground_finding`), the domain ports (`LogSource`,
  `EndpointSource`, `IdentitySource`, …), the [`SecurityAdapter`](build.md)
  protocol, and **bundled offline reference adapters** so the SDK runs
  standalone with no credentials.
- **`tulip-integrations` (community)** ships the maintained, vendor-specific
  integrations. It **depends on core** (one-way — core never imports it).

## Two ways to use an integration

**1. As a domain provider** (recommended) — inject it into a
[`SecurityContext`](../concepts/security-context.md) and your investigation code
stays vendor-agnostic. Swap Okta for Auth0 by changing one line:

```python
from tulip.security import SecurityContext
from tulip_integrations.identity.auth0 import Auth0Identity
from tulip_integrations.threat_intel.virustotal import VirusTotalIntel

ctx = SecurityContext(identity=Auth0Identity(), threat_intel=VirusTotalIntel())
await ctx.identity.risk("mallory@corp.com")     # hits the real Auth0 tenant
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

Either way, every integration follows the same rules: **bring-your-own
credentials** from the environment, JSON-returning tools, and findings routed
through GSAR `ground_finding` so an ungrounded result abstains.

## What each integration does

| Integration | Domain | What it does | Provider | Install |
|---|---|---|---|---|
| **VirusTotal** | threat-intel | Reputation for an IP, domain, or file hash | `VirusTotalIntel` | `threat-intel-virustotal` |
| **Auth0** | identity | Look up a user, risk + sign-ins, disable an account (Management API) | `Auth0Identity` | `identity-auth0` |
| **Okta** | identity | Look up a user, risk + sign-ins, disable an account (SSWS API) | `OktaIdentity` | `identity-okta` |
| **Splunk** | SIEM | Search logs/events with an SPL query | `SplunkLogs` | `siem-splunk` |
| **CrowdStrike Falcon** | EDR | Host forensic timeline, open detections, network-contain a host | `CrowdStrikeEndpoint` | `edr-crowdstrike` |
| **Wiz** | AI-SPM | AI-BOM inventory + posture issues → grounded findings | _(tools)_ | `vuln-wiz` |
| **AWS** | cloud | Read-only cloud-posture evidence (in core) | _(core)_ | `tulip-agents[aws]` |
| **OSV** | supply-chain | Dependency vulnerability lookup (in core) | _(core)_ | built-in |
| **RunPod / Lambda** | compute | Deploy a GPU endpoint to fingerprint-probe a model | _(probe)_ | `compute-runpod` / `compute-lambda` |

Writes — `endpoint.isolate`, `identity.disable` — are real actions: gate them
through `ctx.actions` / `approve()` first.

→ [Build your own integration](build.md) · [SecurityContext](../concepts/security-context.md)
