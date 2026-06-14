from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


_ERROR_CODES_PATH = Path(__file__).resolve().parent / "data" / "error_codes.json"


@lru_cache(maxsize=1)
def error_codes() -> dict[int, str]:
    try:
        raw = json.loads(_ERROR_CODES_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    return {int(code): str(name) for code, name in raw.items()}


def error_code_name(code: int | str | None) -> str | None:
    if code is None:
        return None
    try:
        value = int(code)
    except (TypeError, ValueError):
        return None
    return error_codes().get(value)
