# Security

The security domain ships as the separate `tulip-agents-security` package (`tulip_security`), installed with
`pip install "tulip-agents[security]"`. The core `tulip-agents` package does not
include it. It covers three separable jobs:

- **Red-teaming** an agent — send adversarial probes at a target and report
  what got through.
- **Grounding a finding** — refuse to assert what the evidence does not
  support, and say so explicitly rather than guessing.
- **Building a SOC agent** — tools that talk to a SIEM, an EDR, a scanner, a
  threat-intel feed, and AWS, plus playbooks that sequence them.

The admission gate also lives under this package for historical reasons. Import
it from [`tulip.control`](control.md) instead — that is the domain-neutral
surface and the path that will keep working.

For the concepts, start with [The control layer](../concepts/security-context.md).

## Running a job

The three entry points. Each takes a `Target` and returns a report; none of
them needs an agent instance.

::: tulip_security.jobs.red_team
::: tulip_security.jobs.assure
::: tulip_security.jobs.monitor
::: tulip_security.assess.guardrail_coverage

## Naming a target

A `Target` is what to point a job at — an HTTP endpoint, a local callable, or
an agent in this process. The same target works for every job.

::: tulip_security.target.Target
::: tulip_security.target.Sender

## Probes

A probe is one adversarial attempt with a stated technique and a verdict. The
built-in set maps onto OWASP's ASI and LLM top tens; `suite_probes()` selects
by suite name, which is what `red_team(suite=...)` takes.

::: tulip_security.redteam.base.Probe
::: tulip_security.redteam.base.ProbeOutcome
::: tulip_security.redteam.all_probes
::: tulip_security.redteam.suite_probes

### The built-in probes

::: tulip_security.redteam.probes.DirectPromptInjection
::: tulip_security.redteam.probes.IndirectPromptInjection
::: tulip_security.redteam.probes.Jailbreak
::: tulip_security.redteam.probes.ExcessiveAgency
::: tulip_security.redteam.probes.SensitiveInformationDisclosure
::: tulip_security.redteam.probes.UnsandboxedCodeExecution

## Findings and evidence

[`Evidence`](control.md#tulip.control.findings.Evidence) is the shape every
finding takes — a claim, the observations behind it, and a confidence. It is
documented on the Control page, which is where a finding first matters.
`Indicator` is the atom a threat-intel lookup returns.

::: tulip.control.findings.Indicator
::: tulip.control.findings.Confidence

## Grounding — abstention over assertion

The distinctive part. `ground_finding()` returns either an `Evidence` or an
`Abstention`, never a low-confidence guess dressed as a result, and
`is_finding()` is the narrowing check that separates the two. A pipeline that
cannot tell "no evidence" from "no problem" reports clean when it is blind.

::: tulip.control.grounded.ground_finding
::: tulip.control.grounded.ground_fingerprint
::: tulip.control.grounded.is_finding
::: tulip.control.grounded.Abstention
::: tulip.control.grounded.GroundedFinding

## Verification — trying to refute

[`verify()`](control.md#tulip.control.verification.verify) runs skeptics against a
claim rather than a second model that agrees with the first. A skeptic's job is
to refute; what survives is what gets reported. It and
[`VerificationResult`](control.md#tulip.control.verification.VerificationResult) are
documented on the Control page — a policy can require a verified finding before
it admits an action, which is where they are load-bearing.

::: tulip.control.verification.Refutation
::: tulip.control.verification.Skeptic
::: tulip.control.verification.EvidenceQualitySkeptic
::: tulip.control.verification.AdversarialSkeptic

## Taxonomy

The standard technique vocabularies a finding is tagged with, and the
comparison to use on severity. [`Severity`](control.md#tulip.control.taxonomy.Severity)
itself is documented on the Control page, since a policy's `min_severity`
matches on it — but reach for `severity_at_least()` rather than comparing two
directly: it is a string enum, so `>` orders alphabetically and gets the answer
wrong.

::: tulip.control.taxonomy.severity_at_least
::: tulip.control.taxonomy.SEVERITY_ORDER
::: tulip.control.taxonomy.AtlasTechnique
::: tulip.control.taxonomy.OwaspASI
::: tulip.control.taxonomy.OwaspLLM
::: tulip.control.taxonomy.IndicatorType
::: tulip.control.taxonomy.TaxonomyTag

## Security context — the ports

`SecurityContext` is the seam between the SDK and your estate. Each port is a
protocol, so the offline reference adapters that ship here and the adapters you
write are interchangeable, and neither is privileged.

::: tulip_security.context.SecurityContext
::: tulip_security.context.LogSource
::: tulip_security.context.EndpointSource
::: tulip_security.context.IdentitySource
::: tulip_security.context.CloudSource
::: tulip_security.context.ThreatIntelSource
::: tulip_security.context.ActionsPort

## Writing an adapter

What a vendor adapter has to implement, plus the helpers that keep one small.

::: tulip_security.adapter.SecurityAdapter
::: tulip_security.adapter.ToolAdapter
::: tulip_security.adapter.as_json
::: tulip_security.adapter.env
::: tulip_security.adapter.indicator_type
::: tulip_security.adapter.inference_claim
::: tulip_security.adapter.tool_match

## Tools for an agent

Each capability comes in two forms: a plain function you can call, and a
`@tool`-decorated version to hand an agent. `security_toolset()` returns the
whole set at once.

::: tulip_security.security_toolset

### Threat intelligence

::: tulip_security.intel.enrich_indicator
::: tulip_security.intel.enrich_indicator_tool
::: tulip_security.intel.classify_indicator
::: tulip_security.intel.enrich_to_finding

### SIEM

::: tulip_security.siem.query_siem
::: tulip_security.siem.siem_query_tool

### Endpoint detection and response

::: tulip_security.edr.list_detections
::: tulip_security.edr.list_detections_tool
::: tulip_security.edr.fetch_host_timeline
::: tulip_security.edr.fetch_host_timeline_tool
::: tulip_security.edr.isolate_host
::: tulip_security.edr.isolate_host_tool

### Scanning

::: tulip_security.scanner.scan_endpoint
::: tulip_security.scanner.scan_endpoint_tool
::: tulip_security.scanner.scan_endpoint_to_finding
::: tulip_security.scanner.scan_dependencies
::: tulip_security.scanner.scan_dependencies_tool

### AWS

`use_aws()` refuses any operation whose name does not start with one of the
`READONLY_PREFIXES` verbs (Describe, List, Get, …). It raises `PermissionError`
before any AWS call is made, and there is no override. The `use_aws_tool`
wrapper returns that refusal to the agent as a JSON object with an `error` key.
This name check is defence-in-depth: run under a read-only IAM identity (the
default profile is `tulip-security-audit`, overridable with `TULIP_AWS_PROFILE`),
because that IAM policy is what actually enforces read-only access. Writes
belong behind `admit()` or a gated tool of your own.

::: tulip_security.aws.describe_aws
::: tulip_security.aws.describe_aws_tool
::: tulip_security.aws.use_aws
::: tulip_security.aws.use_aws_tool
::: tulip_security.aws.aws_services
::: tulip_security.aws.is_readonly_operation
::: tulip_security.aws.READONLY_PREFIXES

## Fingerprinting

Identify the model behind an endpoint from response timing alone — no
cooperation from the endpoint required.

::: tulip_security.fingerprint.measure_endpoint_timing
::: tulip_security.fingerprint.fingerprint_endpoint_tool
::: tulip_security.fingerprint.default_classifier
::: tulip_security.fingerprint.fingerprint_to_finding
::: tulip_security.fingerprint.dispatch_timing_probe_reference
::: tulip_security.fingerprint.FEATURE_KEYS
::: tulip.control.findings.FingerprintClassifier
::: tulip.control.findings.FingerprintFinding
::: tulip.control.findings.FingerprintVerdict

## SOC analyst

A prebuilt agent, the report shape it produces, and the grounding pass applied
to that report.

::: tulip_security.soc.create_soc_analyst
::: tulip_security.soc.ground_report
::: tulip_security.soc.submit_posture
::: tulip_security.soc.PostureReport
::: tulip_security.soc.PostureFinding
::: tulip_security.soc.PostureEvidence
::: tulip_security.soc.SecurityControls

## Playbooks

Named sequences for the incident types that recur. Each returns a
[`Playbook`](playbooks.md) you can run or edit.

::: tulip_security.playbooks.all_playbooks
::: tulip_security.playbooks.nist_800_61_ir
::: tulip_security.playbooks.phishing_triage
::: tulip_security.playbooks.ransomware_containment
::: tulip_security.playbooks.cloud_posture_audit
