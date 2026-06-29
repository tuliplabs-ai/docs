# Copyright 2026 tuliplabs
# SPDX-License-Identifier: Apache-2.0
"""Put the repo root on sys.path so the hook + script modules import as
``hooks.cache_bust`` / ``scripts.gen_notebook_pages`` (namespace packages)."""

from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
