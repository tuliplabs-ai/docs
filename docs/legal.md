# Legal notices

## About &amp; disclaimer

**Tulip is maintained independently by The Tulip Authors.** The maintainers
develop the project in the open and do not claim endorsement by model providers
or integration vendors. Its licensing history is described under
[Provenance](#provenance).

Released under the Apache License, Version 2.0.

### Disclaimer of warranty and liability

The software is provided **"AS IS", without warranty of any kind**, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. **The maintainers accept no liability** for any claim, damages, or other consequence arising from the software or its use. **Use is entirely at your own risk.** You are **solely responsible** for ensuring that your use is lawful, authorized, and compliant with all applicable obligations — including security, privacy, export-control, and any policies that govern the systems and data you touch.

### Responsible use

The core `tulip-agents` package does not include offensive-capable tooling. The separate, opt-in `tulip-agents-security` package does — red-team agents, model and hardware fingerprinting, and similar reconnaissance capabilities. **Use it only against systems you own or are explicitly authorized to test.** Running these capabilities against systems you do not own or have not been authorized to assess may be unlawful.

*This page is not legal advice. Consult your own counsel.*

## License

tulip is released under the **Apache License, Version 2.0**.

Copyright 2026 The Tulip Authors.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this software except in compliance with the License. You may obtain a copy of the License at <https://www.apache.org/licenses/LICENSE-2.0>.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

### Provenance

Releases of Tulip before 1.0.0 were published under the **Universal Permissive License v1.0 (UPL-1.0)**. The project was relicensed to the Apache License, Version 2.0 at 1.0.0. Code as it stood in those releases remains available under the UPL-1.0; all changes and additions since 1.0.0 are licensed under the Apache License, Version 2.0. The [`NOTICE`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/NOTICE) file and the [`LICENSES/`](https://github.com/tuliplabs-ai/tulip-agents/tree/main/LICENSES) directory list both license texts and the files that date from the UPL-1.0 releases.

Full text: [LICENSE](https://github.com/tuliplabs-ai/tulip-agents/blob/main/LICENSE) · [NOTICE](https://github.com/tuliplabs-ai/tulip-agents/blob/main/NOTICE) · [LICENSES/](https://github.com/tuliplabs-ai/tulip-agents/tree/main/LICENSES)

---

## Third-party components

tulip uses the following open-source libraries. Their licenses are reproduced below and in full in [`THIRD_PARTY_LICENSES.txt`](https://github.com/tuliplabs-ai/tulip-agents/blob/main/THIRD_PARTY_LICENSES.txt).

### Core dependencies

| Package | License | Copyright |
|---|---|---|
| `httpx` | BSD-3-Clause | © 2019 Encode OSS Ltd. |
| `pydantic` | MIT | © Pydantic Services Inc. and contributors |
| `pydantic-settings` | MIT | © 2022 Samuel Colvin and contributors |
| `typing-extensions` | PSF | © Python Software Foundation |

### Model providers (optional)

| Package | License | Copyright |
|---|---|---|
| `openai` | MIT | © OpenAI |
| `anthropic` | MIT | © Anthropic |
| `cohere` | MIT | © Cohere |

### Observability (optional)

| Package | License | Copyright |
|---|---|---|
| `opentelemetry-api` | Apache-2.0 | © The OpenTelemetry Authors |
| `opentelemetry-sdk` | Apache-2.0 | © The OpenTelemetry Authors |
| `opentelemetry-exporter-otlp` | Apache-2.0 | © The OpenTelemetry Authors |

### MCP integration (optional)

| Package | License | Copyright |
|---|---|---|
| `mcp` | MIT | © Anthropic, PBC |

### Checkpoint / memory backends (optional)

| Package | License | Copyright |
|---|---|---|
| `redis` | MIT | © Redis Inc. |
| `asyncpg` | Apache-2.0 | © MagicStack Inc. |
| `opensearch-py` | Apache-2.0 | © OpenSearch Contributors |
