from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields, required_int


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
