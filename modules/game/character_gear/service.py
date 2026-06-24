from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int


class CharacterGearService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("CharacterGearListRequest")
        return format_character_gear_list(payload)

    async def unlock(
        self,
        *,
        character_server_id: int | None = None,
        slot_index: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character_gear.unlock requires confirm=True")
        fields = compact_fields(
            CharacterServerId=optional_int("character_server_id", character_server_id),
            SlotIndex=optional_int("slot_index", slot_index),
        )
        return await self.request("CharacterGearUnlockRequest", fields)

    async def tier_up(
        self,
        *,
        gear_server_id: int | None = None,
        replace_infos: Any = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character_gear.tier_up requires confirm=True")
        fields = compact_fields(
            GearServerId=optional_int("gear_server_id", gear_server_id),
            ReplaceInfos=replace_infos,
        )
        return await self.request("CharacterGearTierUpRequest", fields)


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
