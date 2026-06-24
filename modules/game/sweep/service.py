from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, int_list, optional_int, required_int


class SweepService(GameService):
    async def skip_history_list(self) -> dict[str, Any]:
        payload = await super().request("SkipHistoryListRequest")
        return format_skip_history_list(payload)

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

    async def set_multi_sweep_preset(
        self,
        *,
        parcel_ids: Any = None,
        preset_id: int | None = None,
        preset_name: str | None = None,
        stage_ids: list[int] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("sweep.set_multi_sweep_preset requires confirm=True")
        fields = compact_fields(
            ParcelIds=parcel_ids,
            PresetId=optional_int("preset_id", preset_id),
            PresetName=str(preset_name) if preset_name is not None else None,
            StageIds=int_list("stage_ids", stage_ids) or None,
        )
        return await super().request("ContentSweepSetMultiSweepPresetRequest", fields)

    async def set_multi_sweep_preset_name(
        self,
        *,
        preset_id: int | None = None,
        preset_name: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("sweep.set_multi_sweep_preset_name requires confirm=True")
        fields = compact_fields(
            PresetId=optional_int("preset_id", preset_id),
            PresetName=str(preset_name) if preset_name is not None else None,
        )
        return await super().request("ContentSweepSetMultiSweepPresetNameRequest", fields)

    async def save_skip_history(
        self,
        *,
        skip_history_db: Any = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("sweep.save_skip_history requires confirm=True")
        fields = compact_fields(
            SkipHistoryDB=skip_history_db,
        )
        return await super().request("SkipHistorySaveRequest", fields)


def format_sweep_preset_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "MultiSweepPresetDBs",
    }
    return {
        "presets": as_list(payload.get("MultiSweepPresetDBs")),
        "extra": extra_fields(payload, known_keys),
    }


def format_skip_history_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "SkipHistoryDB",
        "SkipHistoryDBs",
    }
    skip_history = payload.get("SkipHistoryDB", payload.get("SkipHistoryDBs"))
    return {
        "skip_history": skip_history,
        "count": len(as_list(skip_history)),
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
