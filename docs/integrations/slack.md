# Slack (notify — human handoff)

**The end of the loop.** This is the leg that turns a held action into a human
decision: when an agent's action is held (`require_human`), or a result needs a
person's eyes, this posts it to a Slack channel — a refund waiting for approval,
a deploy waiting for sign-off, a security finding that just cleared `verify()`.
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
| **Import** | `from tulip_integrations.notify import slack_notify, notify_finding, slack_notify_tool, slack_adapter` |
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
    This is the leg that turns a closed agent loop into an actioned one: decided
    → gated → audited → **and someone is told**. Use it when an action is held
    (`require_human`) — a refund awaiting approval, a deploy waiting on a
    sign-off — or to escalate a finding that survives `verify()`.

→ [Integrations overview](index.md) · [Security &amp; grounding](../concepts/security.md)
