from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class EchelonService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("EchelonListRequest")
        return format_echelon_list(payload)


def format_echelon_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "EchelonDBs",
        "EchelonPresetDBs",
    }
    echelons = as_list(payload.get("EchelonDBs"))
    presets = as_list(payload.get("EchelonPresetDBs"))
    return {
        "echelons": echelons,
        "presets": presets,
        "count": len(echelons),
        "preset_count": len(presets),
        "extra": extra_fields(payload, known_keys),
    }
