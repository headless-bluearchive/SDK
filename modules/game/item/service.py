from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, int_list, optional_int


class ItemService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("ItemListRequest")
        return format_item_list(payload)

    async def sell(
        self,
        *,
        target_server_ids: list[int] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("item.sell requires confirm=True")
        fields = compact_fields(
            TargetServerIds=int_list("target_server_ids", target_server_ids) or None,
        )
        return await self.request("ItemSellRequest", fields)

    async def consume(
        self,
        *,
        consume_count: int | None = None,
        target_item_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("item.consume requires confirm=True")
        fields = compact_fields(
            ConsumeCount=optional_int("consume_count", consume_count),
            TargetItemServerId=optional_int("target_item_server_id", target_item_server_id),
        )
        return await self.request("ItemConsumeRequest", fields)

    async def lock(
        self,
        *,
        is_locked: bool | None = None,
        target_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("item.lock requires confirm=True")
        fields = compact_fields(
            IsLocked=is_locked,
            TargetServerId=optional_int("target_server_id", target_server_id),
        )
        return await self.request("ItemLockRequest", fields)

    async def bulk_consume(
        self,
        *,
        consume_count: int | None = None,
        target_item_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("item.bulk_consume requires confirm=True")
        fields = compact_fields(
            ConsumeCount=optional_int("consume_count", consume_count),
            TargetItemServerId=optional_int("target_item_server_id", target_item_server_id),
        )
        return await self.request("ItemBulkConsumeRequest", fields)

    async def select_ticket(
        self,
        *,
        consume_count: int | None = None,
        select_item_unique_id: int | None = None,
        ticket_item_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("item.select_ticket requires confirm=True")
        fields = compact_fields(
            ConsumeCount=optional_int("consume_count", consume_count),
            SelectItemUniqueId=optional_int("select_item_unique_id", select_item_unique_id),
            TicketItemServerId=optional_int("ticket_item_server_id", ticket_item_server_id),
        )
        return await self.request("ItemSelectTicketRequest", fields)

    async def auto_synth(
        self,
        *,
        target_parcels: Any = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("item.auto_synth requires confirm=True")
        fields = compact_fields(
            TargetParcels=target_parcels,
        )
        return await self.request("ItemAutoSynthRequest", fields)


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
