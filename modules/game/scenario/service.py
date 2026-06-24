from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, int_list, optional_int, required_int


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

    async def group_history_update(
        self,
        *,
        scenario_group_unique_id: int | None = None,
        scenario_type: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("scenario.group_history_update requires confirm=True")
        fields = compact_fields(
            ScenarioGroupUniqueId=optional_int("scenario_group_unique_id", scenario_group_unique_id),
            ScenarioType=optional_int("scenario_type", scenario_type),
        )
        return await self.request("ScenarioGroupHistoryUpdateRequest", fields)

    async def skip(
        self,
        *,
        script_group_id: int | None = None,
        skip_point_script_count: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("scenario.skip requires confirm=True")
        fields = compact_fields(
            ScriptGroupId=optional_int("script_group_id", script_group_id),
            SkipPointScriptCount=optional_int("skip_point_script_count", skip_point_script_count),
        )
        return await self.request("ScenarioSkipRequest", fields)

    async def select(
        self,
        *,
        script_group_id: int | None = None,
        script_select_group: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("scenario.select requires confirm=True")
        fields = compact_fields(
            ScriptGroupId=optional_int("script_group_id", script_group_id),
            ScriptSelectGroup=optional_int("script_select_group", script_select_group),
        )
        return await self.request("ScenarioSelectRequest", fields)

    async def account_student_change(
        self,
        *,
        account_student: int | None = None,
        account_student_before: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("scenario.account_student_change requires confirm=True")
        fields = compact_fields(
            AccountStudent=optional_int("account_student", account_student),
            AccountStudentBefore=optional_int("account_student_before", account_student_before),
        )
        return await self.request("ScenarioAccountStudentChangeRequest", fields)

    async def lobby_student_change(
        self,
        *,
        lobby_students: list[int] | None = None,
        lobby_students_before: list[int] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("scenario.lobby_student_change requires confirm=True")
        fields = compact_fields(
            LobbyStudents=int_list("lobby_students", lobby_students) or None,
            LobbyStudentsBefore=int_list("lobby_students_before", lobby_students_before) or None,
        )
        return await self.request("ScenarioLobbyStudentChangeRequest", fields)

    async def special_lobby_change(
        self,
        *,
        memory_lobby_id: int | None = None,
        memory_lobby_id_before: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("scenario.special_lobby_change requires confirm=True")
        fields = compact_fields(
            MemoryLobbyId=optional_int("memory_lobby_id", memory_lobby_id),
            MemoryLobbyIdBefore=optional_int("memory_lobby_id_before", memory_lobby_id_before),
        )
        return await self.request("ScenarioSpecialLobbyChangeRequest", fields)

    async def enter(
        self,
        *,
        scenario_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("scenario.enter requires confirm=True")
        fields = compact_fields(
            ScenarioId=optional_int("scenario_id", scenario_id),
        )
        return await self.request("ScenarioEnterRequest", fields)

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
