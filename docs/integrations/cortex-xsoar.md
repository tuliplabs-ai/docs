# Palo Alto Cortex XSOAR (SOAR)

Meet the SOC where it already lives. A Tulip agent can read Cortex XSOAR
incidents, ground them into typed findings, and **act on them** — close an
incident — through the same model every Tulip integration follows: a read returns
evidence, a write is a governed action, and the live path falls back to a
deterministic offline sample so it runs in CI with no credentials.

```bash
pip install "tulip-integrations[soar-cortex-xsoar]"
```

| | |
|---|---|
| **Env** | `XSOAR_URL` · `XSOAR_API_KEY` (+ `XSOAR_API_KEY_ID` for Cortex 8.x / XSIAM) |
| **Import** | `from tulip_integrations.soar.cortex_xsoar import CortexXSOAR, xsoar_incident_tool, xsoar_search_tool, xsoar_close_tool, xsoar_incident_to_finding` |
| **Provider** | `CortexXSOAR` — methods `get_incident` · `search` · `close` (write) |
| **Functions** | `xsoar_get_incident(id)` · `xsoar_search_incidents(query)` · `xsoar_close_incident(id, reason=…)` ⚠️ write |
| **Agent tools** | `xsoar_incident_tool` · `xsoar_search_tool` · `xsoar_close_tool` (⚠️ closes an incident) |
| **Grounding** | `xsoar_incident_to_finding(id)` → `GroundedFinding` (an `Evidence`, or an `Abstention`) |
| **Adapter** | `xsoar_adapter()` → `ToolAdapter` (a `SecurityAdapter`) |

```python
from tulip_integrations.soar.cortex_xsoar import (
    xsoar_get_incident, xsoar_search_incidents, xsoar_incident_to_finding)
from tulip.security import is_finding

xsoar_search_incidents("travel")          # -> {"total": 1, "incidents": [...]}
xsoar_get_incident("INC-1001")            # -> {"found": True, "incident": {...severity: 3}}

# A high-severity incident grounds to a typed Evidence; a low one abstains.
result = xsoar_incident_to_finding("INC-1001")
print(result.title if is_finding(result) else f"withheld: {result.reason}")
```

Read incidents and search the queue (read), or **close an incident**
(`xsoar_close_incident` — a write, gate it). The live path uses `XSOAR_URL` +
`XSOAR_API_KEY` against the XSOAR REST API (`/incident/search`, `/incident/close`);
add `XSOAR_API_KEY_ID` for Cortex 8.x / XSIAM advanced auth. With no credentials
set, the bundled offline sample ships two incidents (`INC-1001` high-severity,
`INC-1002` benign) so it runs in CI with no secrets. Passes
`tulip.security.testing` conformance.

Closing an incident from an agent should never run on the model's say-so — wrap it
in an `Action` and route it through `admit()` so policy (and a human, in
production) clears it first, and the decision lands on the audit trail:

```python
from tulip.control import Action, admit, ControlPolicy, AuditTrail
from tulip_integrations.soar.cortex_xsoar import xsoar_close_incident

trail = AuditTrail()
await admit(
    Action(name="xsoar_close", asset="INC-1001", environment="production", kind="soar"),
    lambda: xsoar_close_incident("INC-1001", reason="auto-triaged: benign"),
    policy=ControlPolicy(), trail=trail,
)
```

!!! warning "`xsoar_close_incident` is a real action"
    Closing an incident changes SOC state. Approval-gate it in agentic use.

!!! note "Credentials"
    Set `XSOAR_URL` + `XSOAR_API_KEY` (and `XSOAR_API_KEY_ID` on Cortex 8.x /
    XSIAM) to run it against your tenant — adjust paths per deployment.

→ [Integrations overview](index.md) · [SecurityContext](../concepts/security-context.md)
