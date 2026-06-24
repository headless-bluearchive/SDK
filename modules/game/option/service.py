from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import compact_fields

_OPTION_KEYS = ("ArenaIsAnonymous", "CafeAllowCopy", "MainScenarioForceEnterSeriesId")


class OptionService(GameService):
    def current(self) -> dict[str, Any] | None:
        cache = self._cache()
        return dict(cache) if cache is not None else None

    async def save(
        self,
        *,
        option_db: Any = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("option.save requires confirm=True")
        fields = compact_fields(
            OptionDB=option_db,
        )
        return await self.request("OptionSaveRequest", fields)

    def _cache(self) -> dict[str, Any] | None:
        result = getattr(self._owner, "result", None)
        if result is None:
            return None
        cache = extract_option_cache(getattr(result, "options", None))
        if cache is not None:
            return cache
        session = getattr(result, "session", None)
        if isinstance(session, Mapping):
            return extract_option_cache(session.get("options"))
        return None


def extract_option_cache(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    if any(key in value for key in _OPTION_KEYS):
        return {key: value[key] for key in _OPTION_KEYS if key in value}
    nested = value.get("OptionDB")
    if isinstance(nested, Mapping):
        return {key: nested[key] for key in _OPTION_KEYS if key in nested} or None
    return None


__all__ = ["OptionService", "extract_option_cache"]
