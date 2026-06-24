from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int, required_int


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

    async def receive_reward(self, *, phase_id: int, season_id: int, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("world_raid.receive_reward requires confirm=True")
        return await self.request(
            "WorldRaidReceiveRewardRequest",
            {
                "PhaseId": required_int("phase_id", phase_id),
                "SeasonId": required_int("season_id", season_id),
            },
        )

    async def update_carrier_skill(
        self,
        *,
        carrier_skills: Any = None,
        recipe_ingredient_id: int | None = None,
        season_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("world_raid.update_carrier_skill requires confirm=True")
        fields = compact_fields(
            CarrierSkills=carrier_skills,
            RecipeIngredientId=optional_int("recipe_ingredient_id", recipe_ingredient_id),
            SeasonId=optional_int("season_id", season_id),
        )
        return await self.request("WorldRaidUpdateCarrierSkillRequest", fields)


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
