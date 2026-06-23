# VirusTotal (threat intel)

```bash
pip install "tulip-integrations[threat-intel-virustotal]"
```

| | |
|---|---|
| **Env** | `VT_API_KEY` (alias `VIRUSTOTAL_API_KEY`) |
| **Import** | `from tulip_integrations.threat_intel.virustotal import VirusTotalIntel, vt_enrich_tool` |
| **Provider** | `VirusTotalIntel` → `SecurityContext(threat_intel=VirusTotalIntel())` |
| **Tools** | `vt_enrich(indicator)` — IP, domain, URL, or file hash |
| **Adapter** | `virustotal_adapter()` → `SecurityAdapter` |

```python
from tulip.security import SecurityContext
from tulip_integrations.threat_intel.virustotal import VirusTotalIntel

ctx = SecurityContext(threat_intel=VirusTotalIntel())
await ctx.threat_intel.enrich("8.8.8.8")   # reputation + detection ratio
```

Reputation enrichment for an IP, domain, URL, or file hash — the vendor
detection ratio and categories, mapped into the core indicator shape so a finding
can cite it. Passes `tulip.security.testing` conformance.

!!! note "Credentials"
    VirusTotal has a free community API key (rate-limited). Set `VT_API_KEY` to
    run it against the live API.

→ [Integrations overview](index.md) · [SecurityContext](../concepts/security-context.md)
