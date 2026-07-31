# Checkpointers

State persistence between agent runs. S3-compatible object storage
(S3 / MinIO / R2 via boto3) is a production backend, alongside Redis,
PostgreSQL, MySQL, and OpenSearch.

For long-term memory (durable KV store, semantic recall), see
[Memory](memory.md). This page covers the **per-run state snapshot**
contract used by `AgentConfig.checkpointer`.

## Contract

::: tulip.memory.checkpointer.BaseCheckpointer
::: tulip.core.protocols.CheckpointerCapabilities

## Object storage

::: tulip.memory.backends.s3.S3Backend

## Other backends

The file-system, HTTP-API, and in-memory backends implement the
`BaseCheckpointer` contract natively. Redis, PostgreSQL, MySQL, and
OpenSearch ship as simple key-value backends (Pydantic models) that the
`StorageBackendAdapter` (below) wraps into the same contract — use the
factory functions rather than passing them to `AgentConfig.checkpointer`
directly.

::: tulip.memory.backends.RedisBackend
::: tulip.memory.backends.PostgreSQLBackend
::: tulip.memory.backends.MySQLBackend
::: tulip.memory.backends.opensearch.OpenSearchBackend
::: tulip.memory.backends.FileCheckpointer
::: tulip.memory.backends.HTTPCheckpointer
::: tulip.memory.backends.MemoryCheckpointer

## Adapters

`StorageBackendAdapter` wraps any of the simple key-value backends
above into the full `BaseCheckpointer` interface. For the common
backends, use the factory functions — `redis_checkpointer(...)`,
`postgresql_checkpointer(...)`, `mysql_checkpointer(...)`,
`opensearch_checkpointer(...)`, `s3_checkpointer(...)` — which build
the adapter for you.

::: tulip.memory.backends.adapters.StorageBackendAdapter
::: tulip.memory.backends.adapters.redis_checkpointer
::: tulip.memory.backends.adapters.postgresql_checkpointer
::: tulip.memory.backends.adapters.mysql_checkpointer
::: tulip.memory.backends.adapters.opensearch_checkpointer
::: tulip.memory.backends.adapters.s3_checkpointer
