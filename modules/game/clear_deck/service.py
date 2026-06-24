from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import compact_fields, optional_int


class ClearDeckService(GameService):

    async def list(self, *, clear_deck_key: int | None = None) -> dict[str, Any]:
        fields = compact_fields(ClearDeckKey=optional_int("clear_deck_key", clear_deck_key))
        return await self.request("ClearDeckListRequest", fields)

    async def grouped_list(self, *, clear_deck_key: int | None = None) -> dict[str, Any]:
        fields = compact_fields(ClearDeckKey=optional_int("clear_deck_key", clear_deck_key))
        return await self.request("ClearDeckGroupedListRequest", fields)
