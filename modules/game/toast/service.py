from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class ToastService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("ToastListRequest")
        return format_toast_list(payload)


def format_toast_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ToastDBs",
        "Toasts",
    }
    toasts = as_list(payload.get("ToastDBs", payload.get("Toasts")))
    return {
        "toasts": toasts,
        "count": len(toasts),
        "extra": extra_fields(payload, known_keys),
    }
