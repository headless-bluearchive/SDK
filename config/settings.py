
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config.paths import DEFAULT_REPORT_DIR, WORKSPACE_ROOT


@dataclass(frozen=True)
class HeadlessBASettings:

    workspace_root: Path = WORKSPACE_ROOT
    report_dir: Path = DEFAULT_REPORT_DIR
    log_level: str = "INFO"
    json_logs: bool = False
