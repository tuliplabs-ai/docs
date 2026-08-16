# Agent Server

`AgentServer` is the reference way to run any Tulip `Agent` as a
service — drop in an `Agent` (a refund bot, a deploy operator, an
access-grant approver, or a SOC triage agent), and get a FastAPI app
with `/invoke`, `/stream`, and per-thread management out of the box. It
re-emits the same event stream the Python API exposes as Server-Sent
Events, gated by optional bearer-token auth.

!!! note "Single shared key — single principal"
    `AgentServer` takes **one** `api_key`. Every authenticated request
    presents that same token, so all callers hash to the **same**
    principal and share one thread namespace. The principal prefix on
    thread IDs stops an *unauthenticated* guesser and keeps thread IDs
    from colliding — it does **not** give you per-analyst or per-tenant
    isolation behind a shared key. For real multi-tenant isolation, run
    one keyed `AgentServer` instance per tenant.

```python
from tulip.server import AgentServer

server = AgentServer(
    agent=refund_agent,
    title="Refund desk",
    api_key="…",                       # bearer-token auth
)

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
```

## When to use it

| Situation | Use AgentServer? |
|---|---|
| Exposing an agent to a web/mobile UI (a support console, an ops dashboard, a SOC console) | **yes — SSE plus per-thread persistence is what you want** |
| Internal one-off task, single Python script | no — call `agent.run_sync(...)` directly |
| Embedding an agent in your own FastAPI service | possible, but consider importing `AgentServer.app` and mounting it under your existing app |
| Scaling out across many workers, one thread resumable on any of them | yes, **with** an `S3Backend` (or another shared checkpointer) so every worker sees the same thread state |

## Getting started

### 1. Wrap the refund bot

```python
from tulip.agent import Agent
from tulip.core.termination import ToolCalled, ConfidenceMet, MaxIterations
from tulip.memory.backends.file import FileCheckpointer
from tulip.server import AgentServer

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[lookup_order, check_refund_policy, issue_refund],
    system_prompt="You are a refund agent. Cite order evidence; escalate without it.",
    reflexion=True,
    checkpointer=FileCheckpointer(base_dir="./cases"),
    termination=(ToolCalled("issue_refund") & ConfidenceMet(0.9)) | MaxIterations(8),
)

server = AgentServer(agent=agent, api_key="…")
server.run(host="0.0.0.0", port=8080)
```

The SOC variant is one swap:
`tools=security_toolset(siem=True, edr=True, threat_intel=True)` (from
`tulip.security`) and a `ToolCalled("isolate_host")` terminal.

### 2. Call `/invoke` (one-shot)

```bash
curl -sS -X POST http://localhost:8080/invoke \
  -H "Authorization: Bearer $TULIP_SERVER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Refund the duplicate charge on ord-4821.", "thread_id": "ord-4821"}'
```

Returns the full `AgentResult` JSON in one response. Use this for
scheduled jobs, workflow-engine steps, and anything that doesn't render
incrementally.

### 3. Call `/stream` (Server-Sent Events)

`/stream` is a **POST** endpoint: the prompt comes from the JSON body
and the token from the `Authorization` header. The browser `EventSource`
API only issues GET requests, so it can't drive this route — use
`fetch()` + a `ReadableStream` reader and parse the `data:` frames
yourself. Each frame is `data: {json}\n\n`; the JSON carries a `type`
field (`think`, `tool_start`, `tool_complete`, `done`, `error`), and the
stream ends with a literal `data: [DONE]` frame. The route does **not**
emit named SSE events.

```javascript
const res = await fetch("/stream", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token,
  },
  body: JSON.stringify({ prompt: "Refund the duplicate charge on ord-4821.", thread_id: "ord-4821" }),
});

const reader = res.body.getReader();
const decoder = new TextDecoder();
let buf = "";
for (;;) {
  const { value, done } = await reader.read();
  if (done) break;
  buf += decoder.decode(value, { stream: true });
  const frames = buf.split("\n\n");
  buf = frames.pop();                               // keep the partial frame
  for (const frame of frames) {
    const line = frame.replace(/^data: /, "");
    if (line === "[DONE]") continue;
    const evt = JSON.parse(line);
    if (evt.type === "tool_start") {
      status.innerText = `running ${evt.tool}`;     // lookup_order, issue_refund…
    } else if (evt.type === "done") {
      output.innerText = evt.message;
    }
  }
}
```

The `data:` payload is the JSON projection of each agent event (`type`
plus its fields), derived from the same `async for event in
agent.run(...)` stream the Python API exposes.

## Endpoints

| Path | Method | Body | Returns |
|---|---|---|---|
| `/invoke` | POST | `{"prompt": "...", "thread_id": "..."}` | `InvokeResponse` JSON (`message`, `success`, `stop_reason`, `iterations`, `tool_calls`, `duration_ms`) |
| `/stream` | POST | same | `text/event-stream` SSE of `data: {json}` frames |
| `/health` | GET | — | liveness probe (200 OK) |
| `/threads/{tid}` | GET | — | thread state (requires checkpointer) |
| `/threads/{tid}` | DELETE | — | drop a thread |

There is no `/resume` route on the reference `AgentServer` — see
[Human-in-the-loop](#human-in-the-loop) below for how the in-process
interrupt/resume flow actually works.

`/docs`, `/redoc`, and `/openapi.json` are only mounted when
`debug=True` in your settings — production deployments don't expose
schema by default.

## Auth and thread scoping

- **Bearer token (opt-in).** Auth is **off by default**. Pass
  `api_key="..."` to the constructor or set `TULIP_SERVER_API_KEY` to
  turn it on; then every request must carry `Authorization: Bearer
  <token>`, constant-time compared with `hmac.compare_digest`.
- **Loopback-only fallback.** If you don't configure auth and don't
  pass `allow_unauthenticated=True`, the server warns and binds to
  loopback only — no accidental open agent endpoint on `0.0.0.0`.
- **Single-principal thread namespacing.** The principal is derived
  server-side from the presented key — `sha256(token)[:12]`, or `anon`
  when unauthenticated. Because the server holds **one** shared
  `api_key`, every authenticated caller resolves to the **same**
  principal, and thread IDs are prefixed with it (`<principal>:<tid>`).
  This prefix stops an unauthenticated peer from reading or guessing a
  thread (CWE-639, authorization bypass via user-controlled key) and
  namespaces threads per *server instance* — it
  does **not** separate two analysts sharing the same key. For
  per-tenant isolation, run one keyed `AgentServer` per tenant.

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

## Human-in-the-loop

Reads (`lookup_order`, `check_refund_policy`, `get_deploy_status`)
can auto-run. Writes that change the world — `issue_refund`,
`deploy_service`, isolating a host — should pause
for a human first. The SDK primitive for this is the in-process
`interrupt()` / `ask_user()` call: a tool calls it, the agent yields an
`InterruptEvent` and pauses, and the caller continues with
`agent.resume(response)` (see [Interrupts](interrupts.md)).

```python
from tulip.core.interrupt import interrupt

@tool
def request_human_approval(reason: str, action: str) -> str:
    """Pause the run until a human approves the pending action."""
    return interrupt({"reason": reason, "action": action})
```

!!! warning "AgentServer does not expose this over HTTP yet"
    There is **no `PendingApproval` exception** in the SDK and **no
    `/resume` endpoint** on the reference `AgentServer`. The
    interrupt/resume flow above runs in-process. Over `/stream`, an
    unexpected tool exception is caught and returned as a sanitized
    `{"type": "error", "error": "internal error", "correlation_id": ...}`
    frame (details land in the server log under that id) — it does **not**
    park a resumable case. To drive human-in-the-loop over HTTP today,
    handle `InterruptEvent` in your own wrapper around `Agent.run` /
    `Agent.resume` and add your own resume route. The
    [`tulip-gateway`](https://github.com/tuliplabs-ai/tulip-gateway)
    ships exactly this as a service — a language-neutral `/v1/admit`
    endpoint with durable approvals and approve→resume.

## Case persistence

If the underlying `Agent` has a checkpointer, the server honours
`thread_id` in the request body for cross-request continuity. Same key +
same `thread_id` → same thread, same accumulated state.

```bash
# Day 1
curl -X POST .../invoke -d '{"prompt":"Open a case for the duplicate charge on ord-4821", "thread_id":"ord-4821"}'
# Day 2 — same thread_id, the case continues
curl -X POST .../invoke -d '{"prompt":"What did we establish so far?", "thread_id":"ord-4821"}'
```

For multi-worker deployments, swap the checkpointer to one the workers
share so a thread written on one worker can be loaded on any other —
`S3Backend(bucket=..., prefix=...)` is the zero-friction path (it
implements `BaseCheckpointer` directly, so pass it straight to the
agent); the `redis_checkpointer(...)` and `postgresql_checkpointer(...)`
factories work too. See [Checkpointers](checkpointers.md).

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
| Console SSE drops mid-run (~30s) | Reverse-proxy idle timeout. Bump `proxy_read_timeout` in nginx / `idle_timeout` on the LB, or have the agent send heartbeats every ~25s. A long-running tool call is the usual trigger. |
| Threads don't persist across restarts | `FileCheckpointer` writes to disk in the working directory — ephemeral container filesystems lose state on restart. Mount a volume or move to `S3Backend`. |
| `/threads/{tid}` 404s for the right tid | Thread IDs are prefixed with the principal — `<principal>:<tid>` is what's stored. The path you pass is *your* tid; the server prefixes. A request under a different key (or unauthenticated) won't find it. |

## Source and notebook

- [`notebook_68_agent_server.py`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/examples/notebook_68_agent_server.py) — runnable wrapper plus a curl client.
- [`tulip.server`](https://github.com/tuliplabs-ai/tulip-agents/tree/main/src/tulip/server) — `AgentServer`, `InvokeRequest`, `InvokeResponse`.

## See also

- [Interrupts](interrupts.md) — the in-process `interrupt()` / `agent.resume(...)` human-in-the-loop flow.
- [Streaming](streaming.md) — the Python iterator the SSE stream is built on.
- [Events](events.md) — every event type the server re-emits.
- [Checkpointers](checkpointers.md) — picking a backend that survives restarts, keeps parked cases, and scales out.
