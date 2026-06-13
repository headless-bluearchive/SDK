"""Database bootstrap primitives.

The current replay pipeline is stateless. This module establishes a small
standard location for future account/task/history persistence without coupling
business modules to a concrete ORM yet.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatabaseConfig:
    url: str = "sqlite:///headless-bluearchive.sqlite3"


def connect_sqlite(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)
