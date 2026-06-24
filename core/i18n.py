from __future__ import annotations

import json
import locale as _locale
import os
from functools import lru_cache
from pathlib import Path

_override: str | None = None
_cached_auto: str | None = None

_MESSAGES_PATH = Path(__file__).resolve().parent / "data" / "messages.json"


def _normalize(value: str | None) -> str | None:
    if not value:
        return None
    text = str(value).strip().lower().replace("_", "-")
    if not text:
        return None
    if text.startswith("zh") or text in ("cn", "chinese"):
        return "zh"
    if text.startswith("en") or text == "english":
        return "en"
    return None


def _is_zh_locale(text: str | None) -> bool:
    t = (text or "").strip().lower()
    return any(k in t for k in ("zh", "chinese", "china", "taiwan", "hong kong", "hongkong", "macau", "macao"))


def _detect_auto() -> str:
    for env in ("HLBA_LANG", "LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        norm = _normalize(os.environ.get(env))
        if norm:
            return norm
    try:
        loc = (_locale.getlocale() or (None,))[0] or ""
    except Exception:
        loc = ""
    return "zh" if _is_zh_locale(loc) else "en"


def get_language() -> str:
    global _cached_auto
    if _override is not None:
        return _override
    if _cached_auto is None:
        _cached_auto = _detect_auto()
    return _cached_auto


def set_language(lang: str | None) -> None:
    global _override, _cached_auto
    if lang is None or str(lang).strip().lower() in ("", "auto", "system"):
        _override = None
        _cached_auto = None
        return
    _override = _normalize(lang) or "en"


def tr(zh: str, en: str) -> str:
    return zh if get_language() == "zh" else en


@lru_cache(maxsize=1)
def _catalog() -> dict:
    try:
        return json.loads(_MESSAGES_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"messages": {}, "error_codes": {}}


def t(key: str, **fmt: object) -> str:
    entry = _catalog().get("messages", {}).get(key)
    if not isinstance(entry, dict):
        return key
    text = entry.get(get_language()) or entry.get("en") or next(iter(entry.values()), key)
    if not fmt:
        return text
    try:
        return text.format(**fmt)
    except (KeyError, IndexError, ValueError):
        return text


def error_code_text(code: int | str | None) -> str | None:
    from core.error_codes import error_code_name

    name = error_code_name(code)
    if code is None or get_language() != "zh":
        return name
    try:
        key = str(int(code))
    except (TypeError, ValueError):
        return name
    return _catalog().get("error_codes", {}).get(key) or name
