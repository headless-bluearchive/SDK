from __future__ import annotations

from collections.abc import Mapping as _Mapping
from dataclasses import dataclass, field
from typing import Any as _Any
import warnings

from core.client import BAReplayClient
from core.error import LoginRequiredError, SessionRestoreError
from core.i18n import set_language as _set_language, t as _t
from core.official_data import data_status, prepare_global_data
from core.session_lifecycle import stamp_session_daily_reset, validate_session_daily_reset
from core.student_data import configure_proxy as _configure_student_data_proxy, refresh_student_names
from modules.auth.service import Login as _login
from modules.game.account.service import AccountService
from modules.game.attachment.service import AttachmentService
from modules.game.attendance.service import AttendanceService, extract_attendance_cache
from modules.game.battle_pass.service import BattlePassService
from modules.game.billing.service import BillingService, extract_billing_cache
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
from modules.game.clear_deck.service import ClearDeckService
from modules.game.content_save.service import ContentSaveService
from modules.game.field.service import FieldService
from modules.game.multi_floor_raid.service import MultiFloorRaidService
from modules.game.network_time.service import NetworkTimeService
from modules.game.notification.service import NotificationService
from modules.game.open_condition.service import OpenConditionService
from modules.game.resetable_content.service import ResetableContentService
from modules.game.sticker.service import StickerService
from modules.game.time_attack_dungeon.service import TimeAttackDungeonService
from modules.game.tts.service import TTSService
from modules.game.daily_record.service import DailyRecordService
from modules.game.recipe.service import RecipeService
from modules.game.option.service import OptionService, extract_option_cache
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
    billing: dict[str, _Any] | None = None
    options: dict[str, _Any] | None = None
    profile: dict[str, _Any] | None = None
    session: dict[str, _Any] | None = None
    logs: tuple[str, ...] = field(default_factory=tuple, repr=False, compare=False)

    @classmethod
    def from_integrated(cls, value: _Any, *, logs: list[str] | None = None) -> "LoginResult":
        flow = getattr(value, "flow", {}) or {}
        account_data = flow.get("_account_data_raw") or flow.get("account_data")
        player_data = flow.get("_player_data_raw") or flow.get("player_data")
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
            billing=_billing_from_integrated(value),
            options=_options_from_integrated(value),
            profile=_profile_from_integrated(value),
            session=_session_from_integrated(value),
            logs=tuple(logs or ()),
        )

    def __str__(self) -> str:
        values = self.summary()
        return "[" + ", ".join(f"{key}: {value}" for key, value in values.items()) + "]"

    __repr__ = __str__

    def to_dict(self) -> dict[str, _Any]:
        values = self.summary()
        values["ProfilePresent"] = self.profile is not None
        values["SessionPresent"] = self.session is not None
        values["AttendancePresent"] = self.attendance is not None
        values["BillingPresent"] = self.billing is not None
        values["OptionsPresent"] = self.options is not None
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
    def __init__(self, *, debug: bool = False, language: str | None = None, **defaults: _Any) -> None:
        self.debug = bool(debug)
        if language is not None:
            _set_language(language)
        self.defaults = dict(defaults)
        _configure_student_data_proxy(self.defaults.get("proxy"))
        self.result: LoginResult | None = None
        self._gateway_client: BAReplayClient | None = None
        self._services: dict[str, _Any] = {}
        self._data_warning_keys: set[tuple[_Any, ...]] = set()
        self.logs: list[str] = []
        self.account = self._mount_service("account", AccountService)
        self.billing = self._mount_service("billing", BillingService)
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
        self.clear_deck = self._mount_service("clear_deck", ClearDeckService)
        self.content_save = self._mount_service("content_save", ContentSaveService)
        self.field = self._mount_service("field", FieldService)
        self.open_condition = self._mount_service("open_condition", OpenConditionService)
        self.resetable_content = self._mount_service("resetable_content", ResetableContentService)
        self.time_attack_dungeon = self._mount_service("time_attack_dungeon", TimeAttackDungeonService)
        self.multi_floor_raid = self._mount_service("multi_floor_raid", MultiFloorRaidService)
        self.sticker = self._mount_service("sticker", StickerService)
        self.notification = self._mount_service("notification", NotificationService)
        self.tts = self._mount_service("tts", TTSService)
        self.network_time = self._mount_service("network_time", NetworkTimeService)
        self.daily_record = self._mount_service("daily_record", DailyRecordService)
        self.recipe = self._mount_service("recipe", RecipeService)
        self.option = self._mount_service("option", OptionService)
        self._warn_if_data_not_ready()

    async def login(self, account: str, password: str) -> LoginResult:
        region = str(self.defaults.get("region") or "").strip().lower()
        if region in ("", "auto", "detect"):
            return await self._login_auto_region(account, password)
        raw_result = await self._run_login(self.defaults, account, password)
        return self._finalize_login(raw_result)

    async def _run_login(self, base_options: _Mapping[str, _Any], account: str, password: str) -> _Any:
        options = {k: v for k, v in base_options.items() if k != "region_probe_timeout"}
        options.update(nx_id=account, nx_password=password)
        self.logs = []
        if self.debug:
            options["debug_logger"] = self._debug_log
        return await _login(**options)

    async def _login_auto_region(self, account: str, password: str) -> LoginResult:
        from modules.auth.service import LoginAutoRegion

        options = {key: value for key, value in self.defaults.items() if key != "region_probe_timeout"}
        options.pop("region", None)
        options.update(nx_id=account, nx_password=password)
        if self.debug:
            options["debug_logger"] = self._debug_log
        probe_timeout = float(self.defaults.get("region_probe_timeout") or 60.0)
        self.logs = []
        raw_result = await LoginAutoRegion(
            _auto_region_order(), region_probe_timeout=probe_timeout, **options
        )
        return self._finalize_login(raw_result)

    def _finalize_login(self, raw_result: _Any) -> LoginResult:
        self.result = LoginResult.from_integrated(raw_result, logs=self.logs if self.debug else None)
        if self.result.session is not None:
            if self.result.billing is not None:
                self.result.session.setdefault("billing", self.result.billing)
            if self.result.options is not None:
                self.result.session.setdefault("options", self.result.options)
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
            raise SessionRestoreError(_t("login.session_must_be_mapping"))
        restored_session = dict(session)
        restored_profile = dict(profile) if isinstance(profile, _Mapping) else None
        validate_session_daily_reset(restored_session)
        stamp_session_daily_reset(restored_session)
        self._gateway_client = self._restore_gateway_client(restored_session)
        attendance = extract_attendance_cache(restored_session.get("attendance")) or extract_attendance_cache(restored_session)
        billing = extract_billing_cache(restored_session.get("billing"), source="session.billing")
        if billing is not None:
            restored_session.setdefault("billing", billing)
        options = extract_option_cache(restored_session.get("options")) or extract_option_cache(restored_session)
        if options is not None:
            restored_session.setdefault("options", options)
        self.result = LoginResult(
            profile=restored_profile,
            session=restored_session,
            attendance=attendance,
            billing=billing,
            options=options,
        )
        self.logs = []
        self._warn_if_data_not_ready()
        return self.result

    async def aclose(self) -> None:
        if self._gateway_client is not None:
            await self._gateway_client.aclose()

    async def refresh_student_data(self) -> dict[int, str]:
        return await refresh_student_names(proxy=self.defaults.get("proxy"))

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
            proxy=self.defaults.get("proxy"),
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
            proxy=self.defaults.get("proxy"),
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
    def credentials(self) -> None:
        raise LoginRequiredError(_t("login.credentials_hidden"))

    @property
    def profile(self) -> dict[str, _Any] | None:
        if self.result is None:
            raise LoginRequiredError(_t("login.not_completed"))
        return self.result.profile

    @property
    def session(self) -> dict[str, _Any] | None:
        if self.result is None:
            raise LoginRequiredError(_t("login.not_completed"))
        return self.result.session

    def _require_gateway_client(self) -> BAReplayClient:
        if self._gateway_client is None:
            raise LoginRequiredError(_t("login.session_not_restored"))
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
    proxy: str | None = None,
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

    version, _raw = fetch_galaxy_store_client_version(proxy=proxy)
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


def _billing_from_integrated(value: _Any) -> dict[str, _Any] | None:
    session = getattr(value, "session", None)
    if isinstance(session, _Mapping):
        cache = extract_billing_cache(session.get("billing"), source="session.billing")
        if cache is not None:
            return cache

    flow = getattr(value, "flow", {}) or {}
    cache = extract_billing_cache(flow.get("billing"), source="flow.billing")
    if cache is not None:
        return cache

    account_data = flow.get("_account_data_raw")
    cache = extract_billing_cache(account_data, source="Account_Auth")
    if cache is not None:
        return cache

    player_data = flow.get("_player_data_raw")
    cache = extract_billing_cache(player_data, source="Account_LoginSync")
    if cache is not None:
        return cache
    return None


def _options_from_integrated(value: _Any) -> dict[str, _Any] | None:
    session = getattr(value, "session", None)
    if isinstance(session, _Mapping):
        cache = extract_option_cache(session.get("options"))
        if cache is not None:
            return cache

    flow = getattr(value, "flow", {}) or {}
    cache = extract_option_cache(flow.get("options"))
    if cache is not None:
        return cache

    account_data = flow.get("_account_data_raw") or flow.get("account_data")
    cache = extract_option_cache(account_data)
    if cache is not None:
        return cache
    return None


def _auto_region_order() -> list[str]:
    import os
    import re as _re

    from modules.runtime.region_config import ALL_REGIONS, COUNTRY_DEFAULTS

    order = list(ALL_REGIONS)
    candidates: list[str] = []
    try:
        import locale as _locale

        candidates.append((_locale.getlocale() or (None,))[0] or "")
    except Exception:
        pass
    candidates += [os.environ.get("LANG", ""), os.environ.get("LC_ALL", ""), os.environ.get("LANGUAGE", "")]
    country = ""
    for value in candidates:
        match = _re.search(r"[a-z]{2}[_-]([A-Z]{2})", value or "")
        if match:
            country = match.group(1)
            break
    guess = COUNTRY_DEFAULTS.get(country, (None,))[0] if country else None
    if guess and guess in order:
        order.remove(guess)
        order.insert(0, guess)
    return order


__all__ = ["Client", "LoginResult"]
