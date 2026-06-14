from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class WeekDungeonService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("WeekDungeonListRequest")
        return format_week_dungeon_list(payload)


def format_week_dungeon_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AdditionalStageIdList",
        "WeekDungeonStageHistoryDBList",
    }
    history = as_list(payload.get("WeekDungeonStageHistoryDBList"))
    return {
        "additional_stage_ids": as_list(payload.get("AdditionalStageIdList")),
        "stage_history": history,
        "stage_count": len(history),
        "extra": extra_fields(payload, known_keys),
    }
