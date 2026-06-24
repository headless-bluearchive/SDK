from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int, required_int


class CampaignService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("CampaignListRequest")
        return format_campaign_list(payload)

    async def chapter_clear_reward(
        self, *, campaign_chapter_unique_id: int, stage_difficulty: int, confirm: bool = False
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("campaign.chapter_clear_reward requires confirm=True")
        return await self.request(
            "CampaignChapterClearRewardRequest",
            {
                "CampaignChapterUniqueId": required_int("campaign_chapter_unique_id", campaign_chapter_unique_id),
                "StageDifficulty": required_int("stage_difficulty", stage_difficulty),
            },
        )

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

    async def purchase_play_count_hard_stage(
        self,
        *,
        stage_unique_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("campaign.purchase_play_count_hard_stage requires confirm=True")
        fields = compact_fields(
            StageUniqueId=optional_int("stage_unique_id", stage_unique_id),
        )
        return await self.request("CampaignPurchasePlayCountHardStageRequest", fields)

    async def confirm_tutorial_stage(
        self,
        *,
        stage_unique_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("campaign.confirm_tutorial_stage requires confirm=True")
        fields = compact_fields(
            StageUniqueId=optional_int("stage_unique_id", stage_unique_id),
        )
        return await self.request("CampaignConfirmTutorialStageRequest", fields)

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
