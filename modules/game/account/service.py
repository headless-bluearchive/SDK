from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import extra_fields


class AccountService(GameService):
    async def currency(self) -> dict[str, Any]:
        payload = await self.request("AccountCurrencySyncRequest")
        return format_account_currency(payload)


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
