from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int, required_int


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

    async def check(self, battle_pass_id: int) -> dict[str, Any]:
        payload = await self.request(
            "BattlePassCheckRequest",
            compact_fields(BattlePassId=required_int("battle_pass_id", battle_pass_id)),
        )
        return format_battle_pass_check(payload)

    async def receive_reward(
        self, battle_pass_id: int, *, confirm: bool = False, validate: bool = True
    ) -> dict[str, Any]:
        bp_id = required_int("battle_pass_id", battle_pass_id)
        if confirm is not True:
            raise UnsafeOperationError("battle_pass.receive_reward requires confirm=True")
        if validate and not (await self.check(bp_id))["has_not_receive_reward"]:
            raise UnsafeOperationError("battle pass has no unreceived reward")
        return await self.request("BattlePassReceiveRewardRequest", {"BattlePassId": bp_id})

    async def mission_single_reward(
        self, battle_pass_id: int, mission_unique_id: int, *, confirm: bool = False, validate: bool = True
    ) -> dict[str, Any]:
        bp_id = required_int("battle_pass_id", battle_pass_id)
        mission_id = required_int("mission_unique_id", mission_unique_id)
        if confirm is not True:
            raise UnsafeOperationError("battle_pass.mission_single_reward requires confirm=True")
        if validate and not (await self.check(bp_id))["has_complete_mission"]:
            raise UnsafeOperationError("battle pass has no completed mission to claim")
        return await self.request(
            "BattlePassMissionSingleRewardRequest",
            {"BattlePassId": bp_id, "MissionUniqueId": mission_id},
        )

    async def mission_multiple_reward(
        self, battle_pass_id: int, mission_category: int, *, confirm: bool = False, validate: bool = True
    ) -> dict[str, Any]:
        bp_id = required_int("battle_pass_id", battle_pass_id)
        category = required_int("mission_category", mission_category)
        if confirm is not True:
            raise UnsafeOperationError("battle_pass.mission_multiple_reward requires confirm=True")
        if validate and not (await self.check(bp_id))["has_complete_mission"]:
            raise UnsafeOperationError("battle pass has no completed mission to claim")
        return await self.request(
            "BattlePassMissionMultipleRewardRequest",
            {"BattlePassId": bp_id, "MissionCategory": category},
        )

    async def buy_level(
        self,
        *,
        battle_pass_buy_level_count: int | None = None,
        battle_pass_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("battle_pass.buy_level requires confirm=True")
        fields = compact_fields(
            BattlePassBuyLevelCount=optional_int("battle_pass_buy_level_count", battle_pass_buy_level_count),
            BattlePassId=optional_int("battle_pass_id", battle_pass_id),
        )
        return await self.request("BattlePassBuyLevelRequest", fields)


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


def format_battle_pass_check(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "HasNotReceiveReward",
        "HasCompleteMission",
    }
    return {
        "has_not_receive_reward": bool(payload.get("HasNotReceiveReward")),
        "has_complete_mission": bool(payload.get("HasCompleteMission")),
        "extra": extra_fields(payload, known_keys),
    }
