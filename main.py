#!/usr/bin/env python3
"""Compatibility wrapper for the headlessBA CLI."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from headlessba.cli import *  # noqa: F403,E402
from headlessba.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
