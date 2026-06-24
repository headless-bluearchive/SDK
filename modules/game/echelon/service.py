from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int


class EchelonService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("EchelonListRequest")
        return format_echelon_list(payload)

    async def preset_list(self, *, echelon_extension_type: int | None = None) -> dict[str, Any]:
        fields = compact_fields(EchelonExtensionType=optional_int("echelon_extension_type", echelon_extension_type))
        payload = await self.request("EchelonPresetListRequest", fields)
        return format_echelon_preset_list(payload)

    async def save(
        self,
        *,
        assist_use_infos: Any = None,
        echelon_db: Any = None,
        is_practice: bool | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("echelon.save requires confirm=True")
        fields = compact_fields(
            AssistUseInfos=assist_use_infos,
            EchelonDB=echelon_db,
            IsPractice=is_practice,
        )
        return await self.request("EchelonSaveRequest", fields)

    async def preset_save(
        self,
        *,
        preset_db: Any = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("echelon.preset_save requires confirm=True")
        fields = compact_fields(
            PresetDB=preset_db,
        )
        return await self.request("EchelonPresetSaveRequest", fields)

    async def preset_group_rename(
        self,
        *,
        extension_type: int | None = None,
        preset_group_index: int | None = None,
        preset_group_label: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("echelon.preset_group_rename requires confirm=True")
        fields = compact_fields(
            ExtensionType=optional_int("extension_type", extension_type),
            PresetGroupIndex=optional_int("preset_group_index", preset_group_index),
            PresetGroupLabel=str(preset_group_label) if preset_group_label is not None else None,
        )
        return await self.request("EchelonPresetGroupRenameRequest", fields)


def format_echelon_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "EchelonDBs",
        "EchelonPresetDBs",
    }
    echelons = as_list(payload.get("EchelonDBs"))
    presets = as_list(payload.get("EchelonPresetDBs"))
    return {
        "echelons": echelons,
        "presets": presets,
        "count": len(echelons),
        "preset_count": len(presets),
        "extra": extra_fields(payload, known_keys),
    }


def format_echelon_preset_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "PresetGroupDBs",
    }
    groups = as_list(payload.get("PresetGroupDBs"))
    return {
        "preset_groups": groups,
        "count": len(groups),
        "extra": extra_fields(payload, known_keys),
    }
