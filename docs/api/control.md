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
