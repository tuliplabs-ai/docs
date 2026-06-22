# Red-team a customer-support chatbot

Almost every company now ships a customer-support assistant backed by an LLM and
a knowledge base. Two questions a security team has to answer before it goes
live: can someone **inject instructions** into it (directly, or via a poisoned KB
doc), and can they make it **leak data** it was told to protect?

This notebook points Tulip at a support bot and runs the OWASP-ASI / MITRE-ATLAS
suite, then prints graded results — a ``Finding`` (the attack worked, here's the
evidence) or an ``Abstention`` (no proof, so no claim). It assesses two versions:
a *naive* bot with no trust boundary, and a *hardened* one.

It runs fully offline by simulating the bot with ``Target.from_callable``. In
production you would not simulate it — you would point ``Target.endpoint`` at the
real chat API.

Run it:
    python examples/notebook_76_redteam_support_bot.py

## Source

```python
--8<-- "examples/notebook_76_redteam_support_bot.py"
```
