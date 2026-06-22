
from __future__ import annotations

import asyncio
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping

from config.game import DEFAULTS
from core.error import AuthenticationError, ConfigurationError
from modules.runtime.android_mobile_profile import (
    DEFAULT_ANDROID_MOBILE_PROFILE_PATH,
    AndroidMobileProfile,
    app_version_code_from_client_version,
    fetch_galaxy_store_client_version,
    generate_android_mobile_profile,
    load_android_mobile_profile,
    with_client_version,
)
from modules.runtime.ngsm_token import with_ngsm_fingerprint_defaults
from core.client import BAReplayClient
from modules.auth.nexon_login import (
    NexonGameCredentials,
    build_credentials,
    run_main_game_login,
    toy_login_to_dict,
)
from utils.proxy import normalize_proxy_url
from modules.runtime.region_config import profile_for
from modules.runtime.runtime_config import RuntimeConnectionInfo, discover_connection_info
from modules.auth.toysdk_android import AndroidDeviceProfile, AndroidToyConfig, AndroidToySdkClient
from modules.auth.toysdk_models import ToySdkLoginResult


@dataclass(frozen=True)
class IntegratedLoginOptions:
    country: str = DEFAULTS.country
    locale: str = DEFAULTS.locale
    region: str = ""
    env: str = DEFAULTS.env
    gid: str = DEFAULTS.service_id
    host_url: str = ""
    api_url: str = ""
    auto_host: bool = True
    android_mobile_profile_path: Path = DEFAULT_ANDROID_MOBILE_PROFILE_PATH
    no_android_mobile_profile: bool = False
    android_mobile_profile: AndroidMobileProfile | Mapping[str, Any] | None = None
    bundle_version: str = ""
    client_version: str = ""
    access_ip: str = ""
    nx_id: str = ""
    nx_password: str = ""
    nx_preflight_nexon_sn: bool = True
    store_type: str = "google"
    package_name: str = ""
    mobile_skip_enter_toy: bool = False
    mobile_create_np_token: bool = False
    mobile_skip_create_np_token: bool = False
    mobile_skip_user_info: bool = False
    android_uuid: str = ""
    android_uuid2: str = ""
    android_adid: str = ""
    android_model: str = DEFAULTS.android_model
    android_os_version: str = DEFAULTS.android_os_version
    android_app_version_code: int | None = DEFAULTS.app_version_code
    android_client_id: str = DEFAULTS.client_id
    android_game_id: str = DEFAULTS.game_id
    proxy: str = ""
    body_mode: str = DEFAULTS.body_mode
    allow_synthetic_ngsm_token: bool = True
    ngsx_attestation_mode: str = "disabled"
    ngsx_attestation_url: str = ""
    ngsx_attestation_command: str = ""
    ngsx_attestation_file: str = ""
    ngsx_attestation_timeout: float = 30.0
    ngsx_attestation_strict: bool = False
    account_check_key_mode: str = "rsa-oaep-sha1"
    account_check_url_mode: str = "wiki"
    account_check_field_mode: str = "android-minimal"
    queue_subchain: bool = False
    queue_subchain_url_mode: str = "gateway"
    queue_carry_crypto_forward: bool = False
    fetch_sqlcipher_material: bool = True
    session_bootstrap_queue: bool = True
    session_bootstrap_battle_pass_id: int | None = None
    session_bootstrap_account_link_reward: bool = False
    session_bootstrap_continue_on_error: bool = False
    skip_proof_token: bool = False
    proof_token_stage: str = "after-account-check"
    proof_token_url_mode: str = "wiki"
    proof_token_max_attempts: int | None = None
    device_id: str = ""
    device_system_memory_size: int | None = None
    game_option_language: str = ""
    account_auth_country: str = ""
    account_auth_locale: str = ""
    account_auth_advertisement_id: str = ""
    account_auth_idfv: str = ""
    account_auth_version: int | None = None
    account_auth_dev_id: str | None = None
    omit_account_auth_dev_id: bool = False
    account_auth_imei: int | None = 0
    omit_account_auth_imei: bool = False
    market_id: str = DEFAULTS.market_id
    user_type: str = ""
    timeout: float = 60.0
    debug_logger: Callable[[str], None] | None = None


@dataclass(frozen=True)
class IntegratedLoginResult:
    toy_login: ToySdkLoginResult
    credentials: NexonGameCredentials
    connection: RuntimeConnectionInfo | None
    android_mobile_profile: AndroidMobileProfile | None
    session: dict[str, Any]
    flow: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "toy_login": toy_login_to_dict(self.toy_login),
            "connection": self.connection.to_dict() if self.connection else None,
        }


def run_android_direct_login(options: IntegratedLoginOptions) -> IntegratedLoginResult:

    _log(options, "login.start")
    options = apply_region_defaults(options)
    _log(options, f"region.ready region={options.region or 'default'}")
    android_mobile_profile = resolve_android_mobile_profile(options)
    if android_mobile_profile is not None:
        _log(options, f"profile.ready device={android_mobile_profile.device_model} os={android_mobile_profile.os_version}")
    client_version, client_version_source, android_mobile_profile = resolve_client_version(
        options,
        android_mobile_profile=android_mobile_profile,
    )
    _log(options, f"client_version.ready version={client_version} source={client_version_source}")
    options = apply_android_mobile_profile_defaults(options, android_mobile_profile)
    if options.android_app_version_code in (None, 0) and client_version:
        options = replace(options, android_app_version_code=app_version_code_from_client_version(client_version))
    toy_login = resolve_toy_login(options)
    _log(options, f"toysdk.ready npSN={toy_login.np_sn} guid={_mask_tail(toy_login.guid)} npaCode={bool(toy_login.npa_code)}")

    credentials = build_credentials(
        toy_login,
        profile=android_mobile_profile.to_dict() if android_mobile_profile is not None else None,
        allow_synthetic_ngsm_token=options.allow_synthetic_ngsm_token,
    )
    host_url, api_url, connection = resolve_host_url(options)
    _log(options, f"gateway.ready gateway={host_url} wiki={api_url}")

    client = BAReplayClient(
        host_url=host_url,
        api_url=api_url,
        bundle_version=options.bundle_version or client_version or None,
        client_version=client_version,
        timeout=options.timeout,
        proxy=options.proxy,
    )
    flow = run_main_game_login(
        client,
        credentials,
        body_mode=options.body_mode,
        client_version=client_version,
        access_ip=options.access_ip,
        advertisement_id=options.account_auth_advertisement_id,
        idfv=options.account_auth_idfv,
        country=options.account_auth_country or options.country,
        locale=options.account_auth_locale or options.locale,
        device_id=options.device_id,
        os_version=options.android_os_version,
        device_model=options.android_model,
        device_system_memory_size=options.device_system_memory_size,
        market_id=options.market_id,
        user_type=options.user_type,
        game_option_language=options.game_option_language,
        account_auth_version=options.account_auth_version,
        account_auth_dev_id=options.account_auth_dev_id,
        omit_account_auth_dev_id=options.omit_account_auth_dev_id,
        account_auth_imei=options.account_auth_imei,
        omit_account_auth_imei=options.omit_account_auth_imei,
        account_check_key_mode=options.account_check_key_mode,
        account_check_url_mode=options.account_check_url_mode,
        account_check_field_mode=options.account_check_field_mode,
        queue_subchain=options.queue_subchain,
        queue_subchain_url_mode=options.queue_subchain_url_mode,
        queue_carry_crypto_forward=options.queue_carry_crypto_forward,
        fetch_sqlcipher_material=options.fetch_sqlcipher_material,
        session_bootstrap_queue=options.session_bootstrap_queue,
        session_bootstrap_battle_pass_id=options.session_bootstrap_battle_pass_id,
        session_bootstrap_account_link_reward=options.session_bootstrap_account_link_reward,
        session_bootstrap_continue_on_error=options.session_bootstrap_continue_on_error,
        skip_proof_token=options.skip_proof_token,
        proof_token_stage=options.proof_token_stage,
        proof_token_url_mode=options.proof_token_url_mode,
        proof_token_max_attempts=options.proof_token_max_attempts,
        android_mobile_profile=android_mobile_profile.to_dict() if android_mobile_profile is not None else None,
        ngsx_attestation_mode=options.ngsx_attestation_mode,
        ngsx_attestation_url=options.ngsx_attestation_url,
        ngsx_attestation_command=options.ngsx_attestation_command,
        ngsx_attestation_file=options.ngsx_attestation_file,
        ngsx_attestation_timeout=options.ngsx_attestation_timeout,
        ngsx_attestation_strict=options.ngsx_attestation_strict,
        debug_logger=options.debug_logger,
    )
    _log(options, f"login.done status={flow.get('status', '')}")
    session = client.export_session()
    attendance_cache = _attendance_cache_from_flow(flow)
    if attendance_cache is not None:
        session["attendance"] = attendance_cache
    return IntegratedLoginResult(toy_login, credentials, connection, android_mobile_profile, session, flow)


async def run_android_direct_login_async(options: IntegratedLoginOptions) -> IntegratedLoginResult:
    return await asyncio.to_thread(run_android_direct_login, options)


def apply_region_defaults(options: IntegratedLoginOptions) -> IntegratedLoginOptions:
    if options.proxy:
        options = replace(options, proxy=normalize_proxy_url(options.proxy))
    if not options.region:
        return options
    profile = profile_for(options.region, gid=options.gid)
    country = options.country
    locale = options.locale
    if country in ("", "TW") and profile.region != "tw":
        country = profile.default_country
    if locale in ("", "zh-TW") and profile.region != "tw":
        locale = profile.default_locale
    return replace(options, region=profile.region, country=country, locale=locale)


def resolve_android_mobile_profile(
    options: IntegratedLoginOptions,
) -> AndroidMobileProfile | None:
    if options.no_android_mobile_profile:
        return None
    if options.android_mobile_profile is not None:
        return with_ngsm_fingerprint_defaults(_coerce_android_mobile_profile(options.android_mobile_profile))
    profile_path = Path(options.android_mobile_profile_path).expanduser()
    if profile_path.exists():
        return with_ngsm_fingerprint_defaults(load_android_mobile_profile(profile_path))
    return with_ngsm_fingerprint_defaults(generate_android_mobile_profile(country=options.country, locale=options.locale))


def _coerce_android_mobile_profile(value: AndroidMobileProfile | Mapping[str, Any]) -> AndroidMobileProfile:
    if isinstance(value, AndroidMobileProfile):
        return value
    allowed = AndroidMobileProfile.__dataclass_fields__
    values = {key: value.get(key) for key in allowed if key in value}
    return AndroidMobileProfile(**values)


def resolve_client_version(
    options: IntegratedLoginOptions,
    *,
    android_mobile_profile: AndroidMobileProfile | None,
) -> tuple[str, str, AndroidMobileProfile | None]:
    if options.client_version:
        return (
            options.client_version,
            "options",
            update_android_mobile_profile_version(options, android_mobile_profile, options.client_version),
        )
    if android_mobile_profile and android_mobile_profile.client_version:
        updated = update_android_mobile_profile_version(
            options,
            android_mobile_profile,
            android_mobile_profile.client_version,
        )
        return android_mobile_profile.client_version, "android-mobile-profile", updated

    try:
        version, raw = fetch_galaxy_store_client_version(timeout=min(max(options.timeout, 1.0), 10.0))
        android_mobile_profile = update_android_mobile_profile_version(options, android_mobile_profile, version)
        return version, "galaxy-store", android_mobile_profile
    except Exception as exc:
        raise ConfigurationError("client_version is required and Galaxy Store lookup failed") from exc


def update_android_mobile_profile_version(
    options: IntegratedLoginOptions,
    profile: AndroidMobileProfile | None,
    version: str,
) -> AndroidMobileProfile | None:
    if profile is None or not version:
        return profile
    return with_client_version(profile, version)


def apply_android_mobile_profile_defaults(
    options: IntegratedLoginOptions,
    profile: AndroidMobileProfile | None,
) -> IntegratedLoginOptions:
    if profile is None:
        return options
    return replace(
        options,
        android_mobile_profile=profile,
        package_name=options.package_name or profile.package_name,
        store_type=options.store_type or profile.store_type,
        android_uuid=options.android_uuid or profile.uuid,
        android_uuid2=options.android_uuid2 or profile.uuid2,
        android_adid=options.android_adid or profile.advertisement_id,
        android_model=profile.device_model if not options.android_model and profile.device_model else options.android_model,
        android_os_version=profile.os_version if not options.android_os_version and profile.os_version else options.android_os_version,
        android_app_version_code=(
            profile.app_version_code
            if (options.android_app_version_code in (None, 0) and profile.app_version_code is not None)
            else options.android_app_version_code
        ),
        device_id=options.device_id or profile.device_unique_id,
        device_system_memory_size=options.device_system_memory_size or profile.system_memory_mb,
        account_auth_country=options.account_auth_country or profile.country,
        account_auth_locale=options.account_auth_locale or profile.locale,
        account_auth_advertisement_id=options.account_auth_advertisement_id or profile.advertisement_id,
        account_auth_idfv=options.account_auth_idfv or profile.idfv,
    )


def resolve_toy_login(options: IntegratedLoginOptions) -> ToySdkLoginResult:
    client = build_android_toy_client(options)
    if options.nx_id and options.nx_password:
        session = client.login_with_nx_flow(
            options.nx_id,
            options.nx_password,
            enter_toy=not options.mobile_skip_enter_toy,
            get_user_info=not options.mobile_skip_user_info,
            preflight_nexon_sn=options.nx_preflight_nexon_sn,
        )
        login = session.to_toy_login_result()
        return login
    raise AuthenticationError("account and password are required for Android direct login")


def build_android_toy_client(options: IntegratedLoginOptions) -> AndroidToySdkClient:
    package_name = options.package_name or DEFAULTS.package_name
    mobile_profile = options.android_mobile_profile
    runtime_country = mobile_profile.country if mobile_profile is not None else options.country
    runtime_locale = mobile_profile.locale if mobile_profile is not None else options.locale
    initial_country = mobile_profile.initial_country if mobile_profile is not None else options.country
    device_country = mobile_profile.device_country if mobile_profile is not None else options.country
    config = AndroidToyConfig(
        service_id=str(options.gid),
        client_id=str(options.android_client_id),
        game_id=str(options.android_game_id),
        package_name=package_name,
        store_type=options.store_type or DEFAULTS.store_type,
        app_version_code=int(options.android_app_version_code or DEFAULTS.app_version_code),
    )
    device = AndroidDeviceProfile(
        country=runtime_country,
        locale=runtime_locale,
        initial_country=initial_country,
        device_country=device_country,
        uuid=options.android_uuid,
        uuid2=options.android_uuid2,
        os="A",
        os_version=options.android_os_version,
        device_model=options.android_model,
        carrier_name=mobile_profile.carrier_name if mobile_profile is not None else "",
        mnc=int((mobile_profile.mnc if mobile_profile is not None else 0) or 0),
        mcc=int((mobile_profile.mcc if mobile_profile is not None else 0) or 0),
        advertising_id=options.android_adid,
        app_set_scope=mobile_profile.app_set_scope if mobile_profile else 0,
        app_set_id=mobile_profile.app_set_id if mobile_profile else "",
    )
    return AndroidToySdkClient(
        config=config,
        device=device,
        proxy=options.proxy,
        timeout=options.timeout,
    )


def resolve_host_url(options: IntegratedLoginOptions) -> tuple[str, str, RuntimeConnectionInfo | None]:
    if options.host_url:
        return options.host_url, options.api_url, None
    if not options.auto_host:
        return "", options.api_url, None
    connection = discover_connection_info(country=options.country, region=options.region)
    return connection.gateway_url, options.api_url or connection.api_url, connection


def _log(options: IntegratedLoginOptions, message: str) -> None:
    if options.debug_logger is not None:
        options.debug_logger(message)


def _mask_tail(value: str, tail: int = 4) -> str:
    text = str(value or "")
    if not text:
        return ""
    return "*" * max(len(text) - tail, 0) + text[-tail:]


def _attendance_cache_from_flow(flow: Mapping[str, Any]) -> dict[str, Any] | None:
    account_data = flow.get("account_data")
    if not isinstance(account_data, Mapping):
        return None
    rewards = account_data.get("AttendanceBookRewards")
    history = account_data.get("AttendanceHistoryDBs")
    if rewards is None and history is None:
        return None
    return {
        "source": "Account_Auth",
        "AttendanceBookRewards": _as_list(rewards),
        "AttendanceHistoryDBs": _as_list(history),
    }


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]
