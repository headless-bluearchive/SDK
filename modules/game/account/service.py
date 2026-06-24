from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, int_list, optional_int


class AccountService(GameService):
    async def currency(self) -> dict[str, Any]:
        payload = await self.request("AccountCurrencySyncRequest")
        return format_account_currency(payload)

    async def verify_adult_agree(self) -> dict[str, Any]:
        return await self.request("AccountVerifyAdultCheckRequest")

    async def tutorial(self) -> dict[str, Any]:
        payload = await self.request("AccountGetTutorialRequest")
        return format_account_tutorial(payload)

    async def check_level_reward(self) -> dict[str, Any]:
        payload = await self.request("CheckAccountLevelRewardRequest")
        return format_account_level_reward_check(payload)

    async def receive_level_reward(
        self,
        *,
        confirm: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("account.receive_level_reward requires confirm=True")
        if validate:
            state = await self.check_level_reward()
            if not state["account_level_reward_ids"]:
                raise UnsafeOperationError("no account level reward is currently available")
        payload = await self.request("ReceiveAccountLevelRewardRequest")
        return format_account_level_reward_receive(payload)

    async def link_reward(self, *, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("account.link_reward requires confirm=True")
        return await self.request("AccountLinkRewardRequest")

    async def request_birthday_mail(self, *, birthday: Any = None, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("account.request_birthday_mail requires confirm=True")
        return await self.request("AccountRequestBirthdayMailRequest", compact_fields(Birthday=birthday))

    async def set_represent_character_and_comment(
        self,
        *,
        comment: str | None = None,
        represent_character_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("account.set_represent_character_and_comment requires confirm=True")
        fields = compact_fields(
            Comment=str(comment) if comment is not None else None,
            RepresentCharacterServerId=optional_int("represent_character_server_id", represent_character_server_id),
        )
        return await self.request("AccountSetRepresentCharacterAndCommentRequest", fields)

    async def call_name(
        self,
        *,
        call_name: str | None = None,
        call_name_katakana: str | None = None,
        call_name_korean: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("account.call_name requires confirm=True")
        fields = compact_fields(
            CallName=str(call_name) if call_name is not None else None,
            CallNameKatakana=str(call_name_katakana) if call_name_katakana is not None else None,
            CallNameKorean=str(call_name_korean) if call_name_korean is not None else None,
        )
        return await self.request("AccountCallNameRequest", fields)

    async def dismiss_repurchasable_popup(
        self,
        *,
        product_ids: list[int] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("account.dismiss_repurchasable_popup requires confirm=True")
        fields = compact_fields(
            ProductIds=int_list("product_ids", product_ids) or None,
        )
        return await self.request("AccountDismissRepurchasablePopupRequest", fields)

    async def set_check_adult_agree(
        self,
        *,
        check_adult_agree: bool | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("account.set_check_adult_agree requires confirm=True")
        fields = compact_fields(
            CheckAdultAgree=check_adult_agree,
        )
        return await self.request("AccountSetAdultCheckRequest", fields)

    async def set_tutorial(
        self,
        *,
        tutorial_ids: list[int] | tuple[int, ...] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("account.set_tutorial requires confirm=True")
        fields = compact_fields(
            TutorialIds=int_list("tutorial_ids", tutorial_ids) or None,
        )
        return await self.request("AccountSetTutorialRequest", fields)


def format_account_currency(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AccountCurrencyDB",
        "ExpiredCurrency",
    }
    account_currency = payload.get("AccountCurrencyDB")
    currency_dict = account_currency.get("CurrencyDict") if isinstance(account_currency, dict) else {}
    update_time_dict = account_currency.get("UpdateTimeDict") if isinstance(account_currency, dict) else {}
    return {
        "account_currency": account_currency,
        "currency": currency_dict if isinstance(currency_dict, dict) else {},
        "update_time": update_time_dict if isinstance(update_time_dict, dict) else {},
        "expired_currency": payload.get("ExpiredCurrency") if isinstance(payload.get("ExpiredCurrency"), dict) else {},
        "extra": extra_fields(payload, known_keys),
    }


def format_account_tutorial(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "TutorialIds",
    }
    tutorial_ids = as_list(payload.get("TutorialIds"))
    return {
        "tutorial_ids": tutorial_ids,
        "count": len(tutorial_ids),
        "extra": extra_fields(payload, known_keys),
    }


def format_account_level_reward_check(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AccountLevelRewardIds",
    }
    reward_ids = as_list(payload.get("AccountLevelRewardIds"))
    return {
        "account_level_reward_ids": reward_ids,
        "count": len(reward_ids),
        "extra": extra_fields(payload, known_keys),
    }


def format_account_level_reward_receive(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ReceivedAccountLevelRewardIds",
        "ParcelResultDB",
    }
    reward_ids = as_list(payload.get("ReceivedAccountLevelRewardIds"))
    return {
        "received_account_level_reward_ids": reward_ids,
        "count": len(reward_ids),
        "parcel_result": payload.get("ParcelResultDB"),
        "extra": extra_fields(payload, known_keys),
    }
