# Copyright 2026 The Tulip Authors
# SPDX-License-Identifier: Apache-2.0

from types import SimpleNamespace

import pytest

from hooks import build_metadata


def test_on_config_records_the_installed_sdk_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(build_metadata, "_sdk_version", lambda: "9.8.7")
    config = {"extra": {"generator": False}}

    assert build_metadata.on_config(config) is config
    assert config["extra"] == {"generator": False, "sdk_version": "9.8.7"}


def test_page_tokens_expand_from_the_build_and_provider_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(build_metadata, "_provider_table", lambda: "| `openrouter` | OpenRouter |")
    markdown = "SDK {{ tulip_sdk_version }}\n\n{{ tulip_provider_table }}"

    rendered = build_metadata.on_page_markdown(
        markdown,
        config={"extra": {"sdk_version": "2.16.0"}},
    )

    assert rendered == "SDK 2.16.0\n\n| `openrouter` | OpenRouter |"


def test_page_without_provider_token_does_not_import_the_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected() -> str:
        raise AssertionError("provider registry should be lazy")

    monkeypatch.setattr(build_metadata, "_provider_table", unexpected)
    rendered = build_metadata.on_page_markdown(
        "SDK {{ tulip_sdk_version }}",
        config={"extra": {"sdk_version": "2.16.0"}},
    )

    assert rendered == "SDK 2.16.0"


def test_sdk_version_explains_a_missing_build_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing(_: str) -> None:
        raise ModuleNotFoundError("tulip")

    monkeypatch.setattr(build_metadata, "import_module", missing)
    with pytest.raises(RuntimeError, match="Install the Tulip SDK"):
        build_metadata._sdk_version()


def test_sdk_version_comes_from_the_sdk_imported_by_mkdocstrings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = SimpleNamespace(__version__="3.2.1")
    monkeypatch.setattr(build_metadata, "import_module", lambda _: module)

    assert build_metadata._sdk_version() == "3.2.1"


def test_provider_table_comes_from_the_sdk_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    module = SimpleNamespace(provider_table=lambda: "generated table")
    monkeypatch.setattr(build_metadata, "import_module", lambda _: module)

    assert build_metadata._provider_table() == "generated table"
