# Auth0 (identity)

```bash
pip install "tulip-integrations[identity-auth0]"
```

| | |
|---|---|
| **Env** | `AUTH0_DOMAIN` + `AUTH0_MGMT_TOKEN` — or `AUTH0_DOMAIN` + `AUTH0_CLIENT_ID` + `AUTH0_CLIENT_SECRET` (Management API) |
| **Import** | `from tulip_integrations.identity.auth0 import Auth0Identity, auth0_user_tool, auth0_disable_tool` |
| **Provider** | `Auth0Identity` → `SecurityContext(identity=Auth0Identity())`; methods `get_user` (live) · `signins` (live) · `risk` (offline sample) · `disable` (write — simulated offline stub) |
| **Functions** | `auth0_get_user(user)` · `auth0_risk(user)` · `auth0_signins(user)` · `auth0_disable(user)` ⚠️ write |
| **Agent tools** | `auth0_user_tool` (reads a user) · `auth0_disable_tool` (⚠️ disables an account) |
| **Adapter** | `auth0_adapter()` → `ToolAdapter` (a `SecurityAdapter`) |

```python
import asyncio
from tulip.security import SecurityContext
from tulip_integrations.identity.auth0 import Auth0Identity


async def main():
    ctx = SecurityContext(identity=Auth0Identity())
    await ctx.identity.get_user("mallory@example.com")   # Management API lookup (live path)
    await ctx.identity.signins("mallory@example.com")    # recent sign-in logs (live path)
    await ctx.identity.risk("mallory@example.com")        # risk + impossible_travel (offline sample)


asyncio.run(main())
```

Look up a user and pull recent sign-ins (`get_user` / `signins` hit the
Management API live), read a risk signal (`risk`), or block an account
(`disable`). With no credentials set, every call returns a bundled offline sample
(`mallory@example.com` is the high-risk one) so it runs in CI with no secrets.
Only `auth0_user_tool` and `auth0_disable_tool` are exposed as agent tools.
Credentials are either a pre-minted Management API token (`AUTH0_MGMT_TOKEN`) or a
client-credentials pair the adapter exchanges for one. Passes
`tulip.security.testing` conformance.

!!! warning "`risk` and `disable` are offline-reference-only today"
    `auth0_risk` reads the bundled offline sample, not a live Auth0 signal (a
    real user comes back `risk="unknown"`). `auth0_disable` is a **simulated
    no-op** that returns `{"blocked": True, "source": "offline-sample"}` — it
    does **not** yet `PATCH` the Management API to block the user. Once wired
    live, blocking locks the user out, so treat it as a write and approval-gate
    it in agentic use.

!!! note "Credentials"
    Set `AUTH0_DOMAIN` + a Management API token (or client credentials) to run it
    against your tenant.

→ [Integrations overview](index.md) · [SecurityContext](../concepts/security-context.md)
