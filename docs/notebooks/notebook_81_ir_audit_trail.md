# Incident response with a tamper-evident audit chain

A ransomware alert fires at 2 AM. A ``SecureAgent`` runs the ``nist_800_61_r3``
IR playbook (detect → contain → eradicate → recover). Every tool call — host
isolation, SIEM query, IOC enrichment — is logged to an immutable ``AuditTrail``
via ``AuditHook``.

After the response concludes, ``trail.verify()`` confirms the chain has not been
tampered with, and ``trail.export_jsonl()`` produces SIEM-ingestible, legally
defensible evidence: an immutable log of containment actions for SOC 2 / ISO
27001, a decision timeline for NIS2 reporting, and a hash-chained record for
legal hold.

AI agents making containment decisions without an immutable audit log are a
liability — if the agent is later questioned, *"the AI decided"* is not a
defensible answer. ``security_toolset(allow_containment=True)`` opts in to
write-capable tools (``isolate_host``); without it, containment tools are absent
and the agent operates read-only.

Run it:
    python examples/notebook_81_ir_audit_trail.py

## Source

```python
--8<-- "examples/notebook_81_ir_audit_trail.py"
```
