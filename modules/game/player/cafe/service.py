from __future__ import annotations

from core.api_registry import GameApiDescriptor, register_api


CAFE_GET = register_api(
    GameApiDescriptor(
        module="modules.game.player.cafe",
        name="get",
        protocol_name="Cafe_Get",
        request_class="CafeGetRequest",
    )
)
