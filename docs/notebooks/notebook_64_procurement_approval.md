# Vendor Security Review

Real third-party-risk programs have a tier-based escalation chain::

    Vendor intake (questionnaire on file)
       │
       ▼
    Questionnaire analyst  (summarises the vendor's security questionnaire)
       │
       ▼
    Posture analyst  (assesses data exposure + control posture)
       │
       ▼
    Risk-tier router  ── score < 25 ──> auto-approve (low risk)
                      ── 25–49     ──> security-manager approval (interrupt)
                      ── 50–74     ──> manager + GRC approval (two interrupts)
                      ── >= 75     ──> manager + GRC + CISO approval (three interrupts)
       │
       ▼
    Decision recorder  (emits structured VendorDecision)

Each approval gate is a separate `interrupt()` so a reviewer can come
back to it later. The terminal node is SCRIBE, the SOC's compliance
reporter: it emits a typed `VendorDecision` Pydantic model that files
into the vendor-risk register without parsing. Third-party AI services
widen the agentic supply chain (OWASP ASI04), so the posture step is
where you weigh attestations (SOC 2, ISO 27001) against what data the
vendor would actually touch.

- Risk-tier router is a plain conditional edge — no DSL, no policy file.
- Each gate is its own node — easy to add a tier, easy to re-order,
  easy to swap a human gate for an automated rule.
- `output_schema=VendorDecision` keeps the terminal artifact typed.

Run it (defaults to the bundled mock model; set `TULIP_MODEL_PROVIDER` to `openai` / `anthropic` for a live model):

    python examples/notebook_64_procurement_approval.py

Offline:

    TULIP_MODEL_PROVIDER=mock python examples/notebook_64_procurement_approval.py

Pin a strong-enough model for the structured VendorDecision schema:

    TULIP_MODEL_ID=openai.gpt-4.1 python examples/notebook_64_procurement_approval.py

## Source

```python
--8<-- "examples/notebook_64_procurement_approval.py"
```
