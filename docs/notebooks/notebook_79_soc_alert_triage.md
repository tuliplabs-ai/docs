# SOC alert triage with SIEM-grounded verdicts

A commodity AI SOC agent emits a verdict for every alert it sees, whether or not
it can back that verdict with evidence. Here, the SOC analyst grounds every
verdict through ``ground_report``: a proposed ``Evidence`` ships only if the
evidence the agent actually cited clears the GSAR threshold. When the agent
opines without evidence, the result is an ``Abstention`` — nothing is filed, and
the analyst knows to review it manually.

The false-positive case matters most. When the agent sees benign noise and
correctly finds no corroborating evidence, an ``Abstention`` is the right output:
don't file a finding you can't prove. Four SIEM alerts arrive in a one-hour
window — a phishing click, lateral movement, a C2 beacon, and benign process
noise — yielding three grounded ``Evidence`` results and one ``Abstention``.

Runs fully offline on mock SIEM / EDR / intel adapters. Swap them for
``security_toolset(siem=True, edr=True, threat_intel=True)`` and a real model to
run against a live environment.

Run it:
    python examples/notebook_79_soc_alert_triage.py

## Source

```python
--8<-- "examples/notebook_79_soc_alert_triage.py"
```
