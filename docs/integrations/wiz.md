# Wiz (AI-SPM)

**Status:** 🔌 live-path verified · maintained in `tulip-integrations`.

Wiz discovers *what AI exists in your cloud* (the AI-BOM) and the posture issues
around it. This integration brings that into Tulip so an agent can **reason over
it and emit grounded findings** — Wiz finds the attack surface; the Tulip agent
turns each issue into a typed, taxonomy-tagged `Finding`.

```bash
pip install "tulip-integrations[wiz-aispm]"
```

| | |
|---|---|
| **Env** | `WIZ_API_ENDPOINT` · `WIZ_CLIENT_ID` · `WIZ_CLIENT_SECRET` (offline sample otherwise) |
| **Import** | `from tulip_integrations.vuln.wiz import wiz_inventory_tool, wiz_issues_tool` |
| **Tools** | `wiz_inventory()` · `wiz_issues(severity)` |
| **Findings** | `wiz_to_findings()` → grounded `Finding[]` |
| **Adapter** | `wiz_adapter()` → `SecurityAdapter` |
| **Playbook** | `ai_spm_review()` |

```python
from tulip_integrations.vuln.wiz import wiz_to_findings

for f in wiz_to_findings():          # each Wiz issue → a grounded Finding
    print(f.severity, f.title, [t.value for t in f.taxonomy])
# critical  Publicly exposed model endpoint without authentication  ['LLM02']
# high      Over-permissive IAM role attached to AI training job    ['ASI03']
# medium    Model artifact bucket without encryption at rest        ['ASI04']
```

The live path authenticates (OAuth2 client-credentials) and queries the Wiz
GraphQL API; with no credentials it returns a deterministic AI-BOM + issue
sample. Passes `tulip.security.testing` conformance.

!!! note "Live path verified against a mock"
    The OAuth2 client-credentials + GraphQL requests are exercised and asserted
    in [`test_live_paths.py`](https://github.com/tuliplabs-ai/tulip-integrations/blob/main/tests/test_live_paths.py);
    the offline sample runs in CI. Wiz has no free tier, so not yet run against
    a real tenant — adjust fields per your Wiz deployment.
