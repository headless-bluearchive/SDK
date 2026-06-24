from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import compact_fields, optional_int


class ContentSaveService(GameService):

    async def get(self) -> dict[str, Any]:
        return await self.request("ContentSaveGetRequest")

    async def discard(
        self,
        *,
        content_type: int | None = None,
        stage_unique_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("content_save.discard requires confirm=True")
        fields = compact_fields(
            ContentType=optional_int("content_type", content_type),
            StageUniqueId=optional_int("stage_unique_id", stage_unique_id),
        )
        return await self.request("ContentSaveDiscardRequest", fields)
