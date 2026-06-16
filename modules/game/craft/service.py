from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


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
