# RunPod / Lambda (compute — GPU fingerprint probe)

**Status:** 🧪 offline-verified · maintained in `tulip-integrations`.

Inference fingerprinting can measure *where the hardware is* from a co-located
probe. These compute integrations provision GPU hardware, run the timing probe
against a target endpoint, collect the feature vector, and tear the hardware
down — then feed the vector to core
[`fingerprint_to_finding`](../concepts/security.md) for a grounded verdict.

Core ships the **credential-free remote-API measurement** (`measure_endpoint_timing`,
no GPU) and an offline reference dispatch; the **real GPU-cloud lifecycle** lives
here.

```bash
pip install "tulip-integrations[compute-runpod]"   # RunPod (needs the runpod SDK)
pip install "tulip-integrations[compute-lambda]"   # Lambda Cloud (httpx only)
```

| | |
|---|---|
| **Env** | RunPod: `RUNPOD_API_KEY` (+ `RUNPOD_PROBE_IMAGE`) · Lambda: `LAMBDA_API_KEY` (+ `LAMBDA_PROBE_RESULT_URL`) |
| **Import** | `from tulip_integrations.compute import dispatch_timing_probe, probe_to_finding` |
| **Probes** | `runpod_probe(endpoint)` · `lambda_probe(endpoint)` |
| **Grounded** | `probe_to_finding(endpoint, provider)` → grounded `FingerprintFinding` |

```python
from tulip_integrations.compute import probe_to_finding

f = probe_to_finding("203.0.113.10:443", provider="runpod")
print(f.verdict.model, "/", f.verdict.engine, "/", f.verdict.hardware)
# 7-8B class / vLLM (continuous-batching) / H100/A100 class
```

With no credentials each probe returns the deterministic offline sample, so the
flow runs in CI.

!!! warning "Unverified live path"
    The lifecycle is real but depends on a probe container image you supply
    (`RUNPOD_PROBE_IMAGE`). Defensive framing: run it against *your own*
    endpoints to verify what they reveal (MITRE ATLAS AML.T0040 / AML.T0024).
