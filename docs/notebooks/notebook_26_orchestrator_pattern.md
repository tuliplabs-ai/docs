# Orchestrator Pattern

A privacy officer routes a data-subject request to a chosen set of
specialist agents, runs them in parallel under a semaphore, then
correlates their outputs into a single privacy assessment. Compared with
a swarm, the decision of who investigates what is centralised here
instead of emerging from capability tags — a single, auditable choke
point that constrains which systems each specialist may touch, exactly
the accountability and data-minimization posture GDPR and CCPA expect.

This notebook covers:

- `Specialist` — domain-focused agent with tools, system prompt, and a
  confidence threshold. Tulip ships pre-built ones for logs, metrics,
  traces, and code — useful evidence sources when tracing where personal
  data flows.
- `Orchestrator` — registers specialists, emits `RoutingDecision`
  objects, and runs the chosen ones concurrently behind
  `max_parallel_specialists` (an `asyncio.Semaphore`).
- `RoutingDecision` — the typed object the planner returns: which
  specialists, which sub-task per specialist, and the reasoning.
- `OrchestratorResult` — each specialist's output, the decisions
  trail, and a correlated summary.

## Prerequisites

- Agent basics.
- The swarm multi-agent notebook for the unsupervised counterpoint.

## Run

```bash
python examples/notebook_26_orchestrator_pattern.py
```

The default provider is the bundled mock model. Set `TULIP_MODEL_PROVIDER`
(openai / anthropic) and credentials to use a live model. Set
`TULIP_MODEL_PROVIDER=mock` for offline runs.

## Source

```python
--8<-- "examples/notebook_26_orchestrator_pattern.py"
```
