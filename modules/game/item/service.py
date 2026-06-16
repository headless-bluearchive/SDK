from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class ItemService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("ItemListRequest")
        return format_item_list(payload)


def format_item_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ItemDBs",
        "ExpiryItemDBs",
        "EquipmentItemDBs",
        "CharacterGearDBs",
    }
    items = as_list(payload.get("ItemDBs"))
    expiry_items = as_list(payload.get("ExpiryItemDBs"))
    equipment = as_list(payload.get("EquipmentItemDBs"))
    gears = as_list(payload.get("CharacterGearDBs"))
    return {
        "items": items,
        "expiry_items": expiry_items,
        "equipment_items": equipment,
        "character_gears": gears,
        "count": len(items),
        "expiry_count": len(expiry_items),
        "equipment_count": len(equipment),
        "character_gear_count": len(gears),
        "extra": extra_fields(payload, known_keys),
    }
