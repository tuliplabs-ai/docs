# MCP — Model Context Protocol

Build a security tool once — IOC enrichment, host isolation — and
let every part of your SOC call it. [MCP](https://modelcontextprotocol.io)
is the wire for that: wrap `lookup_ioc` and `isolate_host` in an MCP
server, and any MCP client (Claude Desktop, Cline, a Tulip SOC analyst,
your incident-response tooling) invokes them without bespoke glue. The
same SDK also *consumes* existing MCP servers — a threat-intel feed, a
case-management server — so your agent can reach tools it didn't ship.

**The SDK speaks MCP both ways**. Most agent frameworks consume MCP
servers but don't expose their own. Round-trip means a Tulip-built
triage agent can be either side: pull enrichment from a TI server *and*
serve its own containment tools back to the analyst's desktop.

## When to use MCP

| You want… | Use MCP |
|---|---|
| Your SDK agent to use an external threat-intel / case-management MCP server | ✓ — `MCPClient` |
| Your `lookup_ioc` / `isolate_host` library callable by Claude Desktop / Cline / other agents | ✓ — `TulipMCPServer` |
| Two SDK agents to share containment tools across processes / machines | ✓ — works, but [A2A](multi-agent/a2a.md) is the better protocol |
| In-process multi-agent — share tools by importing | use the [tools](tools.md) directly, not MCP |
| Reproducible tests | use a mock model + plain `@tool` — MCP adds I/O |

## Getting started — consume an MCP server

### 1. Install the MCP extras

```bash
pip install "tulip-agents[mcp]"
```

### 2. Spawn the server and wrap it with `MCPClient`

```python
from tulip.integrations.fastmcp import MCPClient

# Spawn a threat-intel MCP server as a subprocess (stdio transport):
ti = MCPClient.stdio(
    command=["python", "-m", "ti_feed.mcp_server"],
)
```

`MCPClient.stdio` runs the subprocess, opens an MCP session over its
stdin/stdout, and discovers what tools the server exposes.

### 3. Pass the tools straight into an Agent

```python
from tulip.agent import Agent
agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[*ti.tools()],          # MCP tools become SDK tools
    system_prompt="Triage the alert. Enrich every indicator before you act.",
)
result = agent.run_sync("Is 198.51.100.23 a known C2 endpoint?")
```

`ti.tools()` returns a list of SDK `Tool` objects with full
schemas, descriptions, and call-through plumbing. The agent doesn't
know they're MCP — they look like any other `@tool`.

### Side effects in the host process — use hooks, not wrappers

A common shape for MCP integrators: the *real* effect of a containment
call lives in the host process (an incident audit log, a ticketing
batch, a SOC console command stream), not inside the tool body that
returns a string to the model. The instinct is to wrap each MCP tool
with a per-tool `@tool` that calls `_audit_log().append(...)` before
returning.

Don't. Use a single `HookProvider` instead — one audit trail over every
tool, so a post-incident review can replay exactly what the agent did:

```python
from tulip.hooks.provider import HookPriority, HookProvider

class MCPAuditTrailHook(HookProvider):
    """Mirror every tool call into an incident audit log, keyed by call id."""

    priority = HookPriority.BUSINESS_DEFAULT

    def __init__(self, audit_log: list[dict]) -> None:
        self._audit_log = audit_log

    async def on_after_tool_call(self, event):
        if event.error is None:
            self._audit_log.append({
                "id": event.tool_call_id,
                "tool": event.tool_name,
                "args": event.arguments,
                "result": event.result,
            })

agent = Agent(
    model=...,
    tools=[*mcp_client.tools()],   # every MCP-sourced TI/EDR tool, untouched
    hooks=[MCPAuditTrailHook(audit_log)],
)
```

One hook covers every MCP-sourced tool. The `tool_call_id` correlates
with the model's `tool_calls[].id`, so parallel enrichments don't get
mixed up. See [hooks](hooks.md#on_after_tool_call-what-the-event-carries)
for the full event surface.

## Getting started — expose your tools as MCP

### 1. Wrap a tool list in `TulipMCPServer`

```python
from tulip.integrations.fastmcp import TulipMCPServer

server = TulipMCPServer(tools=[lookup_ioc, isolate_host])
```

### 2. Pick a transport

```python
server.run_stdio()                    # for desktop clients
server.run_http(port=7400)            # for HTTP MCP clients
```

`run_stdio()` is what Claude Desktop, Cline, and most MCP clients
expect. `run_http()` runs an HTTP MCP server (transport + JSON-RPC)
that any HTTP MCP client can reach.

### 3. Point a client at it

For Claude Desktop, edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "soc-tools": {
      "command": "python",
      "args": ["-m", "soc_tools.mcp_server"]
    }
  }
}
```

Restart Claude Desktop. Your `lookup_ioc` and `isolate_host` tools
appear in the model's tool list.

## What you get out of the box

### Schema preservation

`@tool`'s docstring + type hints become the MCP tool's name,
description, and JSON schema — losslessly. The MCP client sees the
same parameter types, defaults, and descriptions an SDK agent
would.

### Both transports

| Transport | Use case |
|---|---|
| **stdio** — process pipes | Desktop clients (Claude Desktop, Cline). The MCP server is spawned as a subprocess. |
| **HTTP** — JSON-RPC over POST | Networked clients. Good for a shared containment-tool server the whole SOC reaches. |

### Idempotency carries through

`isolate_host` tagged `@tool(idempotent=True)` keeps that semantic when
exposed via MCP — a host gets isolated exactly once even if two clients
fire the same call. The dedup happens SDK-side; the MCP client
doesn't need to know.

## Round-trip example

A common SOC shape: a triage agent A consumes an external threat-intel
MCP server, *and* exposes its own containment tools as MCP for an
incident-response agent B to consume:

```python
# Agent A — consumes threat intel, exposes its own containment tools
ti = MCPClient.stdio(command=[...])      # consumer side
containment = TulipMCPServer(            # producer side
    tools=[lookup_ioc, isolate_host],
)
containment.run_http(port=7400, in_background=True)

agent_a = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[*ti.tools(), lookup_ioc, isolate_host],
)
```

Same `MCPClient` API on the consumer side, same `TulipMCPServer` on
the producer side, same tool definitions. The transport is an
implementation detail.

## Common gotchas

| Symptom | Likely cause |
|---|---|
| `MCP server failed to start` | The MCP server subprocess crashed before establishing the session. Run the command manually to see the error. |
| `Tool 'X' not found in MCP discovery` | The server exposes a different name than you expected. Print `[t.name for t in ti.tools()]` to see the actual list. |
| `Schema validation failed on call` | MCP tool returned an arg type that doesn't match its declared schema. Common with hand-written MCP servers; the standard ones are fine. |
| Claude Desktop doesn't show your SDK tools | `claude_desktop_config.json` not picked up — check the file lives at the right path and Claude has been restarted. |
| Hangs on `MCPClient.stdio` startup | The MCP subprocess is waiting for input on stdin (some servers expect a handshake). Pass `wait_for_init=True` and a timeout. |

## Source and notebook

- [`tulip.integrations.fastmcp`](https://github.com/tuliplabs-ai/sdk-python/blob/main/src/tulip/integrations/fastmcp.py) — built on FastMCP.
- [`notebook_45_mcp_integration.py`](https://github.com/tuliplabs-ai/sdk-python/blob/main/examples/notebook_45_mcp_integration.py) — consumer + producer end-to-end.

## See also

- [Tools](tools.md) — the `@tool` decorator MCP wraps.
- [A2A](multi-agent/a2a.md) — purpose-built protocol for cross-process SDK-to-SDK agent meshes.
