# Agent Server

This notebook deploys an on-call incident triage copilot as an HTTP API.
`AgentServer` wraps any Tulip `Agent` in a FastAPI app: synchronous
invoke, streaming SSE, and persisted incident threads. Auth is a single
shared bearer API key (constructor arg or `TULIP_SERVER_API_KEY`); the
presented key namespaces the thread checkpoints, so incident thread ids
can't be resumed across a different key namespace. That is what keeps two
on-call engineers sharing one server from reading each other's incidents.

Endpoints:

- `POST /invoke` — synchronous invocation.
- `POST /stream` — SSE streaming.
- `GET /threads/{tid}` — load a persisted incident thread.
- `DELETE /threads/{tid}` — drop a persisted incident thread.
- `GET /health` — health check.

When to use `AgentServer` vs `A2AServer`:

- **AgentServer**: first-party HTTP API. Persisted threads,
  single shared-key bearer auth, key-namespaced thread checkpoints. Use
  when Tulip is the system of record and clients are yours (a PagerDuty
  webhook or a deploy dashboard).
- **A2AServer**: cross-framework interop with the A2A message spec.
  Use when another framework (Strands, ADK) needs to call your Tulip
  agent.

Run it:

    # Smoke test against a TestClient (no live server, no live model):
    TULIP_MODEL_PROVIDER=mock python examples/notebook_68_agent_server.py

    # Boot a real uvicorn server on http://127.0.0.1:8000:
    TULIP_NOTEBOOK_BOOT=1 python examples/notebook_68_agent_server.py

Prerequisites:

- `pip install fastapi uvicorn`
- For the persisted thread paths: a Redis instance with `REDIS_URL`
  set. Without that env var the notebook prints what's missing and
  exits.

## Source

```python
--8<-- "examples/notebook_68_agent_server.py"
```
