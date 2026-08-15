# VirusTotal (threat intel)

```bash
pip install "tulip-integrations[threat-intel-virustotal]"
```

| | |
|---|---|
| **Env** | `VT_API_KEY` (alias `VIRUSTOTAL_API_KEY`) |
| **Import** | `from tulip_integrations.threat_intel.virustotal import VirusTotalIntel, vt_enrich_tool` |
| **Provider** | `VirusTotalIntel` → `SecurityContext(threat_intel=VirusTotalIntel())` |
| **Functions** | `vt_enrich(indicator)` — IP, domain, or file hash |
| **Agent tool** | `vt_enrich_tool` — hand it to an agent |
| **Adapter** | `virustotal_adapter()` → `ToolAdapter` (a `SecurityAdapter`) |

```python
import asyncio
from tulip.security import SecurityContext
from tulip_integrations.threat_intel.virustotal import VirusTotalIntel


async def main():
    ctx = SecurityContext(threat_intel=VirusTotalIntel())
    await ctx.threat_intel.enrich("8.8.8.8")   # -> {malicious_detections, classification, ...}


asyncio.run(main())
```

Reputation enrichment for an **IP, domain, or file hash** (the indicator type is
auto-detected; URLs are not supported). The live path returns the malicious
detection count and classification; with no `VT_API_KEY` set it returns a
deterministic offline sample. Passes `tulip.security.testing` conformance.

!!! note "Credentials"
    VirusTotal has a free community API key (rate-limited). Set `VT_API_KEY` to
    run it against the live API.

→ [Integrations overview](index.md) · [SecurityContext](../concepts/security-context.md)
