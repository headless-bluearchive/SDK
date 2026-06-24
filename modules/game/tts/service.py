from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import extra_fields


class TTSService(GameService):

    async def get_file(self) -> dict[str, Any]:
        return await self.request("TTSGetFileRequest")

    async def get_kana(self, call_name: str) -> dict[str, Any]:
        payload = await self.request("TTSGetKanaRequest", {"CallName": str(call_name)})
        return format_tts_kana(payload)


def format_tts_kana(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CallName",
        "ActualCallName",
        "CallNameKatakana",
        "CallNameKorean",
        "ActualCallNameKorean",
    }
    return {
        "call_name": payload.get("CallName"),
        "actual_call_name": payload.get("ActualCallName"),
        "call_name_katakana": payload.get("CallNameKatakana"),
        "call_name_korean": payload.get("CallNameKorean"),
        "actual_call_name_korean": payload.get("ActualCallNameKorean"),
        "extra": extra_fields(payload, known_keys),
    }
