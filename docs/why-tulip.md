# Why Tulip

Tulip is a full-stack, open-source agent framework — tools, memory, multi-agent,
RAG, streaming — and the safest one to build on. Everything you'd expect from an
agent framework is here, behind one `Agent` class. What makes it the *safest* is
that control isn't a guardrail you remember to add; it's wired through the core.

A frontier model can be brilliant and still be talked into a catastrophic action
— by a clever prompt, a poisoned document, or its own confused reasoning. The one
thing it *structurally* cannot do, no matter how smart, is **prove it won't**.
That's not an intelligence problem; it's a control problem. Tulip solves it with
three control points, so safety is a property of the runtime, not a reminder in a
prompt.

## Control in three places

In short: the [cognitive router](concepts/router.md) decides *which shape* runs,
[GSAR](concepts/gsar.md) decides *what gets asserted*, and the admission gate
decides *what actions fire*. This page goes deep on the last one — the gate a
jailbroken model can't reach around.

## The one thing a bare model can't do

Give a capable model a `wipe_database` tool and a clever enough prompt, and
sooner or later it calls it. You can add a system-prompt rule ("never wipe
production"), and a good model will follow it — until a jailbreak, an injected
document, or a confused chain of reasoning talks it past the rule. A rule the
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

## Three ways to "make agents safe"

| | Bare model + prompt rules | Framework guardrails | **Tulip** |
|---|---|---|---|
| **Where safety lives** | In the prompt the model can be argued out of | Input/output filters around the call | An admission gate **around the action** |
| **Can a jailbreak bypass it?** | Yes — talk the model out of the rule | Often — filters score text, not the action's blast radius | **No** — the action runs only if `admit()` allows it |
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
    print(e.decision.outcome)   # -> "require_human"; refund NOT run
```

The refund was *decided* by the model and *held* by the runtime. The hold is on
the audit trail. Nothing the model says in the next turn can release it — only a
human on a side channel can.

## Proven where a wrong action is a breach

The same three control points apply to any agent you build with Tulip — in
payments, in infrastructure, in support. They were proven in the hardest place to
act on a machine's say-so: **security**. There a hallucinated claim isn't an
embarrassment but a false positive that burns an analyst's night, so
`tulip.security` makes a finding *unshippable* unless it's grounded. Findings
carry MITRE ATLAS and OWASP tags and drop into a SIEM without translation — the
same evidence-before-action discipline that makes Tulip safe to let act anywhere.

## Where to start

- [Quickstart](how-to/quickstart.md) — a working agent, then gate its action in step 3.5.
- [The control layer](concepts/security-context.md) — the full policy + admission surface.
- [GSAR grounding](concepts/gsar.md) — why an `Evidence` can't exist without evidence.
- [Bring control to an existing agent](integrations/frameworks.md) — add Tulip's gate to an agent you built elsewhere.
