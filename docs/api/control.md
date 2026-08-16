# Control

The admission gate: decide whether a consequential action may run, and
record the decision either way.

`tulip.control` is the domain-neutral surface. The implementations live under
`tulip.security` for historical reasons — that is where the layer grew up —
and are re-exported here, which is the import path to use.

For the concepts, start with [The control layer](../concepts/security-context.md)
and [Writing a policy that holds](../concepts/policy-authoring.md).

## Admitting an action

`admit()` evaluates the policy, records the decision on the audit trail, and
runs the action only if it was allowed. A held or denied action raises
`AdmissionError` carrying the `ApprovalDecision` that explains why.

::: tulip.security.admit.admit
::: tulip.security.admit.AdmissionError

## Deciding

`approve()` is the pure decision function — no I/O, no side effects. It takes
an action and a policy and returns the outcome. Rules combine by taking the
strongest result, so `deny` beats `require_human` beats `allow`.

::: tulip.security.policy.approve
::: tulip.security.policy.ControlPolicy
::: tulip.security.policy.ApprovalDecision
::: tulip.security.policy.ApprovalOutcome

## Describing an action

A policy matches on what an action *is* — its environment, kind, blast
radius, and tags — never on the name of the tool performing it.

::: tulip.security.policy.Action

## Gating a tool

`gate_tool` puts the gate in front of a tool the agent already has. The
returned tool keeps the original's name, description and parameter schema, so
the model sees no difference and nothing else in the agent changes — which is
what makes the control structural rather than advisory. There is nothing to
notice, so nothing to talk around.

```python
from tulip.control import ControlPolicy, gate_tool

agent = Agent(model=model, tools=[
    lookup_order,                                     # read-only, ungated
    gate_tool(issue_refund, policy=ControlPolicy()),  # gated
])
```

A refusal comes back to the model as a readable result naming the outcome and
the reason, so the agent can explain the hold rather than the run ending in a
traceback. It is the same shape the
[`tulip-frameworks`](https://github.com/tuliplabs-ai/tulip-frameworks) bridges
return, so a policy reads the same whether the agent is Tulip-native or
wrapped from LangChain, CrewAI or the OpenAI Agents SDK. Pass
`on_refusal="raise"` for a caller that would rather stop.

Gating a **sandboxed** tool composes rather than replacing it: the gate
decides, and only an admitted call reaches the sandbox.

::: tulip.control.gate.gate_tool

### Holding an action for a human

A hold is only useful if the agent can find out what happened next. Give
`gate_tool` an `approval` bridge and a held refusal carries an `approval_id` the
agent can poll, while a human decides on a channel the agent cannot reach:

```json
{"status": "held_for_approval", "outcome": "require_human",
 "action": "issue_refund", "asset": "ord-4821", "reason": "...",
 "approval_id": "appr-77",
 "next": "call approval_status(approval_id) once a human decides"}
```

A **denial** deliberately gets no id. It is final, and offering one would invite
the agent to wait for a decision that is not coming.

`ApprovalBridge` is a structural `Protocol` with no import-time dependency, so
the same broker object satisfies this and the bridge of the same name in
`tulip-frameworks` — neither package has to import the other, and a gateway
approval broker matches it in shape.

::: tulip.control.gate.ApprovalBridge

### What the user hears when an action is refused

The `reason` in that payload is, by default, the policy's own — a join of the
checks that fired:

```
"blast radius 3 exceeds the maximum 1; labels ['large_refund'] are denied by policy"
```

That is the right level of detail for the audit trail and for a developer
reading a log. It is also control-plane vocabulary, and a model handed it
repeats it verbatim. Run against a live model, the refusal above reached the
customer as *"the blast radius (3) exceeds the maximum 1"* and *"it's
classified as a `large_refund`"*.

`refusal_reason` gives the model the sentence you want the user to hear
instead. Pass a string, or `(decision) -> str` to vary it by outcome:

```python
gate_tool(
    issue_refund,
    policy=policy,
    trail=trail,
    refusal_reason=lambda d: (
        "We can't refund this amount automatically."
        if d.outcome == "deny"
        else "This refund is waiting on a manager."
    ),
)
```

The full policy reason still goes to the trail — a friendlier sentence for the
customer must not shrink the record. Added in 2.10.0.

## Deriving action labels

Turn a tool call into an `Action` using declarative rules, so the labels a
policy matches on are not hand-written per call site.

::: tulip.control.action.ActionSpec
::: tulip.control.action.resolve_action
::: tulip.control.action.default_action
::: tulip.control.action.action_from_labels
::: tulip.control.action.derive_labels
::: tulip.control.action.DerivedLabels
::: tulip.control.action.asset_from_args
::: tulip.control.action.UNDETERMINED_TAG
::: tulip.security.policy.SANDBOXED_TAG

## The record

A hash-chained log of every decision. Each record commits to the previous
hash, so editing any record breaks `verify()`.

!!! warning "Tamper-evident, not tamper-proof"
    This is a keyless SHA-256 chain held in memory. It *detects* edits when
    checked against a head hash you retain out-of-band; it does not prevent
    them, sign them, or anchor the log. Persist the JSONL and pin the head
    hash externally before relying on it as compliance evidence.

### What `verify()` catches, and the one thing it cannot

Called with no arguments, `verify()` catches every edit, every reorder, and
every deletion **from the middle** of the chain — each leaves a record whose
stored hash no longer matches its contents, or whose `prev_hash` no longer
points at the record before it.

It cannot, on its own, catch a **truncation**:

| Attack | `verify()` | `verify(expected_head=…)` |
| --- | --- | --- |
| Edit a record | `False` | `False` |
| Reorder records | `False` | `False` |
| Delete from the middle | `False` | `False` |
| Drop records off the end | `True` | `False` |
| Discard the trail entirely | `True` | `False` |

Dropping the tail leaves a shorter chain that is perfectly valid on its own
terms. That is a property of hash chains in general, not of this
implementation: nothing inside a chain can attest to a link that was never
handed to it. An agent that can reach its own audit trail can therefore erase
the end of it and still pass a bare `verify()`.

Anchoring closes it. Every attack in that table moves the head, so keep
`head` somewhere the agent cannot reach — a WORM bucket, an append-only log,
a co-signer, a transparency log — and pass it back:

```python
trail = AuditTrail()
...
anchor = trail.head                      # to durable, external storage

# later, on the exported chain
restored = AuditTrail.from_records(records)
restored.verify(expected_head=anchor)    # False if anything was removed
```

Added in 2.10.0, alongside a correction: `verify()` previously documented
itself as detecting "no edit, deletion, or reorder", which overstated what a
chain can prove about its own tail.

::: tulip.security.audit.AuditTrail
::: tulip.security.audit.AuditRecord
::: tulip.security.secure.AuditHook

## Governed agents

An `Agent` pre-wired with grounding, guardrails, and an audit trail.

::: tulip.security.secure.governed_agent
::: tulip.security.secure.GovernedAgent
::: tulip.security.secure.GovernanceProfile

## Verification

Evidence quality and adversarial refutation, feeding the
`require_verification_score` and `min_severity` rules on a policy.

::: tulip.security.verify.verify
::: tulip.security.verify.VerificationResult
::: tulip.security.findings.Evidence
::: tulip.security.taxonomy.Severity
