# Splunk / Elastic (SIEM)

**Status:** 🧪 offline-verified · maintained in `tulip-integrations` · the
reference template for the integration model.

```bash
pip install "tulip-integrations[siem-splunk]"
```

| | |
|---|---|
| **Env** | `SPLUNK_URL` · `SPLUNK_TOKEN` (offline sample otherwise) |
| **Import** | `from tulip_integrations.security.splunk import splunk_siem_tool` |
| **Tools** | `splunk_search(spl, earliest)` |
| **Adapter** | `splunk_adapter()` → `SecurityAdapter` |
| **Playbook** | `splunk_threat_hunt()` |

```python
from tulip.security import security_toolset
from tulip_integrations.security.splunk import splunk_siem_tool

# core SIEM reference off; the maintained Splunk adapter merged in
tools = security_toolset(siem=False, extra=[splunk_siem_tool])
```

The live path POSTs an SPL search to Splunk's export endpoint; with no
credentials it filters a deterministic, benign sample so it runs in CI. Passes
`tulip.security.testing` conformance.

!!! warning "Unverified live path"
    The export query is written to Splunk's documented shape but has not been
    run against a real instance — adjust the path/fields per deployment.
