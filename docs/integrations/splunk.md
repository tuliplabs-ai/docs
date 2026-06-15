# Splunk / Elastic (SIEM)

**Status:** 🔌 live-path verified · maintained in `tulip-integrations` · the
reference template for the integration model.

```bash
pip install "tulip-integrations[siem-splunk]"
```

| | |
|---|---|
| **Env** | `SPLUNK_URL` · `SPLUNK_TOKEN` (offline sample otherwise) |
| **Import** | `from tulip_integrations.siem.splunk import SplunkLogs, splunk_siem_tool` |
| **Provider** | `SplunkLogs` → `SecurityContext(logs=SplunkLogs())` |
| **Tools** | `splunk_search(spl, earliest)` |
| **Adapter** | `splunk_adapter()` → `SecurityAdapter` |
| **Playbook** | `splunk_threat_hunt()` |

```python
from tulip.security import security_toolset
from tulip_integrations.siem.splunk import splunk_siem_tool

# core SIEM reference off; the maintained Splunk adapter merged in
tools = security_toolset(siem=False, extra=[splunk_siem_tool])
```

The live path POSTs an SPL search to Splunk's export endpoint; with no
credentials it filters a deterministic, benign sample so it runs in CI. Passes
`tulip.security.testing` conformance.

!!! note "Live path verified against a mock"
    The export request (URL, `Bearer` auth, response parsing) is exercised and
    asserted in [`test_live_paths.py`](https://github.com/tuliplabs-ai/tulip-integrations/blob/main/tests/test_live_paths.py);
    the offline sample runs in CI. Not yet run against a real Splunk instance —
    adjust the path/fields per deployment.
