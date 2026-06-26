# Microsoft Entra ID (identity)

```bash
pip install "tulip-integrations[identity-entra]"
```

| | |
|---|---|
| **Env** | `ENTRA_TOKEN` (a Microsoft Graph access token) |
| **Import** | `from tulip_integrations.identity.entra import EntraIdentity, entra_user_tool, entra_disable_tool, entra_risk_to_finding` |
| **Provider** | `EntraIdentity` → `SecurityContext(identity=EntraIdentity())`; methods `get_user` (live) · `signins` (live) · `risk` (offline sample) · `disable` (write — simulated offline stub) |
| **Functions** | `entra_get_user(user)` · `entra_risk(user)` · `entra_signins(user)` · `entra_disable(user)` ⚠️ write |
| **Agent tools** | `entra_user_tool` (reads a user) · `entra_disable_tool` (⚠️ disables an account) |
| **Grounding** | `entra_risk_to_finding(user)` → `GroundedFinding` (an `Evidence`, or an `Abstention`) |
| **Adapter** | `entra_adapter()` → `ToolAdapter` (a `SecurityAdapter`) |

```python
from tulip.security import SecurityContext
from tulip_integrations.identity.entra import EntraIdentity

ctx = SecurityContext(identity=EntraIdentity())
await ctx.identity.get_user("mallory@example.com")   # profile (live: GET /users/{id})
await ctx.identity.signins("mallory@example.com")    # recent sign-ins (live: /auditLogs/signIns)
await ctx.identity.risk("mallory@example.com")        # risk + impossible_travel + mfa (offline sample)
```

Look up a user and read sign-ins, read a risk signal, or block an account.
`get_user` and `signins` hit Microsoft Graph v1.0 on the live path (with
`ENTRA_TOKEN`); with no token set, every call returns a bundled offline sample
(`mallory@example.com` is the high-risk one) so it runs in CI with no secrets.

!!! warning "`risk` and `disable` are offline-reference-only today"
    `entra_risk` reads the **bundled offline sample**, not a live tenant risk
    API — a real user comes back `risk="unknown"`. `entra_disable` is a
    **simulated no-op**: it returns `{"disabled": True, "source":
    "offline-sample"}` and does **not** yet issue the Microsoft Graph `PATCH
    /users/{id}` (`accountEnabled=false`). Treat both as reference shapes to wire
    up against your tenant.

Implements the same `IdentitySource` port as Okta and Auth0 — swap providers by
changing one line. Passes `tulip.security.testing` conformance.

The differentiator is grounding: `entra_risk_to_finding(user)` turns an identity
risk signal into a typed `Evidence` **only** when there's tool-backed evidence (a
high/medium risk level or impossible travel); a clean user yields an `Abstention`,
never a hallucinated verdict.

```python
from tulip.security import is_finding
from tulip_integrations.identity.entra import entra_risk_to_finding

result = entra_risk_to_finding("mallory@example.com")
print(result.title if is_finding(result) else f"withheld: {result.reason}")
```

!!! warning "`entra_disable` is shaped as a real action"
    Once wired to the live Graph `PATCH`, disabling an account locks the user
    out — so treat it as a write: approval-gate it in agentic use by wrapping it
    in an `Action` and routing it through `admit()`. (Today it's a simulated
    offline stub; the gating pattern is what carries over.)

!!! note "Credentials"
    Set `ENTRA_TOKEN` to a Microsoft Graph token with the right directory
    permissions to run it against your tenant.

→ [Integrations overview](index.md) · [SecurityContext](../concepts/security-context.md)
