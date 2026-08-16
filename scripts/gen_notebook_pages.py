#!/usr/bin/env python3
# ruff: noqa: T201
"""Scaffold a docs/notebooks/<id>.md page per notebook in the SDK cookbook.

Each scaffolded page renders:
  - H1 = "Notebook NN: <Title>"  (parsed from the .py docstring)
  - the rest of the docstring as the page body
  - a "## Source" section that includes the .py via pymdownx.snippets
    (resolved at build time against the SDK checkout — see the
    snippets ``base_path`` in mkdocs.yml)

Existing pages are SKIPPED: the checked-in pages are hand-curated, and
the raw docstring scaffold is only a starting point. Pass ``--force``
to overwrite anyway (you almost never want this).

The SDK checkout is found via ``TULIP_SDK_DIR``, falling back to
``../tulip-agents`` (the local convention) and ``.sdk`` (where the
deploy workflow checks it out). After adding a notebook to the SDK::

    python scripts/gen_notebook_pages.py
    # then edit the new docs/notebooks/<id>.md and add it to mkdocs.yml
"""

from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "notebooks"


def _sdk_examples() -> Path:
    candidates = [os.environ.get("TULIP_SDK_DIR")] if os.environ.get("TULIP_SDK_DIR") else []
    candidates += [ROOT / ".." / "tulip-agents", ROOT / ".sdk"]
    for cand in candidates:
        ex = (Path(cand) / "examples").resolve()
        if ex.is_dir():
            return ex
    sys.exit(
        "SDK checkout not found — set TULIP_SDK_DIR to a checkout of "
        "tuliplabs-ai/tulip-agents (or clone it next to this repo as "
        "../tulip-agents)."
    )


def _parse(path: Path) -> tuple[int, str, str]:
    """Return (number, title, body) parsed from the .py docstring."""
    src = path.read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(src)) or ""
    m = re.match(r"notebook_(\d+)_", path.name)
    num = int(m.group(1)) if m else 0
    first, _, rest = doc.partition("\n")
    # ``Notebook NN: Title`` — strip the leading prefix for the H1
    title_match = re.match(r"^\s*Notebook\s+\d+\s*[:.]?\s*(.+?)\.?\s*$", first)
    title = title_match.group(1) if title_match else first.strip()
    return num, title, rest.strip()


def main() -> None:
    force = "--force" in sys.argv[1:]
    examples = _sdk_examples()
    OUT.mkdir(parents=True, exist_ok=True)
    pages: list[tuple[int, str, str]] = []
    skipped = 0
    for py in sorted(examples.glob("notebook_*.py")):
        try:
            num, title, body = _parse(py)
        except SyntaxError:
            continue
        if not title:
            continue
        slug = py.stem  # e.g. notebook_14_basic_agent
        page = OUT / f"{slug}.md"
        if page.exists() and not force:
            skipped += 1
            continue
        page.write_text(
            f"# Notebook {num:02d}: {title}\n\n"
            f"{body}\n\n"
            f"## Source\n\n"
            f"```python\n"
            f'--8<-- "examples/{py.name}"\n'
            f"```\n",
            encoding="utf-8",
        )
        pages.append((num, slug, title))
    print(f"read notebooks from {examples}")
    print(f"scaffolded {len(pages)} new pages in {OUT} "
          f"({skipped} existing pages left untouched)")
    if pages:
        print()
        print("# add to mkdocs.yml under `- Notebooks:`:")
        for num, slug, title in pages:
            print(f"  - {num:02d} · {title}: notebooks/{slug}.md")


if __name__ == "__main__":
    main()
