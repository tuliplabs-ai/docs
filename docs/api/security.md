# Security

`tulip.security` is the largest module in the SDK and the one the product is
positioned on. It covers three separable jobs:

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

::: tulip.security.jobs.red_team
::: tulip.security.jobs.assure
::: tulip.security.jobs.monitor
::: tulip.security.assess.guardrail_coverage

## Naming a target

A `Target` is what to point a job at — an HTTP endpoint, a local callable, or
an agent in this process. The same target works for every job.

::: tulip.security.target.Target
::: tulip.security.target.Sender

## Probes

A probe is one adversarial attempt with a stated technique and a verdict. The
built-in set maps onto OWASP's ASI and LLM top tens; `suite_probes()` selects
by suite name, which is what `red_team(suite=...)` takes.

::: tulip.security.redteam.base.Probe
::: tulip.security.redteam.base.ProbeOutcome
::: tulip.security.redteam.all_probes
::: tulip.security.redteam.suite_probes

### The built-in probes

::: tulip.security.redteam.probes.DirectPromptInjection
::: tulip.security.redteam.probes.IndirectPromptInjection
::: tulip.security.redteam.probes.Jailbreak
::: tulip.security.redteam.probes.ExcessiveAgency
::: tulip.security.redteam.probes.SensitiveInformationDisclosure
::: tulip.security.redteam.probes.UnsandboxedCodeExecution

## Findings and evidence

[`Evidence`](control.md#tulip.security.findings.Evidence) is the shape every
finding takes — a claim, the observations behind it, and a confidence. It is
documented on the Control page, which is where a finding first matters.
`Indicator` is the atom a threat-intel lookup returns.

::: tulip.security.findings.Indicator
::: tulip.security.findings.Confidence

## Grounding — abstention over assertion

The distinctive part. `ground_finding()` returns either an `Evidence` or an
`Abstention`, never a low-confidence guess dressed as a result, and
`is_finding()` is the narrowing check that separates the two. A pipeline that
cannot tell "no evidence" from "no problem" reports clean when it is blind.

::: tulip.security.grounded.ground_finding
::: tulip.security.grounded.ground_fingerprint
::: tulip.security.grounded.is_finding
::: tulip.security.grounded.Abstention
::: tulip.security.grounded.GroundedFinding

## Verification — trying to refute

[`verify()`](control.md#tulip.security.verify.verify) runs skeptics against a
claim rather than a second model that agrees with the first. A skeptic's job is
to refute; what survives is what gets reported. It and
[`VerificationResult`](control.md#tulip.security.verify.VerificationResult) are
documented on the Control page — a policy can require a verified finding before
it admits an action, which is where they are load-bearing.

::: tulip.security.verify.Refutation
::: tulip.security.verify.Skeptic
::: tulip.security.verify.EvidenceQualitySkeptic
::: tulip.security.verify.AdversarialSkeptic

## Taxonomy

The standard technique vocabularies a finding is tagged with, and the
comparison to use on severity. [`Severity`](control.md#tulip.security.taxonomy.Severity)
itself is documented on the Control page, since a policy's `min_severity`
matches on it — but reach for `severity_at_least()` rather than comparing two
directly: it is a string enum, so `>` orders alphabetically and gets the answer
wrong.

::: tulip.security.taxonomy.severity_at_least
::: tulip.security.taxonomy.SEVERITY_ORDER
::: tulip.security.taxonomy.AtlasTechnique
::: tulip.security.taxonomy.OwaspASI
::: tulip.security.taxonomy.OwaspLLM
::: tulip.security.taxonomy.IndicatorType
::: tulip.security.taxonomy.TaxonomyTag

## Security context — the ports

`SecurityContext` is the seam between the SDK and your estate. Each port is a
protocol, so the offline reference adapters that ship here and the vendor
adapters in
[`tulip-integrations`](https://github.com/tuliplabs-ai/tulip-integrations)
are interchangeable, and neither is privileged.

::: tulip.security.context.SecurityContext
::: tulip.security.context.LogSource
::: tulip.security.context.EndpointSource
::: tulip.security.context.IdentitySource
::: tulip.security.context.CloudSource
::: tulip.security.context.ThreatIntelSource
::: tulip.security.context.ActionsPort

## Writing an adapter

What a vendor adapter has to implement, plus the helpers that keep one small.

::: tulip.security.adapter.SecurityAdapter
::: tulip.security.adapter.ToolAdapter
::: tulip.security.adapter.as_json
::: tulip.security.adapter.env
::: tulip.security.adapter.indicator_type
::: tulip.security.adapter.inference_claim
::: tulip.security.adapter.tool_match

## Tools for an agent

Each capability comes in two forms: a plain function you can call, and a
`@tool`-decorated version to hand an agent. `security_toolset()` returns the
whole set at once.

::: tulip.security.security_toolset

### Threat intelligence

::: tulip.security.intel.enrich_indicator
::: tulip.security.intel.enrich_indicator_tool
::: tulip.security.intel.classify_indicator
::: tulip.security.intel.enrich_to_finding

### SIEM

::: tulip.security.siem.query_siem
::: tulip.security.siem.siem_query_tool

### Endpoint detection and response

::: tulip.security.edr.list_detections
::: tulip.security.edr.list_detections_tool
::: tulip.security.edr.fetch_host_timeline
::: tulip.security.edr.fetch_host_timeline_tool
::: tulip.security.edr.isolate_host
::: tulip.security.edr.isolate_host_tool

### Scanning

::: tulip.security.scanner.scan_endpoint
::: tulip.security.scanner.scan_endpoint_tool
::: tulip.security.scanner.scan_endpoint_to_finding
::: tulip.security.scanner.scan_dependencies
::: tulip.security.scanner.scan_dependencies_tool

### AWS

`use_aws()` refuses anything outside `READONLY_PREFIXES` unless you say
otherwise, so the default posture is read-only.

::: tulip.security.aws.describe_aws
::: tulip.security.aws.describe_aws_tool
::: tulip.security.aws.use_aws
::: tulip.security.aws.use_aws_tool
::: tulip.security.aws.aws_services
::: tulip.security.aws.is_readonly_operation
::: tulip.security.aws.READONLY_PREFIXES

## Fingerprinting

Identify the model behind an endpoint from response timing alone — no
cooperation from the endpoint required.

::: tulip.security.fingerprint.measure_endpoint_timing
::: tulip.security.fingerprint.fingerprint_endpoint_tool
::: tulip.security.fingerprint.default_classifier
::: tulip.security.fingerprint.fingerprint_to_finding
::: tulip.security.fingerprint.dispatch_timing_probe_reference
::: tulip.security.fingerprint.FEATURE_KEYS
::: tulip.security.findings.FingerprintClassifier
::: tulip.security.findings.FingerprintFinding
::: tulip.security.findings.FingerprintVerdict

## SOC analyst

A prebuilt agent, the report shape it produces, and the grounding pass applied
to that report.

::: tulip.security.soc.create_soc_analyst
::: tulip.security.soc.ground_report
::: tulip.security.soc.submit_posture
::: tulip.security.soc.PostureReport
::: tulip.security.soc.PostureFinding
::: tulip.security.soc.PostureEvidence
::: tulip.security.soc.SecurityControls

## Playbooks

Named sequences for the incident types that recur. Each returns a
[`Playbook`](playbooks.md) you can run or edit.

::: tulip.security.playbooks.all_playbooks
::: tulip.security.playbooks.nist_800_61_ir
::: tulip.security.playbooks.phishing_triage
::: tulip.security.playbooks.ransomware_containment
::: tulip.security.playbooks.cloud_posture_audit
