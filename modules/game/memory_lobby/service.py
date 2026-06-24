from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int


class MemoryLobbyService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("MemoryLobbyListRequest")
        return format_memory_lobby_list(payload)

    async def set_main(
        self,
        *,
        memory_lobby_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("memory_lobby.set_main requires confirm=True")
        fields = compact_fields(
            MemoryLobbyId=optional_int("memory_lobby_id", memory_lobby_id),
        )
        return await self.request("MemoryLobbySetMainRequest", fields)

    async def update_lobby_mode(
        self,
        *,
        is_memory_lobby_mode: bool | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("memory_lobby.update_lobby_mode requires confirm=True")
        fields = compact_fields(
            IsMemoryLobbyMode=is_memory_lobby_mode,
        )
        return await self.request("MemoryLobbyUpdateLobbyModeRequest", fields)

    async def interact(
        self,
        *,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("memory_lobby.interact requires confirm=True")
        return await self.request("MemoryLobbyInteractRequest")


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
