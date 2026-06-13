"""Cafe module extension point.

Concrete Cafe request builders should live in this package when they are added,
for example `Cafe_Get`, `Cafe_Invite`, and future cafe automation workflows.
"""

from __future__ import annotations

from headlessba.core.api_registry import GameApiDescriptor, register_api


CAFE_GET = register_api(
    GameApiDescriptor(
        module="game.player.cafe",
        name="get",
        protocol_name="Cafe_Get",
        request_class="CafeGetRequest",
    )
)
