from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, int_list


class OpenConditionService(GameService):

    async def list(self) -> dict[str, Any]:
        payload = await self.request("OpenConditionListRequest")
        return format_open_condition_list(payload)

    async def event_list(
        self,
        *,
        conquest_event_ids: list[int] | tuple[int, ...] | None = None,
        world_raid_season_and_group_ids: list[int] | tuple[int, ...] | None = None,
    ) -> dict[str, Any]:
        fields = compact_fields(
            ConquestEventIds=int_list("conquest_event_ids", conquest_event_ids) or None,
            WorldRaidSeasonAndGroupIds=int_list(
                "world_raid_season_and_group_ids", world_raid_season_and_group_ids
            )
            or None,
        )
        payload = await self.request("OpenConditionEventListRequest", fields)
        return format_open_condition_event_list(payload)

    async def set(
        self,
        *,
        condition_db: Any = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("open_condition.set requires confirm=True")
        fields = compact_fields(
            ConditionDB=condition_db,
        )
        return await self.request("OpenConditionSetRequest", fields)


def format_open_condition_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ConditionContents",
    }
    return {
        "condition_contents": payload.get("ConditionContents"),
        "extra": extra_fields(payload, known_keys),
    }


def format_open_condition_event_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ConquestTiles",
        "WorldRaidLocalBossDBs",
    }
    return {
        "conquest_tiles": as_list(payload.get("ConquestTiles")),
        "world_raid_local_bosses": as_list(payload.get("WorldRaidLocalBossDBs")),
        "extra": extra_fields(payload, known_keys),
    }
