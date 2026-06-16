from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class AttachmentService(GameService):
    async def get(self) -> dict[str, Any]:
        payload = await self.request("AttachmentGetRequest")
        return format_attachment_get(payload)

    async def emblem_list(self) -> dict[str, Any]:
        payload = await self.request("AttachmentEmblemListRequest")
        return format_attachment_emblem_list(payload)


def format_attachment_get(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AccountAttachmentDB",
    }
    return {
        "account_attachment": payload.get("AccountAttachmentDB"),
        "extra": extra_fields(payload, known_keys),
    }


def format_attachment_emblem_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "EmblemDBs",
    }
    emblems = as_list(payload.get("EmblemDBs"))
    return {
        "emblems": emblems,
        "count": len(emblems),
        "extra": extra_fields(payload, known_keys),
    }
