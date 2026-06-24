from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int, required_int


class ConquestService(GameService):
    async def get_info(self, event_content_id: int) -> dict[str, Any]:
        payload = await self.request(
            "ConquestGetInfoRequest",
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )
        return format_conquest_info(payload)

    async def main_story_get_info(self, event_content_id: int) -> dict[str, Any]:
        payload = await self.request(
            "ConquestMainStoryGetInfoRequest",
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )
        return format_conquest_main_story_info(payload)

    async def check(self, event_content_id: int) -> dict[str, Any]:
        return await self.request(
            "ConquestCheckRequest",
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )

    async def main_story_check(self, event_content_id: int) -> dict[str, Any]:
        return await self.request(
            "ConquestMainStoryCheckRequest",
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )

    async def receive_calculate_rewards(
        self, *, event_content_id: int, difficulty: int, step: int, confirm: bool = False, validate: bool = True
    ) -> dict[str, Any]:
        ecid = required_int("event_content_id", event_content_id)
        if confirm is not True:
            raise UnsafeOperationError("conquest.receive_calculate_rewards requires confirm=True")
        if validate and not bool((await self.check(ecid)).get("CanReceiveCalculateReward")):
            raise UnsafeOperationError("conquest calculate reward is not currently claimable")
        return await self.request(
            "ConquestReceiveRewardsRequest",
            {
                "Difficulty": required_int("difficulty", difficulty),
                "EventContentId": ecid,
                "Step": required_int("step", step),
            },
        )

    async def manage_base(
        self,
        *,
        difficulty: int | None = None,
        event_content_id: int | None = None,
        manage_count: int | None = None,
        tile_unique_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("conquest.manage_base requires confirm=True")
        fields = compact_fields(
            Difficulty=optional_int("difficulty", difficulty),
            EventContentId=optional_int("event_content_id", event_content_id),
            ManageCount=optional_int("manage_count", manage_count),
            TileUniqueId=optional_int("tile_unique_id", tile_unique_id),
        )
        return await self.request("ConquestManageBaseRequest", fields)

    async def upgrade_base(
        self,
        *,
        difficulty: int | None = None,
        event_content_id: int | None = None,
        tile_unique_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("conquest.upgrade_base requires confirm=True")
        fields = compact_fields(
            Difficulty=optional_int("difficulty", difficulty),
            EventContentId=optional_int("event_content_id", event_content_id),
            TileUniqueId=optional_int("tile_unique_id", tile_unique_id),
        )
        return await self.request("ConquestUpgradeBaseRequest", fields)

    async def take_event_object(
        self,
        *,
        conquest_object_db_id: int | None = None,
        event_content_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("conquest.take_event_object requires confirm=True")
        fields = compact_fields(
            ConquestObjectDBId=optional_int("conquest_object_db_id", conquest_object_db_id),
            EventContentId=optional_int("event_content_id", event_content_id),
        )
        return await self.request("ConquestTakeEventObjectRequest", fields)

    async def normalize_echelon(
        self,
        *,
        difficulty: int | None = None,
        event_content_id: int | None = None,
        tile_unique_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("conquest.normalize_echelon requires confirm=True")
        fields = compact_fields(
            Difficulty=optional_int("difficulty", difficulty),
            EventContentId=optional_int("event_content_id", event_content_id),
            TileUniqueId=optional_int("tile_unique_id", tile_unique_id),
        )
        return await self.request("ConquestNormalizeEchelonRequest", fields)


def format_conquest_info(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ConquestInfoDB",
        "ConquestedTileDBs",
        "ConquestObjectDBsWrapper",
        "ConquestStageHistoryDBs",
        "ConquestEchelonDBs",
        "ConquestEventObjectDBs",
        "DifficultyToStepDict",
        "IsFirstEnter",
        "DisplayInfos",
    }
    conquered_tiles = as_list(payload.get("ConquestedTileDBs", payload.get("ConquestStageHistoryDBs")))
    echelons = as_list(payload.get("ConquestEchelonDBs"))
    objects = as_list(payload.get("ConquestEventObjectDBs", payload.get("ConquestObjectDBsWrapper")))
    return {
        "conquest_info": payload.get("ConquestInfoDB"),
        "conquered_tiles": conquered_tiles,
        "echelons": echelons,
        "event_objects": objects,
        "difficulty_to_step": payload.get("DifficultyToStepDict"),
        "is_first_enter": payload.get("IsFirstEnter"),
        "display_infos": as_list(payload.get("DisplayInfos")),
        "conquered_tile_count": len(conquered_tiles),
        "echelon_count": len(echelons),
        "event_object_count": len(objects),
        "extra": extra_fields(payload, known_keys),
    }


def format_conquest_main_story_info(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ConquestMainStoryDBs",
    }
    stories = as_list(payload.get("ConquestMainStoryDBs"))
    return {
        "main_stories": stories,
        "count": len(stories),
        "extra": extra_fields(payload, known_keys),
    }
