from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, int_list, optional_int


class EquipmentService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("EquipmentItemListRequest")
        return format_equipment_list(payload)

    async def sell(
        self,
        *,
        target_server_ids: list[int] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("equipment.sell requires confirm=True")
        fields = compact_fields(
            TargetServerIds=int_list("target_server_ids", target_server_ids) or None,
        )
        return await self.request("EquipmentItemSellRequest", fields)

    async def equip(
        self,
        *,
        character_server_id: int | None = None,
        equipment_server_id: int | None = None,
        equipment_server_ids: list[int] | None = None,
        slot_index: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("equipment.equip requires confirm=True")
        fields = compact_fields(
            CharacterServerId=optional_int("character_server_id", character_server_id),
            EquipmentServerId=optional_int("equipment_server_id", equipment_server_id),
            EquipmentServerIds=int_list("equipment_server_ids", equipment_server_ids) or None,
            SlotIndex=optional_int("slot_index", slot_index),
        )
        return await self.request("EquipmentItemEquipRequest", fields)

    async def level_up(
        self,
        *,
        consume_request_db: Any = None,
        consume_server_ids: list[int] | None = None,
        target_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("equipment.level_up requires confirm=True")
        fields = compact_fields(
            ConsumeRequestDB=consume_request_db,
            ConsumeServerIds=int_list("consume_server_ids", consume_server_ids) or None,
            TargetServerId=optional_int("target_server_id", target_server_id),
        )
        return await self.request("EquipmentItemLevelUpRequest", fields)

    async def tier_up(
        self,
        *,
        replace_infos: Any = None,
        target_equipment_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("equipment.tier_up requires confirm=True")
        fields = compact_fields(
            ReplaceInfos=replace_infos,
            TargetEquipmentServerId=optional_int("target_equipment_server_id", target_equipment_server_id),
        )
        return await self.request("EquipmentItemTierUpRequest", fields)

    async def lock(
        self,
        *,
        is_locked: bool | None = None,
        target_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("equipment.lock requires confirm=True")
        fields = compact_fields(
            IsLocked=is_locked,
            TargetServerId=optional_int("target_server_id", target_server_id),
        )
        return await self.request("EquipmentItemLockRequest", fields)

    async def batch_growth(
        self,
        *,
        equipment_batch_growth_request_dbs: Any = None,
        gear_tier_up_request_db: Any = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("equipment.batch_growth requires confirm=True")
        fields = compact_fields(
            EquipmentBatchGrowthRequestDBs=equipment_batch_growth_request_dbs,
            GearTierUpRequestDB=gear_tier_up_request_db,
        )
        return await self.request("EquipmentBatchGrowthRequest", fields)


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
