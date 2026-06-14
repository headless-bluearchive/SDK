from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService


class AttendanceService(GameService):
    def status(self) -> dict[str, Any]:
        cache = self._cache()
        if cache is None:
            return {
                "available": False,
                "source": None,
                "reason": "attendance cache is not available; login again or restore a session containing Account_Auth attendance fields",
                "attendance_book_rewards": [],
                "attendance_history": [],
                "claimable_rewards": [],
            }
        rewards = _as_list(cache.get("AttendanceBookRewards"))
        history = _as_list(cache.get("AttendanceHistoryDBs"))
        return {
            "available": True,
            "source": cache.get("source", "Account_Auth"),
            "attendance_book_rewards": rewards,
            "attendance_history": history,
            "claimable_rewards": _claimable_rewards(rewards, history),
        }

    async def reward(
        self,
        *,
        attendance_book_unique_id: int | None = None,
        day: int | None = None,
        day_by_book_unique_id: Mapping[int, int] | Mapping[str, int] | None = None,
    ) -> dict[str, Any]:
        status = self.status()
        if not status["available"]:
            raise UnsafeOperationError("attendance cache is not available")

        claim = _resolve_claim(
            status["claimable_rewards"],
            attendance_book_unique_id=attendance_book_unique_id,
            day=day,
            day_by_book_unique_id=day_by_book_unique_id,
        )
        payload = await self.request("AttendanceRewardRequest", claim)
        self._update_cache_from_payload(payload)
        return format_attendance_reward(payload)

    claim = reward

    def _cache(self) -> dict[str, Any] | None:
        result = getattr(self._owner, "result", None)
        attendance = getattr(result, "attendance", None)
        cache = extract_attendance_cache(attendance)
        if cache is not None:
            return cache
        session = getattr(result, "session", None)
        if isinstance(session, Mapping):
            return extract_attendance_cache(session.get("attendance"))
        return None

    def _update_cache_from_payload(self, payload: dict[str, Any]) -> None:
        cache = extract_attendance_cache(payload)
        if cache is None:
            return
        result = getattr(self._owner, "result", None)
        if result is None:
            return
        object.__setattr__(result, "attendance", cache)
        if isinstance(result.session, dict):
            result.session["attendance"] = cache


def extract_attendance_cache(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    rewards = value.get("AttendanceBookRewards")
    history = value.get("AttendanceHistoryDBs")
    if rewards is None and history is None:
        nested = _find_mapping_with_any_key(value, {"AttendanceBookRewards", "AttendanceHistoryDBs"})
        if not nested:
            return None
        rewards = nested.get("AttendanceBookRewards")
        history = nested.get("AttendanceHistoryDBs")
    return {
        "source": str(value.get("source") or "Account_Auth"),
        "AttendanceBookRewards": _as_list(rewards),
        "AttendanceHistoryDBs": _as_list(history),
    }


def format_attendance_reward(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AttendanceBookRewards",
        "AttendanceHistoryDBs",
        "ParcelResultDB",
    }
    return {
        "attendance_book_rewards": _as_list(payload.get("AttendanceBookRewards")),
        "attendance_history": _as_list(payload.get("AttendanceHistoryDBs")),
        "parcel_result": payload.get("ParcelResultDB"),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def _resolve_claim(
    claimable_rewards: list[dict[str, Any]],
    *,
    attendance_book_unique_id: int | None,
    day: int | None,
    day_by_book_unique_id: Mapping[int, int] | Mapping[str, int] | None,
) -> dict[str, Any]:
    explicit_book_id = _optional_int("attendance_book_unique_id", attendance_book_unique_id)
    explicit_day = _optional_int("day", day)
    explicit_day_map = _day_map(day_by_book_unique_id)

    matching = [
        reward
        for reward in claimable_rewards
        if (explicit_book_id is None or _optional_int("AttendanceBookUniqueId", reward.get("AttendanceBookUniqueId")) == explicit_book_id)
        and (explicit_day is None or _optional_int("Day", reward.get("Day")) == explicit_day)
    ]
    if not matching:
        raise UnsafeOperationError("attendance status does not contain a claimable reward matching the requested fields")
    if len(matching) > 1 and (explicit_book_id is None or explicit_day is None):
        raise UnsafeOperationError("multiple claimable attendance rewards exist; provide attendance_book_unique_id and day")

    selected = matching[0]
    book_id = explicit_book_id if explicit_book_id is not None else _optional_int("AttendanceBookUniqueId", selected.get("AttendanceBookUniqueId"))
    selected_day = explicit_day if explicit_day is not None else _optional_int("Day", selected.get("Day"))
    selected_day_map = explicit_day_map if explicit_day_map is not None else _extract_day_by_book_unique_id(selected)
    if book_id is None or selected_day is None or selected_day_map is None:
        raise UnsafeOperationError("attendance reward requires AttendanceBookUniqueId, Day, and DayByBookUniqueId")
    return {
        "AttendanceBookUniqueId": book_id,
        "Day": selected_day,
        "DayByBookUniqueId": selected_day_map,
    }


def _claimable_rewards(rewards: list[Any], history: list[Any]) -> list[dict[str, Any]]:
    claimed_keys = _claimed_keys(history)
    history_by_book = _history_by_book(history)
    claimable: list[dict[str, Any]] = []
    for reward in rewards:
        if not isinstance(reward, Mapping):
            continue
        item = dict(reward)
        if _is_claimed(item, claimed_keys):
            continue
        if _has_explicit_claimable_flag(item):
            claimable.append(item)
            continue
        inferred = _infer_claimable_reward(item, history_by_book)
        if inferred is not None:
            claimable.append(inferred)
    return claimable


def _infer_claimable_reward(
    book: Mapping[str, Any],
    history_by_book: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any] | None:
    book_id = _optional_int("UniqueId", book.get("UniqueId"))
    if book_id is None:
        return None
    book_size = _optional_int("BookSize", book.get("BookSize"))
    if book_size is None:
        return None
    if not _book_is_active(book):
        return None
    history = history_by_book.get(book_id)
    attended = _attended_day_map(history)
    if _already_attended_today(attended):
        return None
    next_day = _next_attend_day(book, attended)
    if next_day is None:
        return None
    if next_day > book_size:
        return None
    item = dict(book)
    item["AttendanceBookUniqueId"] = book_id
    item["Day"] = next_day
    item["DayByBookUniqueId"] = {book_id: next_day}
    item["IsClaimable"] = True
    item["claim_source"] = "AttendanceHistoryDBs.AttendedDay"
    return item


def _has_explicit_claimable_flag(item: Mapping[str, Any]) -> bool:
    true_names = {
        "CanReward",
        "CanReceive",
        "CanClaim",
        "IsRewardable",
        "IsReceivable",
        "IsClaimable",
        "Rewardable",
        "Receivable",
        "Claimable",
    }
    for name in true_names:
        if item.get(name) is True:
            return True
    if item.get("Received") is False or item.get("IsReceived") is False or item.get("Rewarded") is False:
        return _optional_int("AttendanceBookUniqueId", item.get("AttendanceBookUniqueId")) is not None and _optional_int("Day", item.get("Day")) is not None
    return False


def _is_claimed(item: Mapping[str, Any], claimed_keys: set[tuple[int, int]]) -> bool:
    book_id = _optional_int("AttendanceBookUniqueId", item.get("AttendanceBookUniqueId"))
    day = _optional_int("Day", item.get("Day"))
    if book_id is not None and day is not None and (book_id, day) in claimed_keys:
        return True
    return item.get("Received") is True or item.get("IsReceived") is True or item.get("Rewarded") is True


def _claimed_keys(history: list[Any]) -> set[tuple[int, int]]:
    keys: set[tuple[int, int]] = set()
    for item in history:
        if not isinstance(item, Mapping):
            continue
        book_id = _optional_int("AttendanceBookUniqueId", item.get("AttendanceBookUniqueId"))
        day = _optional_int("Day", item.get("Day"))
        if book_id is not None and day is not None:
            keys.add((book_id, day))
        attended = _attended_day_map(item)
        if book_id is not None:
            keys.update((book_id, attended_day) for attended_day in attended)
    return keys


def _history_by_book(history: list[Any]) -> dict[int, Mapping[str, Any]]:
    result: dict[int, Mapping[str, Any]] = {}
    for item in history:
        if not isinstance(item, Mapping):
            continue
        book_id = _optional_int("AttendanceBookUniqueId", item.get("AttendanceBookUniqueId"))
        if book_id is not None:
            result[book_id] = item
    return result


def _attended_day_map(history: Mapping[str, Any] | None) -> dict[int, Any]:
    if not isinstance(history, Mapping):
        return {}
    value = history.get("AttendedDay")
    if not isinstance(value, Mapping):
        return {}
    result: dict[int, Any] = {}
    for key, item in value.items():
        day = _optional_int("AttendedDay key", key)
        if day is not None:
            result[day] = item
    return result


def _next_attend_day(book: Mapping[str, Any], attended: Mapping[int, Any]) -> int | None:
    if attended:
        return max(attended) + 1
    start = _parse_datetime(book.get("StartDate"))
    if start is None or _optional_int("UniqueId", book.get("UniqueId")) == 1:
        return 1
    now = datetime.now()
    if _attendance_day_key(now) < _attendance_day_key(start):
        return None
    return (now.date() - start.date()).days + 1


def _already_attended_today(attended: Mapping[int, Any]) -> bool:
    today = _attendance_day_key(datetime.now())
    for value in attended.values():
        attended_at = _parse_datetime(value)
        if attended_at is not None and _attendance_day_key(attended_at) == today:
            return True
    return False


def _book_is_active(book: Mapping[str, Any]) -> bool:
    now = datetime.now()
    start = _parse_datetime(book.get("StartDate"))
    end = _parse_datetime(book.get("EndDate"))
    if start is not None and now < start:
        return False
    if end is not None and now >= end:
        return False
    return True


def _attendance_day_key(value: datetime) -> datetime.date:
    if value.hour < 4:
        value = value - timedelta(days=1)
    return value.date()


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _extract_day_by_book_unique_id(item: Mapping[str, Any]) -> dict[int, int] | None:
    value = item.get("DayByBookUniqueId")
    if isinstance(value, Mapping):
        return _day_map(value)
    book_id = _optional_int("AttendanceBookUniqueId", item.get("AttendanceBookUniqueId"))
    day = _optional_int("Day", item.get("Day"))
    day_unique_id = _optional_int(
        "DayByBookUniqueId",
        item.get("DayByBookUniqueId") or item.get("AttendanceDayUniqueId") or item.get("RewardUniqueId"),
    )
    if book_id is not None and day_unique_id is not None:
        return {book_id: day_unique_id}
    if book_id is not None and day is not None:
        return {book_id: day}
    return None


def _day_map(value: Mapping[int, int] | Mapping[str, int] | None) -> dict[int, int] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise UnsafeOperationError("day_by_book_unique_id must be a mapping")
    result: dict[int, int] = {}
    for key, item in value.items():
        result[_required_int("day_by_book_unique_id key", key)] = _required_int("day_by_book_unique_id value", item)
    if not result:
        raise UnsafeOperationError("day_by_book_unique_id must not be empty")
    return result


def _find_mapping_with_any_key(value: Any, keys: set[str]) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        if any(key in value for key in keys):
            return value
        for nested in value.values():
            found = _find_mapping_with_any_key(nested, keys)
            if found is not None:
                return found
    if isinstance(value, list):
        for nested in value:
            found = _find_mapping_with_any_key(nested, keys)
            if found is not None:
                return found
    return None


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _required_int(name: str, value: Any) -> int:
    result = _optional_int(name, value)
    if result is None:
        raise UnsafeOperationError(f"{name} is required")
    return result


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
