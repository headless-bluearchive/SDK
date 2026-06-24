from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list

_REPURCHASABLE_KEY = "RepurchasableMonthlyProductCountDBs"
_PARCEL_KEYS = (
    "MonthlyProductParcel",
    "MonthlyProductMail",
    "BiweeklyProductParcel",
    "BiweeklyProductMail",
    "WeeklyProductParcel",
    "WeeklyProductMail",
)
_BILLING_KEYS = (_REPURCHASABLE_KEY, *_PARCEL_KEYS)


def _empty_bucket() -> dict[str, Any]:
    return {"parcel": [], "mail": [], "parcel_count": 0, "mail_count": 0}


class BillingService(GameService):
    def status(self) -> dict[str, Any]:
        cache = self._cache()
        if cache is None:
            return {
                "available": False,
                "source": None,
                "reason": "billing snapshot is not available; log in again or restore a session containing Account_Auth billing fields",
                "repurchasable_monthly_product_counts": [],
                "repurchasable_count": 0,
                "monthly_product": _empty_bucket(),
                "biweekly_product": _empty_bucket(),
                "weekly_product": _empty_bucket(),
                "monthly_product_reward_mail_exist": False,
                "subscription_reward_mail_exist": False,
            }

        repurchasable = _purchase_counts(cache.get(_REPURCHASABLE_KEY))
        monthly = _product_bucket(cache, "Monthly")
        biweekly = _product_bucket(cache, "Biweekly")
        weekly = _product_bucket(cache, "Weekly")
        return {
            "available": True,
            "source": cache.get("source"),
            "repurchasable_monthly_product_counts": repurchasable,
            "repurchasable_count": len(repurchasable),
            "monthly_product": monthly,
            "biweekly_product": biweekly,
            "weekly_product": weekly,
            "monthly_product_reward_mail_exist": monthly["mail_count"] > 0,
            "subscription_reward_mail_exist": any(
                bucket["mail_count"] > 0 for bucket in (monthly, biweekly, weekly)
            ),
        }

    info = status

    def _cache(self) -> dict[str, Any] | None:
        result = getattr(self._owner, "result", None)
        if result is None:
            return None
        cache = extract_billing_cache(getattr(result, "billing", None))
        if cache is not None:
            return cache
        session = getattr(result, "session", None)
        if isinstance(session, Mapping):
            return extract_billing_cache(session.get("billing"), source="session.billing")
        return None


def extract_billing_cache(value: Any, *, source: str = "Account_Auth") -> dict[str, Any] | None:

    if not isinstance(value, Mapping):
        return None
    container: Mapping[str, Any] | None = value
    if not any(key in container for key in _BILLING_KEYS):
        container = _find_mapping_with_any_key(value, set(_BILLING_KEYS))
        if container is None:
            return None
    cache: dict[str, Any] = {"source": str(value.get("source") or source)}
    for key in _BILLING_KEYS:
        cache[key] = as_list(container.get(key))
    return cache


def _product_bucket(cache: Mapping[str, Any], tier: str) -> dict[str, Any]:
    parcel = _parcels(cache.get(f"{tier}ProductParcel"))
    mail = _parcels(cache.get(f"{tier}ProductMail"))
    return {
        "parcel": parcel,
        "mail": mail,
        "parcel_count": len(parcel),
        "mail_count": len(mail),
    }


def _purchase_counts(value: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for entry in as_list(value):
        if not isinstance(entry, Mapping):
            continue
        result.append(
            {
                "shop_cash_id": _optional_int(entry.get("ShopCashId")),
                "purchase_count": _optional_int(entry.get("PurchaseCount")),
                "reset_date": entry.get("ResetDate"),
                "purchase_date": entry.get("PurchaseDate"),
                "manual_reset_date": entry.get("ManualResetDate"),
            }
        )
    return result


def _parcels(value: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for entry in as_list(value):
        if not isinstance(entry, Mapping):
            continue
        key = entry.get("Key")
        key = key if isinstance(key, Mapping) else {}
        result.append(
            {
                "type": key.get("Type"),
                "id": _optional_int(key.get("Id")),
                "amount": _optional_int(entry.get("Amount")),
                "multiplier": entry.get("Multiplier"),
                "probability": entry.get("Probability"),
            }
        )
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


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


__all__ = ["BillingService", "extract_billing_cache"]
