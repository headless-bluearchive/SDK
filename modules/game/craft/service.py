from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int


class CraftService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("CraftInfoListRequest")
        return format_craft_list(payload)

    async def complete_process_all(
        self,
        *,
        confirm: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.complete_process_all requires confirm=True")
        if validate:
            await self._ensure_craft_candidates("craft_infos", "no craft process is present")
        payload = await self.request("CraftCompleteProcessAllRequest")
        return format_craft_complete_process_all(payload)

    async def shifting_complete_process_all(
        self,
        *,
        confirm: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.shifting_complete_process_all requires confirm=True")
        if validate:
            await self._ensure_craft_candidates("shifting_craft_infos", "no shifting craft process is present")
        payload = await self.request("CraftShiftingCompleteProcessAllRequest")
        return format_craft_shifting_complete_process_all(payload)

    async def select_node(
        self,
        *,
        leaf_node_index: int | None = None,
        slot_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.select_node requires confirm=True")
        fields = compact_fields(
            LeafNodeIndex=optional_int("leaf_node_index", leaf_node_index),
            SlotId=optional_int("slot_id", slot_id),
        )
        return await self.request("CraftSelectNodeRequest", fields)

    async def update_node_level(
        self,
        *,
        consume_gold_amount: int | None = None,
        consume_request_db: Any = None,
        craft_node_type: int | None = None,
        slot_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.update_node_level requires confirm=True")
        fields = compact_fields(
            ConsumeGoldAmount=optional_int("consume_gold_amount", consume_gold_amount),
            ConsumeRequestDB=consume_request_db,
            CraftNodeType=optional_int("craft_node_type", craft_node_type),
            SlotId=optional_int("slot_id", slot_id),
        )
        return await self.request("CraftUpdateNodeLevelRequest", fields)

    async def begin_process(
        self,
        *,
        slot_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.begin_process requires confirm=True")
        fields = compact_fields(
            SlotId=optional_int("slot_id", slot_id),
        )
        return await self.request("CraftBeginProcessRequest", fields)

    async def complete_process(
        self,
        *,
        slot_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.complete_process requires confirm=True")
        fields = compact_fields(
            SlotId=optional_int("slot_id", slot_id),
        )
        return await self.request("CraftCompleteProcessRequest", fields)

    async def reward(
        self,
        *,
        slot_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.reward requires confirm=True")
        fields = compact_fields(
            SlotId=optional_int("slot_id", slot_id),
        )
        return await self.request("CraftRewardRequest", fields)

    async def shifting_begin_process(
        self,
        *,
        consume_request_db: Any = None,
        recipe_id: int | None = None,
        slot_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.shifting_begin_process requires confirm=True")
        fields = compact_fields(
            ConsumeRequestDB=consume_request_db,
            RecipeId=optional_int("recipe_id", recipe_id),
            SlotId=optional_int("slot_id", slot_id),
        )
        return await self.request("CraftShiftingBeginProcessRequest", fields)

    async def shifting_complete_process(
        self,
        *,
        slot_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.shifting_complete_process requires confirm=True")
        fields = compact_fields(
            SlotId=optional_int("slot_id", slot_id),
        )
        return await self.request("CraftShiftingCompleteProcessRequest", fields)

    async def shifting_reward(
        self,
        *,
        slot_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.shifting_reward requires confirm=True")
        fields = compact_fields(
            SlotId=optional_int("slot_id", slot_id),
        )
        return await self.request("CraftShiftingRewardRequest", fields)

    async def auto_begin_process(
        self,
        *,
        count: int | None = None,
        preset_index: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.auto_begin_process requires confirm=True")
        fields = compact_fields(
            Count=optional_int("count", count),
            PresetIndex=optional_int("preset_index", preset_index),
        )
        return await self.request("CraftAutoBeginProcessRequest", fields)

    async def reward_all(
        self,
        *,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.reward_all requires confirm=True")
        return await self.request("CraftRewardAllRequest")

    async def shifting_reward_all(
        self,
        *,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.shifting_reward_all requires confirm=True")
        return await self.request("CraftShiftingRewardAllRequest")

    async def save_preset(
        self,
        *,
        preset_slot_db: Any = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.save_preset requires confirm=True")
        fields = compact_fields(
            PresetSlotDB=preset_slot_db,
        )
        return await self.request("CraftSavePresetRequest", fields)

    async def save_preset_name(
        self,
        *,
        preset_index: int | None = None,
        preset_name: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("craft.save_preset_name requires confirm=True")
        fields = compact_fields(
            PresetIndex=optional_int("preset_index", preset_index),
            PresetName=str(preset_name) if preset_name is not None else None,
        )
        return await self.request("CraftSavePresetNameRequest", fields)

    async def _ensure_craft_candidates(self, key: str, message: str) -> None:
        state = await self.list()
        if not state[key]:
            raise UnsafeOperationError(message)


def format_craft_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CraftInfos",
        "ShiftingCraftInfos",
        "CraftInfoDBs",
        "CraftNodeDBs",
        "CraftSlotDBs",
    }
    infos = as_list(payload.get("CraftInfos", payload.get("CraftInfoDBs")))
    shifting_infos = as_list(payload.get("ShiftingCraftInfos"))
    nodes = as_list(payload.get("CraftNodeDBs"))
    slots = as_list(payload.get("CraftSlotDBs"))
    return {
        "craft_infos": infos,
        "shifting_craft_infos": shifting_infos,
        "craft_nodes": nodes,
        "craft_slots": slots,
        "count": len(infos),
        "shifting_count": len(shifting_infos),
        "node_count": len(nodes),
        "slot_count": len(slots),
        "extra": extra_fields(payload, known_keys),
    }


def format_craft_complete_process_all(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CraftInfoDBs",
        "TicketItemDB",
    }
    craft_infos = as_list(payload.get("CraftInfoDBs"))
    return {
        "craft_infos": craft_infos,
        "ticket_item": payload.get("TicketItemDB"),
        "count": len(craft_infos),
        "extra": extra_fields(payload, known_keys),
    }


def format_craft_shifting_complete_process_all(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CraftInfoDBs",
        "ParcelResultDB",
    }
    craft_infos = as_list(payload.get("CraftInfoDBs"))
    return {
        "craft_infos": craft_infos,
        "parcel_result": payload.get("ParcelResultDB"),
        "count": len(craft_infos),
        "extra": extra_fields(payload, known_keys),
    }
