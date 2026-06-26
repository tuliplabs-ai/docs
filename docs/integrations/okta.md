# Okta (identity)

```bash
pip install "tulip-integrations[identity-okta]"
```

| | |
|---|---|
| **Env** | `OKTA_URL` · `OKTA_TOKEN` (SSWS API token) |
| **Import** | `from tulip_integrations.identity.okta import OktaIdentity, okta_user_tool, okta_disable_tool` |
| **Provider** | `OktaIdentity` → `SecurityContext(identity=OktaIdentity())`; methods `get_user` (live) · `signins` (live) · `risk` (offline sample) · `disable` (write — simulated offline stub) |
| **Functions** | `okta_get_user(user)` · `okta_risk(user)` · `okta_signins(user)` · `okta_disable(user)` ⚠️ write |
| **Agent tools** | `okta_user_tool` (reads a user) · `okta_disable_tool` (⚠️ disables an account) |
| **Adapter** | `okta_adapter()` → `ToolAdapter` (a `SecurityAdapter`) |

```python
from tulip.security import SecurityContext
from tulip_integrations.identity.okta import OktaIdentity

ctx = SecurityContext(identity=OktaIdentity())
await ctx.identity.get_user("mallory@example.com")   # profile + MFA (live: GET /api/v1/users)
await ctx.identity.signins("mallory@example.com")     # recent sign-ins (live)
await ctx.identity.risk("mallory@example.com")        # risk + impossible_travel (offline sample)
```

Look up a user and pull recent sign-ins (both live), read a risk signal, or
disable an account. With no credentials set, every call returns a bundled offline
sample (`mallory@example.com` is the high-risk one) so it runs in CI with no
secrets. Only `okta_user_tool` and `okta_disable_tool` are exposed as agent
tools. Implements the same `IdentitySource` port as Auth0 and Entra, so you can
swap providers by changing one line. Passes `tulip.security.testing` conformance.

!!! warning "`risk` and `disable` are offline-reference-only today"
    `okta_risk` reads the bundled offline sample, not a live Okta risk API (a
    real user comes back `risk="unknown"`). `okta_disable` is a **simulated
    no-op** that returns `{"disabled": True, "source": "offline-sample"}` — it
    does **not** yet call the Okta SSWS lifecycle endpoint. Once wired live,
    disabling locks the user out, so treat it as a write and approval-gate it in
    agentic use.

!!! note "Credentials"
    Okta has free developer tenants — set `OKTA_URL` / `OKTA_TOKEN` to run it
    against one.

→ [Integrations overview](index.md) · [SecurityContext](../concepts/security-context.md)
