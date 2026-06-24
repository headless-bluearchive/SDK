from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, int_list, optional_int, required_int


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
            raise UnsafeOperationError("shop.buy_ap requires confirm=True")
        fields = {
            "ShopUniqueId": _required_int("shop_unique_id", shop_unique_id),
            "PurchaseCount": _required_int("purchase_count", purchase_count),
        }
        payload = await self.request("ShopBuyAPRequest", fields)
        return format_shop_purchase(payload)

    async def gacha_recruit_list(self) -> dict[str, Any]:
        payload = await self.request("ShopGachaRecruitListRequest")
        return format_shop_gacha_recruit_list(payload)

    async def beforehand_gacha_get(self) -> dict[str, Any]:
        payload = await self.request("ShopBeforehandGachaGetRequest")
        return format_shop_beforehand_gacha_get(payload)

    async def pickup_selection_gacha_get(self, shop_recruit_id: int) -> dict[str, Any]:
        payload = await self.request(
            "ShopPickupSelectionGachaGetRequest",
            {"ShopRecruitId": required_int("shop_recruit_id", shop_recruit_id)},
        )
        return format_shop_pickup_selection_gacha_get(payload)

    async def buy_eligma(
        self,
        *,
        character_unique_id: int,
        goods_unique_id: int,
        shop_unique_id: int,
        purchase_count: int = 1,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("shop.buy_eligma requires confirm=True")
        fields = {
            "CharacterUniqueId": required_int("character_unique_id", character_unique_id),
            "GoodsUniqueId": required_int("goods_unique_id", goods_unique_id),
            "ShopUniqueId": required_int("shop_unique_id", shop_unique_id),
            "PurchaseCount": required_int("purchase_count", purchase_count),
        }
        return await self.request("ShopBuyEligmaRequest", fields)

    async def buy_merchandise(
        self,
        *,
        goods_id: int | None = None,
        is_refresh_goods: bool | None = None,
        purchase_count: int | None = None,
        shop_unique_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("shop.buy_merchandise requires confirm=True")
        fields = compact_fields(
            GoodsId=optional_int("goods_id", goods_id),
            IsRefreshGoods=is_refresh_goods,
            PurchaseCount=optional_int("purchase_count", purchase_count),
            ShopUniqueId=optional_int("shop_unique_id", shop_unique_id),
        )
        return await self.request("ShopBuyMerchandiseRequest", fields)

    async def refresh(
        self,
        *,
        shop_category_type: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("shop.refresh requires confirm=True")
        fields = compact_fields(
            ShopCategoryType=optional_int("shop_category_type", shop_category_type),
        )
        return await self.request("ShopRefreshRequest", fields)

    async def buy_refresh_merchandise(
        self,
        *,
        shop_unique_ids: list[int] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("shop.buy_refresh_merchandise requires confirm=True")
        fields = compact_fields(
            ShopUniqueIds=int_list("shop_unique_ids", shop_unique_ids) or None,
        )
        return await self.request("ShopBuyRefreshMerchandiseRequest", fields)


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


def format_shop_gacha_recruit_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ShopRecruits",
        "ShopFreeRecruitHistoryDBs",
        "ShopRecruitDBs",
        "RecruitList",
        "AccountCurrencyDB",
    }
    recruits = as_list(payload.get("ShopRecruits", payload.get("ShopRecruitDBs", payload.get("RecruitList"))))
    free_history = as_list(payload.get("ShopFreeRecruitHistoryDBs"))
    return {
        "shop_recruits": recruits,
        "free_recruit_history": free_history,
        "account_currency": payload.get("AccountCurrencyDB"),
        "count": len(recruits),
        "free_history_count": len(free_history),
        "extra": extra_fields(payload, known_keys),
    }


def format_shop_beforehand_gacha_get(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "BeforehandGachaDB",
        "BeforehandGachaHistoryDB",
    }
    return {
        "beforehand_gacha": payload.get("BeforehandGachaDB"),
        "beforehand_gacha_history": payload.get("BeforehandGachaHistoryDB"),
        "extra": extra_fields(payload, known_keys),
    }


def format_shop_pickup_selection_gacha_get(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "PickupSelectionGachaDB",
        "ShopRecruitDB",
    }
    return {
        "pickup_selection_gacha": payload.get("PickupSelectionGachaDB"),
        "shop_recruit": payload.get("ShopRecruitDB"),
        "extra": extra_fields(payload, known_keys),
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
