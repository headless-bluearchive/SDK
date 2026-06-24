from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, optional_int


class AcademyService(GameService):
    async def get_info(self) -> dict[str, Any]:
        payload = await self.request("AcademyGetInfoRequest")
        return format_academy_info(payload)

    async def attend_schedule(self, *, zone_id: int | None = None, validate: bool = True) -> dict[str, Any]:
        resolved_zone_id = optional_int("zone_id", zone_id)
        if validate:
            resolved_zone_id = await self._resolve_zone_id(resolved_zone_id)
        if resolved_zone_id is None:
            raise UnsafeOperationError("zone_id is required")

        payload = await self.request("AcademyAttendScheduleRequest", {"ZoneId": resolved_zone_id})
        return format_academy_attend_schedule(payload)

    async def _resolve_zone_id(self, zone_id: int | None) -> int:
        info = await self.get_info()
        zone_ids = list(info["available_zone_ids"])
        attended_zone_ids = set(info["attended_zone_ids"])
        candidate_zone_ids = [value for value in zone_ids if value not in attended_zone_ids]
        if not zone_ids:
            raise UnsafeOperationError("no academy zone is present")
        if zone_id is None:
            if not candidate_zone_ids:
                raise UnsafeOperationError("no unvisited academy zone is present")
            if len(candidate_zone_ids) > 1:
                raise UnsafeOperationError("multiple academy zones exist; provide zone_id")
            return candidate_zone_ids[0]
        if zone_id not in zone_ids:
            raise UnsafeOperationError("zone_id is not present in current academy zones")
        if zone_id in attended_zone_ids:
            raise UnsafeOperationError("academy zone has already been attended")
        return zone_id


def format_academy_info(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AcademyDB",
        "AcademyLocationDBs",
    }
    return {
        "academy": payload.get("AcademyDB"),
        "locations": as_list(payload.get("AcademyLocationDBs")),
        "available_zone_ids": _zone_ids(payload.get("AcademyDB"), "ZoneVisitCharacterDBs"),
        "attended_zone_ids": _zone_ids(payload.get("AcademyDB"), "ZoneScheduleGroupRecords"),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def format_academy_attend_schedule(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AcademyDB",
        "ParcelResultDB",
        "ExtraRewards",
    }
    return {
        "academy": payload.get("AcademyDB"),
        "parcel_result": payload.get("ParcelResultDB"),
        "extra_rewards": as_list(payload.get("ExtraRewards")),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def _zone_ids(academy: Any, key: str) -> list[int]:
    if not isinstance(academy, dict):
        return []
    value = academy.get(key)
    if not isinstance(value, dict):
        return []
    result: list[int] = []
    for raw in value.keys():
        zone_id = optional_int("zone_id", raw)
        if zone_id is not None:
            result.append(zone_id)
    return result
