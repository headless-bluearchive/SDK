from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import required_int


class MultiFloorRaidService(GameService):

    async def sync(self, season_id: int) -> dict[str, Any]:
        return await self.request(
            "MultiFloorRaidSyncRequest",
            {"SeasonId": required_int("season_id", season_id)},
        )

    async def login(self) -> dict[str, Any]:
        return await self.request("MultiFloorRaidLoginRequest")

    async def receive_reward(
        self,
        *,
        reward_difficulty: int,
        season_id: int,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("multi_floor_raid.receive_reward requires confirm=True")
        return await self.request(
            "MultiFloorRaidReceiveRewardRequest",
            {
                "RewardDifficulty": required_int("reward_difficulty", reward_difficulty),
                "SeasonId": required_int("season_id", season_id),
            },
        )
