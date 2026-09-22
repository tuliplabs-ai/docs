# Copyright 2026 The Tulip Authors
# SPDX-License-Identifier: Apache-2.0
"""Build documentation facts from the SDK used for this exact build.

The deploy workflow installs a tagged SDK checkout before MkDocs runs. Reading
the imported SDK and provider registry here means an older docs build
cannot accidentally display a newer PyPI release, and provider tables cannot
drift from the routes the SDK actually registers.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any


SDK_VERSION_TOKEN = "{{ tulip_sdk_version }}"
PROVIDER_TABLE_TOKEN = "{{ tulip_provider_table }}"


def _sdk_version() -> str:
    try:
        sdk = import_module("tulip")
    except ModuleNotFoundError as exc:  # pragma: no cover - build misconfiguration
        raise RuntimeError(
            "Install the Tulip SDK used for this documentation build before running MkDocs"
        ) from exc
    return str(sdk.__version__)


def _provider_table() -> str:
    providers = import_module("tulip.models.providers")
    return str(providers.provider_table())


def on_config(config: Any) -> Any:
    extra = dict(config.get("extra", {}))
    extra["sdk_version"] = _sdk_version()
    config["extra"] = extra
    return config


def on_page_markdown(markdown: str, *, config: Any, **_: Any) -> str:
    """Expand build facts only where their explicit tokens appear."""
    sdk_version = config["extra"]["sdk_version"]
    rendered = markdown.replace(SDK_VERSION_TOKEN, sdk_version)
    if PROVIDER_TABLE_TOKEN in rendered:
        rendered = rendered.replace(PROVIDER_TABLE_TOKEN, _provider_table())
    return rendered
