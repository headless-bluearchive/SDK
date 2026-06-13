from __future__ import annotations

from collections.abc import Mapping as _Mapping
from dataclasses import dataclass, field
from typing import Any as _Any

from core.error import LoginRequiredError
from modules.auth.service import Login as _login


@dataclass(frozen=True)
class LoginResult:
    account_id: int | None = None
    nickname: str | None = None
    level: int | None = None
    exp: int | None = None
    friend_code: str | None = None
    publisher_account_id: int | None = None
    credentials: _Any = field(default=None, repr=False, compare=False)
    logs: tuple[str, ...] = field(default_factory=tuple, repr=False, compare=False)

    @classmethod
    def from_integrated(cls, value: _Any, *, logs: list[str] | None = None) -> "LoginResult":
        flow = getattr(value, "flow", {}) or {}
        account_data = flow.get("account_data")
        player_data = flow.get("player_data")
        account_db = _find_mapping_with_key(account_data, "AccountDB")
        return cls(
            account_id=_first_value(
                _find_value(account_data, {"AccountId", "accountId"}),
                _find_value(account_db, {"ServerId", "serverId", "AccountId", "accountId"}),
            ),
            nickname=_first_value(
                _find_value(account_db, {"Nickname", "NickName", "nickname"}),
                _find_value(account_data, {"Nickname", "NickName", "nickname"}),
            ),
            level=_first_value(_find_value(account_db, {"Level", "level"}), _find_value(account_data, {"Level", "level"})),
            exp=_first_value(_find_value(account_db, {"Exp", "exp"}), _find_value(account_data, {"Exp", "exp"})),
            friend_code=_first_value(
                _find_value(player_data, {"FriendCode", "friendCode"}),
                _find_value(account_data, {"FriendCode", "friendCode"}),
            ),
            publisher_account_id=_first_value(
                _find_value(account_db, {"PublisherAccountId", "publisherAccountId"}),
                _find_value(account_data, {"PublisherAccountId", "publisherAccountId"}),
            ),
            credentials=getattr(value, "credentials", None),
            logs=tuple(logs or ()),
        )

    def __str__(self) -> str:
        values = self.to_dict()
        return "[" + ", ".join(f"{key}: {value}" for key, value in values.items()) + "]"

    __repr__ = __str__

    def to_dict(self) -> dict[str, _Any]:
        return {
            "AccountId": self.account_id,
            "Nickname": self.nickname,
            "Level": self.level,
            "Exp": self.exp,
            "FriendCode": self.friend_code,
            "PublisherAccountId": self.publisher_account_id,
        }


class Client:
    def __init__(self, *, debug: bool = False, **defaults: _Any) -> None:
        self.debug = bool(debug)
        self.defaults = dict(defaults)
        self.result: LoginResult | None = None
        self._raw_result: _Any | None = None
        self.logs: list[str] = []

    async def login(self, account: str, password: str) -> LoginResult:
        options = {**self.defaults, "nx_id": account, "nx_password": password}
        self.logs = []
        if self.debug:
            options["debug_logger"] = self._debug_log
        raw_result = await _login(**options)
        self.result = LoginResult.from_integrated(raw_result, logs=self.logs if self.debug else None)
        self._raw_result = raw_result if self.debug else None
        return self.result

    @property
    def credentials(self) -> _Any:
        if self.result is None:
            raise LoginRequiredError("login has not completed")
        return self.result.credentials

    @property
    def raw_result(self) -> _Any:
        return self._raw_result

    def _debug_log(self, message: str) -> None:
        self.logs.append(message)
        print(f"[debug] {message}", flush=True)


def _find_value(obj: _Any, names: set[str]) -> _Any:
    if isinstance(obj, _Mapping):
        for key, value in obj.items():
            if key in names:
                return value
        for value in obj.values():
            found = _find_value(value, names)
            if found not in (None, ""):
                return found
    if isinstance(obj, list):
        for value in obj:
            found = _find_value(value, names)
            if found not in (None, ""):
                return found
    return None


def _find_mapping_with_key(obj: _Any, key: str) -> dict[str, _Any]:
    if isinstance(obj, _Mapping):
        value = obj.get(key)
        if isinstance(value, _Mapping):
            return dict(value)
        for nested in obj.values():
            found = _find_mapping_with_key(nested, key)
            if found:
                return found
    if isinstance(obj, list):
        for nested in obj:
            found = _find_mapping_with_key(nested, key)
            if found:
                return found
    return {}


def _first_value(*values: _Any) -> _Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


__all__ = ["Client", "LoginResult"]
