# Research

Findings from building a control runtime for agents that take real actions.
Everything here comes from running code against real catalogs, real tools and
real models — the numbers are reproducible, and where a result is a single
illustration rather than a benchmark, it says so.

## Papers

**[GSAR: Typed Grounding for Hallucination Detection and Recovery in
Multi-Agent LLMs](https://arxiv.org/abs/2604.23366)** — Federico A. Kamelhar,
2026. Partitions every claim an agent makes into grounded / ungrounded /
contradicted / complementary against typed evidence, scores the partition, and
routes the result to proceed, regenerate, replan or abstain. Evaluated with
multiple LLM judges on FEVER.

Implemented in the SDK as [GSAR](../concepts/gsar.md); `ground_finding()`
returns evidence *or* an abstention, so an ungrounded claim is not something
the caller can accidentally ship.

## Findings

**[The family of harm your agent policy cannot see](policy-blindness.md)** — a
risk policy tends to encode one family of consequence and stay silent about the
others, and the silence survives code review, its own tests, validation against
the real tool catalog, and training.

Three independent instances, one of them measured: **Clusiana-Admit-4B** on
8,989 held-out rows reaches a 0.74% false-allow rate, but its errors cluster —
5.45% on execution and 5.32% on egress against 0.00% on destruction. Includes a
seven-model comparison against GPT-5 and Claude Opus/Sonnet/Haiku on identical
rows, and the reason the headline number from that comparison is misleading.
