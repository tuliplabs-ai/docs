# CrowdStrike Falcon (EDR)

```bash
pip install "tulip-integrations[edr-crowdstrike]"
```

| | |
|---|---|
| **Env** | `CROWDSTRIKE_URL` · `CROWDSTRIKE_TOKEN` (aliases `FALCON_URL` · `FALCON_TOKEN`) |
| **Import** | `from tulip_integrations.edr.crowdstrike import CrowdStrikeEndpoint, crowdstrike_adapter` |
| **Provider** | `CrowdStrikeEndpoint` → `SecurityContext(endpoint=CrowdStrikeEndpoint())` |
| **Tools** | `cs_host_timeline(host, window)` · `cs_detections(host=None)` · `cs_isolate(host_id)` ⚠️ write |
| **Adapter** | `crowdstrike_adapter()` → `SecurityAdapter` |

```python
from tulip.security import SecurityContext
from tulip_integrations.edr.crowdstrike import CrowdStrikeEndpoint

ctx = SecurityContext(endpoint=CrowdStrikeEndpoint())
await ctx.endpoint.get_host("WIN-ABC", window="24h")   # forensic timeline
await ctx.endpoint.detections()                         # open detections
```

The read tools pull a host's forensic timeline and open detections from the
Falcon API; `cs_isolate` network-contains a host — a **write**, so gate it
through `ctx.actions` / `approve()` first. Passes `tulip.security.testing`
conformance.

!!! warning "`cs_isolate` is a real action"
    Network-containment cuts a host off the network. It's marked idempotent and
    must be approval-gated in agentic use.

!!! note "Credentials"
    Set `CROWDSTRIKE_URL` / `CROWDSTRIKE_TOKEN` (or the `FALCON_*` aliases) to run
    it against your Falcon tenant. Adjust the path/fields per deployment.

→ [Integrations overview](index.md) · [SecurityContext](../concepts/security-context.md)
