# Copyright 2026 The Tulip Authors
# SPDX-License-Identifier: Apache-2.0

from types import SimpleNamespace

import pytest

from hooks import build_metadata


def test_on_config_records_the_installed_sdk_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(build_metadata, "_sdk_version", lambda: "9.8.7")
    monkeypatch.delenv("TULIP_SDK_DIR", raising=False)
    config = {"extra": {"generator": False}}

    assert build_metadata.on_config(config) is config
    assert config["extra"] == {"generator": False, "sdk_version": "9.8.7", "sdk_checkout": None}


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


# ── rules that keep the site from going stale ────────────────────────────────
SDK_MAIN = "https://github.com/tuliplabs-ai/tulip-agents/blob/main/src/tulip/tools/executor.py#L21"


def test_example_model_comes_from_one_setting() -> None:
    rendered = build_metadata.on_page_markdown(
        'Agent(model="{{ tulip_example_model }}")',
        config={"extra": {"sdk_version": "dev", "example_model": "openai:some-model"}},
    )
    assert rendered == 'Agent(model="openai:some-model")'


def test_example_model_token_without_a_setting_fails_loudly() -> None:
    with pytest.raises(RuntimeError, match="extra.example_model"):
        build_metadata.on_page_markdown(
            "{{ tulip_example_model }}", config={"extra": {"sdk_version": "dev"}}
        )


def test_event_facts_come_from_the_sdk_constants(monkeypatch: pytest.MonkeyPatch) -> None:
    emit = SimpleNamespace(
        EV_A="agent.started", EV_B="agent.done", EV_C="tool.sandbox.started", NOT_AN_EVENT="x"
    )
    monkeypatch.setattr(build_metadata, "import_module", lambda _: emit)
    rendered = build_metadata.on_page_markdown(
        "{{ tulip_event_count }} events across {{ tulip_event_prefixes }}",
        config={"extra": {"sdk_version": "dev"}},
    )
    assert rendered == "0+ events across `agent.*`, `tool.*`"


def test_event_count_rounds_down_so_it_stays_true() -> None:
    assert build_metadata._event_count([f"a.{i}" for i in range(68)]) == "60+"


def test_page_without_event_tokens_does_not_import_the_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected(_: str) -> None:
        raise AssertionError("event registry should be lazy")

    monkeypatch.setattr(build_metadata, "import_module", unexpected)
    assert build_metadata.on_page_markdown("plain", config={"extra": {"sdk_version": "dev"}}) == "plain"


def test_sdk_links_pin_to_the_documented_release(tmp_path) -> None:
    (tmp_path / "src/tulip/tools").mkdir(parents=True)
    (tmp_path / "src/tulip/tools/executor.py").write_text("")
    pinned = build_metadata.pin_sdk_links(f"[x]({SDK_MAIN})", "2.16.0", tmp_path)
    assert pinned == (
        "[x](https://github.com/tuliplabs-ai/tulip-agents/blob/v2.16.0/src/tulip/tools/executor.py#L21)"
    )


def test_a_file_missing_at_the_release_stays_on_main(tmp_path) -> None:
    """A page may link a file added to main after the release; pinning it would 404."""
    assert build_metadata.pin_sdk_links(f"[x]({SDK_MAIN})", "2.16.0", tmp_path) == f"[x]({SDK_MAIN})"


def test_links_pin_without_a_checkout_to_check_against() -> None:
    assert "/blob/v2.16.0/" in build_metadata.pin_sdk_links(SDK_MAIN, "2.16.0", None)


def test_a_dev_build_has_no_tag_so_links_stay_on_main() -> None:
    assert build_metadata.pin_sdk_links(SDK_MAIN, "2.17.0.dev3", None) == SDK_MAIN


def test_links_to_the_docs_repo_itself_are_left_alone() -> None:
    link = "https://github.com/tuliplabs-ai/docs/blob/main/examples/homepage_control_demo.py"
    assert build_metadata.pin_sdk_links(link, "2.16.0", None) == link


def test_tree_links_pin_too() -> None:
    link = "https://github.com/tuliplabs-ai/tulip-agents/tree/main/examples"
    assert build_metadata.pin_sdk_links(link, "2.16.0", None).endswith("/tree/v2.16.0/examples")


def test_checkout_is_found_from_the_env_then_the_deploy_path(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TULIP_SDK_DIR", str(tmp_path))
    assert build_metadata._sdk_checkout({}) == tmp_path

    monkeypatch.delenv("TULIP_SDK_DIR")
    (tmp_path / ".sdk").mkdir()
    config = {"config_file_path": str(tmp_path / "mkdocs.yml")}
    assert build_metadata._sdk_checkout(config) == tmp_path / ".sdk"


def test_no_checkout_anywhere_is_none(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("TULIP_SDK_DIR", raising=False)
    assert build_metadata._sdk_checkout({"config_file_path": str(tmp_path / "mkdocs.yml")}) is None


def test_on_config_records_where_the_sdk_checkout_is(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(build_metadata, "_sdk_version", lambda: "2.16.0")
    monkeypatch.setenv("TULIP_SDK_DIR", str(tmp_path))
    assert build_metadata.on_config({})["extra"]["sdk_checkout"] == str(tmp_path)


def test_page_links_are_pinned_during_the_build(tmp_path) -> None:
    (tmp_path / "src/tulip/tools").mkdir(parents=True)
    (tmp_path / "src/tulip/tools/executor.py").write_text("")
    rendered = build_metadata.on_page_markdown(
        f"[x]({SDK_MAIN})",
        config={"extra": {"sdk_version": "2.16.0", "sdk_checkout": str(tmp_path)}},
    )
    assert "/blob/v2.16.0/" in rendered
