# Notebook 09: a chat loop — actually talking to your agent

Every other example in this suite is a batch script: it asks one thing,
prints the answer, and exits. That is the right shape for teaching a
primitive and the wrong shape for the first thing most people want to do,
which is have a conversation.

This is the missing REPL. It is deliberately small — a loop, a checkpointer,
and one ``thread_id`` — because the interesting part is not the loop, it is
that continuity comes from the checkpointer rather than from anything you
have to hold in your own code. Every turn is saved; the next turn resumes
from the saved state. Swap ``MemoryCheckpointer`` for Redis or Postgres and
the same conversation survives a restart.

Key ideas:
- A ``thread_id`` names the conversation; the checkpointer stores it.
- The loop keeps no history of its own — the agent's state is the history.
- Tool calls are printed as they happen, so you can see the agent act
  rather than infer it from the answer.
- ``/reset`` starts a fresh thread, which shows the boundary a
  ``thread_id`` draws: same agent, no shared memory.

Run it:
    .venv/bin/python examples/notebook_09_chat_loop.py

Non-interactive (CI, or just to see the shape) — the script detects a
non-tty and replays a scripted conversation instead of prompting:
    echo "" | .venv/bin/python examples/notebook_09_chat_loop.py

Live model:
    TULIP_MODEL_PROVIDER=openai TULIP_MODEL_ID=gpt-4o
    (or TULIP_MODEL_PROVIDER=anthropic, or any OpenAI-compatible
    provider: ollama, vllm, groq, together, openrouter, ...).
Set TULIP_MODEL_PROVIDER=mock for an offline run.

## Source

```python
--8<-- "examples/notebook_09_chat_loop.py"
```
