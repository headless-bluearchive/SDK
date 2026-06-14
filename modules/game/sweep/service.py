from __future__ import annotations

from typing import Any

from modules.game.base import GameService


class SweepService(GameService):
    async def preset_list(self) -> dict[str, Any]:
        payload = await self.request("ContentSweepMultiSweepPresetListRequest")
        return format_sweep_preset_list(payload)


def format_sweep_preset_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "MultiSweepPresetDBs",
    }
    return {
        "presets": _as_list(payload.get("MultiSweepPresetDBs")),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]
