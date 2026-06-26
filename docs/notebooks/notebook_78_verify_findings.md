# Verify findings — the SDK that prevents security hallucinations

A Tulip ``Evidence`` is a *claim*. Before you act on it, ``verify()`` puts it through an
independent skeptic that challenges the evidence and scores confidence. A
well-grounded finding **survives**; an unsupported or fabricated one is
**refuted** — so a hallucinated "critical" never drives a real action.

``verify()`` is framework-agnostic: it takes a Tulip ``Evidence`` *or* a
finding-shaped dict produced by any other agent (LangGraph, CrewAI, anything),
which is what lets Tulip sit **above** the stack as the verification layer. The
notebook verifies a real grounded finding (survives), a fabricated one with no
evidence (refuted), and an external finding that has references but was never
grounded (refuted).

Runs fully offline.

Run it:
    python examples/notebook_78_verify_findings.py

See also: [Agentic AI-security](../concepts/agentic-ai-security.md) ·
[SecurityContext](../concepts/security-context.md).

## Source

```python
--8<-- "examples/notebook_78_verify_findings.py"
```
