from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, extra_fields, required_int


class CampaignService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("CampaignListRequest")
        return format_campaign_list(payload)

    async def confirm_main_stage(
        self,
        stage_unique_id: int,
        *,
        confirm: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        stage_id = required_int("stage_unique_id", stage_unique_id)
        if confirm is not True:
            raise UnsafeOperationError("campaign.confirm_main_stage requires confirm=True")
        if validate:
            self._require_active_stage_context()
        payload = await self.request("CampaignConfirmMainStageRequest", {"StageUniqueId": stage_id})
        return format_campaign_confirm_main_stage(payload)

    @staticmethod
    def _require_active_stage_context() -> None:
        raise UnsafeOperationError(
            "campaign.confirm_main_stage requires an active main stage save; "
            "Campaign_List stage_history is not a valid precondition. "
            "Pass validate=False only after obtaining StageUniqueId from an active stage flow."
        )


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


def format_campaign_confirm_main_stage(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ParcelResultDB",
        "SaveDataDB",
        "StageInfo",
    }
    return {
        "parcel_result": payload.get("ParcelResultDB"),
        "save_data": payload.get("SaveDataDB"),
        "stage_info": payload.get("StageInfo"),
        "extra": extra_fields(payload, known_keys),
    }

