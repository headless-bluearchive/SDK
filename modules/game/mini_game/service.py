from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields, required_int


class MiniGameService(GameService):
    async def stage_list(self, event_content_id: int) -> dict[str, Any]:
        payload = await self._event_request("MiniGameStageListRequest", event_content_id)
        return format_mini_game_stage_list(payload)

    async def mission_list(self, event_content_id: int) -> dict[str, Any]:
        payload = await self._event_request("MiniGameMissionListRequest", event_content_id)
        return format_mini_game_mission_list(payload)

    async def shooting_lobby(self, event_content_id: int) -> dict[str, Any]:
        payload = await self._event_request("MiniGameShootingLobbyRequest", event_content_id)
        return format_mini_game_shooting_lobby(payload)

    async def table_board_sync(self, event_content_id: int) -> dict[str, Any]:
        payload = await self._event_request("MiniGameTableBoardSyncRequest", event_content_id)
        return format_mini_game_table_board_sync(payload)

    async def dream_maker_get_info(self, event_content_id: int) -> dict[str, Any]:
        payload = await self._event_request("MiniGameDreamMakerGetInfoRequest", event_content_id)
        return format_mini_game_dream_maker_info(payload)

    async def defense_get_info(self, event_content_id: int) -> dict[str, Any]:
        payload = await self._event_request("MiniGameDefenseGetInfoRequest", event_content_id)
        return format_mini_game_defense_info(payload)

    async def road_puzzle_get_info(self, event_content_id: int) -> dict[str, Any]:
        payload = await self._event_request("MiniGameRoadPuzzleGetInfoRequest", event_content_id)
        return format_mini_game_road_puzzle_info(payload)

    async def ccg_lobby(self, event_content_id: int) -> dict[str, Any]:
        payload = await self._event_request("MiniGameCCGLobbyRequest", event_content_id)
        return format_mini_game_ccg_lobby(payload)

    async def _event_request(self, request_class: str, event_content_id: int) -> dict[str, Any]:
        return await self.request(
            request_class,
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )


def format_mini_game_stage_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "MiniGameHistoryDBs",
        "MiniGameStageDBs",
        "StageHistoryDBs",
    }
    stages = as_list(payload.get("MiniGameHistoryDBs", payload.get("MiniGameStageDBs", payload.get("StageHistoryDBs"))))
    return {
        "stages": stages,
        "count": len(stages),
        "extra": extra_fields(payload, known_keys),
    }


def format_mini_game_mission_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "MissionHistoryUniqueIds",
        "ProgressDBs",
    }
    progress = as_list(payload.get("ProgressDBs"))
    return {
        "mission_history_unique_ids": as_list(payload.get("MissionHistoryUniqueIds")),
        "progress": progress,
        "count": len(progress),
        "extra": extra_fields(payload, known_keys),
    }


def format_mini_game_shooting_lobby(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ShootingLobbyDB",
        "ShootingStageHistoryDBs",
        "AccountCurrencyDB",
    }
    history = as_list(payload.get("ShootingStageHistoryDBs"))
    return {
        "shooting_lobby": payload.get("ShootingLobbyDB"),
        "stage_history": history,
        "account_currency": payload.get("AccountCurrencyDB"),
        "stage_count": len(history),
        "extra": extra_fields(payload, known_keys),
    }


def format_mini_game_table_board_sync(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "TableBoardDB",
        "TableBoardStageDBs",
        "AccountCurrencyDB",
    }
    stages = as_list(payload.get("TableBoardStageDBs"))
    return {
        "table_board": payload.get("TableBoardDB"),
        "stages": stages,
        "account_currency": payload.get("AccountCurrencyDB"),
        "stage_count": len(stages),
        "extra": extra_fields(payload, known_keys),
    }


def format_mini_game_dream_maker_info(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "DreamMakerDB",
        "DreamMakerScheduleDBs",
        "AccountCurrencyDB",
    }
    schedules = as_list(payload.get("DreamMakerScheduleDBs"))
    return {
        "dream_maker": payload.get("DreamMakerDB"),
        "schedules": schedules,
        "account_currency": payload.get("AccountCurrencyDB"),
        "schedule_count": len(schedules),
        "extra": extra_fields(payload, known_keys),
    }


def format_mini_game_defense_info(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "DefenseDB",
        "DefenseStageHistoryDBs",
        "AccountCurrencyDB",
    }
    history = as_list(payload.get("DefenseStageHistoryDBs"))
    return {
        "defense": payload.get("DefenseDB"),
        "stage_history": history,
        "account_currency": payload.get("AccountCurrencyDB"),
        "stage_count": len(history),
        "extra": extra_fields(payload, known_keys),
    }


def format_mini_game_road_puzzle_info(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "RoadPuzzleDB",
        "RoadPuzzleStageHistoryDBs",
        "AccountCurrencyDB",
    }
    history = as_list(payload.get("RoadPuzzleStageHistoryDBs"))
    return {
        "road_puzzle": payload.get("RoadPuzzleDB"),
        "stage_history": history,
        "account_currency": payload.get("AccountCurrencyDB"),
        "stage_count": len(history),
        "extra": extra_fields(payload, known_keys),
    }


def format_mini_game_ccg_lobby(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CCGDB",
        "CCGDeckDBs",
        "AccountCurrencyDB",
    }
    decks = as_list(payload.get("CCGDeckDBs"))
    return {
        "ccg": payload.get("CCGDB"),
        "decks": decks,
        "account_currency": payload.get("AccountCurrencyDB"),
        "deck_count": len(decks),
        "extra": extra_fields(payload, known_keys),
    }
