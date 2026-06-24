from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService


class FieldService(GameService):

    async def sync(self) -> dict[str, Any]:
        return await self.request("FieldSyncRequest")

    async def scene_changed(self, *, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("field.scene_changed requires confirm=True")
        return await self.request("FieldSceneChangedRequest")

    async def end_date(self, *, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("field.end_date requires confirm=True")
        return await self.request("FieldEndDateRequest")
