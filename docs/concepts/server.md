# Agent Server

`AgentServer` is the reference way to run a SOC agent as a service —
drop in a security `Agent`, get a FastAPI app with `/invoke`,
`/stream`, and per-case thread management out of the box. It re-emits
the same event stream the Python API exposes as Server-Sent Events,
gated by bearer-token auth with per-principal (per-analyst, per-tenant)
thread isolation by default. One containment-grade containment agent,
fronted for many analysts without leaking one tenant's investigation
into another's.

```python
from tulip.server import AgentServer

server = AgentServer(
    agent=soc_agent,
    title="SOC triage & response",
    api_key="…",                       # bearer-token auth
)

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
```

## When to use it

| Situation | Use AgentServer? |
|---|---|
| Exposing a triage agent to analysts via a SOC console / mobile app | **yes — SSE plus per-case thread persistence is what you want** |
| Internal one-off hunt, single Python script | no — call `agent.run_sync(...)` directly |
| Embedding triage in your own SOAR / FastAPI service | possible, but consider importing `AgentServer.app` and mounting it under your existing app |
| Scaling out across many workers, one case resumable on any of them | yes, **with** an `S3Backend` (or another shared checkpointer) so every worker sees the same investigation history |

## Getting started

### 1. Wrap a SOC agent

```python
from tulip.agent import Agent
from tulip.core.termination import ToolCalled, ConfidenceMet, MaxIterations
from tulip.memory.backends.file import FileCheckpointer
from tulip.security import security_toolset
from tulip.server import AgentServer

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=security_toolset(siem=True, edr=True, threat_intel=True),
    system_prompt="You are a SOC analyst. Cite SIEM/EDR evidence; abstain without it.",
    reflexion=True,
    checkpointer=FileCheckpointer(directory="./cases"),
    termination=(ToolCalled("isolate_host") & ConfidenceMet(0.9)) | MaxIterations(8),
)

server = AgentServer(agent=agent, api_key="…")
server.run(host="0.0.0.0", port=8080)
```

### 2. Call `/invoke` (one-shot)

```bash
curl -sS -X POST http://localhost:8080/invoke \
  -H "Authorization: Bearer $TULIP_SERVER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Triage alert A-42.", "thread_id": "case-4821"}'
```

Returns the full `AgentResult` JSON in one response. Use this for
scheduled hunts, SOAR playbook steps, and anything that doesn't render
incrementally.

### 3. Call `/stream` (Server-Sent Events)

```javascript
const es = new EventSource(
  "/stream?token=" + encodeURIComponent(token),
);

es.addEventListener("model_chunk", (e) => {
  const { content } = JSON.parse(e.data);
  output.innerText += content;
});

es.addEventListener("tool_start", (e) => {
  const { tool_name } = JSON.parse(e.data);     // query_siem, enrich_indicator, isolate_host…
  status.innerText = `running ${tool_name}`;
});

es.addEventListener("terminate", (e) => {
  // reason === "PendingApproval" → a gated write (isolate_host /
  // block_indicator) is parked, waiting on a human. See HITL below.
  es.close();
});
```

Every typed event becomes its own SSE event-name; the `data:` payload
is the JSON-serialised event. Same shape as the Python API's
`async for event in agent.run(...)`.

## Endpoints

| Path | Method | Body | Returns |
|---|---|---|---|
| `/invoke` | POST | `{"prompt": "...", "thread_id": "..."}` | full `AgentResult` JSON |
| `/stream` | POST | same | `text/event-stream` SSE of typed events |
| `/resume` | POST | `{"thread_id": "...", "response": "approved"}` | continues a case parked on `PendingApproval` |
| `/health` | GET | — | liveness probe (200 OK) |
| `/threads/{tid}` | GET | — | case history (requires checkpointer) |
| `/threads/{tid}` | DELETE | — | drop a case thread |

`/docs`, `/redoc`, and `/openapi.json` are only mounted when
`debug=True` in your settings — production deployments don't expose
schema by default.

## Auth and tenant isolation

- **Bearer token.** Pass `api_key="..."` to the constructor or set
  `TULIP_SERVER_API_KEY`. Every request must carry
  `Authorization: Bearer <token>`. Constant-time compared with
  `hmac.compare_digest`.
- **Loopback-only fallback.** If you don't configure auth and don't
  pass `allow_unauthenticated=True`, the server warns and binds to
  loopback only — no accidental open agent endpoints (each one a SIEM
  read and a containment write) on `0.0.0.0`.
- **Per-principal thread namespacing.** The principal — the analyst or
  tenant behind the bearer token — is derived server-side; case
  thread IDs are prefixed with it. One authenticated analyst can't
  read or resume another tenant's investigation by guessing the
  `thread_id` (CWE-639: authorization bypass through a user-controlled
  key). The same prefix scopes `/threads/{tid}` and `/resume`.

```python
server = AgentServer(
    agent=agent,
    api_key=os.environ["TULIP_SERVER_API_KEY"],
)
```

For unauthenticated dev:

```python
server = AgentServer(agent=agent, allow_unauthenticated=True)
server.run(host="127.0.0.1", port=8080)   # never 0.0.0.0
```

## Human-in-the-loop containment

Reads (`query_siem`, `enrich_indicator`, `lookup_hash`, `fetch_alert`)
auto-run. Writes that change the world — `isolate_host`,
`block_indicator` — should pause for a human. Gate the write tool with
your own `PendingApproval` sentinel (see
[Interrupts](interrupts.md)); the server catches it, checkpoints the
case, and ends the run with `TerminateEvent(reason="PendingApproval")`.

```python
@tool
def request_human_approval(reason: str, action: str) -> dict:
    """Park the case for an incident lead to approve."""
    raise PendingApproval(reason=reason, action=action)
```

The analyst's console reads the reason off the terminate event,
surfaces an approve/deny prompt, and resumes the parked case — scoped
to the same principal, so only this tenant can release the
containment action:

```bash
curl -X POST http://localhost:8080/resume \
  -H "Authorization: Bearer $TULIP_SERVER_API_KEY" \
  -d '{"thread_id":"case-4821", "response":"approved"}'
```

`/resume` rehydrates from the checkpointer, threads the human's answer
back into the loop, and `isolate_host` fires only after sign-off.

## Case persistence

If the underlying `Agent` has a checkpointer, the server honours
`thread_id` in the request body for cross-request continuity. Same
analyst + same `thread_id` → same case, same investigation memory.

```bash
# Day 1
curl -X POST .../invoke -d '{"prompt":"Open investigation for alert A-42", "thread_id":"case-4821"}'
# Day 2 — same thread_id, the investigation continues
curl -X POST .../invoke -d '{"prompt":"What did we establish so far?", "thread_id":"case-4821"}'
```

For multi-worker deployments, swap the checkpointer to one workers
share so a case parked for approval on one worker can be `/resume`d on
any other — `S3Backend(bucket=..., namespace=...)` is the
zero-friction path; `RedisCheckpointer` and
`PostgresCheckpointer` work too.

## Deployment

The server is plain FastAPI — deploy it however you deploy FastAPI.

| Target | Path |
|---|---|
| **Kubernetes / container services** | `docker build` and ship; gunicorn-uvicorn workers in front |
| **serverless functions** | Mangum-style adapter; cold-start friendly because `Agent` is constructed lazily |
| **Compute / VM** | `uvicorn tulip.server:app --workers 4 --port 8080` once you've defined `app` at module scope |
| **Anywhere else FastAPI runs** | …yes |

Auth, rate-limiting, and request logging are FastAPI middleware
concerns — Tulip does not own
them. Add `slowapi`, `prometheus-fastapi-instrumentator`, or whatever
your platform expects.

## Common gotchas

| Symptom | Likely cause |
|---|---|
| Server starts but binds to loopback only | No `api_key` and no `allow_unauthenticated=True`. Pick one. |
| Console SSE drops mid-investigation (~30s) | Reverse-proxy idle timeout. Bump `proxy_read_timeout` in nginx / `idle_timeout` on the LB, or have the agent send heartbeats every ~25s. A long `query_siem` is the usual trigger. |
| Cases don't persist across restarts | `FileCheckpointer` writes to disk in the working directory — ephemeral container filesystems lose parked, awaiting-approval cases. Mount a volume or move to `S3Backend`. |
| `/threads/{tid}` or `/resume` 404s for the right tid | Case IDs are scoped to the principal — `<principal>:<tid>` is what's stored. The path you pass is *your* tid; the server prefixes. Resuming under a different token won't find the parked case. |

## Source and notebook

- [`notebook_68_agent_server.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_68_agent_server.py) — runnable wrapper plus a curl client.
- [`tulip.server`](https://github.com/tuliplabs-ai/sdk-python/tree/main/src/tulip/server) — `AgentServer`, `InvokeRequest`, `InvokeResponse`.

## See also

- [Interrupts](interrupts.md) — the `PendingApproval` / `agent.resume(...)` flow `/resume` is built on.
- [Streaming](streaming.md) — the Python iterator the SSE stream is built on.
- [Events](events.md) — every event type the server re-emits.
- [Checkpointers](checkpointers.md) — picking a backend that survives restarts, keeps parked cases, and scales out.
