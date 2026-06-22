# Live vendor integrations — IOC intel, SIEM, GPU probe dispatch

The earlier notebooks used inline mock tools to keep the focus on agent
mechanics. Real SOC work calls real systems: a threat-intel feed to score
an indicator, a SIEM to pull the events behind an alert, a GPU cloud to run
an inference-fingerprint probe. This notebook wires three *worked* vendor
integrations (``examples/integrations/``) into a triage agent.

Every integration follows one convention: read the vendor credential from
the environment and call the live API when it's set; otherwise return a
deterministic, benign sample so the notebooks run offline with no account.
The return shape is identical either way, so the agent's reasoning doesn't
change between this offline demo and a live deployment.

- ``enrich_indicator`` — VirusTotal/GreyNoise-shaped IOC reputation
  (``VT_API_KEY``).
- ``query_siem`` — Splunk/Elastic-shaped log/alert search
  (``SIEM_URL`` + ``SIEM_TOKEN``).
- ``dispatch_timing_probe`` — RunPod/Lambda inference-fingerprint probe
  (``RUNPOD_API_KEY`` / ``LAMBDA_API_KEY``); see the specialist agents
  notebook for grounding the verdict.

Run it:
    .venv/bin/python examples/notebook_70_vendor_integrations.py

The default provider is the bundled mock model, and every vendor tool falls
back to its offline sample, so this runs end-to-end with no credentials. See
``examples/integrations/README.md`` for the live-credential contract.

Prerequisites:
- The Agent-with-tools notebook.
- The specialist agents notebook (CURATOR) — grounds the fingerprint the probe feeds.

## Source

```python
--8<-- "examples/notebook_70_vendor_integrations.py"
```
