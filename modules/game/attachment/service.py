from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, extra_fields, int_list, required_int


class AttachmentService(GameService):
    async def get(self) -> dict[str, Any]:
        payload = await self.request("AttachmentGetRequest")
        return format_attachment_get(payload)

    async def emblem_list(self) -> dict[str, Any]:
        payload = await self.request("AttachmentEmblemListRequest")
        return format_attachment_emblem_list(payload)

    async def emblem_acquire(
        self,
        unique_ids: list[int] | tuple[int, ...],
        *,
        confirm: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        resolved_unique_ids = int_list("unique_ids", unique_ids, allow_empty=False)
        if confirm is not True:
            raise UnsafeOperationError("attachment.emblem_acquire requires confirm=True")
        if validate:
            await self._ensure_emblem_unique_ids_available(resolved_unique_ids)
        payload = await self.request(
            "AttachmentEmblemAcquireRequest",
            {"UniqueIds": resolved_unique_ids},
        )
        return format_attachment_emblem_acquire(payload)

    async def emblem_attach(
        self,
        unique_id: int,
        *,
        confirm: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        resolved_unique_id = required_int("unique_id", unique_id)
        if confirm is not True:
            raise UnsafeOperationError("attachment.emblem_attach requires confirm=True")
        if validate:
            await self._ensure_emblem_unique_id_available(resolved_unique_id)
        payload = await self.request(
            "AttachmentEmblemAttachRequest",
            {"UniqueId": resolved_unique_id},
        )
        return format_attachment_emblem_attach(payload)

    async def _ensure_emblem_unique_ids_available(self, unique_ids: list[int]) -> None:
        state = await self.emblem_list()
        available_ids = _emblem_unique_ids(state["emblems"])
        missing_ids = [unique_id for unique_id in unique_ids if unique_id not in available_ids]
        if missing_ids:
            raise UnsafeOperationError("unique_ids contain emblem that is not present in current emblem list")

    async def _ensure_emblem_unique_id_available(self, unique_id: int) -> None:
        state = await self.emblem_list()
        available_ids = _emblem_unique_ids(state["emblems"])
        if unique_id not in available_ids:
            raise UnsafeOperationError("unique_id is not present in current emblem list")


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


def format_attachment_emblem_acquire(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "EmblemDBs",
    }
    emblems = as_list(payload.get("EmblemDBs"))
    return {
        "emblems": emblems,
        "count": len(emblems),
        "extra": extra_fields(payload, known_keys),
    }


def format_attachment_emblem_attach(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AttachmentDB",
    }
    return {
        "attachment": payload.get("AttachmentDB"),
        "extra": extra_fields(payload, known_keys),
    }


def _emblem_unique_ids(records: list[Any]) -> set[int]:
    ids: set[int] = set()
    for record in records:
        if not isinstance(record, dict):
            continue
        for key in ("UniqueId", "EmblemUniqueId", "AttachmentUniqueId"):
            value = record.get(key)
            if value is None:
                continue
            try:
                unique_id = int(value)
            except (TypeError, ValueError):
                continue
            if unique_id >= 0:
                ids.add(unique_id)
                break
    return ids
