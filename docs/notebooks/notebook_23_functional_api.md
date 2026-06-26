# Functional API

Express a payment dispute triage workflow as decorated async functions
instead of a graph. If `StateGraph` feels like overkill for a
straight-line dispute pipeline, the functional API lets you write the
same workflow as ordinary Python: decorate the units of work with
`@task`, decorate the orchestrator with `@entrypoint`, and Tulip tracks
timing, retries, and caching behind the scenes. The scenario here is
payments operations: fetch the transaction, look up a risk score, and
assess the dispute.

What you'll see:

- `@task` — a unit of work; can declare `retry_attempts` and `cache`.
- `@entrypoint` — the top-level coroutine; tracks every task it awaits.
- `pipeline.get_result()` returns an `EntrypointResult` with per-task
  metadata.
- Same execution semantics as `StateGraph`, written imperatively.

The notebook walks through four parts: a two-task fetch-and-assess
pipeline, `@task(retry_attempts=3)` riding out a flaky payment
processor feed, `@task(cache=True)` skipping a repeated risk-score
lookup, and a `@task` wrapping a full Agent call for fraud-risk
assessment.

Runs on the same default (mock) as the rest of the notebooks:

```bash
TULIP_MODEL_ID=openai.gpt-4.1 python examples/notebook_23_functional_api.py
# or, fully offline:
TULIP_MODEL_PROVIDER=mock python examples/notebook_23_functional_api.py
```

## Source

```python
--8<-- "examples/notebook_23_functional_api.py"
```
