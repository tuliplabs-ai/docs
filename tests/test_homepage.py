# Copyright 2026 The Tulip Authors
# SPDX-License-Identifier: Apache-2.0
"""The landing page states facts about code it also shows. These check they agree.

overrides/home.html carries the example files it teaches from, the line counts it
prints beside them, and the plain-text briefing served at /llms.txt. Each of those
is a claim that can drift the moment someone edits the page, and nothing else in
the build would notice.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOME = (ROOT / "overrides" / "home.html").read_text()
LLMS = (ROOT / "docs" / "llms.txt").read_text()


def _source(name: str) -> str:
    """One of the example files the page embeds for its copy buttons."""
    block = re.search(rf'<script type="text/plain" id="src-{name}">\n(.*?)</script>', HOME, re.S)
    assert block, f"the page has no embedded source named src-{name}"
    return html.unescape(block.group(1))


@pytest.mark.parametrize("step", ["01", "02", "03", "04"])
def test_the_line_count_shown_matches_the_file_shown(step: str) -> None:
    """agent.py grows chapter by chapter, and the page prints its length each time."""
    lines = len(_source(step).rstrip("\n").split("\n"))
    shown = [int(n) for n in re.findall(rf'after {step} · <span data-generated="count">(\d+)</span> lines', HOME)]
    assert shown, f"the page never prints a line count for step {step}"
    assert all(n == lines for n in shown), f"step {step}: page says {shown}, file has {lines}"


def test_the_hero_count_matches_the_first_file() -> None:
    first = len(_source("00").rstrip("\n").split("\n"))
    hero = int(re.search(r'agent\.py</span><span class="meta"><span data-generated="count">(\d+)</span> lines', HOME).group(1))
    assert hero == first, f"hero says {hero} lines, src-00 has {first}"


def test_the_whole_file_count_matches_the_last_step() -> None:
    """The hero promises a length; the last chapter has to deliver exactly it."""
    final = len(_source("05").rstrip("\n").split("\n"))
    promised = [int(n) for n in re.findall(r'this file is <a href="#whole"[^>]*><span data-generated="count">(\d+)</span> lines', HOME)]
    assert promised == [final], f"hero promises {promised} lines, agent.py ends at {final}"


def test_llms_txt_is_the_briefing_the_page_shows() -> None:
    """/llms.txt is what the page tells a coding agent to read first."""
    assert LLMS == _source("brief"), "docs/llms.txt and the briefing on the page have diverged"


def test_the_briefing_points_only_at_pages_that_exist() -> None:
    docs = ROOT / "docs"
    missing = []
    for url in re.findall(r"https://tulipagents\.ai/([\w/-]+)/", LLMS):
        if not ((docs / f"{url}.md").is_file() or (docs / url / "index.md").is_file()):
            missing.append(url)
    assert not missing, f"the briefing links pages that do not exist: {missing}"


def test_the_page_hardcodes_no_sdk_version() -> None:
    """Versions come from the build (config.extra.sdk_version), never from the page."""
    body = re.sub(r"\{#.*?#\}", "", HOME, flags=re.S)  # the authoring note may cite one
    # A bare "2.36.51" is an SVG path coordinate; a version is written as a
    # release: "v2.16.0", or "tulip-agents 2.16.0".
    assert not re.findall(r"(?:tulip-agents |\bv)\d+\.\d+\.\d+", body)
