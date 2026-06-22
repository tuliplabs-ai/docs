# Auth0 (identity)

Maintained in `tulip-integrations`.

```bash
pip install "tulip-integrations[identity-auth0]"
```

| | |
|---|---|
| **Env** | `AUTH0_DOMAIN` + `AUTH0_MGMT_TOKEN` — or `AUTH0_DOMAIN` + `AUTH0_CLIENT_ID` + `AUTH0_CLIENT_SECRET` (Management API) |
| **Import** | `from tulip_integrations.identity.auth0 import Auth0Identity, auth0_user_tool, auth0_disable_tool` |
| **Provider** | `Auth0Identity` → `SecurityContext(identity=Auth0Identity())` |
| **Tools** | `auth0_get_user(user)` · `auth0_risk(user)` · `auth0_signins(user)` · `auth0_disable(user)` ⚠️ write |
| **Adapter** | `auth0_adapter()` → `SecurityAdapter` |

```python
from tulip.security import SecurityContext
from tulip_integrations.identity.auth0 import Auth0Identity

ctx = SecurityContext(identity=Auth0Identity())
await ctx.identity.risk("mallory@corp.com")   # hits the real Auth0 tenant
```

Look up a user, pull risk + recent sign-ins (read), or block an account
(`auth0_disable` — a **write**, gate it). Credentials are either a pre-minted
Management API token (`AUTH0_MGMT_TOKEN`) or a client-credentials pair the
adapter exchanges for one. Passes `tulip.security.testing` conformance.

!!! warning "`auth0_disable` is a real action"
    Blocking an account locks the user out. Approval-gate it in agentic use.

!!! note "Credentials"
    Set `AUTH0_DOMAIN` + a Management API token (or client credentials) to run it
    against your tenant.

→ [Integrations overview](index.md) · [SecurityContext](../concepts/security-context.md)
