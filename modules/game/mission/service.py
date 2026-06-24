from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, optional_int, required_int


MISSION_CATEGORIES = {
    "challenge": 0,
    "daily": 1,
    "weekly": 2,
    "achievement": 3,
    "guide_mission": 4,
    "guide": 4,
    "all": 5,
    "mini_game_score": 6,
    "mini_game_event": 7,
    "event_achievement": 8,
    "daily_sudden": 9,
    "daily_fixed": 10,
    "event_fixed": 11,
}


class MissionService(GameService):
    async def sync(self) -> dict[str, Any]:
        return await self.request("MissionSyncRequest")

    async def list(self, *, event_content_id: int | None = None) -> dict[str, Any]:
        fields: dict[str, Any] = {}
        if event_content_id is not None:
            fields["EventContentId"] = int(event_content_id)
        payload = await self.request("MissionListRequest", fields)
        return format_mission_list(payload)

    async def guide_season_list(self) -> dict[str, Any]:
        payload = await self.request("GuideMissionSeasonListRequest")
        return format_guide_mission_season_list(payload)

    async def reward(
        self,
        mission_unique_id: int,
        *,
        progress_server_id: int | None = None,
        event_content_id: int | None = None,
        validate: bool = True,
    ) -> dict[str, Any]:
        mission_id = required_int("mission_unique_id", mission_unique_id)
        progress_id = optional_int("progress_server_id", progress_server_id)
        event_id = optional_int("event_content_id", event_content_id)

        if validate:
            await self._ensure_rewardable(
                mission_unique_id=mission_id,
                progress_server_id=progress_id,
                event_content_id=event_id,
            )

        fields: dict[str, Any] = {"MissionUniqueId": mission_id}
        if progress_id is not None:
            fields["ProgressServerId"] = progress_id
        if event_id is not None:
            fields["EventContentId"] = event_id

        payload = await self.request("MissionRewardRequest", fields)
        return format_mission_reward(payload)

    async def multiple_reward(
        self,
        mission_category: int | str,
        *,
        event_content_id: int | None = None,
        guide_mission_season_id: int | None = None,
        validate: bool = True,
    ) -> dict[str, Any]:
        category = _mission_category(mission_category)
        event_id = optional_int("event_content_id", event_content_id)
        season_id = optional_int("guide_mission_season_id", guide_mission_season_id)

        if validate:
            await self._ensure_any_completed(event_content_id=event_id)

        fields: dict[str, Any] = {"MissionCategory": category}
        if season_id is not None:
            fields["GuideMissionSeasonId"] = season_id
        if event_id is not None:
            fields["EventContentId"] = event_id

        payload = await self.request("MissionMultipleRewardRequest", fields)
        return format_mission_multiple_reward(payload)

    async def _ensure_rewardable(
        self,
        *,
        mission_unique_id: int,
        progress_server_id: int | None,
        event_content_id: int | None,
    ) -> None:
        missions = await self.list(event_content_id=event_content_id)
        progress = _find_progress(missions["progress"], mission_unique_id)
        if progress is None:
            raise UnsafeOperationError("mission is not present in current mission list")
        if progress.get("Complete") is not True:
            raise UnsafeOperationError("mission is not completed")
        actual_progress_id = _progress_server_id(progress)
        if progress_server_id is not None and actual_progress_id is not None and actual_progress_id != progress_server_id:
            raise UnsafeOperationError("progress_server_id does not match current mission progress")

    async def _ensure_any_completed(self, *, event_content_id: int | None) -> None:
        missions = await self.list(event_content_id=event_content_id)
        if not any(isinstance(item, dict) and item.get("Complete") is True for item in missions["progress"]):
            raise UnsafeOperationError("no completed mission is present")


def format_mission_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "MissionHistoryUniqueIds",
        "ProgressDBs",
        "DailySuddenMissionInfo",
        "ClearedOrignalMissionIds",
        "ClearedOriginalMissionIds",
    }
    return {
        "mission_history_unique_ids": as_list(payload.get("MissionHistoryUniqueIds")),
        "progress": as_list(payload.get("ProgressDBs")),
        "daily_sudden_mission_info": payload.get("DailySuddenMissionInfo"),
        "cleared_original_mission_ids": as_list(
            payload.get("ClearedOrignalMissionIds", payload.get("ClearedOriginalMissionIds"))
        ),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def format_mission_reward(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AddedHistoryDB",
        "MissionProgressDBs",
        "ParcelResultDB",
        "ParcelResult",
    }
    return {
        "added_history": payload.get("AddedHistoryDB"),
        "mission_progress": as_list(payload.get("MissionProgressDBs")),
        "parcel_result": payload.get("ParcelResultDB", payload.get("ParcelResult")),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def format_mission_multiple_reward(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AddedHistoryDBs",
        "MissionProgressDBs",
        "ParcelResultDB",
    }
    return {
        "added_histories": as_list(payload.get("AddedHistoryDBs")),
        "mission_progress": as_list(payload.get("MissionProgressDBs")),
        "parcel_result": payload.get("ParcelResultDB"),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def format_guide_mission_season_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "GuideMissionSeasonDBs",
    }
    seasons = as_list(payload.get("GuideMissionSeasonDBs"))
    return {
        "guide_mission_seasons": seasons,
        "count": len(seasons),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def _find_progress(progress: list[Any], mission_unique_id: int) -> dict[str, Any] | None:
    for item in progress:
        if isinstance(item, dict) and optional_int("MissionUniqueId", item.get("MissionUniqueId")) == mission_unique_id:
            return item
    return None


def _progress_server_id(progress: dict[str, Any]) -> int | None:
    for key in ("ProgressServerId", "ServerId", "Id", "UniqueId"):
        value = progress.get(key)
        if value is not None:
            return optional_int(key, value)
    return None


def _mission_category(value: int | str) -> int:
    if isinstance(value, str):
        key = value.strip().lower().replace("-", "_").replace(" ", "_")
        if key in MISSION_CATEGORIES:
            return MISSION_CATEGORIES[key]
    return required_int("mission_category", value)
