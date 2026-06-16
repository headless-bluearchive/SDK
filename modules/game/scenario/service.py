from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, extra_fields, required_int


class ScenarioService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("ScenarioListRequest")
        return format_scenario_list(payload)

    async def confirm_main_stage(
        self,
        stage_unique_id: int,
        *,
        confirm: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        stage_id = required_int("stage_unique_id", stage_unique_id)
        if confirm is not True:
            raise UnsafeOperationError("scenario.confirm_main_stage requires confirm=True")
        if validate:
            self._require_active_stage_context("scenario.confirm_main_stage")
        payload = await self.request("ScenarioConfirmMainStageRequest", {"StageUniqueId": stage_id})
        return format_scenario_confirm_main_stage(payload)

    async def skip_main_stage(
        self,
        stage_unique_id: int,
        *,
        confirm: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        stage_id = required_int("stage_unique_id", stage_unique_id)
        if confirm is not True:
            raise UnsafeOperationError("scenario.skip_main_stage requires confirm=True")
        if validate:
            self._require_active_stage_context("scenario.skip_main_stage")
        payload = await self.request("ScenarioSkipMainStageRequest", {"StageUniqueId": stage_id})
        return format_scenario_skip_main_stage(payload)

    @staticmethod
    def _require_active_stage_context(method_name: str) -> None:
        raise UnsafeOperationError(
            f"{method_name} requires an active scenario main stage save; "
            "Scenario_List scenario_history is not a valid precondition. "
            "Pass validate=False only after obtaining StageUniqueId from an active stage flow."
        )


def format_scenario_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ScenarioHistoryDBs",
        "ScenarioGroupHistoryDBs",
        "ScenarioCollectionDBs",
    }
    scenarios = as_list(payload.get("ScenarioHistoryDBs"))
    groups = as_list(payload.get("ScenarioGroupHistoryDBs"))
    collections = as_list(payload.get("ScenarioCollectionDBs"))
    return {
        "scenario_history": scenarios,
        "scenario_group_history": groups,
        "scenario_collections": collections,
        "count": len(scenarios),
        "group_count": len(groups),
        "collection_count": len(collections),
        "extra": extra_fields(payload, known_keys),
    }


def format_scenario_confirm_main_stage(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ParcelResultDB",
        "SaveDataDB",
        "ScenarioIds",
    }
    scenario_ids = as_list(payload.get("ScenarioIds"))
    return {
        "parcel_result": payload.get("ParcelResultDB"),
        "save_data": payload.get("SaveDataDB"),
        "scenario_ids": scenario_ids,
        "scenario_count": len(scenario_ids),
        "extra": extra_fields(payload, known_keys),
    }


def format_scenario_skip_main_stage(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "extra": extra_fields(payload, set()),
    }

