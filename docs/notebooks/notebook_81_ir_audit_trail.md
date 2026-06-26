# Incident response with a tamper-evident audit chain

A production outage pages the on-call at 2 AM. A ``GovernedAgent`` runs the
``sre_incident_runbook`` (detect → triage → mitigate → recover). Every tool
call — metrics query, log tail, deploy rollback — is logged to a tamper-evident
``AuditTrail`` via ``AuditHook``.

After the incident concludes, ``trail.verify()`` recomputes the SHA-256 hash
chain and confirms no record was altered since it was written, and
``trail.export_jsonl()`` produces a portable record of the mitigation actions.
The chain is tamper-*evident*, not tamper-proof: it is a keyless, in-memory hash
chain held in a list, so it *detects* edits when checked against a trusted head
hash you retain out-of-band — it does not prevent them, sign, or anchor the log.
Persist the JSONL and pin the head hash externally before relying on it for
SOC 2 / ISO 27001 change-management evidence, postmortem records, or audit hold.

AI agents making remediation decisions without any audit log are a
liability — if the agent is later questioned, *"the AI decided"* is not a
defensible answer; a tamper-evident trail at least shows what was done and flags
after-the-fact edits. ``ops_toolset(allow_mitigation=True)`` opts in to
write-capable tools (``rollback_deploy``); without it, mitigation tools are
absent and the agent operates read-only.

Run it:
    python examples/notebook_81_ir_audit_trail.py

## Source

```python
--8<-- "examples/notebook_81_ir_audit_trail.py"
```
