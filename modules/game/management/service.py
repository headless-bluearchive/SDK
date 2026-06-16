from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class ManagementService(GameService):
    async def banner_list(self) -> dict[str, Any]:
        payload = await self.request("ManagementBannerListRequest")
        return format_management_banner_list(payload)

    async def protocol_lock_list(self) -> dict[str, Any]:
        payload = await self.request("ManagementProtocolLockListRequest")
        return format_management_protocol_lock_list(payload)


def format_management_banner_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "BannerDBs",
        "Banners",
    }
    banners = as_list(payload.get("BannerDBs", payload.get("Banners")))
    return {
        "banners": banners,
        "count": len(banners),
        "extra": extra_fields(payload, known_keys),
    }


def format_management_protocol_lock_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ProtocolLockDBs",
        "ProtocolLocks",
    }
    locks = as_list(payload.get("ProtocolLockDBs", payload.get("ProtocolLocks")))
    return {
        "protocol_locks": locks,
        "count": len(locks),
        "extra": extra_fields(payload, known_keys),
    }
