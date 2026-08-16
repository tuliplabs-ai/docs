# MCP — Model Context Protocol

Build a tool once — issue a refund, roll out a deploy, enrich an
IOC (indicator of compromise — an IP, domain, or file hash) — and let
any agent call it. [MCP](https://modelcontextprotocol.io)
is the wire for that: wrap a function like `lookup_order` or `issue_refund`
in an MCP server, and any MCP client (Claude Desktop, Cline, a Tulip
agent, your own tooling) invokes it without bespoke glue. The same SDK
also *consumes* existing MCP servers — a billing service, a
case-management server, a threat-intel feed — so your agent can reach
tools it didn't ship.

**The SDK speaks MCP both ways**. Most agent frameworks consume MCP
servers but don't expose their own. Round-trip means a Tulip-built
agent can be either side: pull data from a billing server *and*
serve its own refund tools back to the operator's desktop.

## When to use MCP

| You want… | Use MCP |
|---|---|
| Your SDK agent to use an external billing / case-management / threat-intel MCP server | ✓ — `MCPClient` |
| Your `lookup_order` / `issue_refund` library callable by Claude Desktop / Cline / other agents | ✓ — `TulipMCPServer` |
| Two SDK agents to share side-effecting tools across processes / machines | ✓ — works, but [A2A](multi-agent/a2a.md) is the better protocol |
| In-process multi-agent — share tools by importing | use the [tools](tools.md) directly, not MCP |
| Reproducible tests | use a mock model + plain `@tool` — MCP adds I/O |

## Getting started — consume an MCP server

### 1. Install the MCP extras

```bash
pip install "tulip-agents[mcp]"
```

### 2. Spawn the server and wrap it with `MCPClient`

```python
import asyncio
from tulip.integrations.fastmcp import MCPClient


async def main():
    # Point MCPClient at a threat-intel MCP server launched over stdio:
    ti = MCPClient(server_command=["python", "-m", "ti_feed.mcp_server"])
    await ti.connect()


asyncio.run(main())
```

`MCPClient(server_command=[...])` describes a stdio MCP server;
`await ti.connect()` spawns the subprocess, opens an MCP session over
its stdin/stdout, and prepares tool discovery. (For an HTTP server, pass
`base_url=` instead of `server_command=`.)

### 3. Pass the tools straight into an Agent

```python
from tulip.agent import Agent

# Discover the server's tools and convert them to SDK tools:
mcp_tools = ti.to_tulip_tools(await ti.list_tools())

agent = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[*mcp_tools],           # MCP tools become SDK tools
    system_prompt="Triage the alert. Enrich every indicator before you act.",
)
result = agent.run_sync("Is 198.51.100.23 a known malicious endpoint?")
```

`await ti.list_tools()` returns the server's tool descriptors; passing
them through `ti.to_tulip_tools(...)` produces SDK `Tool` objects with
full schemas, descriptions, and call-through plumbing. The agent doesn't
know they're MCP — they look like any other `@tool`.

### Side effects in the host process — use hooks, not wrappers

A common shape for MCP integrators: the *real* effect of a
side-effecting call lives in the host process (a case log, a ticketing
batch, a console command stream), not inside the tool body that
returns a string to the model. The instinct is to wrap each MCP tool
with a per-tool `@tool` that calls `_case_log().append(...)` before
returning.

Don't. Use a single `HookProvider` instead — one log over every
tool, so a post-hoc review can replay exactly what the agent did:

```python
from tulip.hooks.provider import HookPriority, HookProvider

class MCPCallLogHook(HookProvider):
    """Mirror every tool call into a case log, keyed by call id."""

    priority = HookPriority.BUSINESS_DEFAULT

    def __init__(self, call_log: list[dict]) -> None:
        self._call_log = call_log

    async def on_after_tool_call(self, event):
        if event.error is None:
            self._call_log.append({
                "id": event.tool_call_id,
                "tool": event.tool_name,
                "args": event.arguments,
                "result": event.result,
            })

agent = Agent(
    model=...,
    # every MCP-sourced tool, untouched
    tools=[*mcp_client.to_tulip_tools(await mcp_client.list_tools())],
    hooks=[MCPCallLogHook(call_log)],
)
```

One hook covers every MCP-sourced tool. The `tool_call_id` correlates
with the model's `tool_calls[].id`, so parallel enrichments don't get
mixed up. See [hooks](hooks.md#on_after_tool_call-what-the-event-carries)
for the full event surface. Note this list is a faithful trace for
replay, not a tamper-evident record — for decisions an auditor must
trust, route the action through the hash-chained
[`AuditTrail`](agentic-ai-security.md) (each entry commits to the one
before it, so editing any record breaks verification).

## Getting started — expose your tools as MCP

### 1. Wrap an agent in `TulipMCPServer`

`TulipMCPServer` exposes a Tulip **agent** (and the tools registered on
it) over MCP. Build the agent with the tools you want to publish:

```python
from tulip.agent import Agent
from tulip.integrations.fastmcp import TulipMCPServer

agent = Agent(model="anthropic:claude-sonnet-4-6", tools=[lookup_order, issue_refund])
server = TulipMCPServer(agent=agent, name="billing-tools")
```

### 2. Pick a transport

```python
server.run(transport="stdio")         # for desktop clients (default)
server.run(transport="http")          # for HTTP MCP clients
```

`run(transport="stdio")` is what Claude Desktop, Cline, and most MCP
clients expect. `run(transport="http")` runs an HTTP MCP server
(transport + JSON-RPC) that any HTTP MCP client can reach. The supported
transports are `"stdio"`, `"http"`, `"sse"`, and `"streamable-http"`.

### 3. Point a client at it

For Claude Desktop, edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "billing-tools": {
      "command": "python",
      "args": ["-m", "billing_tools.mcp_server"]
    }
  }
}
```

Restart Claude Desktop. Your `lookup_order` and `issue_refund` tools
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
| **HTTP** — JSON-RPC over POST | Networked clients. Good for a shared tool server the whole team reaches. |

### Idempotency is per-run, not cross-client

The `idempotent=True` dedup is a property of a single agent's ReAct loop
— it suppresses a *repeated* call within one run (see
[idempotency](idempotency.md)). It does **not** carry across MCP: tools
the SDK consumes from a remote MCP server are wrapped with
`idempotent=False`, and the MCP server wrapper invokes each tool
directly, so two separate clients firing the same call will each run it.
If you need exactly-once across clients, enforce it in the tool body
(e.g. an idempotency key checked against your own store).

## Round-trip example

A common shape: a support agent A consumes an external billing
MCP server, *and* exposes its own refund tools as MCP for a
case-management agent B to consume:

```python
# Agent A — consumes billing data, exposes its own refund tools
billing = MCPClient(server_command=[...])     # consumer side
await billing.connect()

agent_a = Agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[*billing.to_tulip_tools(await billing.list_tools()), lookup_order, issue_refund],
)

# Producer side — publish agent_a's own tools back over MCP.
# server.run(transport="http") blocks, so run it on its own thread/process.
refunds = TulipMCPServer(agent=agent_a, name="refunds")
refunds.run(transport="http")
```

Same `MCPClient` API on the consumer side, same `TulipMCPServer` on
the producer side, same tool definitions. The transport is an
implementation detail.

## Common gotchas

| Symptom | Likely cause |
|---|---|
| `MCP server failed to start` | The MCP server subprocess crashed before establishing the session. Run the command manually to see the error. |
| `Tool 'X' not found in MCP discovery` | The server exposes a different name than you expected. Print `[t["name"] for t in await ti.list_tools()]` to see the actual list. |
| `Schema validation failed on call` | MCP tool returned an arg type that doesn't match its declared schema. Common with hand-written MCP servers; the standard ones are fine. |
| Claude Desktop doesn't show your SDK tools | `claude_desktop_config.json` not picked up — check the file lives at the right path and Claude has been restarted. |
| Hangs on `await ti.connect()` | The MCP subprocess is waiting for input on stdin (some servers expect a handshake) or never finished its init. Run the `server_command` manually to see what it prints, and wrap `connect()` in `asyncio.wait_for(..., timeout=...)`. |

## Source and notebook

- [`tulip.integrations.fastmcp`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/src/tulip/integrations/fastmcp.py) — built on FastMCP.
- [`notebook_45_mcp_integration.py`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/examples/notebook_45_mcp_integration.py) — consumer + producer end-to-end.

## See also

- [Tools](tools.md) — the `@tool` decorator MCP wraps.
- [A2A](multi-agent/a2a.md) — purpose-built protocol for cross-process SDK-to-SDK agent meshes.
