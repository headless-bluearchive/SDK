from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService


class ShopService(GameService):
    async def list(self, *, category_list: list[int] | tuple[int, ...] | None = None) -> dict[str, Any]:
        categories = [] if category_list is None else _int_list("category_list", category_list)
        payload = await self.request("ShopListRequest", {"CategoryList": categories})
        return format_shop_list(payload)

    async def buy_ap(
        self,
        shop_unique_id: int,
        *,
        purchase_count: int = 1,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("buy_ap requires confirm=True")
        fields = {
            "ShopUniqueId": _required_int("shop_unique_id", shop_unique_id),
            "PurchaseCount": _required_int("purchase_count", purchase_count),
        }
        payload = await self.request("ShopBuyAPRequest", fields)
        return format_shop_purchase(payload)


def format_shop_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ShopInfos",
        "ShopEligmaHistoryDBs",
    }
    return {
        "shop_infos": _as_list(payload.get("ShopInfos")),
        "eligma_history": _as_list(payload.get("ShopEligmaHistoryDBs")),
        "extra": {key: value for key, value in payload.items() if key not in known_keys},
    }


def format_shop_purchase(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AccountCurrencyDB",
        "ConsumeResultDB",
        "ParcelResultDB",
        "MailDB",
        "ShopProductDB",
    }
    return {
        "account_currency": payload.get("AccountCurrencyDB"),
        "consume_result": payload.get("ConsumeResultDB"),
        "parcel_result": payload.get("ParcelResultDB"),
        "mail": payload.get("MailDB"),
        "shop_product": payload.get("ShopProductDB"),
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


def _int_list(name: str, values: Any) -> list[int]:
    if not isinstance(values, (list, tuple)):
        raise UnsafeOperationError(f"{name} must be a list")
    return [_required_int(name, value) for value in values]


def _required_int(name: str, value: Any) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise UnsafeOperationError(f"{name} must be an integer") from exc
    if result < 0:
        raise UnsafeOperationError(f"{name} must not be negative")
    return result
