# Integrations

Tulip follows a **core + community** split (the LangChain model):

- **`tulip-agents` (core)** ships the agent engine, the grounding contracts
  (`Finding` / `ground_finding`), the
  [`SecurityAdapter`](build.md) protocol, the conformance kit, and a set of
  **bundled reference/offline adapters** so the SDK runs standalone with no
  credentials.
- **`tulip-integrations` (community)** ships maintained, vendor-specific
  integration *templates* + community playbooks. It **depends on core**
  (one-way — core never imports it).

Discovery is **explicit** — you import the adapter you want and merge its tools
into the toolset; there is no entry-point magic:

```python
from tulip.agent import Agent
from tulip.security import security_toolset
from tulip_integrations.security.splunk import splunk_siem_tool

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=security_toolset(siem=False, extra=[splunk_siem_tool]),
    system_prompt="You are a SOC analyst. Cite the evidence behind every verdict.",
)
```

Every integration follows the core conventions: **bring-your-own credentials**
from the environment, a deterministic **offline sample** when none are set (so
it runs in CI), JSON-returning `@tool`s, and findings routed through GSAR
`ground_finding` so an ungrounded result abstains.

## Catalog

The **Status** column is the honesty signal: **✅ verified** = exercised against
a real tenant; **🧪 offline** = the live path is written to the vendor's shape
but only the offline sample is exercised in CI (bring your own verification).

| Integration | Category | Install | Import | Status |
|---|---|---|---|---|
| [AWS posture](#) | cloud | `tulip-agents[aws]` | `tulip.security.use_aws` | ✅ verified |
| [OSV](#) | supply-chain | built-in | `tulip.integrations.osv` | ✅ verified |
| [Splunk](splunk.md) | SIEM | `tulip-integrations[siem-splunk]` | `tulip_integrations.security.splunk` | 🧪 offline |
| [Wiz](wiz.md) | AI-SPM | `tulip-integrations[wiz-aispm]` | `tulip_integrations.security.wiz` | 🧪 offline |
| [RunPod](runpod.md) | compute | `tulip-integrations[compute-runpod]` | `tulip_integrations.compute.runpod` | 🧪 offline |
| Lambda Cloud | compute | `tulip-integrations[compute-lambda]` | `tulip_integrations.compute.lambda_cloud` | 🧪 offline |

Bundled **reference adapters** also live in core (`tulip.security`): IOC intel,
SIEM, EDR, vuln/posture scanner, and the inference-fingerprint contract — useful
standalone and as the template to copy. The maintained vendor versions are the
entries above.

→ [Build your own integration](build.md)
