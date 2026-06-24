from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class ResetableContentService(GameService):

    async def get(self) -> dict[str, Any]:
        payload = await self.request("ResetableContentGetRequest")
        return format_resetable_content_get(payload)


def format_resetable_content_get(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ResetableContentValueDBs",
    }
    values = as_list(payload.get("ResetableContentValueDBs"))
    return {
        "values": values,
        "count": len(values),
        "extra": extra_fields(payload, known_keys),
    }
