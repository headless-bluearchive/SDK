from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class SchoolDungeonService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("SchoolDungeonListRequest")
        return format_school_dungeon_list(payload)


def format_school_dungeon_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "SchoolDungeonStageHistoryDBList",
        "SchoolDungeonStageHistoryDBs",
        "SchoolDungeonBestTeamDBs",
    }
    history = as_list(payload.get("SchoolDungeonStageHistoryDBList", payload.get("SchoolDungeonStageHistoryDBs")))
    teams = as_list(payload.get("SchoolDungeonBestTeamDBs"))
    return {
        "stage_history": history,
        "best_teams": teams,
        "stage_count": len(history),
        "best_team_count": len(teams),
        "extra": extra_fields(payload, known_keys),
    }
