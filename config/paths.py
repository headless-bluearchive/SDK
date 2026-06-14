
from __future__ import annotations

import os
from pathlib import Path


def _env_path(name: str, default: str | Path) -> Path:
    return Path(os.environ.get(name) or str(default)).resolve()


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = _env_path("HEADLESS_BLUEARCHIVE_PROJECT_ROOT", PACKAGE_ROOT)
WORKSPACE_ROOT = _env_path("HEADLESS_BLUEARCHIVE_WORKSPACE", PROJECT_ROOT)
DEFAULT_RUNTIME_DIR = _env_path("HEADLESS_BLUEARCHIVE_RUNTIME_DIR", Path.home() / ".headless-bluearchive")

DEFAULT_REPORT_DIR = _env_path(
    "HEADLESS_BLUEARCHIVE_REPORT_DIR",
    DEFAULT_RUNTIME_DIR / "reports",
)
CORE_DATA_DIR = PACKAGE_ROOT / "core" / "data"
OFFICIAL_DATA_DIR = _env_path("HEADLESS_BLUEARCHIVE_OFFICIAL_DATA_DIR", PROJECT_ROOT / "temp" / "official_data")
