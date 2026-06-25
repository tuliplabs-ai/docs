# Okta (identity)

```bash
pip install "tulip-integrations[identity-okta]"
```

| | |
|---|---|
| **Env** | `OKTA_URL` · `OKTA_TOKEN` (SSWS API token) |
| **Import** | `from tulip_integrations.identity.okta import OktaIdentity, okta_user_tool, okta_disable_tool` |
| **Provider** | `OktaIdentity` → `SecurityContext(identity=OktaIdentity())`; methods `get_user` · `risk` · `signins` · `disable` (write) |
| **Functions** | `okta_get_user(user)` · `okta_risk(user)` · `okta_signins(user)` · `okta_disable(user)` ⚠️ write |
| **Agent tools** | `okta_user_tool` (reads a user) · `okta_disable_tool` (⚠️ disables an account) |
| **Adapter** | `okta_adapter()` → `ToolAdapter` (a `SecurityAdapter`) |

```python
from tulip.security import SecurityContext
from tulip_integrations.identity.okta import OktaIdentity

ctx = SecurityContext(identity=OktaIdentity())
await ctx.identity.get_user("mallory@example.com")   # profile + MFA (live: GET /api/v1/users)
await ctx.identity.risk("mallory@example.com")        # risk + impossible_travel
await ctx.identity.signins("mallory@example.com")     # recent sign-ins
```

Look up a user and pull risk signals + recent sign-ins (read), or disable an
account (`disable` — a **write**, gate it). With no credentials set, every call
returns a bundled offline sample (`mallory@example.com` is the high-risk one) so
it runs in CI with no secrets. Only `okta_user_tool` and `okta_disable_tool` are
exposed as agent tools. Implements the same `IdentitySource` port as Auth0 and
Entra, so you can swap providers by changing one line. Passes
`tulip.security.testing` conformance.

!!! warning "`okta_disable` is a real action"
    Disabling an account locks the user out. Approval-gate it in agentic use.

!!! note "Credentials"
    Okta has free developer tenants — set `OKTA_URL` / `OKTA_TOKEN` to run it
    against one.

→ [Integrations overview](index.md) · [SecurityContext](../concepts/security-context.md)
