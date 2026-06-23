# RunPod (compute — co-located GPU fingerprint probe)

**Security capability — inference fingerprinting.** Timing an AI endpoint is
reconnaissance: by renting a GPU *next to* a target and measuring how it streams
tokens, an adversary can infer the **model class, inference engine, and hardware**
behind an API — the opening move of model extraction
(**MITRE ATLAS [AML.T0040](https://atlas.mitre.org/techniques/AML.T0040) — Inference
API Access** → **[AML.T0024](https://atlas.mitre.org/techniques/AML.T0024) —
Exfiltration via ML Inference API**). This integration runs that probe
**defensively**: point it at endpoints *you operate* to measure what they leak and
close the gap before someone else maps it. Every verdict is **grounded** — a thin
measurement abstains instead of asserting an identity.

The RunPod backend is a **pod + container-image** model: it provisions a real GPU
pod from your probe image, runs the probe against the target endpoint, collects the
timing feature vector, tears the pod down, and feeds the vector to core
[`fingerprint_to_finding`](../concepts/security.md) for a grounded
`FingerprintFinding`.

## Install

```bash
pip install "tulip-integrations[compute-runpod]"   # pulls the runpod SDK
```

## At a glance

| | |
|---|---|
| **Env** | `RUNPOD_API_KEY` (+ `RUNPOD_PROBE_IMAGE`, your image; default `tuliplabs/timing-probe:latest`) |
| **Install** | `tulip-integrations[compute-runpod]` — needs the `runpod` SDK |
| **Import** | `from tulip_integrations.compute.runpod import runpod_probe` |
| **Probe** | `runpod_probe(endpoint)` → timing feature vector |
| **Grounded** | `probe_to_finding(endpoint, provider="runpod")` → grounded `FingerprintFinding` |
| **ATLAS** | tags `AML.T0040` (Inference API Access) · `AML.T0024` (Exfiltration via Inference API) |

## How the RunPod lifecycle works

1. `create_pod(...)` from `RUNPOD_PROBE_IMAGE` on an H100-class GPU, with
   `TARGET_ENDPOINT` passed in the pod env.
2. `wait_for_output(pod_id)` — the probe measures the endpoint's streaming timing
   (TTFT p50, inter-token latency, its coefficient of variation, tokens/sec) and
   emits a JSON feature vector.
3. The vector is parsed and the pod is **terminated in a `finally`**, so the bill
   stops even if the probe fails.
4. `fingerprint_to_finding(vector, asset=endpoint)` grounds it — full coverage
   ships a `FingerprintFinding`; thin coverage returns an `Abstention`.

**You supply the probe** — on RunPod it *is* the container image. It must emit:

```json
{"ttft_ms_p50": 38.2, "itl_ms_mean": 11.4, "itl_cv": 0.07, "tps_mean": 87.6}
```

## Run it

```python
from tulip_integrations.compute import probe_to_finding

f = probe_to_finding("https://my-endpoint/v1", provider="runpod")
print(f.verdict.model, "/", f.verdict.engine, "/", f.verdict.hardware)
# 7-8B class / vLLM (continuous-batching) / H100/A100 class
```

Set `RUNPOD_API_KEY` and point `RUNPOD_PROBE_IMAGE` at your published probe image,
and the lifecycle above runs against a live GPU.

## Grounding

The timing feature vector routes through core `fingerprint_to_finding`, so an
under-observed endpoint abstains rather than asserting a model identity.
`runpod_probe()` orchestrates the full provision → probe → terminate lifecycle;
point `RUNPOD_PROBE_IMAGE` at your published probe image to run it against a
live GPU.

!!! warning "The live path is billable"
    A live run spins up an H100-class GPU. Gate it behind explicit approval and a
    provider spend limit, and rely on the `finally` teardown.

!!! note "Defensive framing"
    Run this against endpoints **you operate** to verify what they reveal. It is
    the same measurement an attacker uses for model-extraction recon
    (`AML.T0040` / `AML.T0024`) — which is exactly why the verdict is grounded: a
    thin measurement must never assert a model identity.

→ [Lambda Cloud probe](lambda.md) · [Integrations overview](index.md) · [Security &amp; grounding](../concepts/security.md)
