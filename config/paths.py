"""Central project paths for headless-bluearchive.

Runtime data should be supplied through CLI arguments or environment variables
in production. The defaults keep local development convenient without binding
the package to the old reverse-engineering workspace layout.
"""

from __future__ import annotations

import os
from pathlib import Path


def _env_path(name: str, default: str | Path) -> Path:
    return Path(os.environ.get(name) or str(default)).resolve()


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = _env_path("HEADLESS_BLUEARCHIVE_PROJECT_ROOT", PACKAGE_ROOT)
WORKSPACE_ROOT = _env_path("HEADLESS_BLUEARCHIVE_WORKSPACE", PROJECT_ROOT)

DEFAULT_REPORT_DIR = _env_path(
    "HEADLESS_BLUEARCHIVE_REPORT_DIR",
    WORKSPACE_ROOT / "analysis_reports" / "nexon_webview_login",
)

DEFAULT_TOOLS_DIR = _env_path("HEADLESS_BLUEARCHIVE_TOOLS_DIR", PROJECT_ROOT / "tools")
DEFAULT_EXTERNAL_DIR = _env_path("HEADLESS_BLUEARCHIVE_EXTERNAL_DIR", PROJECT_ROOT / "external")
DEFAULT_BLUEARCHIVE_CORE_PACKET_DIR = _env_path(
    "HEADLESS_BLUEARCHIVE_CORE_PACKET_DIR",
    DEFAULT_EXTERNAL_DIR / "BlueArchive_core_packet",
)
DEFAULT_NXINFACE_CONFIG_PATH = DEFAULT_BLUEARCHIVE_CORE_PACKET_DIR / "nxinface.enconfig.json"
