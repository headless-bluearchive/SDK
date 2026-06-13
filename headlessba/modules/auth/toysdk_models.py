"""Shared TOYSDK result models without native DLL dependencies."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NativeCallbackResult:
    payload: str
    parsed: Any
    handle: int | None = None
    callback_id: int | None = None


@dataclass(frozen=True)
class ToySdkTicketResult:
    ticket: str
    callback: NativeCallbackResult


@dataclass(frozen=True)
class ToySdkLoginResult:
    np_sn: int | None
    np_token: str
    npa_code: str
    session_token: str
    guid: str = ""
    member_id: str = ""
    member_type: str = ""
    um_key: str = ""
    game_token: str = ""
    ngsm_token: str = ""
    callback: NativeCallbackResult | None = None

    def require_game_login_fields(self) -> "ToySdkLoginResult":
        missing = []
        if self.np_sn is None:
            missing.append("npSN")
        if not self.np_token:
            missing.append("npToken")
        if not self.npa_code:
            missing.append("npaCode")
        if missing:
            raw = self.callback.payload if self.callback else json.dumps(self.__dict__, ensure_ascii=False)
            raise ValueError(f"TOYSDK login result missing {', '.join(missing)}; raw={raw[:1000]}")
        return self
