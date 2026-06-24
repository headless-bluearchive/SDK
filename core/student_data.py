from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

import httpx

from config.game import DEFAULTS
from config.paths import CORE_DATA_DIR
from utils.proxy import normalize_proxy_url

STUDENT_NAMES_CACHE = CORE_DATA_DIR / "students_cn.json"

_LOCK = asyncio.Lock()
_MEMORY_NAMES: dict[int, str] | None = None
_MEMORY_LOADED_AT = 0.0
_DEFAULT_PROXY: str | None = None


def configure_proxy(proxy: str | None) -> None:
    global _DEFAULT_PROXY
    _DEFAULT_PROXY = normalize_proxy_url(proxy) or None


async def student_names(
    *,
    refresh: bool = False,
    max_age_seconds: int | None = None,
    proxy: str | None = None,
) -> dict[int, str]:
    ttl = DEFAULTS.student_data_cache_ttl_seconds if max_age_seconds is None else max_age_seconds
    async with _LOCK:
        if not refresh and _MEMORY_NAMES is not None and _memory_is_fresh(ttl):
            return dict(_MEMORY_NAMES)

        if not refresh and _cache_is_fresh(STUDENT_NAMES_CACHE, ttl):
            return _set_memory(_load_names(STUDENT_NAMES_CACHE))

        fetched = await _fetch_names(proxy=proxy)
        if fetched:
            _save_names(STUDENT_NAMES_CACHE, fetched)
            return _set_memory(fetched)

        cached = _load_names(STUDENT_NAMES_CACHE)
        if cached:
            return _set_memory(cached)

        return _set_memory({})


async def student_name(character_id: int, *, refresh: bool = False, proxy: str | None = None) -> str:
    names = await student_names(refresh=refresh, proxy=proxy)
    return names.get(int(character_id)) or str(character_id)


def cached_student_name(character_id: int) -> str:
    names = _MEMORY_NAMES or _load_names(STUDENT_NAMES_CACHE)
    return names.get(int(character_id)) or str(character_id)


async def refresh_student_names(*, proxy: str | None = None) -> dict[int, str]:
    return await student_names(refresh=True, proxy=proxy)


def _memory_is_fresh(ttl: int) -> bool:
    if ttl <= 0:
        return True
    return time.time() - _MEMORY_LOADED_AT <= ttl


def _cache_is_fresh(path: Path, ttl: int) -> bool:
    if not path.exists():
        return False
    if ttl <= 0:
        return True
    return time.time() - path.stat().st_mtime <= ttl


async def _fetch_names(*, proxy: str | None = None) -> dict[int, str]:
    headers = {
        "User-Agent": DEFAULTS.student_data_user_agent,
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://blue-archive.io/",
    }
    resolved_proxy = normalize_proxy_url(proxy) or _DEFAULT_PROXY
    urls = [DEFAULTS.student_data_url, DEFAULTS.student_data_fallback_url]
    async with httpx.AsyncClient(
        timeout=20.0,
        follow_redirects=True,
        headers=headers,
        trust_env=False,
        proxy=resolved_proxy or None,
    ) as client:
        for url in urls:
            try:
                response = await client.get(url)
                response.raise_for_status()
                names = _extract_names(response.json())
            except (httpx.HTTPError, json.JSONDecodeError, ValueError):
                continue
            if names:
                return names
    return {}


def _extract_names(raw: Any) -> dict[int, str]:
    items = raw.items() if isinstance(raw, dict) else enumerate(raw) if isinstance(raw, list) else []
    result: dict[int, str] = {}
    for raw_key, value in items:
        if not isinstance(value, dict):
            continue
        student_id = _safe_int(value.get("Id")) or _safe_int(raw_key)
        name = _select_name(value)
        if student_id is None or not isinstance(name, str) or not name.strip():
            continue
        result[student_id] = name.strip()
    return result


def _select_name(value: dict[str, Any]) -> str | None:
    for key in ("Name", "NameCN", "NameCn", "NameZh", "NameTW", "NameTw", "NameJP", "NameJp"):
        name = value.get(key)
        if isinstance(name, str) and name.strip():
            return name.strip()
    names = value.get("Names")
    if isinstance(names, dict):
        for key in ("CN", "Cn", "zh_CN", "zh-CN", "TW", "Tw", "JP", "Jp"):
            name = names.get(key)
            if isinstance(name, str) and name.strip():
                return name.strip()
    return None


def _load_names(path: Path) -> dict[int, str]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    result: dict[int, str] = {}
    for raw_key, raw_name in raw.items():
        student_id = _safe_int(raw_key)
        if student_id is not None and isinstance(raw_name, str) and raw_name.strip():
            result[student_id] = raw_name.strip()
    return result


def _save_names(path: Path, names: dict[int, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {str(key): names[key] for key in sorted(names)}
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def _set_memory(names: dict[int, str]) -> dict[int, str]:
    global _MEMORY_LOADED_AT, _MEMORY_NAMES
    _MEMORY_NAMES = dict(names)
    _MEMORY_LOADED_AT = time.time()
    return dict(_MEMORY_NAMES)


def _safe_int(value: Any) -> int | None:
    try:
        result = int(value)
    except (TypeError, ValueError):
        return None
    return result if result >= 0 else None
