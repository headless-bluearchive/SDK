"""Central project paths for headlessBA.

Runtime data should be supplied through CLI arguments or environment variables
in production. The defaults keep local development convenient without binding
the package to the old reverse-engineering workspace layout.
"""

from __future__ import annotations

import os
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(os.environ.get("HEADLESSBA_PROJECT_ROOT", PACKAGE_ROOT.parents[1])).resolve()
WORKSPACE_ROOT = Path(os.environ.get("HEADLESSBA_WORKSPACE", PROJECT_ROOT)).resolve()

DEFAULT_REPORT_DIR = Path(
    os.environ.get(
        "HEADLESSBA_REPORT_DIR",
        str(WORKSPACE_ROOT / "analysis_reports" / "nexon_webview_login"),
    )
).resolve()

DEFAULT_TOOLS_DIR = Path(os.environ.get("HEADLESSBA_TOOLS_DIR", str(PROJECT_ROOT / "tools"))).resolve()
DEFAULT_EXTERNAL_DIR = Path(os.environ.get("HEADLESSBA_EXTERNAL_DIR", str(PROJECT_ROOT / "external"))).resolve()
DEFAULT_BLUEARCHIVE_CORE_PACKET_DIR = Path(
    os.environ.get(
        "HEADLESSBA_CORE_PACKET_DIR",
        str(DEFAULT_EXTERNAL_DIR / "BlueArchive_core_packet"),
    )
).resolve()
DEFAULT_NXINFACE_CONFIG_PATH = DEFAULT_BLUEARCHIVE_CORE_PACKET_DIR / "nxinface.enconfig.json"
