from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class CampaignService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("CampaignListRequest")
        return format_campaign_list(payload)


def format_campaign_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CampaignChapterClearRewardHistoryDBs",
        "StageHistoryDBs",
        "StrategyObjecthistoryDBs",
    }
    stages = as_list(payload.get("StageHistoryDBs"))
    return {
        "chapter_clear_reward_history": as_list(payload.get("CampaignChapterClearRewardHistoryDBs")),
        "stage_history": stages,
        "strategy_object_history": as_list(payload.get("StrategyObjecthistoryDBs")),
        "stage_count": len(stages),
        "extra": extra_fields(payload, known_keys),
    }
