from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, extra_fields, optional_int, required_int


class SweepService(GameService):
    async def preset_list(self) -> dict[str, Any]:
        payload = await super().request("ContentSweepMultiSweepPresetListRequest")
        return format_sweep_preset_list(payload)

    async def request(
        self,
        *,
        content: int,
        stage_id: int,
        count: int,
        event_content_id: int = 0,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("sweep.request requires confirm=True")
        fields = {
            "Content": required_int("content", content),
            "StageId": required_int("stage_id", stage_id),
            "EventContentId": optional_int("event_content_id", event_content_id) or 0,
            "Count": _positive_int("count", count),
        }
        payload = await super().request("ContentSweepRequest", fields)
        return format_sweep_result(payload)

    async def multi_sweep(
        self,
        parameters: list[dict[str, Any]] | tuple[dict[str, Any], ...],
        *,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("sweep.multi_sweep requires confirm=True")
        if not isinstance(parameters, (list, tuple)) or not parameters:
            raise UnsafeOperationError("parameters must be a non-empty list")
        fields = {"MultiSweepParameters": [_multi_sweep_parameter(item) for item in parameters]}
        payload = await super().request("ContentSweepMultiSweepRequest", fields)
        return format_multi_sweep_result(payload)


def format_sweep_preset_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "MultiSweepPresetDBs",
    }
    return {
        "presets": as_list(payload.get("MultiSweepPresetDBs")),
        "extra": extra_fields(payload, known_keys),
    }


def format_sweep_result(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ClearParcels",
        "BonusParcels",
        "EventContentBonusParcels",
        "ParcelResult",
        "CampaignStageHistoryDB",
    }
    return {
        "clear_parcels": as_list(payload.get("ClearParcels")),
        "bonus_parcels": as_list(payload.get("BonusParcels")),
        "event_content_bonus_parcels": as_list(payload.get("EventContentBonusParcels")),
        "parcel_result": payload.get("ParcelResult"),
        "campaign_stage_history": payload.get("CampaignStageHistoryDB"),
        "extra": extra_fields(payload, known_keys),
    }


def format_multi_sweep_result(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ClearParcels",
        "BonusParcels",
        "EventContentBonusParcels",
        "ParcelResult",
        "CampaignStageHistoryDBs",
    }
    return {
        "clear_parcels": as_list(payload.get("ClearParcels")),
        "bonus_parcels": as_list(payload.get("BonusParcels")),
        "event_content_bonus_parcels": as_list(payload.get("EventContentBonusParcels")),
        "parcel_result": payload.get("ParcelResult"),
        "campaign_stage_history": as_list(payload.get("CampaignStageHistoryDBs")),
        "extra": extra_fields(payload, known_keys),
    }


def _multi_sweep_parameter(value: dict[str, Any]) -> dict[str, int]:
    if not isinstance(value, dict):
        raise UnsafeOperationError("multi_sweep parameter must be a dict")
    return {
        "EventContentId": optional_int("event_content_id", value.get("EventContentId", value.get("event_content_id"))) or 0,
        "ContentType": required_int("content_type", value.get("ContentType", value.get("content_type"))),
        "StageId": required_int("stage_id", value.get("StageId", value.get("stage_id"))),
        "SweepCount": _positive_int("sweep_count", value.get("SweepCount", value.get("sweep_count"))),
    }


def _positive_int(name: str, value: Any) -> int:
    result = required_int(name, value)
    if result <= 0:
        raise UnsafeOperationError(f"{name} must be greater than zero")
    return result
