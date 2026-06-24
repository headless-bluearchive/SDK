from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, extra_fields, required_int


class EventService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("EventListRequest")
        return format_event_list(payload)

    async def image(self, event_id: int) -> dict[str, Any]:
        payload = await self.request("EventImageRequest", {"EventId": required_int("event_id", event_id)})
        return format_event_image(payload)

    async def use_coupon(self, coupon_serial: str, *, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("event.use_coupon requires confirm=True")
        return await self.request("UseCouponRequest", {"CouponSerial": str(coupon_serial)})

    async def reward_increase(self, *, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("event.reward_increase requires confirm=True")
        return await self.request("EventRewardIncreaseRequest")


def format_event_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "EventInfoDBs",
        "EventContentDBs",
        "EventDBs",
        "Events",
    }
    events = as_list(payload.get("EventInfoDBs", payload.get("EventContentDBs", payload.get("EventDBs", payload.get("Events")))))
    return {
        "events": events,
        "count": len(events),
        "extra": extra_fields(payload, known_keys),
    }


def format_event_image(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "EventImageDB",
        "EventImageDBs",
        "Images",
    }
    images = as_list(payload.get("EventImageDBs", payload.get("Images")))
    return {
        "event_image": payload.get("EventImageDB"),
        "images": images,
        "count": len(images),
        "extra": extra_fields(payload, known_keys),
    }
