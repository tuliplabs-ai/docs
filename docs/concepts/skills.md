# Skills

A skill is a reusable capability bundle the agent loads only when it
needs it. You give the agent fifty skills; it sees fifty one-line
descriptions in its system prompt and pays the cost of one. When the
model decides a skill is relevant to the current task, the full
instructions for *that one skill* enter the conversation. This is the
[AgentSkills.io](https://agentskills.io) spec — **progressive
disclosure** — and it's how you compose **broad agents** (one model,
many domain skills) without blowing the context budget on capabilities
the run won't use.

Each skill is a folder with a `SKILL.md`. Point your agent at the
parent directory and Tulip
handles the disclosure tiers:

- **L1 — catalog.** Names + one-line descriptions live in the system
  prompt. Cheap, always loaded.
- **L2 — instructions.** When the model decides a skill is relevant,
  the full `SKILL.md` body loads into the conversation.
- **L3 — resources.** Scripts, references, and assets in
  `scripts/`, `references/`, `assets/` subfolders only enter context
  when the agent reaches for them.

```python
from tulip.agent import Agent
from tulip.agent import AgentConfig
from tulip.skills import Skill

skill = Skill(
    name="release-notes",
    description="Use when drafting release notes from a list of merged changes.",
    instructions=(
        "# Release Notes Checklist\n"
        "1. Group changes: features, fixes, breaking\n"
        "2. Lead with user-visible impact, not internals\n"
        "3. Call out migration steps for breaking changes\n"
        "Report each entry as: NOTE: <description>"
    ),
)

agent = Agent(config=AgentConfig(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="You are a release manager. Use available skills.",
    skills=[skill],
))
```

## When to reach for skills

| Situation | Skills? |
|---|---|
| One agent that handles many domains (research / coding / triage) — context budget would explode if every domain's prompt is always loaded | **yes — progressive disclosure earns its keep here** |
| Capability written and edited by non-engineers (markdown, not code) | **yes** |
| Reusable across agents and projects (clone the skill folder) | **yes** |
| Single-domain agent with a fixed system prompt | no — just put the prompt in `system_prompt=` |
| Strict compliance workflow with audit-able steps | use [Playbooks](playbooks.md) instead — skills are *recommendations*, playbooks *enforce* |

## Getting started

### Programmatic — define a skill in code

```python
from tulip.skills import Skill

refund_triage = Skill(
    name="refund-triage",
    description="Use when a customer asks for a refund or disputes a charge.",
    instructions=(
        "# Refund Triage\n\n"
        "1. Pull the order with `lookup_order`; check the payment history.\n"
        "2. Check eligibility with `check_refund_policy` — window, amount cap, prior refunds.\n"
        "3. Weigh order value, account age, and dispute history.\n"
        "4. Return a recommendation (approve / deny / escalate) with the evidence.\n"
        "5. No corroborating evidence? Escalate — never guess.\n"
    ),
    allowed_tools=["lookup_order", "check_refund_policy"],
)
```

`allowed_tools` is an **advisory hint**: when the skill activates, its
allowed-tools list is surfaced to the model as an `Allowed tools: …`
line appended to the skill instructions. It is not a hard loop-level
filter — the model still sees every tool registered on the agent, so
treat `allowed_tools` as guidance, not enforcement. When you need a tool
to be genuinely unreachable, don't register it on the agent (or gate it
with a [hook](hooks.md)). A skill with `allowed_tools=None` adds no such
line.

### Filesystem — drop a `SKILL.md`

```text
skills/refund-triage/
├── SKILL.md
├── scripts/
│   └── payment_history.py
└── references/
    └── refund-policy.md
```

```markdown
---
name: refund-triage
description: Use when a customer asks for a refund or disputes a charge.
allowed-tools: lookup_order check_refund_policy
metadata:
  author: support-team
  version: 1.0
---

# Refund Triage

Pull the order, check eligibility, and weigh order value, account age,
and dispute history. Escalate when nothing corroborates the request.
Reference `references/refund-policy.md` for the caps and windows. Use
`scripts/payment_history.py` to pull related charges.
```

### Load and attach

```python
from pathlib import Path
from tulip.skills import Skill

skills = Skill.from_directory(Path("./skills"))   # all SKILL.md folders
# …or one at a time:
single = Skill.from_file("./skills/refund-triage")

agent = Agent(config=AgentConfig(model=..., skills=skills))
```

### Worked example — a contained refund-triage skill

Refund triage, scoped so the loaded skill is *steered* to read and
recommend rather than pay out — the refund itself stays a deliberate,
separately-authorised step. (Because `allowed_tools` is advisory, the
hard guarantee comes from how you register tools, not the skill — see
below.)

```python
from tulip.agent import Agent, AgentConfig
from tulip.skills import Skill

refund_triage = Skill(
    name="refund-triage",
    description="Use when a customer asks for a refund or disputes a charge.",
    instructions=(
        "# Refund triage — verify & recommend\n\n"
        "1. Pull the order with `lookup_order`; correlate charges "
        "with `lookup_customer`.\n"
        "2. Check eligibility with `check_refund_policy` — window, "
        "amount cap, prior refunds.\n"
        "3. Ground each conclusion: only report what a tool returned. "
        "No evidence -> ESCALATE, do not speculate.\n"
        "4. Recommend the refund in prose. Do NOT call `issue_refund` "
        "— that is the approver's call.\n"
    ),
    # read + check only; steers the model away from the write tool
    allowed_tools=["lookup_order", "lookup_customer", "check_refund_policy"],
)

agent = Agent(config=AgentConfig(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="You are a support agent. Cite evidence; escalate without it.",
    # register the full toolset; the skill narrows it while active
    tools=[lookup_order, lookup_customer, check_refund_policy, issue_refund],
    skills=[refund_triage],
))

result = agent.run("Customer on ord-4821 reports a duplicate charge — triage it.")
```

`issue_refund` is registered on the agent, and the skill's
instructions steer the model away from it while `refund-triage` is
loaded. Because `allowed_tools` is advisory (not a hard filter), if
you need the write to be *unreachable* during triage, don't register
`issue_refund` at all. Either way, a human (or a separate, audited
[playbook](playbooks.md)) pulls the trigger.

The security-flavored variant is the same lesson. A phishing-triage
skill steers the model to `fetch_alert` / `query_siem` /
`enrich_indicator` and ends with *"Recommend containment in prose. Do
NOT call `isolate_host` — that is the responder's call"*, over
`tools=security_toolset(allow_containment=True)` — and gates the final
verdict through `ground_finding` so an unsupported compromise claim
abstains instead of shipping. See [Security](security.md) and
[GSAR](gsar.md).

## Why progressive disclosure earns its keep

A naive "stuff every capability into the system prompt" approach
costs you tokens on every turn for skills the run never uses. With
progressive disclosure:

- The catalog is ~1 line per skill — fits 50+ skills in a few hundred
  tokens.
- The full instructions only load when the model decides the skill is
  relevant.
- Resource files (`scripts/`, `references/`, `assets/`) load only
  when the agent explicitly opens them — typically once or twice per
  run, not every turn.

For an agent with 30 skills, that's the difference between **30k
tokens of system prompt every turn** and **~600 tokens catalog +
2-3k of one skill's instructions when it's the right call**.

## Skill vs Playbook vs Tool

Easy to confuse. Quick disambiguation:

| Primitive | What it is | When to use |
|---|---|---|
| **Tool** | A typed function the model can call | The atomic unit — every primitive bottoms out in tools |
| **Skill** | A markdown bundle the model loads when relevant | Reusable capability with prose instructions |
| **Playbook** | An ordered, enforced execution plan | Compliance / audit / exact-sequence requirements |

A skill *suggests*; a playbook *enforces*. A tool is the verb both
of them call.

## Common gotchas

| Symptom | Likely cause |
|---|---|
| Skill never activates | `description` doesn't match how the user phrases the request. Rewrite it as a "use when…" sentence with the user's vocabulary. |
| All skills load every turn | Progressive disclosure only kicks in if `skills=[...]` is set — passing skills as raw text in `system_prompt=` defeats it. |
| A tool in `allowed_tools` is never called | `allowed_tools` doesn't register tools — it only adds an advisory `Allowed tools:` hint to the skill. The tool must still be registered on the agent (`tools=[...]`) for the model to call it. |
| The model called a tool *not* in `allowed_tools` | Expected — `allowed_tools` is advisory, not an enforced filter. To make a tool unreachable, don't register it (or gate it with a hook). |
| Skill resource file isn't read | The model has to ask for it. If a reference is mandatory, inline its key bullets in `instructions=` instead. |

## Source and notebook

- [`notebook_48_skills.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_48_skills.py) — programmatic and filesystem-loaded skills end-to-end.
- [`tulip.skills`](https://github.com/tuliplabs-ai/sdk-python/tree/main/src/tulip/skills) — `Skill`, `SkillsPlugin`.
- [AgentSkills.io specification](https://agentskills.io) — the format the SDK implements.

## See also

- [Playbooks](playbooks.md) — ordered, enforced plans (compliance-grade).
- [Tools](tools.md) — what skills ultimately call.
- [Prompts](prompts.md) — for single-domain agents, a system prompt is simpler.
