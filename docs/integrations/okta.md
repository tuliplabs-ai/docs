# Okta (identity)

```bash
pip install "tulip-integrations[identity-okta]"
```

| | |
|---|---|
| **Env** | `OKTA_URL` · `OKTA_TOKEN` (SSWS API token) |
| **Import** | `from tulip_integrations.identity.okta import OktaIdentity, okta_user_tool, okta_disable_tool` |
| **Provider** | `OktaIdentity` → `SecurityContext(identity=OktaIdentity())` |
| **Tools** | `okta_get_user(user)` · `okta_risk(user)` · `okta_signins(user)` · `okta_disable(user)` ⚠️ write |
| **Adapter** | `okta_adapter()` → `SecurityAdapter` |

```python
from tulip.security import SecurityContext
from tulip_integrations.identity.okta import OktaIdentity

ctx = SecurityContext(identity=OktaIdentity())
await ctx.identity.risk("mallory@corp.com")      # status + risk signals
await ctx.identity.signins("mallory@corp.com")   # recent sign-ins
```

Look up a user, pull risk signals and recent sign-ins (read), or disable an
account (`okta_disable` — a **write**, gate it). Implements the same
`IdentitySource` port as Auth0, so you can swap providers by changing one line.
Passes `tulip.security.testing` conformance.

!!! warning "`okta_disable` is a real action"
    Disabling an account locks the user out. Approval-gate it in agentic use.

!!! note "Credentials"
    Okta has free developer tenants — set `OKTA_URL` / `OKTA_TOKEN` to run it
    against one.

→ [Integrations overview](index.md) · [SecurityContext](../concepts/security-context.md)
