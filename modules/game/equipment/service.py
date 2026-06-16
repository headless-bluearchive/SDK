from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class EquipmentService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("EquipmentItemListRequest")
        return format_equipment_list(payload)


def format_equipment_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "EquipmentItemDBs",
    }
    items = as_list(payload.get("EquipmentItemDBs"))
    return {
        "equipment_items": items,
        "count": len(items),
        "extra": extra_fields(payload, known_keys),
    }
