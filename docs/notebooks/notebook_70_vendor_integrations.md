# Live vendor integrations — PII discovery, data map, scan dispatch

The earlier notebooks used inline mock tools to keep the focus on agent
mechanics. Real privacy work calls real systems: a data-classification
feed to score an identifier, a data catalog to pull the records behind a
subject request, a scanning cloud to run a PII-discovery probe over a
data store. This notebook wires three *worked* vendor integrations into a
data-subject-request (DSAR) triage agent.

Every integration follows one convention: read the vendor credential from
the environment and call the live API when it's set; otherwise return a
deterministic, synthetic sample so the notebooks run offline with no
account. The return shape is identical either way, so the agent's
reasoning doesn't change between this offline demo and a live deployment.

- ``scan_for_pii`` — BigID/OneTrust-shaped identifier classification
  (``DATAMAP_API_KEY``).
- ``query_data_map`` — Collibra/Atlan-shaped data-catalog search
  (``DATAMAP_URL`` + ``DATAMAP_TOKEN``).
- ``scan_dataset_reference`` — PII-discovery scan over a named data store;
  the live version dispatches the scan to a classification cloud
  (``SCANNER_API_KEY``). See the specialist agents notebook for grounding
  the data inventory it feeds.

Run it:
    .venv/bin/python examples/notebook_70_vendor_integrations.py

The default provider is the bundled mock model, and every vendor tool falls
back to its offline sample, so this runs end-to-end with no credentials.
Set the matching credential to swap any offline sample for the live API.

Prerequisites:
- The Agent-with-tools notebook.
- The specialist agents notebook (CURATOR) — grounds the data inventory the scan feeds.

## Source

```python
--8<-- "examples/notebook_70_vendor_integrations.py"
```
