from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, extra_fields


class CharacterService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("CharacterListRequest")
        return format_character_list(payload)


def format_character_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CharacterDBs",
        "TSSCharacterDBs",
    }
    characters = as_list(payload.get("CharacterDBs"))
    tss_characters = as_list(payload.get("TSSCharacterDBs"))
    return {
        "characters": characters,
        "tss_characters": tss_characters,
        "count": len(characters),
        "extra": extra_fields(payload, known_keys),
    }
