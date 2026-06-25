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
    name="code-review",
    description="Use when reviewing code for bugs and security issues.",
    instructions=(
        "# Code Review Checklist\n"
        "1. Check for SQL injection\n"
        "2. Check for hardcoded credentials\n"
        "3. Check error handling\n"
        "Report findings as: FINDING: <description>"
    ),
)

agent = Agent(config=AgentConfig(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="You are a security reviewer. Use available skills.",
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

enrichment = Skill(
    name="ioc-enrichment",
    description="Use when triaging an indicator of compromise (IP, domain, URL, hash).",
    instructions=(
        "# IOC Enrichment\n\n"
        "1. Classify the indicator (IP / domain / URL / hash).\n"
        "2. Enrich it with `enrich_indicator`; for file hashes use `lookup_hash`.\n"
        "3. Weigh vendor detections, registrar age, and prior sightings.\n"
        "4. Return a verdict (malicious / suspicious / benign / unknown) with the evidence.\n"
        "5. No corroborating evidence? Abstain — return `unknown`, never guess.\n"
    ),
    allowed_tools=["enrich_indicator", "lookup_hash"],
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
skills/ioc-enrichment/
├── SKILL.md
├── scripts/
│   └── correlate.py
└── references/
    └── severity-tiers.md
```

```markdown
---
name: ioc-enrichment
description: Use when triaging an indicator of compromise (IP, domain, URL, hash).
allowed-tools: enrich_indicator lookup_hash
metadata:
  author: soc-team
  version: 1.0
---

# IOC Enrichment

Classify the indicator, enrich it, and weigh vendor detections,
registrar age, and prior sightings. Abstain to `unknown` when nothing
corroborates. Reference `references/severity-tiers.md` for the internal
score-to-severity mapping. Use `scripts/correlate.py` to pull related
alerts.
```

### Load and attach

```python
from pathlib import Path
from tulip.skills import Skill

skills = Skill.from_directory(Path("./skills"))   # all SKILL.md folders
# …or one at a time:
single = Skill.from_file("./skills/ioc-enrichment")

agent = Agent(config=AgentConfig(model=..., skills=skills))
```

### Worked example — a contained incident-response skill

Phishing-link triage, scoped so the loaded skill is *steered* to read
and enrich rather than isolate a host — containment stays a deliberate,
separately-authorised step. (Because `allowed_tools` is advisory, the
hard guarantee comes from how you register tools, not the skill — see
below.)

```python
from tulip.agent import Agent, AgentConfig
from tulip.security import security_toolset, ground_finding, is_finding, Severity
from tulip.reasoning.gsar import Claim, EvidenceType, Partition
from tulip.skills import Skill

ir_triage = Skill(
    name="ir-phishing-triage",
    description="Use when a user reports a phishing email or clicked a suspicious link.",
    instructions=(
        "# Phishing IR — detection & analysis\n\n"
        "1. Pull the alert with `fetch_alert`; correlate logins/proxy "
        "hits with `query_siem`.\n"
        "2. Enrich every URL and sender domain with `enrich_indicator`; "
        "any attachment hash with `lookup_hash`.\n"
        "3. Ground each conclusion: only report what a tool returned. "
        "No evidence -> ABSTAIN, do not speculate.\n"
        "4. Recommend containment in prose. Do NOT call `isolate_host` "
        "or `block_indicator` — that is the responder's call.\n"
    ),
    # read + enrich only; steers the model away from containment tools
    allowed_tools=["fetch_alert", "query_siem", "enrich_indicator", "lookup_hash"],
)

agent = Agent(config=AgentConfig(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="You are a SOC analyst. Cite evidence; abstain without it.",
    # register the full toolset; the skill narrows it while active
    tools=security_toolset(allow_containment=True),
    skills=[ir_triage],
))

result = agent.run("User clicked a link in alert AL-4471 — triage it.")

# Gate the verdict through GSAR: ground_finding ships an Evidence only if
# the supporting claims clear the threshold, else an Abstention. Build the
# partition from what your tools actually returned (see GSAR for details).
partition = Partition(
    grounded=[
        Claim(
            text="enrich_indicator flagged the sender domain as malicious",
            type=EvidenceType.TOOL_MATCH,
            evidence_refs=[f"tool:{ex.name}" for ex in result.tool_executions],
        ),
    ],
)
verdict = ground_finding(
    title="Phishing compromise confirmed for AL-4471",
    description="User clicked a link whose sender domain is known-malicious.",
    severity=Severity.HIGH,
    asset="AL-4471",
    remediation="Reset the user's credentials and isolate the host.",
    partition=partition,
)
if is_finding(verdict):
    print("CONFIRMED:", verdict.title, verdict.severity)
else:
    print("ABSTAINED —", verdict.reason)
```

`security_toolset(allow_containment=True)` registers `isolate_host` and
`block_indicator` on the agent, and the skill's instructions steer the
model away from them while `ir-phishing-triage` is loaded. Because
`allowed_tools` is advisory (not a hard filter), if you need containment
to be *unreachable* during triage, omit `allow_containment=True` so the
tools are never registered. Either way, a human (or a separate, audited
[playbook](playbooks.md)) pulls the trigger.

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
