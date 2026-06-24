from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import compact_fields, extra_fields, int_list, optional_int


class StickerService(GameService):

    async def login(self) -> dict[str, Any]:
        return await self.request("StickerLoginRequest")

    async def lobby(
        self,
        *,
        acquire_sticker_unique_ids: list[int] | tuple[int, ...] | None = None,
    ) -> dict[str, Any]:
        fields = compact_fields(
            AcquireStickerUniqueIds=int_list("acquire_sticker_unique_ids", acquire_sticker_unique_ids) or None
        )
        payload = await self.request("StickerLobbyRequest", fields)
        return format_sticker_lobby(payload)

    async def use_sticker(
        self,
        *,
        sticker_unique_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("sticker.use_sticker requires confirm=True")
        fields = compact_fields(
            StickerUniqueId=optional_int("sticker_unique_id", sticker_unique_id),
        )
        return await self.request("StickerUseStickerRequest", fields)


def format_sticker_lobby(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "StickerBookDB",
    }
    return {
        "sticker_book": payload.get("StickerBookDB"),
        "extra": extra_fields(payload, known_keys),
    }
