# DPA & Security-Addendum Review

Reviewing a vendor's Data Processing Agreement involves multiple
stakeholders working in parallel, then a back-and-forth negotiation
phase, then sign-off::

    DPA intake
       │
       ▼
    Parser  (extracts clauses)
       │
       ▼
    Scatter to 3 parallel reviewers
       ├── Privacy     (breach notice, residency, sub-processors, deletion)
       ├── Security    (encryption, audit rights, incident response)
       └── Compliance  (attestations, GDPR Art. 28 terms, liability for fines)
       ▼
    Synthesizer  (consolidated review report)
       │
       ▼
    Negotiation gate ── any blockers? ── yes ──> Negotiate (interrupt; loop)
                                       │            │
                                       │            └── revised terms ──┐
                                       │                                │
                                       └── no ──┐                       │
                                                ▼                       │
                                          Sign-off  <───────────────────┘
                                                ▼
                                          ContractDecision (typed)

The DPA governs a processor in the AI stack's supply chain (OWASP ASI04),
so a weak breach-notification window or a missing audit right is a real
control gap, not a paperwork nit. SCRIBE — the SOC's compliance reporter
— writes the typed sign-off.

- `Send`: three reviewers run concurrently.
- `add_conditional_edges` with cycles enabled: negotiation can loop
  back to re-review when terms change. Hard cap of 3 rounds.
- `interrupt()`: negotiation step pauses for human counsel to edit terms.
- `output_schema=ContractDecision`: typed terminal artifact.

Run it (defaults to the bundled mock model; set `TULIP_MODEL_PROVIDER` to `openai` / `anthropic` for a live model):

    python examples/notebook_65_contract_review.py

Offline:

    TULIP_MODEL_PROVIDER=mock python examples/notebook_65_contract_review.py

Pin a strong-enough model for the structured ContractDecision schema:

    TULIP_MODEL_ID=openai.gpt-4.1 python examples/notebook_65_contract_review.py

## Source

```python
--8<-- "examples/notebook_65_contract_review.py"
```
