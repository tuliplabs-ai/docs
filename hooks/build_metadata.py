# Copyright 2026 The Tulip Authors
# SPDX-License-Identifier: Apache-2.0
"""Build documentation facts from the SDK used for this exact build.

The deploy workflow installs a tagged SDK checkout before MkDocs runs. Reading
the imported SDK and provider registry here means an older docs build
cannot accidentally display a newer PyPI release, and provider tables cannot
drift from the routes the SDK actually registers.
"""

from __future__ import annotations

import os
import re
from importlib import import_module
from pathlib import Path
from typing import Any


SDK_VERSION_TOKEN = "{{ tulip_sdk_version }}"
PROVIDER_TABLE_TOKEN = "{{ tulip_provider_table }}"
EXAMPLE_MODEL_TOKEN = "{{ tulip_example_model }}"
EVENT_COUNT_TOKEN = "{{ tulip_event_count }}"
EVENT_PREFIXES_TOKEN = "{{ tulip_event_prefixes }}"

_SDK_REPO = "https://github.com/tuliplabs-ai/tulip-agents/"
#: A link into the SDK repo on its moving ``main`` branch.
_SDK_MAIN_LINK = re.compile(
    r"https://github\.com/tuliplabs-ai/tulip-agents/(blob|tree)/main/([^)\s\"'#>]+)"
)
#: Only a plain release has a tag to pin to; a dev or local build does not.
_RELEASE = re.compile(r"^\d+\.\d+\.\d+$")


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


def _events() -> list[str]:
    """Every canonical event name the SDK declares, from its ``EV_*`` constants."""
    emit = import_module("tulip.observability.emit")
    return sorted(
        value for name, value in vars(emit).items()
        if name.startswith("EV_") and isinstance(value, str)
    )


def _event_count(events: list[str]) -> str:
    """Rounded down to the ten, so "60+" stays true as events are added."""
    return f"{len(events) // 10 * 10}+"


def _event_prefixes(events: list[str]) -> str:
    return ", ".join(f"`{prefix}.*`" for prefix in sorted({e.split(".")[0] for e in events}))


def _sdk_checkout(config: Any) -> Path | None:
    """The SDK repository this build installed, when one is on disk.

    The deploy workflow checks the tagged SDK out at ``.sdk``; a local build
    points ``TULIP_SDK_DIR`` at a sibling checkout.
    """
    candidates = []
    if os.environ.get("TULIP_SDK_DIR"):
        candidates.append(Path(os.environ["TULIP_SDK_DIR"]))
    if config.get("config_file_path"):
        candidates.append(Path(config["config_file_path"]).parent / ".sdk")
    return next((c for c in candidates if c.is_dir()), None)


def pin_sdk_links(markdown: str, version: str, checkout: Path | None) -> str:
    """Point SDK source links at the release this site documents.

    A ``blob/main`` link shows whatever the SDK's main branch holds today, which
    drifts from the documented release, and its ``#L`` line anchors break the
    first time the file changes. A tag never moves. A path that does not exist
    at the release (added to main after it) is left on main rather than turned
    into a 404.
    """
    if not _RELEASE.match(version):
        return markdown

    def pin(match: re.Match[str]) -> str:
        kind, path = match.group(1), match.group(2)
        if checkout is not None and not (checkout / path).exists():
            return match.group(0)
        return f"{_SDK_REPO}{kind}/v{version}/{path}"

    return _SDK_MAIN_LINK.sub(pin, markdown)


def on_config(config: Any) -> Any:
    extra = dict(config.get("extra", {}))
    extra["sdk_version"] = _sdk_version()
    checkout = _sdk_checkout(config)
    extra["sdk_checkout"] = str(checkout) if checkout else None
    config["extra"] = extra
    return config


def on_page_markdown(markdown: str, *, config: Any, **_: Any) -> str:
    """Expand build facts only where their explicit tokens appear."""
    extra = config["extra"]
    sdk_version = extra["sdk_version"]
    rendered = markdown.replace(SDK_VERSION_TOKEN, sdk_version)
    if PROVIDER_TABLE_TOKEN in rendered:
        rendered = rendered.replace(PROVIDER_TABLE_TOKEN, _provider_table())
    if EXAMPLE_MODEL_TOKEN in rendered:
        if not extra.get("example_model"):
            raise RuntimeError(
                "A page uses {{ tulip_example_model }} but mkdocs.yml sets no extra.example_model"
            )
        rendered = rendered.replace(EXAMPLE_MODEL_TOKEN, extra["example_model"])
    if EVENT_COUNT_TOKEN in rendered or EVENT_PREFIXES_TOKEN in rendered:
        events = _events()
        rendered = rendered.replace(EVENT_COUNT_TOKEN, _event_count(events))
        rendered = rendered.replace(EVENT_PREFIXES_TOKEN, _event_prefixes(events))
    checkout = extra.get("sdk_checkout")
    return pin_sdk_links(rendered, sdk_version, Path(checkout) if checkout else None)
