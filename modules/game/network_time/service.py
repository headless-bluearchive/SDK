from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import extra_fields


class NetworkTimeService(GameService):

    async def sync(self) -> dict[str, Any]:
        payload = await self.request("NetworkTimeSyncRequest")
        return format_network_time_sync(payload)


def format_network_time_sync(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ReceiveTick",
        "EchoSendTick",
    }
    return {
        "receive_tick": payload.get("ReceiveTick"),
        "echo_send_tick": payload.get("EchoSendTick"),
        "extra": extra_fields(payload, known_keys),
    }
