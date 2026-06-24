from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_ROOT / "data"


def _load_json(name: str) -> dict[str, Any]:
    path = DATA_DIR / name
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


@lru_cache(maxsize=1)
def request_schemas() -> dict[str, Any]:
    return _load_json("request_schemas.json")


def request_schema(request_class_or_short_name: str) -> dict[str, Any]:
    schemas = request_schemas()
    if request_class_or_short_name in schemas:
        return schemas[request_class_or_short_name]
    full = request_class_or_short_name
    if not full.endswith("Request"):
        full += "Request"
    if full in schemas:
        return schemas[full]
    raise KeyError(f"unknown request schema: {request_class_or_short_name!r}")


def request_template(request_class_or_short_name: str, *, include_none: bool = False) -> dict[str, Any]:
    schema = request_schema(request_class_or_short_name)
    fields = schema.get("fields", [])
    template: dict[str, Any] = {}
    for field in fields:
        name = field.get("name")
        if not name:
            continue
        default = field.get("default", None)
        if include_none or default is not None:
            template[name] = default
    return template
