# Agentic AI red-teaming

The flagship of the agentic-AI-security SDK: point a ``Target`` at an AI system
and run the OWASP-ASI / MITRE-ATLAS red-team suite. Every result is a grounded
``Finding`` (the attack landed, with tool-backed evidence) or an ``Abstention``
(no evidence — so nothing is asserted).

That abstain-by-construction property is the line no other red-team tool draws:
AI scorers hallucinate vulnerabilities; Tulip refuses to ship one it cannot
evidence. The notebook points the same suite at two targets — a *vulnerable* bot
that obeys injected instructions (→ grounded Findings) and a *hardened* one that
refuses them (→ Abstentions).

Runs fully offline via ``Target.from_callable``. Point
``Target.endpoint(url, ...)`` at a real LLM / agent endpoint to red-team it for
real.

Run it:
    python examples/notebook_75_agent_red_team.py

## Source

```python
--8<-- "examples/notebook_75_agent_red_team.py"
```
