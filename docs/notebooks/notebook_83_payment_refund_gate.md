# A refund gate that pays small refunds and holds big ones

A support agent talks to an upset customer and decides a refund is owed. It
should be free to settle the small stuff on its own — a $12 shipping credit, a
duplicate-charge reversal — without paging a human. But a $4,000 refund, or one
that reverses a whole batch of charges, should stop and wait for a person.

The decision of *whether the money moves* does not live in the agent's prompt.
It lives in ``admit()``, a gate that runs before the payout. The agent can be
confused, jailbroken, or wrong about the dollar amount; the refund still only
goes through if the ``ControlPolicy`` admits it. Each proposed refund becomes an
``Action`` whose dollar amount drives two policy-visible attributes: how many
ledger entries it touches (``blast_radius``) and whether it crosses the
human-review line (a ``high_value`` tag). The policy auto-allows a
single-ledger-entry refund that carries no ``high_value`` tag and holds anything
bigger.

``require_verification_score`` is set to ``0`` on purpose: a refund is a business
action, not a security finding — there is no threat to verify, so the gate
reasons purely over amount and scope. Everything that happens — the paid refund
and the held one — lands on a tamper-evident ``AuditTrail``, and
``trail.verify()`` confirms the SHA-256 chain was not altered after the fact.

In this run the small refund (one ledger entry, $12.50) is paid automatically,
while the large one ($4,000 reversing a six-charge subscription batch) trips
*both* rules — the blast radius exceeds ``max_blast_radius`` and the
``high_value`` tag is in ``require_human_for`` — so it raises an
``AdmissionError(require_human)``, the payout never runs, and the hold is queued
for a human approver. Both decisions are recorded on the trail.

Runs offline — no network, no credentials; the payout is a local ledger stub.

Run it:
    python examples/notebook_83_payment_refund_gate.py

## Source

```python
--8<-- "examples/notebook_83_payment_refund_gate.py"
```
