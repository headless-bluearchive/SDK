from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService


class MailService(GameService):
    async def check(self) -> dict[str, Any]:
        payload = await self.request("MailCheckRequest")
        return format_mail_check(payload)

    async def list(
        self,
        *,
        is_read_mail: bool | None = None,
        pivot_time: str | None = None,
        pivot_index: int | None = None,
        is_descending: bool | None = None,
        sorting_rule: int | str | None = None,
    ) -> dict[str, Any]:
        fields: dict[str, Any] = {}
        if is_read_mail is not None:
            fields["IsReadMail"] = bool(is_read_mail)
        if pivot_time is not None:
            fields["PivotTime"] = str(pivot_time)
        if pivot_index is not None:
            fields["PivotIndex"] = _optional_int("pivot_index", pivot_index)
        if is_descending is not None:
            fields["IsDescending"] = bool(is_descending)
        if sorting_rule is not None:
            fields["mailSortingRule"] = sorting_rule

        payload = await self.request("MailListRequest", fields)
        return format_mail_list(payload)

    async def receive(self, mail_server_ids: list[int] | tuple[int, ...], *, validate: bool = True) -> dict[str, Any]:
        ids = _required_int_list("mail_server_ids", mail_server_ids)
        if validate:
            await self._ensure_receivable(ids)

        payload = await self.request("MailReceiveRequest", {"MailServerIds": ids})
        return format_mail_receive(payload)

    async def _ensure_receivable(self, mail_server_ids: list[int]) -> None:
        mails = await self.list()
        existing_ids = {
            server_id
            for mail in mails["mails"]
            if isinstance(mail, dict)
            for server_id in [_optional_int("mail_server_id", mail.get("ServerId"))]
            if server_id is not None
        }
        missing_ids = [server_id for server_id in mail_server_ids if server_id not in existing_ids]
        if missing_ids:
            raise UnsafeOperationError("mail_server_ids contain mail that is not present in current mail list")


def format_mail_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "MailDBs",
        "Count",
    }
    mails = _as_list(payload.get("MailDBs"))
    return {
        "mails": mails,
        "count": _optional_int("count", payload.get("Count")) if payload.get("Count") is not None else len(mails),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def format_mail_check(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "Count",
        "CommonMailCount",
    }
    count = payload.get("CommonMailCount", payload.get("Count"))
    return {
        "count": _optional_int("count", count) if count is not None else 0,
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def format_mail_receive(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "MailServerIds",
        "ParcelResultDB",
        "BattlePassInfoDBs",
    }
    return {
        "mail_server_ids": _as_list(payload.get("MailServerIds")),
        "parcel_result": payload.get("ParcelResultDB"),
        "battle_pass_info": _as_list(payload.get("BattlePassInfoDBs")),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _required_int_list(name: str, values: Any) -> list[int]:
    if not isinstance(values, (list, tuple)):
        raise UnsafeOperationError(f"{name} must be a list")
    result = [_optional_int(name, value) for value in values]
    if not result or any(value is None for value in result):
        raise UnsafeOperationError(f"{name} must not be empty")
    return [int(value) for value in result if value is not None]


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
