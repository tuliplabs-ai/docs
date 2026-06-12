# Security layer — evidence-grounded findings

`tulip.security` is the primitive that makes Tulip a cybersecurity SDK
rather than a general one: a security **finding can only be produced from
evidence that clears the [GSAR](gsar.md) grounding threshold.** Below the
bar, the agent abstains and records why. An ungrounded finding is a false
positive *by construction* — there is no public path that builds one.

## The grounding bridge

[`ground_finding()`][gh] takes a candidate finding plus the GSAR
`Partition` of its claims, scores the partition, and returns either a
typed `Finding` (it ships) or an `Abstention` (it is withheld, with an
audit record of why).

```python
from tulip.security import ground_finding, Severity, is_finding
from tulip.reasoning.gsar import Claim, EvidenceType, Partition

result = ground_finding(
    title="Expired TLS certificate on 192.0.2.10:443",
    description="The serving endpoint presents an expired certificate.",
    severity=Severity.HIGH,
    asset="192.0.2.10:443",
    remediation="Rotate the certificate; enforce automated renewal.",
    partition=Partition(
        grounded=[
            Claim(
                text="certificate expired 2026-05-30",
                type=EvidenceType.TOOL_MATCH,
                evidence_refs=["tool:tls_scan:not_after=2026-05-30"],
            ),
        ],
    ),
)

if is_finding(result):
    print("SHIPPED", result.title, result.gsar_score)
else:
    print("WITHHELD", result.decision, "—", result.reason)
```

A `Finding` carries the `gsar_score` that admitted it and the
`evidence_refs` flattened from its claims — it always knows how strongly
it is grounded and what it is grounded in. `Finding` has no constructor
without a score, so the invariant holds at the type level, not by
convention.

## Threat taxonomy

Findings tag themselves with the published catalogues, so they drop into
a SIEM or a compliance report without translation:

| Enum | Catalogue |
|---|---|
| `AtlasTechnique` | [MITRE ATLAS](https://atlas.mitre.org/) — `AML.Txxxx` |
| `OwaspLLM` | OWASP Top 10 for LLM Applications (2025) — `LLM01`–`LLM10` |
| `OwaspASI` | OWASP Top 10 for Agentic Applications (2026) — `ASI01`–`ASI10` |

```python
from tulip.security import AtlasTechnique, OwaspLLM

# tag a finding with the standards it maps to
taxonomy = [OwaspLLM.PROMPT_INJECTION, AtlasTechnique.PROMPT_INJECTION]  # LLM01 / AML.T0051
```

Every ID in these three catalogues maps to a runnable defense gist — see the
[threat-scenarios coverage matrix](threat-scenarios.md).

## Inference fingerprinting

`ground_fingerprint()` is the same admit/abstain contract for the
flagship AI-security surface: identifying the model, inference engine,
and hardware behind an endpoint from **timing side-channels**, with the
timing feature vector as the evidence. A `FingerprintClassifier` protocol
lets a real service plug in behind a deterministic mock; low feature
coverage abstains rather than asserting a fingerprint.

```python
from tulip.security import FingerprintVerdict, ground_fingerprint

verdict = classifier(features)              # FingerprintClassifier
finding = ground_fingerprint(
    verdict=verdict,
    asset="192.0.2.20:8000",
    partition=evidence_partition,
)
```

## GPU-level analysis

Tulip operates at the **infrastructure level of AI systems**, not just the
prompt level. Inference fingerprinting is a measurement problem: the
model, engine, and accelerator serving an endpoint leave a signature in
*timing* — time-to-first-token, inter-token cadence, throughput under
contention.

The measurement runs where the hardware is. Tulip integrates with
**dedicated GPU clusters** — Lambda, RunPod, AWS, and other GPU cloud
providers — dispatching a probe to real target-class accelerators, then
turning the returned timing profile into a grounded finding. The
dispatch target is provider-agnostic; the grounding contract is the
same everywhere, and an under-observed probe abstains rather than
asserting a fingerprint.

The pattern is always the same three steps — **measure → classify →
ground** — with the agent orchestrating tools and `ground_fingerprint`
enforcing the evidence bar:

```python
from tulip.security import (
    FingerprintVerdict, ground_fingerprint, is_finding,
    Indicator, IndicatorType, AtlasTechnique,
)
from tulip.reasoning.gsar import Claim, EvidenceType, Partition

# 1. MEASURE — a probe runs on a dedicated GPU cluster (Lambda / RunPod /
#    AWS / …) against the target endpoint and returns a timing feature
#    vector. Here the values are illustrative.
features = {
    "ttft_ms": 41.2, "inter_token_ms_p50": 7.8,
    "tokens_per_s": 128.0, "contention_slope": 0.34,
}

# 2. CLASSIFY — any object satisfying the FingerprintClassifier protocol.
#    A real deployment plugs in its trained classifier; the verdict
#    reports how much of the expected feature space was observed.
verdict = FingerprintVerdict(
    model="open-weights-8b", engine="vllm", hardware="datacenter-gpu",
    confidence=0.93, feature_coverage=1.0,
)

# 3. GROUND — the timing feature vector IS the evidence. Full coverage
#    clears the bar; sparse coverage would abstain.
partition = Partition(grounded=[
    Claim(text="TTFT/cadence profile matches vLLM/8B on datacenter GPU",
          type=EvidenceType.TOOL_MATCH,
          evidence_refs=[f"probe:timing:{k}={v}" for k, v in features.items()]),
])

finding = ground_fingerprint(
    verdict=verdict,
    asset="192.0.2.20:8000",
    partition=partition,
    indicators=[Indicator(type=IndicatorType.ENDPOINT, value="192.0.2.20:8000")],
    taxonomy=[AtlasTechnique.INFERENCE_API_ACCESS],  # AML.T0040
)

if is_finding(finding):
    print("FINGERPRINTED", finding.verdict.model, "→", finding.gsar_score)
else:
    print("ABSTAINED — insufficient feature coverage:", finding.reason)
```

### Dispatching the probe to RunPod / Lambda

The MEASURE step runs on a dedicated GPU cluster. The dispatch is an
ordinary Tulip `@tool`, so the agent decides when to probe — and the
target provider is a one-argument swap. Bring your own API key; with
none set, the tool returns a deterministic sample so the workflow stays
runnable offline (the same bring-your-own-credentials pattern the rest of
the cookbook uses).

!!! note "Illustrative sketch"
    The provider calls below outline the shape of a real dispatch — the
    pod/instance lifecycle and feature collection are elided. Adapt them
    to your GPU provider and probe image; only the offline-sample path is
    runnable as written.

```python
import os
from tulip.tools import tool

# Illustrative offline fallback — replace with a real measurement.
_SAMPLE = {"ttft_ms": 41.2, "inter_token_ms_p50": 7.8,
           "tokens_per_s": 128.0, "contention_slope": 0.34}


def _runpod_probe(endpoint: str) -> dict[str, float]:
    """Submit a timing-probe pod, poll to completion, collect features."""
    import runpod                                  # pip install runpod
    runpod.api_key = os.environ["RUNPOD_API_KEY"]
    pod = runpod.create_pod(name="tulip-timing-probe", gpu_type_id="NVIDIA H100",
                            image_name="tuliplabs/timing-probe:latest",
                            env={"TARGET_ENDPOINT": endpoint})
    return runpod.wait_for_output(pod["id"])["features"]   # tears down on exit


def _lambda_probe(endpoint: str) -> dict[str, float]:
    """Launch a Lambda Cloud instance, run the probe, terminate it."""
    import httpx
    key = os.environ["LAMBDA_API_KEY"]
    with httpx.Client(base_url="https://cloud.lambdalabs.com/api/v1",
                      headers={"Authorization": f"Bearer {key}"}) as c:
        c.post("/instance-operations/launch",
               json={"instance_type_name": "gpu_1x_h100_pcie",
                     "name": "tulip-timing-probe"})
        # Run the probe image on the instance, collect features, then
        # terminate it. Elided here; returns the measured vector.
        return _SAMPLE


@tool
def dispatch_timing_probe(endpoint: str, provider: str = "runpod") -> dict[str, float]:
    """Run a timing side-channel probe against `endpoint` on a dedicated
    GPU cluster and return the measured feature vector. provider is
    'runpod' or 'lambda'."""
    if provider == "runpod" and os.getenv("RUNPOD_API_KEY"):
        return _runpod_probe(endpoint)
    if provider == "lambda" and os.getenv("LAMBDA_API_KEY"):
        return _lambda_probe(endpoint)
    return _SAMPLE  # offline / no-credential fallback
```

Hand `dispatch_timing_probe` to an `Agent` alongside your classifier and
`ground_fingerprint`, and the full **measure → classify → ground** loop
runs end to end — on RunPod, on Lambda, or against the offline sample —
with the grounding bar enforced identically on every path.

The same shape powers a complete agent workflow in the cookbook
([forensics specialist](../notebooks/notebook_27_specialist_agents.md)),
where a low-coverage probe correctly abstains and a full-coverage probe
ships a finding mapped to compliance controls.

## Where it shows up

- Applied end-to-end: [cloud-posture agent](cloud-posture.md) — grounded,
  read-only AWS auditing built on `ground_finding`.
- Complete defense catalogue: [threat scenarios](threat-scenarios.md) — every
  OWASP LLM / OWASP ASI / MITRE ATLAS ID mapped to a runnable gist.
- Cookbook flagship: [GSAR typed grounding](../notebooks/notebook_37_gsar_typed_grounding.md)
- Prompt-injection findings: [guardrails](../notebooks/notebook_50_guardrails_security.md)
- Fingerprinting: [forensics specialist](../notebooks/notebook_27_specialist_agents.md)
- RAG poisoning: [intel copilot](../notebooks/notebook_40_rag_agents.md)

[gh]: https://github.com/tuliplabs-ai/sdk-python/tree/main/src/tulip/security
