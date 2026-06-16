from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class CharacterGearService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("CharacterGearListRequest")
        return format_character_gear_list(payload)


def format_character_gear_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "GearDBs",
        "CharacterGearDBs",
    }
    gears = as_list(payload.get("GearDBs", payload.get("CharacterGearDBs")))
    return {
        "character_gears": gears,
        "count": len(gears),
        "extra": extra_fields(payload, known_keys),
    }
