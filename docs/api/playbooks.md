# Playbooks

Structured execution plans for agents — declared step sequences with
expected tools, validation criteria, and guidance hints. Attach one
via `AgentConfig.playbook`; enforcement details below.

## Models

::: tulip.playbooks.models.Playbook
::: tulip.playbooks.models.PlaybookStep
::: tulip.playbooks.models.PlaybookPlan
::: tulip.playbooks.models.StepExecution
::: tulip.playbooks.models.StepStatus

## Loader

::: tulip.playbooks.loader.load_playbook
::: tulip.playbooks.loader.PlaybookLoader
::: tulip.playbooks.loader.PlaybookLoadError

## Enforcer

`PlaybookEnforcer` is the enforcement engine that holds the model to
the playbook's step sequence. `PlaybookEnforcerHook` is the
`HookProvider` wrapper around it, installed automatically when
`AgentConfig.playbook` is set.

::: tulip.playbooks.enforcer.PlaybookEnforcer
::: tulip.playbooks.enforcer.EnforcementResult
::: tulip.playbooks.enforcer.EnforcementViolation
::: tulip.playbooks.hook.PlaybookEnforcerHook
