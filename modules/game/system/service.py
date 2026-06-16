from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import extra_fields


class SystemService(GameService):
    async def version(self) -> dict[str, Any]:
        payload = await self.request("SystemVersionRequest", include_base_defaults=False)
        return format_system_version(payload)


def format_system_version(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CurrentVersion",
        "MinimumVersion",
        "IsDevelopment",
    }
    return {
        "current_version": payload.get("CurrentVersion"),
        "minimum_version": payload.get("MinimumVersion"),
        "is_development": payload.get("IsDevelopment"),
        "extra": extra_fields(payload, known_keys),
    }
