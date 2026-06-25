# Why Tulip

Most agent frameworks help the model **decide**. Tulip governs what happens
**after** it decides — the moment an agent stops advising and starts *acting*:
moving money, deleting a resource, disabling an account, isolating a host.

A frontier model can be brilliant and still be talked into the catastrophic
action. The thing it structurally **cannot** do — no matter how smart — is
*prove it won't*. That proof is not an intelligence problem; it's a control
problem. Tulip is the control layer.

## The one thing a bare model can't do

Give a capable model a `wipe_database` tool and a clever enough prompt, and
sooner or later it calls it. You can add a system-prompt rule ("never wipe
production"), and a good model will follow it — until a jailbreak, an injected
document, or a confused chain of reasoning talks it past the rule. A rule the
model *chooses* to follow is advisory by definition.

Tulip makes the rule **structural**. The side-effecting call runs only after it
clears an admission gate — `admit()` — that the model has no way to reach around.
Fool the model all you like; you can't talk past the runtime.

## Library vs. runtime

A trust *library* offers grounding, verification, and policy as functions you
*may* call. A trust *runtime* makes them mandatory: a side-effecting action runs
**only after** it has cleared the chain — evidence → verification → policy →
approval → admission → audit. That last gate is the whole difference.

## Three ways to "make agents safe"

| | Bare model + prompt rules | Framework guardrails | **Tulip** |
|---|---|---|---|
| **Where safety lives** | In the prompt the model can be argued out of | Input/output filters around the call | An admission gate **around the action** |
| **Can a jailbreak bypass it?** | Yes — talk the model out of the rule | Often — filters score text, not the action's blast radius | **No** — the action runs only if `admit()` allows it |
| **Human-in-the-loop** | Ad-hoc, if you wire it | Sometimes, per-framework | First-class: `require_human_for` by environment / kind / tag |
| **Proof of what happened** | Logs you can edit | App logs | **Hash-chained `AuditTrail`** — `verify()` fails on any edit |
| **Evidence behind a claim** | "Trust the model" | None | **GSAR grounding** — a `Finding` exists only above threshold, else `Abstention` |
| **Works with your stack** | — | You adopt the framework | Drop-in: wrap a call your agent already makes |

Guardrails and grounding are good and Tulip ships both. But the moat is the
**admission gate**: a wrong action isn't filtered after the fact, it's *prevented*
before it runs, and the decision is recorded whether it ran or not.

## See it in ~8 lines

```python
from tulip.security import (
    Action, admit, SecurityPolicy, AuditTrail, AdmissionError)

policy = SecurityPolicy()   # conservative: production → human
trail = AuditTrail()        # tamper-evident, replayable

risky = Action(name="refund", asset="cust:4821",
               blast_radius=1, kind="payment", environment="production")

try:
    await admit(risky, lambda: refund("cust:4821"), policy=policy, trail=trail)
except AdmissionError as e:
    print(e.decision.outcome)   # -> "require_human"; refund NOT run
```

The refund was *decided* by the model and *held* by the runtime. The hold is on
the audit trail. Nothing the model says in the next turn can release it — only a
human on a side channel can.

## When Tulip is overkill

If your agent only reads and summarizes — no side effects, no money, no
infrastructure, no irreversible writes — you may not need an admission gate yet.
Tulip still gives you grounded findings and a typed event stream, but the control
runtime earns its keep the moment an action can *cost* something.

## Where to start

- [Quickstart](how-to/quickstart.md) — a working agent, then gate its action in step 3.5.
- [The security layer](concepts/security.md) — the full policy + admission surface.
- [GSAR grounding](concepts/gsar.md) — why a `Finding` can't exist without evidence.
- [Drop Tulip into your framework](integrations/frameworks.md) — keep LangChain / CrewAI / your stack; add the gate.
