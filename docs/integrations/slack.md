# Slack (notify — human handoff)

Maintained in `tulip-integrations`.

**The end of the loop.** A finding is only useful once it reaches a human or a
ticket. After an agent grounds → verifies → admits a finding, this posts it to a
Slack channel — closing the SOC loop on `require_human` or right after `admit()`.
**Live-only:** with no `SLACK_WEBHOOK_URL` it raises rather than pretending to
notify anyone.

## Install

```bash
pip install "tulip-integrations[notify-slack]"   # httpx only — no extra SDK
```

## At a glance

| | |
|---|---|
| **Env** | `SLACK_WEBHOOK_URL` (a Slack incoming webhook; `NOTIFY_WEBHOOK_URL` also works for any Slack-compatible sink) |
| **Import** | `from tulip_integrations.notify import slack_notify, notify_finding, slack_notify_tool` |
| **Functions** | `slack_notify(text)` · `notify_finding(finding)` |
| **Tool** | `slack_notify_tool` — hand it to an agent |
| **Adapter** | `slack_adapter()` → `ToolAdapter` |

## Run it

```python
from tulip_integrations.notify import notify_finding

# After a finding clears verify() + admit(), hand it to the on-call channel:
notify_finding(finding)
# posts:  🟠 *HIGH* — Root account has no MFA  (`aws:account:root`)
```

Or give the tool to an agent so it can escalate within its own loop:

```python
from tulip.agent import Agent
from tulip_integrations.notify import slack_notify_tool

agent = Agent(model="anthropic:claude-sonnet-4-6", tools=[slack_notify_tool])
```

## How it works

`slack_notify` / `notify_finding` make an HTTPS POST of the Slack-shaped payload
(`{"text": …}`) to your incoming webhook. Point `SLACK_WEBHOOK_URL` at your
workspace's webhook for production. It is **live-only** — no `SLACK_WEBHOOK_URL`
raises `RuntimeError`. It either reaches a human or it tells you it can't.

!!! note "Why this matters"
    This is the leg that turns a closed agent loop into an actioned one: grounded
    → verified → policy-gated → admitted → audited → **and someone is told**. Use
    it on `require_human`, or to escalate a finding that survives `verify()`.

→ [Integrations overview](index.md) · [Security &amp; grounding](../concepts/security.md)
