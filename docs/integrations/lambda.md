# Lambda Cloud (compute — co-located GPU fingerprint probe)

!!! note "Advanced — a specialized probe, not a starting integration"
    Same niche as the [RunPod probe](runpod.md): only for teams that **operate a
    model endpoint** and want to measure its timing exposure. New to Tulip
    integrations? Start with the [action and evidence integrations](index.md) —
    EDR, identity, SIEM, threat-intel.

**Security capability — inference fingerprinting.** Same defensive recon as the
[RunPod probe](runpod.md): rent a GPU next to a target endpoint, time how it
streams tokens, and infer the **model class, inference engine, and hardware** —
the first move of model extraction
(**MITRE ATLAS** — a public catalog of attack techniques against AI systems —
**[AML.T0040](https://atlas.mitre.org/techniques/AML.T0040) — Inference
API Access** → **[AML.T0024](https://atlas.mitre.org/techniques/AML.T0024) —
Exfiltration via ML Inference API**). Point it at endpoints *you operate* to
measure your own exposure; the verdict is **grounded**, so a thin measurement
abstains rather than guessing.

Lambda Cloud differs from RunPod in **how it collects the result**. Lambda has no
"wait for pod output" call, so the probe **pushes its feature JSON to a result
sink** that the launcher polls — an **instance + result-sink** model.

## Install

```bash
pip install "tulip-integrations[compute-lambda]"   # httpx only — no extra SDK
```

## At a glance

| | |
|---|---|
| **Env** | `LAMBDA_API_KEY` · `LAMBDA_REGION` (default `us-east-1`) · `LAMBDA_PROBE_RESULT_URL` (where the probe uploads its JSON) |
| **Install** | `tulip-integrations[compute-lambda]` — no extra runtime dep (uses core `httpx`) |
| **Import** | `from tulip_integrations.compute.lambda_cloud import lambda_probe` |
| **Probe** | `lambda_probe(endpoint)` → timing feature vector |
| **Grounded** | `probe_to_finding(endpoint, provider="lambda")` → `GroundedFinding` (`FingerprintFinding`, or `Abstention`) |
| **ATLAS** | tags `AML.T0040` (Inference API Access) · `AML.T0024` (Exfiltration via Inference API) |

## How the Lambda lifecycle works

1. `POST /instance-operations/launch` over `httpx` (Bearer auth) — boots a
   `gpu_1x_h100_pcie` instance named `tulip-timing-probe` in `LAMBDA_REGION`.
2. The probe on the instance measures the endpoint's streaming timing and
   **uploads its feature JSON to `LAMBDA_PROBE_RESULT_URL`** (an S3 object or a
   small HTTP endpoint).
3. The launcher **polls that sink** (30 attempts × 10s) until the vector lands.
4. The instance is **terminated in a `finally`** (`POST
   /instance-operations/terminate`) so the bill stops even on error.
5. `fingerprint_to_finding(...)` grounds the vector exactly as RunPod does.

**You supply two things:** the probe that runs on the instance, and the sink it
uploads to (`LAMBDA_PROBE_RESULT_URL`). The feature schema is identical to RunPod:

```json
{"ttft_ms_p50": 38.2, "itl_ms_mean": 11.4, "itl_cv": 0.07, "tps_mean": 87.6}
```

## Example

```python
from tulip_integrations.compute import probe_to_finding

f = probe_to_finding("https://my-endpoint/v1", provider="lambda")
print(f.verdict.model, "/", f.verdict.engine, "/", f.verdict.hardware)
# 7-8B class / vLLM (continuous-batching) / H100/A100 class
```

## Grounding

The feature vector routes through core `fingerprint_to_finding` (shared with
RunPod), so a thin measurement abstains rather than asserting a model identity.

!!! warning "Unverified live path"
    Only the **offline sample path is exercised in CI.** The launch → poll →
    terminate lifecycle is written to Lambda Cloud's documented API but has not been
    run against a live account; you also supply the probe and its result sink. Treat
    the live path as a reference implementation to validate in your own environment.

!!! warning "The live path is billable"
    A live run boots an H100-class instance. Gate it behind explicit approval and a
    spend limit, and rely on the `finally` teardown.

!!! note "Defensive framing"
    Same as RunPod: a grounded, abstaining verdict means a thin measurement never
    asserts a model identity. Use it to audit your own exposure
    (`AML.T0040` / `AML.T0024`).

→ [RunPod probe](runpod.md) · [Integrations overview](index.md) · [Security &amp; grounding](../concepts/security.md)
