# Why Tulip

Tulip is a **complete open-source agent framework** — tools, memory, multi-agent,
RAG, streaming, all behind one `Agent` class — where control is native rather than
an add-on you remember to wire. The same runtime also
[governs agents you already run elsewhere](integrations/frameworks.md).

The breadth is what makes the control claim possible. Picking which shape runs,
checking what gets asserted, and gating what actually fires are three different
moments in one loop — you can only hold all three if you own that loop.

A frontier model can be brilliant and still be talked into a catastrophic action
— by a misleading document, its own confused reasoning, or a cleverly worded
request. The one
thing it *structurally* cannot do, no matter how smart, is **prove it won't**.
That's not an intelligence problem; it's a control problem. Tulip solves it with
three control points, so safety is a property of the runtime, not a reminder in a
prompt.

## Control in three places

In short: the [agent loop](concepts/agent-loop.md) decides *what to do next*,
[GSAR](concepts/gsar.md) decides *what gets asserted*, and the admission gate
decides *what actions fire*. This page goes deep on the last one — the gate the
model can't reach around, whatever it was talked into.

## The one thing a bare model can't do

Give a capable model a `wipe_database` tool and a clever enough prompt, and
sooner or later it calls it. You can add a system-prompt rule ("never wipe
production"), and a good model will follow it — until a misleading document, a
confused chain of reasoning, or a determined-enough request talks it past the rule. A rule the
model *chooses* to follow is advisory by definition.

Tulip makes the rule **structural**. The action runs only after it clears an
admission gate — `admit()` — that lives in your code, not in the prompt. You can
trick the model into *trying* the action. You cannot trick the gate that decides
whether it actually runs.

## Library vs. runtime

A trust *library* offers grounding, verification, and policy as functions you
*may* call. A trust *runtime* makes them mandatory: a side-effecting action runs
**only after** it has cleared the chain — evidence → verification → policy →
approval → admission → audit. That last gate is the whole difference.

## Three places control can live

| | Bare model + prompt rules | Framework guardrails | **Tulip** |
|---|---|---|---|
| **Where control lives** | In the prompt the model can be argued out of | Input/output filters around the call | An admission gate **around the action** |
| **Can the model be talked past it?** | Yes — argue it out of the rule | Often — filters score text, not what the action can touch | **No** — the action runs only if `admit()` allows it |
| **Human-in-the-loop** | Ad-hoc, if you wire it | Sometimes, per-framework | First-class: `require_human_for` by environment / kind / tag |
| **Proof of what happened** | Logs you can edit | App logs | **Hash-chained `AuditTrail`** — `verify()` fails on any edit |
| **Evidence behind a claim** | "Trust the model" | None | **GSAR grounding** — an `Evidence` exists only above threshold, else `Abstention` |

Guardrails and grounding are good and Tulip ships both. But the difference is the
**admission gate**: a wrong action isn't filtered after the fact, it's *prevented*
before it runs, and the decision is recorded whether it ran or not.

## See it in ~8 lines

```python
from tulip.control import (
    Action, admit, ControlPolicy, AuditTrail, AdmissionError)

policy = ControlPolicy()   # conservative: production → human
trail = AuditTrail()        # tamper-evident, replayable

risky = Action(name="refund", asset="cust:4821",
               blast_radius=1, kind="payment", environment="production")

try:
    await admit(risky, lambda: refund("cust:4821"), policy=policy, trail=trail)
except AdmissionError as e:
    print(e.decision.outcome)   # -> "require_human" — held; refund NOT run
```

The refund was *decided* by the model and *held* by the runtime. The hold is on
the audit trail. Nothing the model says in the next turn can release it — only a
human on a side channel can.

## Proven in the hardest domain first

The same three control points apply to any agent you build with Tulip — in
payments, in infrastructure, in support. They were proven in the hardest place to
act on a machine's say-so: **security**. There a hallucinated claim isn't an
embarrassment but a false positive that burns an analyst's night, so
`tulip.security` makes a finding *unshippable* unless it's grounded. Findings
carry tags from the standard security catalogues (MITRE ATLAS, OWASP) and export
straight into a security team's log platform (a SIEM) — the same
evidence-before-action discipline that makes Tulip safe to let act anywhere.

## Where to start

- [Quickstart](how-to/quickstart.md) — a working agent, then gate its action in step 3.5.
- [The control layer](concepts/security-context.md) — the full policy + admission surface.
- [GSAR grounding](concepts/gsar.md) — why an `Evidence` can't exist without evidence.
- [Bring control to an existing agent](integrations/frameworks.md) — add Tulip's gate to an agent you built elsewhere.
