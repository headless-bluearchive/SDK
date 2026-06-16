from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields, required_int


class BattlePassService(GameService):
    async def get_info(self, battle_pass_id: int) -> dict[str, Any]:
        payload = await self.request(
            "BattlePassGetInfoRequest",
            {"BattlePassId": required_int("battle_pass_id", battle_pass_id)},
        )
        return format_battle_pass_info(payload)

    async def mission_list(self, battle_pass_id: int) -> dict[str, Any]:
        payload = await self.request(
            "BattlePassMissionListRequest",
            {"BattlePassId": required_int("battle_pass_id", battle_pass_id)},
        )
        return format_battle_pass_mission_list(payload)


def format_battle_pass_info(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "BattlePassInfo",
    }
    return {
        "battle_pass_info": payload.get("BattlePassInfo"),
        "extra": extra_fields(payload, known_keys),
    }


def format_battle_pass_mission_list(payload: dict[str, Any]) -> dict[str, Any]:
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
