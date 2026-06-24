from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToySdkCallbackResult:
    handle: int | None = None
    callback_id: int | None = None


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
    ngsm_token: str = ""
    callback: ToySdkCallbackResult | None = None

    def require_game_login_fields(self) -> "ToySdkLoginResult":
        missing = []
        if self.np_sn is None:
            missing.append("npSN")
        if not self.np_token:
            missing.append("npToken")
        if not self.npa_code:
            missing.append("npaCode")
        if missing:
            present = {
                "npSN": self.np_sn is not None,
                "npToken": bool(self.np_token),
                "npaCode": bool(self.npa_code),
            }
            raise ValueError(f"TOYSDK login result missing {', '.join(missing)}; present={present}")
        return self
