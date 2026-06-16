from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class PermanentRaidService(GameService):
    async def lobby(self) -> dict[str, Any]:
        payload = await self.request("PermanentRaidLobbyRequest")
        return format_permanent_raid_lobby(payload)


def format_permanent_raid_lobby(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "PermanentRaidLobbyInfoDBs",
        "PermanentRaidSeasonDBs",
        "AccountCurrencyDB",
    }
    lobby_infos = as_list(payload.get("PermanentRaidLobbyInfoDBs"))
    seasons = as_list(payload.get("PermanentRaidSeasonDBs"))
    return {
        "lobby_infos": lobby_infos,
        "seasons": seasons,
        "account_currency": payload.get("AccountCurrencyDB"),
        "count": len(lobby_infos),
        "season_count": len(seasons),
        "extra": extra_fields(payload, known_keys),
    }
