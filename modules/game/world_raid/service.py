from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields, required_int


class WorldRaidService(GameService):
    async def lobby(self, content_type: int, season_id: int) -> dict[str, Any]:
        payload = await self.request(
            "WorldRaidLobbyRequest",
            {
                "ContentType": required_int("content_type", content_type),
                "SeasonId": required_int("season_id", season_id),
            },
        )
        return format_world_raid_lobby(payload)

    async def boss_list(
        self,
        content_type: int,
        season_id: int,
        *,
        request_only_world_boss_data: bool = False,
    ) -> dict[str, Any]:
        payload = await self.request(
            "WorldRaidBossListRequest",
            {
                "ContentType": required_int("content_type", content_type),
                "SeasonId": required_int("season_id", season_id),
                "RequestOnlyWorldBossData": bool(request_only_world_boss_data),
            },
        )
        return format_world_raid_boss_list(payload)


def format_world_raid_lobby(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ClearHistoryDBs",
        "LocalBossDBs",
        "BossGroups",
    }
    clear_history = as_list(payload.get("ClearHistoryDBs"))
    local_bosses = as_list(payload.get("LocalBossDBs"))
    boss_groups = as_list(payload.get("BossGroups"))
    return {
        "clear_history": clear_history,
        "local_bosses": local_bosses,
        "boss_groups": boss_groups,
        "clear_history_count": len(clear_history),
        "local_boss_count": len(local_bosses),
        "boss_group_count": len(boss_groups),
        "extra": extra_fields(payload, known_keys),
    }


def format_world_raid_boss_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "BossListInfoDBs",
    }
    bosses = as_list(payload.get("BossListInfoDBs"))
    return {
        "boss_list_info": bosses,
        "count": len(bosses),
        "extra": extra_fields(payload, known_keys),
    }
