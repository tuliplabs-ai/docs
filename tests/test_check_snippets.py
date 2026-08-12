# Copyright 2026 tuliplabs
# SPDX-License-Identifier: Apache-2.0
"""Tests for the docs snippet checker.

A stub ``tulip`` package is injected into ``sys.modules`` rather than
depending on the real SDK: the test env deliberately does not install it
(``skip-install = true``), and the checker's logic is about resolving and
comparing signatures, not about any particular SDK version.

Each case below corresponds to a real class of drift the checker exists
to catch, or to a real false positive it had to learn to suppress.
"""

from __future__ import annotations

import sys
import types

import pytest
from pydantic import BaseModel

from scripts.check_snippets import (
    Problem,
    check,
    check_block,
    iter_blocks,
    main,
)


class Widget(BaseModel):
    """Pydantic model: two required fields, extra keys silently ignored."""

    name: str
    provider: str
    tags: dict[str, str] = {}


class Flexible:
    """Sets ``__signature__`` while really accepting ``**kwargs`` — the
    shape that made an earlier version of this checker report eleven
    false positives against ``Agent``."""

    __signature__ = __import__("inspect").Signature(
        [
            __import__("inspect").Parameter(
                "model", __import__("inspect").Parameter.POSITIONAL_OR_KEYWORD
            )
        ]
    )

    def __init__(self, model: str = "", **kwargs: object) -> None:
        self.model = model


def plain(alpha: int = 1, beta: int = 2) -> int:
    """Ordinary function: no ``**kwargs``, so unknown keywords are real."""
    return alpha + beta


@pytest.fixture(autouse=True)
def stub_tulip():
    """Install a fake ``tulip`` package for the duration of a test."""
    pkg = types.ModuleType("tulip")
    pkg.__path__ = []  # marks it as a package
    fake = types.ModuleType("tulip.fake")
    fake.Widget = Widget
    fake.Flexible = Flexible
    fake.plain = plain
    sys.modules["tulip"] = pkg
    sys.modules["tulip.fake"] = fake
    pkg.fake = fake
    yield
    del sys.modules["tulip"], sys.modules["tulip.fake"]


def write(tmp_path, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    return path


# --------------------------------------------------------------------- blocks


def test_extracts_python_blocks_and_ignores_other_languages(tmp_path):
    page = write(
        tmp_path,
        "p.md",
        "text\n\n```python\nx = 1\n```\n\n```bash\nnot python\n```\n\n```py\ny = 2\n```\n",
    )
    assert [src.strip() for _, src in iter_blocks(page)] == ["x = 1", "y = 2"]


def test_dedents_an_indented_fence(tmp_path):
    page = write(tmp_path, "p.md", "1. step\n\n   ```python\n   x = 1\n   ```\n")
    (_, source), = iter_blocks(page)
    assert source.strip() == "x = 1"


def test_html_comment_skips_only_the_next_block(tmp_path):
    page = write(
        tmp_path,
        "p.md",
        "<!-- docs: skip -->\n```python\nfirst = 1\n```\n\n```python\nsecond = 2\n```\n",
    )
    assert [src.strip() for _, src in iter_blocks(page)] == ["second = 2"]


def test_inline_skip_marker(tmp_path):
    page = write(tmp_path, "p.md", "```python\n# docs: skip\nwhatever = 1\n```\n")
    assert list(iter_blocks(page)) == []


# ---------------------------------------------------------------------- checks


def test_syntax_error_is_reported():
    (kind, message), = check_block("def f(:\n    pass\n")
    assert kind == "syntax"
    assert message


def test_missing_symbol_is_reported():
    problems = check_block("from tulip.fake import Nope\n")
    assert ("symbol", "tulip.fake.Nope does not exist") in problems


def test_missing_module_is_reported():
    (kind, message), = check_block("from tulip.gone import Thing\n")
    assert kind == "import"
    assert "tulip.gone" in message


def test_plain_import_of_missing_module_is_reported():
    (kind, message), = check_block("import tulip.absent\n")
    assert kind == "import"


def test_non_tulip_imports_are_ignored():
    assert check_block("import os\nfrom json import dumps\n") == []


def test_good_snippet_is_silent():
    assert check_block("from tulip.fake import plain\nplain(alpha=3)\n") == []


def test_unknown_keyword_on_a_plain_callable():
    problems = check_block("from tulip.fake import plain\nplain(gamma=1)\n")
    assert ("kwarg", "tulip.fake.plain(...) has no parameter 'gamma'") in problems


def test_var_keyword_callable_is_never_flagged():
    """The ``Agent`` false-positive regression."""
    source = "from tulip.fake import Flexible\nFlexible(model='m', anything=1, more=2)\n"
    assert check_block(source) == []


def test_pydantic_unknown_field_is_flagged_even_though_ignored():
    source = "from tulip.fake import Widget\nWidget(name='a', provider='b', nope=1)\n"
    problems = check_block(source)
    assert any("has no field 'nope'" in m for _, m in problems)


def test_pydantic_missing_required_field():
    source = "from tulip.fake import Widget\nWidget(name='a')\n"
    problems = check_block(source)
    assert ("required", "tulip.fake.Widget(...) is missing required field 'provider'") in problems


def test_pydantic_positional_or_splat_suppresses_required_check():
    """Both hide fields this checker cannot see, so it must not guess."""
    assert check_block("from tulip.fake import Widget\nWidget(**payload)\n") == []
    assert check_block("from tulip.fake import Widget\nWidget(data, name='a')\n") == []


def test_aliased_import_is_tracked():
    source = "from tulip.fake import plain as go\ngo(gamma=1)\n"
    problems = check_block(source)
    assert any("has no parameter 'gamma'" in m for _, m in problems)


def test_attribute_call_through_a_module_import():
    problems = check_block("import tulip.fake\ntulip.fake.plain(gamma=1)\n")
    assert any("has no parameter 'gamma'" in m for _, m in problems)


def test_calls_to_unbound_names_are_ignored():
    assert check_block("something_else(gamma=1)\n") == []


def test_non_callable_attribute_is_ignored():
    assert check_block("from tulip.fake import Widget\nWidget.model_fields\n") == []


# ----------------------------------------------------------------------- walk


def test_check_walks_a_tree_and_counts_parsed_blocks(tmp_path):
    write(tmp_path, "ok.md", "```python\nfrom tulip.fake import plain\nplain()\n```\n")
    write(tmp_path, "sub/bad.md", "```python\nfrom tulip.fake import Nope\n```\n")
    parsed, problems = check(tmp_path)
    assert parsed == 2
    assert [p.kind for p in problems] == ["symbol"]
    assert problems[0].path.endswith("bad.md")


def test_problem_renders_readably():
    text = str(Problem("docs/x.md", 3, "symbol", "tulip.a.B does not exist"))
    assert text == "docs/x.md: block 3: [symbol] tulip.a.B does not exist"


def test_main_returns_zero_when_clean(tmp_path, capsys):
    write(tmp_path, "p.md", "```python\nx = 1\n```\n")
    assert main(["check_snippets.py", str(tmp_path)]) == 0
    assert "no problems found" in capsys.readouterr().out


def test_main_returns_one_and_explains_the_opt_out(tmp_path, capsys):
    write(tmp_path, "p.md", "```python\nfrom tulip.fake import Nope\n```\n")
    assert main(["check_snippets.py", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "1 problem(s)" in out
    assert "docs: skip" in out


def test_main_rejects_a_missing_path(tmp_path, capsys):
    assert main(["check_snippets.py", str(tmp_path / "nope")]) == 2
    assert "no such path" in capsys.readouterr().err


# ------------------------------------------------------- resolution edge cases


def test_unresolvable_attribute_chain_is_ignored():
    """``Widget.missing(...)`` names nothing — no crash, no report."""
    assert check_block("from tulip.fake import Widget\nWidget.missing(x=1)\n") == []


def test_star_import_is_skipped():
    assert check_block("from tulip.fake import *\n") == []


def test_aliased_module_import_is_tracked():
    source = "import tulip.fake as tf\ntf.plain(gamma=1)\n"
    problems = check_block(source)
    assert any("has no parameter 'gamma'" in m for _, m in problems)


def test_non_tulip_plain_import_is_ignored():
    assert check_block("import os.path\nos.path.join(a='x')\n") == []


def test_callable_without_an_introspectable_signature_is_tolerated():
    """``inspect.signature`` raises for some C types (``dict`` is one).
    The checker must fall silent rather than crash the whole run."""
    sys.modules["tulip.fake"].opaque = dict
    try:
        assert check_block("from tulip.fake import opaque\nopaque(anything=1)\n") == []
    finally:
        del sys.modules["tulip.fake"].opaque
