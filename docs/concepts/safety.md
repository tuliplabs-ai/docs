# Safety, guardrails, and steering

Three layers cooperate inside an agent run:

1. **Validation** — typed tool arguments are JSON-schema-checked before
   the call lands. No opt-in needed.
2. **Guardrails** — content policy, PII redaction, dangerous-tool
   blocking, prompt/result length caps. Runs as a hook on the
   prompt-in / output-out boundaries.
3. **Steering** — a second model votes on every tool call before it
   fires. The judge sees the system prompt, the user goal, and the
   tool-call arguments, and emits *approve / reject / rewrite*.

Each layer plugs in independently. You can turn one on without the
others.

## When to reach for which layer

| Situation | Layer |
|---|---|
| Tool args from the model are sometimes malformed | Validation — already on; nothing to do |
| Public-facing agent — block prompt injection, SQL/command/path-traversal patterns, cap input length | `GuardrailsHook` with the default `GuardrailConfig` |
| Customer-facing answer where leaking PII (emails, SSN, credit cards, IPs) is a compliance issue | `GuardrailsHook` with PII patterns enabled |
| High-stakes tools (`isolate_host`, `block_indicator`, `delete_*`) — want a second model to sanity-check the call | `SteeringHook` with a judge model and a policy string |
| Domain restriction — *"the user came in to triage this alert, reject anything else"* | `SteeringHook` with that policy verbatim |
| Internal-only agent, trusted prompts, low-stakes tools | none of the above; default validation is enough |

## Getting started

### Guardrails — block dangerous tools and redact PII

```python
from tulip.agent import Agent
from tulip.hooks.builtin.guardrails import (
    GuardrailsHook, GuardrailConfig, GuardrailAction,
)

config = GuardrailConfig(
    block_dangerous_tools=frozenset({"shell", "exec", "rm", "drop"}),
    max_prompt_length=50_000,
    default_action=GuardrailAction.BLOCK,
)

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[query_siem, summarise],
    hooks=[GuardrailsHook(config=config)],
)
```

`GuardrailsHook` ships with sensible defaults — the empty
`GuardrailConfig()` already blocks `eval`, `exec`, `system`, `shell`,
`rm`, `delete`, `drop`, `truncate`; detects email / phone / SSN /
credit-card / IP patterns; and watches for SQL-injection,
path-traversal, and command-injection shapes in tool inputs.

### Topic and content policies — domain restriction

```python
from tulip.hooks.builtin.guardrails import (
    GuardrailsHook, TopicPolicy, ContentPolicy,
)

topic_policy = TopicPolicy(
    blocked_topics={"weapons", "hacking"},
    keywords={
        "weapons": ["gun", "rifle", "ammunition"],
        "hacking": ["exploit", "zero-day", "rootkit"],
    },
)

content_policy = ContentPolicy(
    enabled_categories={"hate_speech", "self_harm", "illegal_activity"},
)

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[...],
    hooks=[GuardrailsHook(
        config=GuardrailConfig(),
        topic_policy=topic_policy,
        content_policy=content_policy,
    )],
)
```

Both policies are simple keyword classifiers — fast, predictable,
auditable. For production-grade content moderation, swap in an
ML-backed policy (OpenAI Moderation, etc.)
behind the same `Policy.check(text) -> str | None` shape.

### Steering — a second model judges every tool call

```python
from tulip.hooks.builtin.steering import SteeringHook

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[query_siem, block_indicator, isolate_host],
    hooks=[
        SteeringHook(
            judge_model="anthropic:claude-sonnet-4-6",
            policy=(
                "The user came in to triage alert A-4271. "
                "Reject any tool call unrelated to that alert."
            ),
        ),
    ],
)
```

Before `block_indicator` or `isolate_host` fires, the judge sees the
system prompt, the user goal, and the proposed tool call. Three possible
verdicts:

- **approve** — the call goes through.
- **reject** — the call is replaced with an error the model sees,
  triggering a re-plan.
- **rewrite** — the judge can hand back modified arguments (for
  scoping a query, narrowing a block to a single indicator, etc).

Use the smallest model that gives reliable verdicts — a `mini` /
`flash` / `haiku` is usually enough.

## Validation (you don't have to do anything)

The `@tool` decorator builds a JSON schema from the function's typed
signature. Every model tool call goes through that schema before the
function body runs. Schema violations come back to the model as a
tool error so it can retry with corrected arguments — you don't have
to write any of that defensively.

```python
@tool
def isolate_host(host_id: str, incident_id: str, mode: Literal["full", "soft", "audit"]) -> dict:
    ...
```

A model call with `mode="quarantine"` is rejected before the body
runs; the model sees the typed-error message and retries with `"full"`.

## Structural guardrails — restrict the tool, not just the call

The strongest guardrail is a tool that *cannot* perform the dangerous action
in the first place. Hooks and steering inspect a call and decide; a
capability-restricted tool removes the capability, so there is nothing to
decide. The two compose — but when you can constrain the tool, do that first.

The [cloud-posture agent](cloud-posture.md) is the worked example. Its
`use_aws` tool admits an operation only if its name starts with a read verb
(`Describe` / `List` / `Get` / …), and it checks **before** any API call:

```python
from tulip.security import use_aws

use_aws("iam", "CreateUser", {"UserName": "x"})
# PermissionError: refused: iam:CreateUser is not a read-only operation.
```

The principle is **defense in depth across a trust boundary**: pair an
in-process gate (fast, explicit intent) with an out-of-process backstop that
doesn't trust your code at all —

| In-process gate | Out-of-process backstop |
|---|---|
| read-verb allowlist in `use_aws` | read-only IAM identity (`SecurityAudit` + `ViewOnlyAccess`) |
| `block_dangerous_tools` in `GuardrailsHook` | container without the binary; seccomp profile |
| SQL-shape detection in tool inputs | database role with `SELECT`-only grants |

If the gate is ever bypassed, the backstop still refuses. Neither layer trusts
the model — and the backstop doesn't trust the gate either.

## Common gotchas

| Symptom | Likely cause |
|---|---|
| PII redaction over-aggressive | The default IP regex matches version strings too. Drop `ip_address` from `pii_patterns` or tighten to a CIDR-aware pattern. |
| Steering rejects almost everything | Judge model is too strict. Tune the policy or move to a stronger model — a `nano` is often too small for nuanced judgement. |
| `GuardrailsHook` blocks a legitimate message | Inspect `hook._violations` after the run for the violation type, then add an action override (`action_overrides={"sql_injection": ALLOW}`) or trim the regex. |
| Validation error swallows a tool-arg bug | The error came back to the model — it's in the trace, look for `ToolCompleteEvent.error`. |

## Source and notebooks

- [`notebook_50_guardrails_security.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_50_guardrails_security.py) — basic guardrails.
- [`notebook_51_guardrails_advanced.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_51_guardrails_advanced.py) — topic + content + PII layered.
- [`notebook_49_steering.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_49_steering.py) — judge-model approval.
- [`tulip.hooks.builtin.guardrails`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/hooks/builtin/guardrails.py)
- [`tulip.hooks.builtin.steering`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/hooks/builtin/steering.py)

## See also

- [Hooks](hooks.md) — how `GuardrailsHook` and `SteeringHook` plug into the lifecycle.
- [Tools](tools.md) — the `@tool` decorator and its schema validation.
- [Reasoning: grounding](reasoning.md#grounding) — the answer-side analogue, claim-by-claim.
- [Cloud-posture agent](cloud-posture.md) — read-only-by-construction tools in practice.
- [Threat scenarios](threat-scenarios.md) — which guardrail defends which OWASP / ATLAS item.
