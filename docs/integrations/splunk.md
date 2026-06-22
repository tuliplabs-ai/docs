# Splunk / Elastic (SIEM)

Maintained in `tulip-integrations` · the reference template for the integration
model.

```bash
pip install "tulip-integrations[siem-splunk]"
```

| | |
|---|---|
| **Env** | `SPLUNK_URL` · `SPLUNK_TOKEN` |
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

The live path POSTs an SPL search to Splunk's export endpoint. Passes
`tulip.security.testing` conformance.

!!! note "Credentials"
    Set `SPLUNK_URL` / `SPLUNK_TOKEN` to run it against your Splunk instance —
    adjust the path/fields per deployment.
