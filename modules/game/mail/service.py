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

    async def list_semi_permanent(
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

        payload = await self.request("MailListSemiPermanentRequest", fields)
        return format_mail_list_semi_permanent(payload)

    async def receive_semi_permanent(
        self,
        mail_db_id: int,
        *,
        product_id: int | None = None,
        validate: bool = True,
    ) -> dict[str, Any]:
        db_id = _required_int("mail_db_id", mail_db_id)
        resolved_product_id = _optional_int("product_id", product_id)
        if validate:
            await self._ensure_semi_permanent_receivable(db_id, resolved_product_id)

        fields: dict[str, Any] = {"MailDBId": db_id}
        if resolved_product_id is not None:
            fields["ProductId"] = resolved_product_id
        payload = await self.request("MailReceiveSemiPermanentRequest", fields)
        return format_mail_receive_semi_permanent(payload)

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

    async def _ensure_semi_permanent_receivable(self, mail_db_id: int, product_id: int | None) -> None:
        mails = await self.list_semi_permanent()
        matched = None
        for mail in mails["mails"]:
            if not isinstance(mail, dict):
                continue
            current_id = _mail_db_id(mail)
            if current_id == mail_db_id:
                matched = mail
                break
        if matched is None:
            raise UnsafeOperationError("mail_db_id is not present in current semi-permanent mail list")
        current_product_id = _optional_int("product_id", matched.get("ProductId"))
        if product_id is not None and current_product_id is not None and current_product_id != product_id:
            raise UnsafeOperationError("product_id does not match current semi-permanent mail")


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


def format_mail_list_semi_permanent(payload: dict[str, Any]) -> dict[str, Any]:
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


def format_mail_receive_semi_permanent(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "MailDBId",
        "ParcelResultDB",
        "AppliedMonthlyProductPurchaseDB",
        "AppliedDailyRecordDB",
        "AppliedBattlePassProductPurchaseDB",
        "AppliedBattlePassInfoDB",
        "BattlePassInfoDBs",
    }
    return {
        "mail_db_id": _optional_int("mail_db_id", payload.get("MailDBId")),
        "parcel_result": payload.get("ParcelResultDB"),
        "applied_monthly_product_purchase": payload.get("AppliedMonthlyProductPurchaseDB"),
        "applied_daily_record": payload.get("AppliedDailyRecordDB"),
        "applied_battle_pass_product_purchase": payload.get("AppliedBattlePassProductPurchaseDB"),
        "applied_battle_pass_info": payload.get("AppliedBattlePassInfoDB"),
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


def _required_int(name: str, value: Any) -> int:
    result = _optional_int(name, value)
    if result is None:
        raise UnsafeOperationError(f"{name} is required")
    return result


def _mail_db_id(mail: dict[str, Any]) -> int | None:
    for key in ("MailDBId", "MailId", "ServerId", "Id", "UniqueId"):
        value = mail.get(key)
        if value is not None:
            return _optional_int(key, value)
    return None


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
