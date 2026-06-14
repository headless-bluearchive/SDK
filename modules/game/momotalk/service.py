from __future__ import annotations

from typing import Any
import asyncio
import json
from functools import lru_cache

from core.official_data import ACADEMY_FAVOR_SCHEDULE_DATA, ACADEMY_MESSANGER_DATA
from core.student_data import cached_student_name, student_names
from core.error import GameApiError, UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, extra_fields, normalize_id_map, optional_int, required_int

FAVOR_STORY_SUFFIXES = (2, 3, 5, 6, 8, 9, 15, 20)
MESSAGE_DETAIL_CONCURRENCY = 1
MESSAGE_CONDITION_NONE = 0
MESSAGE_CONDITION_FAVOR_RANK_UP = 1
MESSAGE_CONDITION_ACADEMY_SCHEDULE = 2
MESSAGE_CONDITION_ANSWER = 3
MESSAGE_CONDITION_FEEDBACK = 4


class MomoTalkService(GameService):
    async def status(
        self,
        *,
        character_ids: list[int] | None = None,
        include_message_details: bool = False,
        include_owned_without_outline: bool = True,
    ) -> dict[str, Any]:
        await student_names()
        outline = await self.outline()
        character_result = await self._owner.character.list()
        return await self._format_status(
            outline,
            character_result,
            character_ids=character_ids,
            include_message_details=include_message_details,
            include_owned_without_outline=include_owned_without_outline,
        )

    async def scan_messages(
        self,
        *,
        character_ids: list[int] | None = None,
        include_owned_without_outline: bool = True,
    ) -> dict[str, Any]:
        return await self.status(
            character_ids=character_ids,
            include_message_details=True,
            include_owned_without_outline=include_owned_without_outline,
        )

    async def unread_candidates(
        self,
        *,
        character_ids: list[int] | None = None,
        include_message_details: bool = False,
    ) -> dict[str, Any]:
        status = await self.status(
            character_ids=character_ids,
            include_message_details=include_message_details,
            include_owned_without_outline=True,
        )
        return {
            "characters": status["actionable"]["messages"],
            "count": len(status["actionable"]["messages"]),
            "exact_unread_count_available": status.get("exact_unread_count_available", False),
            "unread_count_source": status.get("unread_count_source"),
            "unread_total_count": status["actionable"].get("unread_total_count", 0),
            "reason": status["actionable"]["message_detection"],
            "next_step": "call client.momotalk.advance_dialog(...) with the returned advance_args",
        }

    async def claim_available_favor_stories(
        self,
        *,
        character_ids: list[int] | None = None,
        include_errors: bool = False,
        allow_heuristic: bool = False,
    ) -> dict[str, Any]:
        status = await self.status(character_ids=character_ids, include_message_details=False)
        if not status["actionable"]["exact_favor_story_detection"] and not allow_heuristic:
            raise UnsafeOperationError(
                "exact favor story detection is unavailable; pass allow_heuristic=True to try generated candidates"
            )
        successes = []
        errors = []
        for candidate in status["actionable"]["favor_story_candidates"]:
            schedule_id = candidate["schedule_id"]
            try:
                result = await self.complete_favor_schedule(schedule_id, refresh=True)
            except Exception as exc:
                if include_errors:
                    errors.append(_format_claim_error(candidate, exc))
                continue
            successes.append(
                {
                    "character_id": candidate["character_id"],
                    "character_name": candidate["character_name"],
                    "schedule_id": schedule_id,
                    "parcel_result": result.get("parcel_result"),
                    "favor_schedule_records": result.get("favor_schedule_records", {}).get(
                        candidate["character_id"],
                        [],
                    ),
                }
            )
        return {
            "claimed": successes,
            "claimed_count": len(successes),
            "errors": errors,
            "error_count": len(errors),
            "needs_refresh": True,
            "next_step": "call client.momotalk.status() again",
        }

    async def outline(self) -> dict[str, Any]:
        await student_names()
        payload = await self.request("MomoTalkOutLineRequest")
        return format_momotalk_outline(payload)

    async def messages(self, character_db_id: int) -> dict[str, Any]:
        await student_names()
        payload = await self.request(
            "MomoTalkMessageListRequest",
            {"CharacterDBId": required_int("character_db_id", character_db_id)},
        )
        return format_momotalk_messages(payload)

    async def read(
        self,
        character_db_id: int,
        last_read_message_group_id: int,
        *,
        chosen_message_id: int | None = None,
    ) -> dict[str, Any]:
        fields: dict[str, Any] = {
            "CharacterDBId": required_int("character_db_id", character_db_id),
            "LastReadMessageGroupId": required_int("last_read_message_group_id", last_read_message_group_id),
        }
        chosen_id = optional_int("chosen_message_id", chosen_message_id)
        if chosen_id is not None:
            fields["ChosenMessageId"] = chosen_id
        payload = await self.request("MomoTalkReadRequest", fields)
        result = format_momotalk_messages(payload)
        result["needs_refresh"] = True
        result["next_step"] = "call client.momotalk.outline() or client.momotalk.messages(character_db_id) again"
        return result

    async def advance_dialog(
        self,
        character_db_id: int,
        last_read_message_group_id: int,
        *,
        chosen_message_id: int | None = None,
    ) -> dict[str, Any]:
        return await self.read(
            character_db_id,
            last_read_message_group_id,
            chosen_message_id=chosen_message_id,
        )

    async def favor_schedule(self, schedule_id: int, *, refresh: bool = True) -> dict[str, Any]:
        payload = await self.request(
            "MomoTalkFavorScheduleRequest",
            {"ScheduleId": required_int("schedule_id", schedule_id)},
        )
        result = format_momotalk_favor_schedule(payload)
        result["requires_refresh_for_next_story"] = True
        result["next_step"] = "reopen MomoTalk with client.momotalk.outline() before trying the next favor story"
        if refresh:
            refreshed = await self.outline()
            result["refreshed_outline"] = refreshed
            result["needs_refresh"] = False
            result["has_favor_records"] = bool(refreshed["favor_schedule_records"])
        else:
            result["needs_refresh"] = True
        return result

    async def complete_favor_schedule(self, schedule_id: int, *, refresh: bool = True) -> dict[str, Any]:
        return await self.favor_schedule(schedule_id, refresh=refresh)

    async def refresh_student_names(self) -> dict[int, str]:
        return await student_names(refresh=True)

    async def _format_status(
        self,
        outline: dict[str, Any],
        character_result: dict[str, Any],
        *,
        character_ids: list[int] | None,
        include_message_details: bool,
        include_owned_without_outline: bool,
    ) -> dict[str, Any]:
        wanted = {required_int("character_id", item) for item in character_ids} if character_ids is not None else None
        characters = {
            character_id: item
            for item in character_result.get("characters", [])
            if isinstance(item, dict)
            for character_id in [_character_id(item)]
            if character_id is not None
        }
        outlines = {
            character_id: item
            for item in outline["outlines"]
            for character_id in [_outline_int(item, "CharacterId")]
            if character_id is not None
        }
        if wanted is not None:
            row_ids = [character_id for character_id in wanted if character_id in outlines or character_id in characters]
        elif include_owned_without_outline:
            row_ids = list(dict.fromkeys([*outlines.keys(), *characters.keys()]))
        else:
            row_ids = list(outlines.keys())

        rows = []
        master = _load_momotalk_master_data()
        for character_id in row_ids:
            outline_item = outlines.get(character_id)
            row = _format_status_row(
                outline_item,
                characters.get(character_id),
                outline["favor_schedule_records"].get(character_id, []),
                master=master,
            )
            rows.append(row)
        if include_message_details:
            await self._attach_message_details(rows)
        actionable = _format_actionable(rows, include_message_details=include_message_details)
        return {
            "characters": rows,
            "count": len(rows),
            "actionable": actionable,
            "outline_count": outline["outline_count"],
            "owned_character_count": character_result["count"],
            "exact_unread_count_available": master["ready"],
            "unread_count_source": master["source"],
        }

    async def _attach_message_details(self, rows: list[dict[str, Any]]) -> None:
        semaphore = asyncio.Semaphore(MESSAGE_DETAIL_CONCURRENCY)

        async def load(row: dict[str, Any]) -> None:
            if row["character_db_id"] is None:
                return
            async with semaphore:
                try:
                    message_result = await self.messages(row["character_db_id"])
                except GameApiError as exc:
                    row["message_error"] = {
                        "error_code": getattr(exc, "error_code", None),
                        "error_name": getattr(exc, "error_name", None),
                    }
                    return
            row["message"] = {
                "choice_count": message_result["choice_count"],
                "choice_message_group_ids": [
                    group_id
                    for group_id in (_choice_int(item, "MessageGroupId") for item in message_result["choices"])
                    if group_id is not None
                ],
                "max_choice_message_group_id": _max_choice_group_id(message_result["choices"]),
                "can_read_next": message_result["can_read_next"],
            }
            row["readable_message"] = _message_action(row)

        await asyncio.gather(*(load(row) for row in rows))


def format_momotalk_outline(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "MomoTalkOutLineDBs",
        "FavorScheduleRecords",
    }
    outlines = [item for item in as_list(payload.get("MomoTalkOutLineDBs")) if isinstance(item, dict)]
    records = normalize_id_map(payload.get("FavorScheduleRecords"))
    formatted_outlines = [_with_character_name(item) for item in outlines]
    return {
        "outlines": formatted_outlines,
        "favor_schedule_records": records,
        "outline_count": len(outlines),
        "characters_with_favor_records": [
            {
                "character_id": character_id,
                "character_name": cached_student_name(character_id),
                "schedule_ids": schedule_ids,
                "count": len(schedule_ids),
            }
            for character_id, schedule_ids in records.items()
            if schedule_ids
        ],
        "extra": extra_fields(payload, known_keys),
    }


def format_momotalk_messages(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "MomoTalkOutLineDB",
        "MomoTalkChoiceDBs",
    }
    outline = payload.get("MomoTalkOutLineDB")
    choices = [item for item in as_list(payload.get("MomoTalkChoiceDBs")) if isinstance(item, dict)]
    character_id = _outline_int(outline, "CharacterId")
    return {
        "outline": _with_character_name(outline) if isinstance(outline, dict) else None,
        "choices": choices,
        "choice_count": len(choices),
        "character_db_id": _outline_int(outline, "CharacterDBId"),
        "character_id": character_id,
        "character_name": cached_student_name(character_id) if character_id is not None else None,
        "latest_message_group_id": _outline_int(outline, "LatestMessageGroupId"),
        "chosen_message_id": _outline_int(outline, "ChosenMessageId"),
        "can_read_next": _outline_int(outline, "LatestMessageGroupId") is not None,
        "extra": extra_fields(payload, known_keys),
    }


def format_momotalk_favor_schedule(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ParcelResultDB",
        "FavorScheduleRecords",
    }
    records = normalize_id_map(payload.get("FavorScheduleRecords"))
    return {
        "parcel_result": payload.get("ParcelResultDB"),
        "favor_schedule_records": records,
        "characters_with_favor_records": [
            {
                "character_id": character_id,
                "character_name": cached_student_name(character_id),
                "schedule_ids": schedule_ids,
                "count": len(schedule_ids),
            }
            for character_id, schedule_ids in records.items()
            if schedule_ids
        ],
        "extra": extra_fields(payload, known_keys),
    }


def _outline_int(outline: Any, key: str) -> int | None:
    if not isinstance(outline, dict):
        return None
    try:
        return optional_int(key, outline.get(key))
    except UnsafeOperationError:
        return None


def _with_character_name(outline: dict[str, Any]) -> dict[str, Any]:
    result = dict(outline)
    character_id = _outline_int(result, "CharacterId")
    if character_id is not None:
        result["CharacterName"] = cached_student_name(character_id)
    return result


def _format_status_row(
    outline: dict[str, Any] | None,
    character: dict[str, Any] | None,
    schedule_ids: list[int],
    *,
    master: dict[str, Any] | None = None,
) -> dict[str, Any]:
    character_id = _outline_int(outline, "CharacterId") or _character_id(character or {})
    row = {
        "character_id": character_id,
        "character_db_id": _outline_int(outline, "CharacterDBId") or _character_int(character, "ServerId"),
        "character_name": cached_student_name(character_id) if character_id is not None else None,
        "favor_rank": _character_int(character, "FavorRank"),
        "has_outline": isinstance(outline, dict),
        "latest_message_group_id": _outline_int(outline, "LatestMessageGroupId"),
        "chosen_message_id": _outline_int(outline, "ChosenMessageId"),
        "last_update_date": outline.get("LastUpdateDate") if isinstance(outline, dict) else None,
        "completed_favor_schedule_ids": schedule_ids,
        "completed_favor_schedule_count": len(schedule_ids),
        "favor_story_candidates": [],
        "unread_count": 0,
        "unread_items": [],
        "readable_message": None,
    }
    if master and master.get("ready"):
        _apply_master_momotalk_state(row, master)
    else:
        row["favor_story_candidates"] = _favor_story_candidates(row)
    row["readable_message"] = _message_action(row)
    return row


def _format_actionable(rows: list[dict[str, Any]], *, include_message_details: bool) -> dict[str, Any]:
    messages = [
        action
        for action in (row.get("readable_message") for row in rows)
        if isinstance(action, dict)
    ]
    favor_story_candidates = [
        candidate
        for row in rows
        for candidate in row.get("favor_story_candidates", [])
    ]
    favor_stories = [candidate for candidate in favor_story_candidates if candidate.get("verified")]
    return {
        "messages": messages,
        "message_count": len(messages),
        "message_detection": (
            "computed from MomoTalk outline and Academy master data; MessageList detail scanned"
            if include_message_details
            else "computed from MomoTalk outline and Academy master data"
        ),
        "favor_stories": favor_stories,
        "favor_story_count": len(favor_stories),
        "favor_story_candidates": favor_story_candidates,
        "favor_story_candidate_count": len(favor_story_candidates),
        "favor_story_detection": "computed from AcademyFavorSchedule and current MomoTalk outline",
        "exact_favor_story_detection": any(candidate.get("confidence") == "exact" for candidate in favor_story_candidates),
        "unread_total_count": sum(int(row.get("unread_count") or 0) for row in rows),
    }


def _message_action(row: dict[str, Any]) -> dict[str, Any] | None:
    unread_items = [item for item in row.get("unread_items", []) if isinstance(item, dict)]
    if unread_items:
        first = unread_items[0]
        action: dict[str, Any] = {
            "character_id": row["character_id"],
            "character_name": row["character_name"],
            "character_db_id": row["character_db_id"],
            "unread_count": row.get("unread_count", len(unread_items)),
            "unread_items": unread_items,
            "reason": first.get("reason", "Academy master data found unread MomoTalk state"),
        }
        if first.get("type") == "message":
            action["advance_args"] = {
                "character_db_id": row["character_db_id"],
                "last_read_message_group_id": row.get("latest_message_group_id"),
            }
        elif first.get("type") == "choice":
            action["choice_required"] = True
            action["choices"] = first.get("choices", [])
        elif first.get("type") == "favor_story":
            action["complete_args"] = {"schedule_id": first.get("schedule_id")}
        return action

    if not row.get("has_outline") or row.get("latest_message_group_id") is None:
        return None
    latest = row.get("latest_message_group_id")
    chosen = row.get("chosen_message_id")
    if chosen is None:
        return None
    return {
        "character_id": row["character_id"],
        "character_name": row["character_name"],
        "character_db_id": row["character_db_id"],
        "unread_count": 1,
        "unread_items": [
            {
                "type": "choice",
                "message_group_id": latest,
                "chosen_message_id": chosen,
                "reason": "outline has a pending chosen message",
            }
        ],
        "latest_message_group_id": latest,
        "chosen_message_id": chosen,
        "reason": "outline has a pending chosen message",
        "advance_args": {
            "character_db_id": row["character_db_id"],
            "last_read_message_group_id": latest,
            "chosen_message_id": chosen,
        },
    }


def _apply_master_momotalk_state(row: dict[str, Any], master: dict[str, Any]) -> None:
    character_id = row.get("character_id")
    latest_group_id = row.get("latest_message_group_id")
    completed = set(row.get("completed_favor_schedule_ids") or [])
    favor_rank = row.get("favor_rank")
    row["favor_story_candidates"] = _exact_favor_story_candidates(row, master)
    if character_id is None or latest_group_id is None:
        return

    unread_items: list[dict[str, Any]] = []
    current_group = _message_group(master, latest_group_id)
    current_last = _last_message(current_group)
    if current_last:
        schedule_id = _optional_positive_int(current_last.get("favor_schedule_id"))
        if schedule_id is not None and schedule_id not in completed:
            unread_items.append(
                {
                    "type": "favor_story",
                    "message_group_id": latest_group_id,
                    "schedule_id": schedule_id,
                    "reason": "latest message group points to an uncompleted favor story",
                }
            )

    visited: set[int] = set()
    frontier = _next_group_ids(current_group)
    while frontier:
        group_id = frontier.pop(0)
        if group_id in visited:
            continue
        visited.add(group_id)
        group = _message_group(master, group_id)
        first = _first_message(group)
        if first is None:
            continue
        if _message_allowed_for_new_arrival(first, favor_rank=favor_rank, completed_schedule_ids=completed):
            unread_items.append(
                {
                    "type": "message",
                    "message_group_id": group_id,
                    "message_count": len(group),
                    "reason": "next message group is available from current outline",
                }
            )
            frontier.extend(next_id for next_id in _next_group_ids(group) if next_id not in visited)
            continue
        if _message_condition(first) == MESSAGE_CONDITION_ANSWER:
            unread_items.append(
                {
                    "type": "choice",
                    "message_group_id": group_id,
                    "choices": [
                        {
                            "chosen_message_id": _message_id(message),
                            "message": _display_message(message),
                        }
                        for message in group
                        if _message_id(message) is not None
                    ],
                    "reason": "next message group requires a reply choice",
                }
            )
        break

    row["unread_items"] = unread_items
    row["unread_count"] = len(unread_items)


def _exact_favor_story_candidates(row: dict[str, Any], master: dict[str, Any]) -> list[dict[str, Any]]:
    character_id = row.get("character_id")
    if character_id is None:
        return []
    completed = set(row.get("completed_favor_schedule_ids") or [])
    favor_rank = row.get("favor_rank")
    candidates = []
    for item in master["favor_by_character"].get(character_id, []):
        schedule_id = _optional_positive_int(item.get("id"))
        required_rank = _optional_positive_int(item.get("favor_rank")) or 0
        if schedule_id is None or schedule_id in completed:
            continue
        available = favor_rank is not None and int(favor_rank) >= required_rank
        candidates.append(
            {
                "character_id": character_id,
                "character_name": row.get("character_name"),
                "schedule_id": schedule_id,
                "required_favor_rank": required_rank,
                "current_favor_rank": favor_rank,
                "available": available,
                "confidence": "exact",
                "verified": available,
                "reason": "matched AcademyFavorSchedule master data",
            }
        )
    return candidates


@lru_cache(maxsize=1)
def _load_momotalk_master_data() -> dict[str, Any]:
    if not ACADEMY_MESSANGER_DATA.exists() or not ACADEMY_FAVOR_SCHEDULE_DATA.exists():
        return {
            "ready": False,
            "source": "Academy master data is missing; call await client.prepare_data()",
            "message_by_group": {},
            "favor_by_character": {},
        }
    messages = json.loads(ACADEMY_MESSANGER_DATA.read_text(encoding="utf-8"))
    schedules = json.loads(ACADEMY_FAVOR_SCHEDULE_DATA.read_text(encoding="utf-8"))
    message_by_group: dict[int, list[dict[str, Any]]] = {}
    for item in messages:
        if not isinstance(item, dict):
            continue
        group_id = _optional_positive_int(item.get("message_group_id"))
        if group_id is None:
            continue
        message_by_group.setdefault(group_id, []).append(item)
    for group in message_by_group.values():
        group.sort(key=lambda item: _message_id(item) or 0)

    favor_by_character: dict[int, list[dict[str, Any]]] = {}
    for item in schedules:
        if not isinstance(item, dict):
            continue
        character_id = _optional_positive_int(item.get("character_id"))
        if character_id is None:
            continue
        favor_by_character.setdefault(character_id, []).append(item)
    for rows in favor_by_character.values():
        rows.sort(key=lambda item: ((_optional_positive_int(item.get("favor_rank")) or 0), _optional_positive_int(item.get("id")) or 0))
    return {
        "ready": True,
        "source": "computed from MomoTalk outline plus core/data/academy_messanger.json and academy_favor_schedule.json",
        "message_by_group": message_by_group,
        "favor_by_character": favor_by_character,
    }


def _message_group(master: dict[str, Any], group_id: int) -> list[dict[str, Any]]:
    return list(master["message_by_group"].get(group_id, []))


def _first_message(group: list[dict[str, Any]]) -> dict[str, Any] | None:
    return group[0] if group else None


def _last_message(group: list[dict[str, Any]]) -> dict[str, Any] | None:
    return group[-1] if group else None


def _next_group_ids(group: list[dict[str, Any]]) -> list[int]:
    result = []
    for item in group:
        next_id = _optional_positive_int(item.get("next_group_id"))
        if next_id is not None and next_id not in result:
            result.append(next_id)
    return result


def _message_allowed_for_new_arrival(
    message: dict[str, Any],
    *,
    favor_rank: int | None,
    completed_schedule_ids: set[int],
) -> bool:
    condition = _message_condition(message)
    pre_schedule_id = _optional_positive_int(message.get("pre_condition_favor_schedule_id"))
    if pre_schedule_id is not None and pre_schedule_id not in completed_schedule_ids:
        return False
    if condition in (MESSAGE_CONDITION_NONE, MESSAGE_CONDITION_FEEDBACK, MESSAGE_CONDITION_ACADEMY_SCHEDULE):
        return True
    if condition == MESSAGE_CONDITION_FAVOR_RANK_UP:
        required = _optional_positive_int(message.get("condition_value")) or 0
        return favor_rank is not None and int(favor_rank) >= required
    return False


def _message_condition(message: dict[str, Any]) -> int:
    value = message.get("message_condition")
    try:
        return int(value)
    except (TypeError, ValueError):
        return MESSAGE_CONDITION_NONE


def _message_id(message: dict[str, Any]) -> int | None:
    return _optional_positive_int(message.get("id"))


def _optional_positive_int(value: Any) -> int | None:
    try:
        result = int(value)
    except (TypeError, ValueError):
        return None
    return result if result > 0 else None


def _display_message(message: dict[str, Any]) -> str | None:
    for key in ("message_tw", "message_en", "message_jp", "message_kr"):
        value = message.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _favor_story_candidates(row: dict[str, Any]) -> list[dict[str, Any]]:
    character_id = row.get("character_id")
    if character_id is None:
        return []
    completed = set(row.get("completed_favor_schedule_ids") or [])
    result = []
    for suffix in FAVOR_STORY_SUFFIXES:
        schedule_id = character_id * 10 + suffix
        if schedule_id in completed:
            continue
        result.append(
            {
                "character_id": character_id,
                "character_name": row.get("character_name"),
                "schedule_id": schedule_id,
                "suffix": suffix,
                "confidence": "heuristic",
                "verified": False,
                "reason": "candidate generated from observed favor schedule id suffixes",
            }
        )
    return result


def _format_claim_error(candidate: dict[str, Any], exc: Exception) -> dict[str, Any]:
    return {
        "character_id": candidate["character_id"],
        "character_name": candidate["character_name"],
        "schedule_id": candidate["schedule_id"],
        "error_type": type(exc).__name__,
        "error_code": getattr(exc, "error_code", None),
        "error_name": getattr(exc, "error_name", None),
    }


def _character_id(character: dict[str, Any]) -> int | None:
    for key in ("UniqueId", "CharacterId", "Id"):
        value = _character_int(character, key)
        if value is not None:
            return value
    return None


def _character_int(character: dict[str, Any] | None, key: str) -> int | None:
    if not isinstance(character, dict):
        return None
    try:
        return optional_int(key, character.get(key))
    except UnsafeOperationError:
        return None


def _choice_int(choice: Any, key: str) -> int | None:
    if not isinstance(choice, dict):
        return None
    try:
        return optional_int(key, choice.get(key))
    except UnsafeOperationError:
        return None


def _max_choice_group_id(choices: list[dict[str, Any]]) -> int | None:
    groups = [
        group_id
        for group_id in (_choice_int(choice, "MessageGroupId") for choice in choices)
        if group_id is not None
    ]
    return max(groups) if groups else None
