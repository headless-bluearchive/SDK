from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import required_int


class DailyRecordService(GameService):

    async def reward(self, daily_record_id: int, *, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("daily_record.reward requires confirm=True")
        return await self.request(
            "DailyRecordRewardRequest",
            {"DailyRecordId": required_int("daily_record_id", daily_record_id)},
        )
