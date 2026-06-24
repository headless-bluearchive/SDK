from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import extra_fields


class NotificationService(GameService):

    async def lobby_check(self) -> dict[str, Any]:
        return await self.request("NotificationLobbyCheckRequest")

    async def event_content_reddot_check(self) -> dict[str, Any]:
        payload = await self.request("NotificationEventContentReddotRequest")
        return format_notification_reddot(payload)


def format_notification_reddot(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "Reddots",
    }
    return {
        "reddots": payload.get("Reddots"),
        "extra": extra_fields(payload, known_keys),
    }
