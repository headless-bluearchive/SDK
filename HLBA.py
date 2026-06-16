from __future__ import annotations

from collections.abc import Mapping as _Mapping
from dataclasses import dataclass, field
from typing import Any as _Any
import warnings

from core.client import BAReplayClient
from core.error import LoginRequiredError, SessionRestoreError
from core.official_data import data_status, prepare_global_data
from core.session_lifecycle import stamp_session_daily_reset, validate_session_daily_reset
from core.student_data import refresh_student_names
from modules.auth.service import Login as _login
from modules.game.account.service import AccountService
from modules.game.attachment.service import AttachmentService
from modules.game.attendance.service import AttendanceService, extract_attendance_cache
from modules.game.battle_pass.service import BattlePassService
from modules.game.campaign.service import CampaignService
from modules.game.character.service import CharacterService
from modules.game.character_gear.service import CharacterGearService
from modules.game.clan.service import ClanService
from modules.game.conquest.service import ConquestService
from modules.game.craft.service import CraftService
from modules.game.echelon.service import EchelonService
from modules.game.eliminate_raid.service import EliminateRaidService
from modules.game.equipment.service import EquipmentService
from modules.game.event.service import EventService
from modules.game.event_content.service import EventContentService
from modules.game.friend.service import FriendService
from modules.game.item.service import ItemService
from modules.game.mail.service import MailService
from modules.game.management.service import ManagementService
from modules.game.memory_lobby.service import MemoryLobbyService
from modules.game.mini_game.service import MiniGameService
from modules.game.mission.service import MissionService
from modules.game.momotalk.service import MomoTalkService
from modules.game.permanent_raid.service import PermanentRaidService
from modules.game.player.academy.service import AcademyService
from modules.game.player.cafe.service import CafeService
from modules.game.raid.service import RaidService
from modules.game.scenario.service import ScenarioService
from modules.game.school_dungeon.service import SchoolDungeonService
from modules.game.shop.service import ShopService
from modules.game.sweep.service import SweepService
from modules.game.system.service import SystemService
from modules.game.toast.service import ToastService
from modules.game.week_dungeon.service import WeekDungeonService
from modules.game.world_raid.service import WorldRaidService
from modules.runtime.android_mobile_profile import (
    app_version_code_from_client_version,
    fetch_galaxy_store_client_version,
)


@dataclass(frozen=True)
class LoginResult:
    account_id: int | None = None
    nickname: str | None = None
    level: int | None = None
    exp: int | None = None
    friend_code: str | None = None
    publisher_account_id: int | None = None
    attendance: dict[str, _Any] | None = None
    profile: dict[str, _Any] | None = None
    session: dict[str, _Any] | None = None
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
            attendance=extract_attendance_cache(account_data),
            profile=_profile_from_integrated(value),
            session=_session_from_integrated(value),
            credentials=getattr(value, "credentials", None),
            logs=tuple(logs or ()),
        )

    def __str__(self) -> str:
        values = self.summary()
        return "[" + ", ".join(f"{key}: {value}" for key, value in values.items()) + "]"

    __repr__ = __str__

    def to_dict(self) -> dict[str, _Any]:
        values = self.summary()
        values["Profile"] = self.profile
        values["Session"] = self.session
        values["Attendance"] = self.attendance
        return values

    def summary(self) -> dict[str, _Any]:
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
        self._gateway_client: BAReplayClient | None = None
        self._services: dict[str, _Any] = {}
        self._data_warning_keys: set[tuple[_Any, ...]] = set()
        self.logs: list[str] = []
        self.account = self._mount_service("account", AccountService)
        self.attachment = self._mount_service("attachment", AttachmentService)
        self.battle_pass = self._mount_service("battle_pass", BattlePassService)
        self.mission = self._mount_service("mission", MissionService)
        self.cafe = self._mount_service("cafe", CafeService)
        self.academy = self._mount_service("academy", AcademyService)
        self.mail = self._mount_service("mail", MailService)
        self.shop = self._mount_service("shop", ShopService)
        self.sweep = self._mount_service("sweep", SweepService)
        self.attendance = self._mount_service("attendance", AttendanceService)
        self.momotalk = self._mount_service("momotalk", MomoTalkService)
        self.character = self._mount_service("character", CharacterService)
        self.character_gear = self._mount_service("character_gear", CharacterGearService)
        self.campaign = self._mount_service("campaign", CampaignService)
        self.week_dungeon = self._mount_service("week_dungeon", WeekDungeonService)
        self.clan = self._mount_service("clan", ClanService)
        self.conquest = self._mount_service("conquest", ConquestService)
        self.craft = self._mount_service("craft", CraftService)
        self.echelon = self._mount_service("echelon", EchelonService)
        self.eliminate_raid = self._mount_service("eliminate_raid", EliminateRaidService)
        self.equipment = self._mount_service("equipment", EquipmentService)
        self.event = self._mount_service("event", EventService)
        self.event_content = self._mount_service("event_content", EventContentService)
        self.friend = self._mount_service("friend", FriendService)
        self.item = self._mount_service("item", ItemService)
        self.management = self._mount_service("management", ManagementService)
        self.memory_lobby = self._mount_service("memory_lobby", MemoryLobbyService)
        self.mini_game = self._mount_service("mini_game", MiniGameService)
        self.permanent_raid = self._mount_service("permanent_raid", PermanentRaidService)
        self.raid = self._mount_service("raid", RaidService)
        self.scenario = self._mount_service("scenario", ScenarioService)
        self.school_dungeon = self._mount_service("school_dungeon", SchoolDungeonService)
        self.system = self._mount_service("system", SystemService)
        self.toast = self._mount_service("toast", ToastService)
        self.world_raid = self._mount_service("world_raid", WorldRaidService)
        self._warn_if_data_not_ready()

    async def login(self, account: str, password: str) -> LoginResult:
        options = {**self.defaults, "nx_id": account, "nx_password": password}
        self.logs = []
        if self.debug:
            options["debug_logger"] = self._debug_log
        raw_result = await _login(**options)
        self.result = LoginResult.from_integrated(raw_result, logs=self.logs if self.debug else None)
        self._raw_result = raw_result if self.debug else None
        if self.result.session is not None:
            stamp_session_daily_reset(self.result.session)
            if self.result.attendance is not None:
                self.result.session.setdefault("attendance", self.result.attendance)
            self._gateway_client = self._restore_gateway_client(self.result.session)
        self._warn_if_data_not_ready()
        return self.result

    async def restore_session(
        self,
        session: _Mapping[str, _Any],
        profile: _Mapping[str, _Any] | None = None,
    ) -> LoginResult:
        if not isinstance(session, _Mapping):
            raise SessionRestoreError("session payload must be a mapping")
        restored_session = dict(session)
        restored_profile = dict(profile) if isinstance(profile, _Mapping) else None
        validate_session_daily_reset(restored_session)
        stamp_session_daily_reset(restored_session)
        self._gateway_client = self._restore_gateway_client(restored_session)
        attendance = extract_attendance_cache(restored_session.get("attendance")) or extract_attendance_cache(restored_session)
        self.result = LoginResult(profile=restored_profile, session=restored_session, attendance=attendance)
        self._raw_result = None
        self.logs = []
        self._warn_if_data_not_ready()
        return self.result

    async def aclose(self) -> None:
        if self._gateway_client is not None:
            await self._gateway_client.aclose()

    async def refresh_student_data(self) -> dict[int, str]:
        return await refresh_student_names()

    async def refresh_official_data(
        self,
        *,
        client_version: str | None = None,
        build_number: int | str | None = None,
        sqlcipher_key: bytes | str | None = None,
        sqlcipher_license: str | None = None,
        download_large: bool = True,
        show_progress: bool = True,
        workers: int | None = None,
        chunk_size: int | None = None,
        cleanup_after_parse: bool = True,
    ) -> dict[str, _Any]:
        return await self.prepare_data(
            client_version=client_version,
            build_number=build_number,
            sqlcipher_key=sqlcipher_key,
            sqlcipher_license=sqlcipher_license,
            download_large=download_large,
            show_progress=show_progress,
            workers=workers,
            chunk_size=chunk_size,
            cleanup_after_parse=cleanup_after_parse,
        )

    async def prepare_data(
        self,
        *,
        client_version: str | None = None,
        build_number: int | str | None = None,
        sqlcipher_key: bytes | str | None = None,
        sqlcipher_license: str | None = None,
        download_large: bool = True,
        show_progress: bool = True,
        workers: int | None = None,
        chunk_size: int | None = None,
        cleanup_after_parse: bool = True,
    ) -> dict[str, _Any]:
        profile = self.result.profile if self.result is not None else None
        session = self.result.session if self.result is not None else None
        version, build, source = _resolve_prepare_data_version(
            profile,
            client_version=client_version,
            build_number=build_number,
        )
        self.logs.append(f"official_data.version source={source} version={version}")
        return await prepare_global_data(
            client_version=version,
            build_number=build,
            sqlcipher_key=sqlcipher_key,
            sqlcipher_license=sqlcipher_license,
            session=session,
            profile=profile,
            download_large=download_large,
            show_progress=show_progress,
            workers=workers,
            chunk_size=chunk_size,
            cleanup_after_parse=cleanup_after_parse,
        )

    def data_status(
        self,
        *,
        client_version: str | None = None,
        build_number: int | str | None = None,
    ) -> dict[str, _Any]:
        profile = self.result.profile if self.result is not None else None
        version = client_version or _profile_text(profile, "client_version")
        build = build_number or _profile_text(profile, "app_version_code")
        return data_status(client_version=version, build_number=build)

    @property
    def credentials(self) -> _Any:
        if self.result is None:
            raise LoginRequiredError("login has not completed")
        return self.result.credentials

    @property
    def profile(self) -> dict[str, _Any] | None:
        if self.result is None:
            raise LoginRequiredError("login has not completed")
        return self.result.profile

    @property
    def session(self) -> dict[str, _Any] | None:
        if self.result is None:
            raise LoginRequiredError("login has not completed")
        return self.result.session

    @property
    def raw_result(self) -> _Any:
        return self._raw_result

    def _require_gateway_client(self) -> BAReplayClient:
        if self._gateway_client is None:
            raise LoginRequiredError("session has not been restored")
        if self.result is not None and self.result.session is not None:
            validate_session_daily_reset(self.result.session)
        return self._gateway_client

    def _restore_gateway_client(self, session: _Mapping[str, _Any]) -> BAReplayClient:
        return BAReplayClient.from_session(
            session,
            timeout=float(self.defaults.get("timeout") or 20.0),
            proxy=self.defaults.get("proxy"),
        )

    def _mount_service(self, name: str, service_type: type[_Any]) -> _Any:
        service = service_type(self)
        self._services[name] = service
        setattr(self, name, service)
        return service

    def _debug_log(self, message: str) -> None:
        self.logs.append(message)
        print(f"[HLBA] {message}", flush=True)

    def _warn_if_data_not_ready(self) -> None:
        status = self.data_status()
        if status.get("ready") or not (status.get("needs_download") or status.get("needs_update")):
            return
        key = (
            status.get("reason"),
            status.get("expected_client_version"),
            status.get("cached_client_version"),
        )
        if key in self._data_warning_keys:
            return
        self._data_warning_keys.add(key)
        warnings.warn(
            f"HLBA official data is not ready: {status.get('reason')}. "
            "Call await client.prepare_data() to download/update dependency files.",
            RuntimeWarning,
            stacklevel=2,
        )


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


def _profile_text(profile: _Any, key: str) -> str | None:
    if isinstance(profile, _Mapping):
        value = profile.get(key)
        if isinstance(value, (str, int)):
            return str(value)
    return None


def _resolve_prepare_data_version(
    profile: _Any,
    *,
    client_version: str | None,
    build_number: int | str | None,
) -> tuple[str, str | int | None, str]:
    if client_version:
        return client_version, build_number or app_version_code_from_client_version(client_version), "argument"

    profile_version = _profile_text(profile, "client_version")
    if profile_version:
        return (
            profile_version,
            build_number or _profile_text(profile, "app_version_code") or app_version_code_from_client_version(profile_version),
            "profile",
        )

    version, _raw = fetch_galaxy_store_client_version()
    return version, build_number or app_version_code_from_client_version(version), "galaxy-store"


def _first_value(*values: _Any) -> _Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def _profile_from_integrated(value: _Any) -> dict[str, _Any] | None:
    profile = getattr(value, "android_mobile_profile", None)
    if profile is not None and hasattr(profile, "to_dict"):
        return profile.to_dict()
    raw = getattr(value, "profile", None)
    if isinstance(raw, _Mapping):
        return dict(raw)
    raw = getattr(value, "android_mobile_profile", None)
    if isinstance(raw, _Mapping):
        return dict(raw)
    return None


def _session_from_integrated(value: _Any) -> dict[str, _Any] | None:
    session = getattr(value, "session", None)
    if isinstance(session, _Mapping):
        return dict(session)
    return None


__all__ = ["Client", "LoginResult"]
