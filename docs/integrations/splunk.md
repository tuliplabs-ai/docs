# Splunk / Elastic (SIEM)

```bash
pip install "tulip-integrations[siem-splunk]"
```

| | |
|---|---|
| **Env** | `SPLUNK_URL` · `SPLUNK_TOKEN` |
| **Import** | `from tulip_integrations.siem.splunk import SplunkLogs, splunk_siem_tool` |
| **Provider** | `SplunkLogs` → `SecurityContext(logs=SplunkLogs())` |
| **Function** | `splunk_search(spl, earliest)` |
| **Agent tool** | `splunk_siem_tool` |
| **Adapter** | `splunk_adapter()` → `ToolAdapter` (a `SecurityAdapter`) |
| **Playbook** | `splunk_threat_hunt()` — from `tulip_integrations.playbooks` |

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
