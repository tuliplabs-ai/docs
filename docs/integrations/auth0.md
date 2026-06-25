# Auth0 (identity)

```bash
pip install "tulip-integrations[identity-auth0]"
```

| | |
|---|---|
| **Env** | `AUTH0_DOMAIN` + `AUTH0_MGMT_TOKEN` — or `AUTH0_DOMAIN` + `AUTH0_CLIENT_ID` + `AUTH0_CLIENT_SECRET` (Management API) |
| **Import** | `from tulip_integrations.identity.auth0 import Auth0Identity, auth0_user_tool, auth0_disable_tool` |
| **Provider** | `Auth0Identity` → `SecurityContext(identity=Auth0Identity())`; methods `get_user` · `risk` · `signins` · `disable` (write) |
| **Functions** | `auth0_get_user(user)` · `auth0_risk(user)` · `auth0_signins(user)` · `auth0_disable(user)` ⚠️ write |
| **Agent tools** | `auth0_user_tool` (reads a user) · `auth0_disable_tool` (⚠️ disables an account) |
| **Adapter** | `auth0_adapter()` → `ToolAdapter` (a `SecurityAdapter`) |

```python
from tulip.security import SecurityContext
from tulip_integrations.identity.auth0 import Auth0Identity

ctx = SecurityContext(identity=Auth0Identity())
await ctx.identity.get_user("mallory@example.com")   # Management API lookup (live path)
await ctx.identity.signins("mallory@example.com")    # recent sign-in logs (live path)
await ctx.identity.risk("mallory@example.com")        # risk + impossible_travel
```

Look up a user and pull recent sign-ins (`get_user` / `signins` hit the
Management API live), read risk + impossible-travel (`risk`), or block an account
(`disable` — a **write**, gate it). With no credentials set, every call returns a
bundled offline sample (`mallory@example.com` is the high-risk one) so it runs in
CI with no secrets. Only `auth0_user_tool` and `auth0_disable_tool` are exposed as
agent tools. Credentials are either a pre-minted Management API token
(`AUTH0_MGMT_TOKEN`) or a client-credentials pair the adapter exchanges for one.
Passes `tulip.security.testing` conformance.

!!! warning "`auth0_disable` is a real action"
    Blocking an account locks the user out. Approval-gate it in agentic use.

!!! note "Credentials"
    Set `AUTH0_DOMAIN` + a Management API token (or client credentials) to run it
    against your tenant.

→ [Integrations overview](index.md) · [SecurityContext](../concepts/security-context.md)
