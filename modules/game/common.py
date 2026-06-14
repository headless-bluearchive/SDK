from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def required_int(name: str, value: Any) -> int:
    result = optional_int(name, value)
    if result is None:
        raise UnsafeOperationError(f"{name} is required")
    return result


def optional_int(name: str, value: Any) -> int | None:
    if value is None:
        return None
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise UnsafeOperationError(f"{name} must be an integer") from exc
    if result < 0:
        raise UnsafeOperationError(f"{name} must not be negative")
    return result


def normalize_id_map(value: Any) -> dict[int, list[int]]:
    if not isinstance(value, dict):
        return {}
    result: dict[int, list[int]] = {}
    for raw_key, raw_items in value.items():
        key = _safe_int(raw_key)
        if key is None:
            continue
        result[key] = [
            item
            for item in (_safe_int(raw_item) for raw_item in as_list(raw_items))
            if item is not None
        ]
    return result


def extra_fields(payload: dict[str, Any], known_keys: set[str]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key not in known_keys}


def _safe_int(value: Any) -> int | None:
    try:
        result = int(value)
    except (TypeError, ValueError):
        return None
    return result if result >= 0 else None
