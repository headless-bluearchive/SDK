from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class CafeService(GameService):
    async def get(self, *, account_server_id: int | None = None) -> dict[str, Any]:
        account_id = _optional_int("account_server_id", account_server_id)
        if account_id is None:
            account_id = _optional_int("account_server_id", self.client.account_id)
        if account_id is None:
            raise UnsafeOperationError("account_server_id is required")

        payload = await self.request("CafeGetInfoRequest", {"AccountServerId": account_id})
        return format_cafe_get(payload)

    async def interact(
        self,
        *,
        cafe_db_id: int | None = None,
        character_id: int | None = None,
        validate: bool = True,
    ) -> dict[str, Any]:
        cafe_id = _optional_int("cafe_db_id", cafe_db_id)
        char_id = _optional_int("character_id", character_id)

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
        account_id = _optional_int("account_server_id", account_server_id)
        if account_id is None:
            account_id = _optional_int("account_server_id", self.client.account_id)
        if account_id is None:
            raise UnsafeOperationError("account_server_id is required")

        cafe_id = _optional_int("cafe_db_id", cafe_db_id)
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
            _optional_int("CafeDBId", cafe.get("CafeDBId"))
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
    cafes = _as_list(payload.get("CafeDBs"))
    cafe = payload.get("CafeDB")
    if cafe is None and cafes:
        cafe = cafes[0]
    return {
        "cafe": cafe,
        "cafes": cafes,
        "furniture": _as_list(payload.get("FurnitureDBs")),
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
        "cafes": _as_list(payload.get("CafeDBs")),
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
        cafe_id = _optional_int("CafeDBId", cafe.get("CafeDBId"))
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
            character_id = _optional_int("character_id", key)
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
        value = _optional_int(key, visit.get(key))
        if value is not None:
            return value
    return None


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _optional_int(name: str, value: Any) -> int | None:
    if value is None:
        return None
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise UnsafeOperationError(f"{name} must be an integer") from exc
    if result < 0:
        raise UnsafeOperationError(f"{name} must not be negative")
    return result
