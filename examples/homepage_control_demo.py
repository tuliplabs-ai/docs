#!/usr/bin/env python3
# Copyright 2026 The Tulip Authors
# SPDX-License-Identifier: Apache-2.0
"""Deterministic source for the four scenarios shown on the homepage.

The deploy callable only appends to an in-memory list. This demonstrates the
runtime's control flow without claiming that a cluster or model was contacted.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from tulip.control import Action, AdmissionError, AuditTrail, ControlPolicy, admit
from tulip.reasoning.gsar import Claim, Decision, EvidenceType, Partition, decide, gsar_score


@dataclass(frozen=True)
class DemoResult:
    scenario: str
    outcome: str
    side_effect: str
    reason: str


POLICY = ControlPolicy(
    require_verification_score=0.0,
    max_blast_radius=4,
    require_human_for=frozenset({"production"}),
    deny_for=frozenset({"prohibited"}),
)


async def evaluate_deploy(
    scenario: str,
    action: Action,
    trail: AuditTrail,
    applied: list[str],
) -> DemoResult:
    async def deploy() -> str:
        applied.append(action.environment)
        return "simulated rollout applied"

    try:
        side_effect = await admit(action, deploy, policy=POLICY, trail=trail)
    except AdmissionError as exc:
        return DemoResult(scenario, exc.decision.outcome, "not run", exc.decision.reason)
    return DemoResult(scenario, "allow", side_effect, "policy checks passed")


def evaluate_diagnosis() -> DemoResult:
    partition = Partition(
        ungrounded=[
            Claim(
                text="The deployment failed because the database is saturated",
                type=EvidenceType.INFERENCE,
            )
        ]
    )
    score = gsar_score(partition)
    outcome = decide(score)
    assert outcome is Decision.REPLAN
    return DemoResult(
        "unsupported diagnosis",
        outcome.value,
        "deployment not proposed",
        "the causal claim has no supporting evidence reference",
    )


async def run_demo() -> tuple[list[DemoResult], AuditTrail, list[str]]:
    trail = AuditTrail()
    applied: list[str] = []
    results = [
        await evaluate_deploy(
            "staging deploy",
            Action(name="deploy", asset="checkout-api", blast_radius=3, environment="staging", kind="deploy"),
            trail,
            applied,
        ),
        await evaluate_deploy(
            "production deploy",
            Action(name="deploy", asset="checkout-api", blast_radius=3, environment="production", kind="deploy"),
            trail,
            applied,
        ),
        await evaluate_deploy(
            "prohibited deploy",
            Action(
                name="deploy",
                asset="checkout-api",
                blast_radius=1,
                environment="staging",
                kind="deploy",
                tags=frozenset({"prohibited"}),
            ),
            trail,
            applied,
        ),
        evaluate_diagnosis(),
    ]
    return results, trail, applied


async def main() -> None:
    results, trail, applied = await run_demo()
    assert [result.outcome for result in results] == [
        "allow",
        "require_human",
        "deny",
        "replan",
    ]
    assert applied == ["staging"]
    assert len(trail.records()) == 3
    assert trail.verify()
    for result in results:
        print(f"{result.scenario}: {result.outcome} — {result.side_effect}")
    print(f"audit decisions: {len(trail.records())}; chain valid: {trail.verify()}")
    print(f"simulated side effects: {applied}")


if __name__ == "__main__":
    asyncio.run(main())
