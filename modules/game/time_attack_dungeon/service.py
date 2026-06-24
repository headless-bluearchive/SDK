from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import required_int


class TimeAttackDungeonService(GameService):

    async def lobby(self) -> dict[str, Any]:
        return await self.request("TimeAttackDungeonLobbyRequest")

    async def login(self) -> dict[str, Any]:
        return await self.request("TimeAttackDungeonLoginRequest")

    async def sweep(self, *, sweep_count: int = 1, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("time_attack_dungeon.sweep requires confirm=True")
        return await self.request(
            "TimeAttackDungeonSweepRequest",
            {"SweepCount": required_int("sweep_count", sweep_count)},
        )
