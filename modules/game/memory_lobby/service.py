from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class MemoryLobbyService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("MemoryLobbyListRequest")
        return format_memory_lobby_list(payload)


def format_memory_lobby_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "MemoryLobbyDBs",
    }
    memory_lobbies = as_list(payload.get("MemoryLobbyDBs"))
    return {
        "memory_lobbies": memory_lobbies,
        "count": len(memory_lobbies),
        "extra": extra_fields(payload, known_keys),
    }
