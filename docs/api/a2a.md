# A2A

`tulip.a2a` implements the Agent-to-Agent protocol: one agent calls another
over HTTP, across process and organisation boundaries, without either side
importing the other's code.

Two generations of the wire format ship side by side. The `A2AV1*` types are
the v1 spec — use these for anything new. The unprefixed types are the earlier
shape, kept because deployed peers still speak it; `A2AServer` accepts both.

For the concepts, start with [the A2A protocol](../concepts/multi-agent/a2a.md)
and the [walkthrough notebook](../notebooks/notebook_28_a2a_protocol.md).

## Client and server

`A2AServer` exposes an agent over the protocol; `A2AClient` calls one. Neither
requires the other side to be built with Tulip.

::: tulip.a2a.protocol.A2AServer
::: tulip.a2a.protocol.A2AClient

## Agent cards — discovery

An agent card is what a peer publishes about itself: who runs it, what it can
do, and how to reach it. It is the only thing a caller needs before the first
request.

::: tulip.a2a.spec.AgentCard
::: tulip.a2a.spec.AgentSkill
::: tulip.a2a.spec.AgentCapabilities
::: tulip.a2a.spec.AgentProvider
::: tulip.a2a.spec.AgentInterface

## v1 protocol

The current wire format. `A2A_V1_PROTOCOL_VERSION` is the version string sent
on the wire and the one a peer negotiates against.

::: tulip.a2a.spec_v1.A2A_V1_PROTOCOL_VERSION

### Sending a message

::: tulip.a2a.spec_v1.A2AV1SendMessageRequest
::: tulip.a2a.spec_v1.A2AV1SendMessageResponse
::: tulip.a2a.spec_v1.A2AV1SendMessageConfiguration
::: tulip.a2a.spec_v1.A2AV1Message
::: tulip.a2a.spec_v1.A2AV1Part
::: tulip.a2a.spec_v1.A2AV1Role

### Tasks

A request that is not answered immediately becomes a task the caller polls or
streams. `A2AV1TaskState` is the state machine; the update events are what a
streaming caller receives.

::: tulip.a2a.spec_v1.A2AV1Task
::: tulip.a2a.spec_v1.A2AV1TaskState
::: tulip.a2a.spec_v1.A2AV1TaskStatus
::: tulip.a2a.spec_v1.A2AV1GetTaskRequest
::: tulip.a2a.spec_v1.A2AV1CancelTaskRequest
::: tulip.a2a.spec_v1.A2AV1ListTasksRequest
::: tulip.a2a.spec_v1.A2AV1ListTasksResponse

### Streaming and artifacts

::: tulip.a2a.spec_v1.A2AV1StreamResponse
::: tulip.a2a.spec_v1.A2AV1TaskStatusUpdateEvent
::: tulip.a2a.spec_v1.A2AV1TaskArtifactUpdateEvent
::: tulip.a2a.spec_v1.A2AV1Artifact

## Messages and parts

A message is a list of parts. `Part` is the discriminated union — a part is
text, a file, or structured data, and the `kind` field decides which.

::: tulip.a2a.spec.Message
::: tulip.a2a.spec.Part
::: tulip.a2a.spec.TextPart
::: tulip.a2a.spec.DataPart
::: tulip.a2a.spec.FilePart
::: tulip.a2a.spec.FileWithBytes
::: tulip.a2a.spec.FileWithUri
::: tulip.a2a.spec.Artifact

## Tasks

::: tulip.a2a.spec.Task
::: tulip.a2a.spec.TaskState
::: tulip.a2a.spec.TaskStatus
::: tulip.a2a.spec.TaskIdParams
::: tulip.a2a.spec.TaskQueryParams
::: tulip.a2a.spec.TaskStatusUpdateEvent
::: tulip.a2a.spec.TaskArtifactUpdateEvent
::: tulip.a2a.spec.MessageSendParams
::: tulip.a2a.spec.MessageSendConfiguration

## Push notifications

For work long enough that polling is the wrong shape: the peer calls you back
when the task changes.

::: tulip.a2a.spec.PushNotificationConfig
::: tulip.a2a.spec.TaskPushNotificationConfig
::: tulip.a2a.spec.PushNotificationAuthenticationInfo

## JSON-RPC envelope

The transport shapes. You rarely construct these directly — `A2AClient` and
`A2AServer` do — but an error response is worth being able to read.

::: tulip.a2a.spec.JsonRpcRequest
::: tulip.a2a.spec.JsonRpcSuccessResponse
::: tulip.a2a.spec.JsonRpcErrorResponse
::: tulip.a2a.spec.JsonRpcError

## Legacy shapes

The pre-v1 request/response types. `A2AServer` still accepts them so deployed
peers keep working; do not build anything new on them.

::: tulip.a2a.protocol.A2AMessage
::: tulip.a2a.protocol.A2ARequest
::: tulip.a2a.protocol.A2AResponse
