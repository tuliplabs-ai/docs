# Incident response with a tamper-evident audit chain

A ransomware alert fires at 2 AM. A ``GovernedAgent`` runs the ``nist_800_61_ir``
IR playbook (detect → contain → eradicate → recover). Every tool call — host
isolation, SIEM query, IOC enrichment — is logged to a tamper-evident
``AuditTrail`` via ``AuditHook``.

After the response concludes, ``trail.verify()`` recomputes the SHA-256 hash
chain and confirms no record was altered since it was written, and
``trail.export_jsonl()`` produces a SIEM-ingestible record of containment
actions. The chain is tamper-*evident*, not tamper-proof: it is a keyless,
in-memory hash chain held in a list, so it *detects* edits when checked against
a trusted head hash you retain out-of-band — it does not prevent them, sign, or
anchor the log. Persist the JSONL and pin the head hash externally before
relying on it for SOC 2 / ISO 27001 evidence, NIS2 reporting, or legal hold.

AI agents making containment decisions without any audit log are a
liability — if the agent is later questioned, *"the AI decided"* is not a
defensible answer; a tamper-evident trail at least shows what was done and flags
after-the-fact edits. ``security_toolset(allow_containment=True)`` opts in to
write-capable tools (``isolate_host``); without it, containment tools are absent
and the agent operates read-only.

Run it:
    python examples/notebook_81_ir_audit_trail.py

## Source

```python
--8<-- "examples/notebook_81_ir_audit_trail.py"
```
