from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int, required_int


class CafeService(GameService):
    async def get(self, *, account_server_id: int | None = None) -> dict[str, Any]:
        account_id = optional_int("account_server_id", account_server_id)
        if account_id is None:
            account_id = optional_int("account_server_id", self.client.account_id)
        if account_id is None:
            raise UnsafeOperationError("account_server_id is required")

        payload = await self.request("CafeGetInfoRequest", {"AccountServerId": account_id})
        return format_cafe_get(payload)

    async def list_preset(self) -> dict[str, Any]:
        return await self.request("CafeListPresetRequest")

    async def preset_detail(self, *, preset_type: int, slot_id: int) -> dict[str, Any]:
        return await self.request(
            "CafePresetDetailRequest",
            {
                "PresetType": required_int("preset_type", preset_type),
                "SlotId": required_int("slot_id", slot_id),
            },
        )

    async def interact(
        self,
        *,
        cafe_db_id: int | None = None,
        character_id: int | None = None,
        validate: bool = True,
    ) -> dict[str, Any]:
        cafe_id = optional_int("cafe_db_id", cafe_db_id)
        char_id = optional_int("character_id", character_id)

        if validate:
            target = await self._resolve_interaction_target(cafe_db_id=cafe_id, character_id=char_id)
            cafe_id = target["CafeDBId"]
            char_id = target["CharacterId"]

        if cafe_id is None or char_id is None:
            raise UnsafeOperationError("cafe_db_id and character_id are required")

        payload = await self.request(
            "CafeInteractWithCharacterRequest",
            {"CafeDBId": cafe_id, "CharacterId": char_id},
        )
        return format_cafe_interact(payload)

    async def receive_currency(
        self,
        *,
        cafe_db_id: int | None = None,
        account_server_id: int | None = None,
        validate: bool = True,
    ) -> dict[str, Any]:
        account_id = optional_int("account_server_id", account_server_id)
        if account_id is None:
            account_id = optional_int("account_server_id", self.client.account_id)
        if account_id is None:
            raise UnsafeOperationError("account_server_id is required")

        cafe_id = optional_int("cafe_db_id", cafe_db_id)
        if validate:
            cafe_id = await self._resolve_cafe_db_id(cafe_id)
        if cafe_id is None:
            raise UnsafeOperationError("cafe_db_id is required")

        payload = await self.request(
            "CafeReceiveCurrencyRequest",
            {"AccountServerId": account_id, "CafeDBId": cafe_id},
        )
        return format_cafe_receive_currency(payload)

    async def trophy_history(self) -> dict[str, Any]:
        payload = await self.request("CafeTrophyHistoryRequest")
        return format_cafe_trophy_history(payload)

    async def ack(self, *, cafe_db_id: int | None = None, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.ack requires confirm=True")
        fields = compact_fields(
            CafeDBId=optional_int("cafe_db_id", cafe_db_id),
        )
        return await self.request("CafeAckRequest", fields)

    async def rename_preset(
        self,
        *,
        preset_name: str | None = None,
        preset_type: int | None = None,
        slot_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.rename_preset requires confirm=True")
        fields = compact_fields(
            PresetName=str(preset_name) if preset_name is not None else None,
            PresetType=optional_int("preset_type", preset_type),
            SlotId=optional_int("slot_id", slot_id),
        )
        return await self.request("CafeRenamePresetRequest", fields)

    async def clear_preset(
        self,
        *,
        preset_type: int | None = None,
        slot_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.clear_preset requires confirm=True")
        fields = compact_fields(
            PresetType=optional_int("preset_type", preset_type),
            SlotId=optional_int("slot_id", slot_id),
        )
        return await self.request("CafeClearPresetRequest", fields)

    async def update_preset_furniture(
        self,
        *,
        cafe_db_id: int | None = None,
        slot_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.update_preset_furniture requires confirm=True")
        fields = compact_fields(
            CafeDBId=optional_int("cafe_db_id", cafe_db_id),
            SlotId=optional_int("slot_id", slot_id),
        )
        return await self.request("CafeUpdatePresetFurnitureRequest", fields)

    async def apply_preset(
        self,
        *,
        cafe_db_id: int | None = None,
        preset_type: int | None = None,
        slot_id: int | None = None,
        use_other_cafe_furniture: bool | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.apply_preset requires confirm=True")
        fields = compact_fields(
            CafeDBId=optional_int("cafe_db_id", cafe_db_id),
            PresetType=optional_int("preset_type", preset_type),
            SlotId=optional_int("slot_id", slot_id),
            UseOtherCafeFurniture=use_other_cafe_furniture,
        )
        return await self.request("CafeApplyPresetRequest", fields)

    async def apply_template(
        self,
        *,
        cafe_db_id: int | None = None,
        template_id: int | None = None,
        use_other_cafe_furniture: bool | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.apply_template requires confirm=True")
        fields = compact_fields(
            CafeDBId=optional_int("cafe_db_id", cafe_db_id),
            TemplateId=optional_int("template_id", template_id),
            UseOtherCafeFurniture=use_other_cafe_furniture,
        )
        return await self.request("CafeApplyTemplateRequest", fields)

    async def open(self, *, cafe_id: int | None = None, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.open requires confirm=True")
        fields = compact_fields(
            CafeId=optional_int("cafe_id", cafe_id),
        )
        return await self.request("CafeOpenRequest", fields)

    async def travel(
        self,
        *,
        current_visiting_account_id: int | None = None,
        target_account_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.travel requires confirm=True")
        fields = compact_fields(
            CurrentVisitingAccountId=optional_int("current_visiting_account_id", current_visiting_account_id),
            TargetAccountId=optional_int("target_account_id", target_account_id),
        )
        return await self.request("CafeTravelRequest", fields)

    async def update_copy_preset_furniture(
        self,
        *,
        slot_id: int | None = None,
        target_account_id: int | None = None,
        target_cafe_db_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.update_copy_preset_furniture requires confirm=True")
        fields = compact_fields(
            SlotId=optional_int("slot_id", slot_id),
            TargetAccountId=optional_int("target_account_id", target_account_id),
            TargetCafeDBId=optional_int("target_cafe_db_id", target_cafe_db_id),
        )
        return await self.request("CafeUpdateCopyPresetFurnitureRequest", fields)

    async def rank_up(
        self,
        *,
        account_server_id: int | None = None,
        cafe_db_id: int | None = None,
        consume_request_db: Any = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.rank_up requires confirm=True")
        fields = compact_fields(
            AccountServerId=optional_int("account_server_id", account_server_id),
            CafeDBId=optional_int("cafe_db_id", cafe_db_id),
            ConsumeRequestDB=consume_request_db,
        )
        return await self.request("CafeRankUpRequest", fields)

    async def give_gift(
        self,
        *,
        cafe_db_id: int | None = None,
        character_unique_id: int | None = None,
        consume_request_db: Any = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.give_gift requires confirm=True")
        fields = compact_fields(
            CafeDBId=optional_int("cafe_db_id", cafe_db_id),
            CharacterUniqueId=optional_int("character_unique_id", character_unique_id),
            ConsumeRequestDB=consume_request_db,
        )
        return await self.request("CafeGiveGiftRequest", fields)

    async def summon_character(
        self,
        *,
        cafe_db_id: int | None = None,
        character_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.summon_character requires confirm=True")
        fields = compact_fields(
            CafeDBId=optional_int("cafe_db_id", cafe_db_id),
            CharacterServerId=optional_int("character_server_id", character_server_id),
        )
        return await self.request("CafeSummonCharacterRequest", fields)

    async def summon_character_ticket_use(
        self,
        *,
        cafe_db_id: int | None = None,
        character_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("cafe.summon_character_ticket_use requires confirm=True")
        fields = compact_fields(
            CafeDBId=optional_int("cafe_db_id", cafe_db_id),
            CharacterServerId=optional_int("character_server_id", character_server_id),
        )
        return await self.request("CafeSummonCharacterTicketUseRequest", fields)

    async def _resolve_interaction_target(
        self,
        *,
        cafe_db_id: int | None,
        character_id: int | None,
    ) -> dict[str, int]:
        state = await self.get()
        targets = [
            target
            for target in _interaction_targets(state["cafes"])
            if (cafe_db_id is None or target["CafeDBId"] == cafe_db_id)
            and (character_id is None or target["CharacterId"] == character_id)
        ]
        if not targets:
            raise UnsafeOperationError("no interactable cafe character is present")
        if len(targets) > 1 and (cafe_db_id is None or character_id is None):
            raise UnsafeOperationError("multiple cafe interaction targets exist; provide cafe_db_id and character_id")
        return targets[0]

    async def _resolve_cafe_db_id(self, cafe_db_id: int | None) -> int:
        state = await self.get()
        cafe_ids = [
            optional_int("CafeDBId", cafe.get("CafeDBId"))
            for cafe in state["cafes"]
            if isinstance(cafe, dict) and cafe.get("CafeDBId") is not None
        ]
        cafe_ids = [value for value in cafe_ids if value is not None]
        if not cafe_ids:
            raise UnsafeOperationError("no cafe is present")
        if cafe_db_id is None:
            return cafe_ids[0]
        if cafe_db_id not in cafe_ids:
            raise UnsafeOperationError("cafe_db_id is not present in current cafe list")
        return cafe_db_id


def format_cafe_get(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CafeDB",
        "CafeDBs",
        "FurnitureDBs",
    }
    cafes = as_list(payload.get("CafeDBs"))
    cafe = payload.get("CafeDB")
    if cafe is None and cafes:
        cafe = cafes[0]
    return {
        "cafe": cafe,
        "cafes": cafes,
        "furniture": as_list(payload.get("FurnitureDBs")),
        "interaction_targets": _interaction_targets(cafes),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def format_cafe_interact(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CafeDB",
        "CharacterDB",
        "ParcelResultDB",
    }
    return {
        "cafe": payload.get("CafeDB"),
        "character": payload.get("CharacterDB"),
        "parcel_result": payload.get("ParcelResultDB"),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def format_cafe_receive_currency(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CafeDB",
        "CafeDBs",
        "ParcelResultDB",
    }
    return {
        "cafe": payload.get("CafeDB"),
        "cafes": as_list(payload.get("CafeDBs")),
        "parcel_result": payload.get("ParcelResultDB"),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def format_cafe_trophy_history(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "RaidSeasonRankingHistoryDBs",
    }
    history = as_list(payload.get("RaidSeasonRankingHistoryDBs"))
    return {
        "raid_season_ranking_history": history,
        "count": len(history),
        "extra": extra_fields(payload, known_keys),
    }


def _interaction_targets(cafes: list[Any]) -> list[dict[str, int]]:
    targets: list[dict[str, int]] = []
    for cafe in cafes:
        if not isinstance(cafe, dict):
            continue
        cafe_id = optional_int("CafeDBId", cafe.get("CafeDBId"))
        if cafe_id is None:
            continue
        for visit in _visit_records(cafe.get("CafeVisitCharacterDBs")):
            if not isinstance(visit, dict) or not _visit_can_interact(visit):
                continue
            character_id = _visit_character_id(visit)
            if character_id is not None:
                targets.append({"CafeDBId": cafe_id, "CharacterId": character_id})
    return targets


def _visit_records(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, Mapping):
        if _looks_like_single_visit(value):
            return [dict(value)]
        records: list[dict[str, Any]] = []
        for key, item in value.items():
            if not isinstance(item, Mapping):
                continue
            record = dict(item)
            character_id = optional_int("character_id", key)
            if character_id is not None and "CharacterId" not in record:
                record["CharacterId"] = character_id
            records.append(record)
        return records
    return []


def _looks_like_single_visit(value: Mapping[str, Any]) -> bool:
    visit_keys = {
        "CharacterId",
        "CharacterUniqueId",
        "CharacterServerId",
        "ServerId",
        "UniqueId",
        "CanInteract",
        "Interactable",
        "IsInteractable",
        "CanReceive",
        "CanReward",
        "IsInteract",
        "Interacted",
        "IsInteracted",
        "LastInteractTime",
    }
    return any(key in value for key in visit_keys)


def _visit_can_interact(visit: dict[str, Any]) -> bool:
    for key in ("CanInteract", "Interactable", "IsInteractable", "CanReceive", "CanReward"):
        if key in visit:
            return visit.get(key) is True
    for key in ("IsInteract", "Interacted", "IsInteracted"):
        if key in visit:
            return visit.get(key) is False
    return True


def _visit_character_id(visit: dict[str, Any]) -> int | None:
    for key in ("CharacterId", "UniqueId", "CharacterUniqueId"):
        value = optional_int(key, visit.get(key))
        if value is not None:
            return value
    return None
