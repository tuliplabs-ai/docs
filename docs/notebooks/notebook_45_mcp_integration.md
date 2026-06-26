# MCP Integration

MCP (Model Context Protocol) is the open standard that lets AI
assistants call tools running in a different process — exactly how a
support desk wires its order system, help center, and billing services
into an agent without bundling them. Tulip speaks both sides of it.

- Publish a Tulip support agent as an MCP server — tools and the agent's
  own `run_agent` become MCP methods.
- Connect a Tulip agent to an external MCP server (an order system, a
  knowledge base) and use its tools as ordinary `@tool`-decorated
  callables.
- Convert tool schemas in both directions
  (`tulip_tool_to_mcp` / `mcp_tool_to_tulip`).
- Handle `tools/list` and `tools/call` requests programmatically.
- Expose a **refund-eligibility probe** as an MCP tool: a deterministic
  classifier returns an `EligibilityVerdict`, and a GSAR grounding step
  (`gsar_score` / `decide`) either ships the refund decision or abstains
  when signal coverage is too low.

The configured provider drives the agent. The MCP layer is transport-only
— the same agent works against any provider. All tool outputs are mock
data (invented order ids, fixed signals) — no live order system.

## Run it

The bundled mock model is the default; set `TULIP_MODEL_PROVIDER` for a live provider:

```bash
TULIP_MODEL_ID=openai.gpt-4.1 python examples/notebook_45_mcp_integration.py
```

Offline:

```bash
TULIP_MODEL_PROVIDER=mock python examples/notebook_45_mcp_integration.py
```

## Prerequisites

- An OpenAI or Anthropic API key, or `TULIP_MODEL_PROVIDER` set to
  `openai` / `anthropic` / `mock`.
- Optional: `pip install fastmcp` to exercise live request handling.

See <https://modelcontextprotocol.io> for the MCP specification.

## Source

```python
--8<-- "examples/notebook_45_mcp_integration.py"
```
