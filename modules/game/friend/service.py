from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, int_list, optional_int, required_int


class FriendService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("FriendListRequest")
        return format_friend_list(payload)

    async def detailed_info(self, friend_account_id: int) -> dict[str, Any]:
        payload = await self.request(
            "FriendGetFriendDetailedInfoRequest",
            {"FriendAccountId": required_int("friend_account_id", friend_account_id)},
        )
        return format_friend_detailed_info(payload)

    async def id_card(self) -> dict[str, Any]:
        payload = await self.request("FriendGetIdCardRequest")
        return format_friend_id_card(payload)

    async def search(self, *, friend_code: str | None = None, level_option: int | None = None) -> dict[str, Any]:
        fields = compact_fields(
            FriendCode=str(friend_code) if friend_code is not None else None,
            LevelOption=optional_int("level_option", level_option),
        )
        payload = await self.request("FriendSearchRequest", fields)
        return format_friend_search(payload)

    async def list_by_ids(self, target_account_ids: list[int] | tuple[int, ...]) -> dict[str, Any]:
        payload = await self.request(
            "FriendListByIdsRequest",
            {"TargetAccountIds": int_list("target_account_ids", target_account_ids, allow_empty=False)},
        )
        return format_friend_list_by_ids(payload)

    async def send_request(
        self,
        target_account_id: int,
        *,
        confirm: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        target_id = _target_account_id(target_account_id)
        if confirm is not True:
            raise UnsafeOperationError("friend.send_request requires confirm=True")
        if validate:
            await self._ensure_can_send_request(target_id)
        payload = await self.request("FriendSendFriendRequestRequest", {"TargetAccountId": target_id})
        return format_friend_mutation(payload)

    async def accept_request(
        self,
        target_account_id: int,
        *,
        confirm: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        target_id = _target_account_id(target_account_id)
        if confirm is not True:
            raise UnsafeOperationError("friend.accept_request requires confirm=True")
        if validate:
            await self._ensure_received_request_exists(target_id)
        payload = await self.request("FriendAcceptFriendRequestRequest", {"TargetAccountId": target_id})
        return format_friend_mutation(payload)

    async def decline_request(
        self,
        target_account_id: int,
        *,
        confirm: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        target_id = _target_account_id(target_account_id)
        if confirm is not True:
            raise UnsafeOperationError("friend.decline_request requires confirm=True")
        if validate:
            await self._ensure_received_request_exists(target_id)
        payload = await self.request("FriendDeclineFriendRequestRequest", {"TargetAccountId": target_id})
        return format_friend_mutation(payload)

    async def cancel_request(
        self,
        target_account_id: int,
        *,
        confirm: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        target_id = _target_account_id(target_account_id)
        if confirm is not True:
            raise UnsafeOperationError("friend.cancel_request requires confirm=True")
        if validate:
            await self._ensure_sent_request_exists(target_id)
        payload = await self.request("FriendCancelFriendRequestRequest", {"TargetAccountId": target_id})
        return format_friend_mutation(payload)

    async def _ensure_can_send_request(self, target_account_id: int) -> None:
        state = await self.list()
        if target_account_id in _account_ids(state["friends"]):
            raise UnsafeOperationError("target_account_id is already a friend")
        if target_account_id in _account_ids(state["sent_requests"]):
            raise UnsafeOperationError("target_account_id already has a pending sent friend request")
        if target_account_id in _account_ids(state["received_requests"]):
            raise UnsafeOperationError("target_account_id already has a received request; use accept_request or decline_request")
        if target_account_id in _account_ids(state["blocked_friends"]):
            raise UnsafeOperationError("target_account_id is blocked")

    async def _ensure_received_request_exists(self, target_account_id: int) -> None:
        state = await self.list()
        if target_account_id not in _account_ids(state["received_requests"]):
            raise UnsafeOperationError("target_account_id is not present in received friend requests")

    async def _ensure_sent_request_exists(self, target_account_id: int) -> None:
        state = await self.list()
        if target_account_id not in _account_ids(state["sent_requests"]):
            raise UnsafeOperationError("target_account_id is not present in sent friend requests")


def format_friend_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "IdCardBackgroundDBs",
        "FriendDBs",
        "SentRequestFriendDBs",
        "ReceivedRequestFriendDBs",
        "BlockedUserDBs",
        "FriendIdCardDB",
        "ReceivedFriendRequestDBs",
        "SentFriendRequestDBs",
        "BlockedFriendDBs",
    }
    friends = as_list(payload.get("FriendDBs"))
    received = as_list(payload.get("ReceivedRequestFriendDBs", payload.get("ReceivedFriendRequestDBs")))
    sent = as_list(payload.get("SentRequestFriendDBs", payload.get("SentFriendRequestDBs")))
    blocked = as_list(payload.get("BlockedUserDBs", payload.get("BlockedFriendDBs")))
    return {
        "id_card_backgrounds": as_list(payload.get("IdCardBackgroundDBs")),
        "friends": friends,
        "received_requests": received,
        "sent_requests": sent,
        "blocked_friends": blocked,
        "friend_id_card": payload.get("FriendIdCardDB"),
        "count": len(friends),
        "received_count": len(received),
        "sent_count": len(sent),
        "blocked_count": len(blocked),
        "extra": extra_fields(payload, known_keys),
    }


def format_friend_detailed_info(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "DetailedAccountInfoDB",
        "FriendDB",
    }
    return {
        "detailed_account_info": payload.get("DetailedAccountInfoDB"),
        "friend": payload.get("FriendDB"),
        "extra": extra_fields(payload, known_keys),
    }


def format_friend_id_card(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "IdCardDB",
        "AccountIdCardDB",
    }
    return {
        "id_card": payload.get("IdCardDB", payload.get("AccountIdCardDB")),
        "extra": extra_fields(payload, known_keys),
    }


def format_friend_search(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "SearchFriendDBs",
        "FriendDBs",
    }
    friends = as_list(payload.get("SearchFriendDBs", payload.get("FriendDBs")))
    return {
        "friends": friends,
        "count": len(friends),
        "extra": extra_fields(payload, known_keys),
    }


def format_friend_list_by_ids(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "FriendDBs",
        "DetailedAccountInfoDBs",
    }
    friends = as_list(payload.get("FriendDBs", payload.get("DetailedAccountInfoDBs")))
    return {
        "friends": friends,
        "count": len(friends),
        "extra": extra_fields(payload, known_keys),
    }


def format_friend_mutation(payload: dict[str, Any]) -> dict[str, Any]:
    return format_friend_list(payload)


def _target_account_id(value: Any) -> int:
    return required_int("target_account_id", value)


def _account_ids(records: list[Any]) -> set[int]:
    ids: set[int] = set()
    for record in records:
        if not isinstance(record, dict):
            continue
        for key in ("AccountId", "FriendAccountId", "TargetAccountId", "ServerId", "UniqueId"):
            value = _safe_optional_int(record.get(key))
            if value is not None:
                ids.add(value)
                break
    return ids


def _safe_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        result = int(value)
    except (TypeError, ValueError):
        return None
    return result if result >= 0 else None
